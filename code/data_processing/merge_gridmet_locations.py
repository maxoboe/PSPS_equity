import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import rtree
import netCDF4 as nc
import os
import datetime
import time
import csv
from shapely.geometry import Point
from dateutil import parser
base = '/pool001/vilgalys/inferring_expectations/'

geospatial_resolution = 0.041666666666666
min_dist = geospatial_resolution / np.sqrt(2)

""" 
Read FPA fire locations 
"""
fire_gdb = gpd.read_file(base + 'data/FPA_FOD_20210617.gdb')
fire_gdb = fire_gdb[fire_gdb.STATE == 'CA']
def parse_time(text):
    if text is None: return None
    text = text.split('T')[0]
    return parser.parse(text, dayfirst=False)
fire_gdb['discovery_date'] = fire_gdb['DISCOVERY_DATE'].apply(parse_time)
fire_gdb['cont_date'] = fire_gdb['CONT_DATE'].apply(parse_time)
fire_gdb['days_since'] = (fire_gdb.discovery_date - datetime.datetime(1900,1,1)).dt.days
fire_gdb['UniqueID'] = 'FPA_' + fire_gdb.FPA_ID
fire_gdb.head()

"""
Read WFIGS fire locations
"""
wfigs = pd.read_csv(base + 'data/WFIGS_locations.csv')
wfigs = wfigs[wfigs.POOState == 'US-CA']
def parse_time(text):
    if str(text) == 'nan': return None
    text = text.split(' ')[0]
    return parser.parse(text, dayfirst=False)
wfigs['discovery_date'] = wfigs['FireDiscoveryDateTime'].apply(parse_time)
wfigs['cont_date'] = wfigs['ContainmentDateTime'].apply(parse_time)
wfigs = wfigs[wfigs.discovery_date.dt.year >= 2019]
wfigs = wfigs[wfigs.discovery_date.dt.year < 2022]
wfigs['FIRE_SIZE'] = np.where(np.isfinite(wfigs.CalculatedAcres), wfigs['CalculatedAcres'], wfigs['DailyAcres'])
wfigs['days_since'] = (wfigs.discovery_date - datetime.datetime(1900,1,1)).dt.days
wfigs['LATITUDE'] = wfigs.Y
wfigs['LONGITUDE'] = wfigs.X
wfigs['UniqueID'] = wfigs.UniqueFireIdentifier

complete_fires = fire_gdb[['UniqueID','FIRE_SIZE','discovery_date','cont_date', 'days_since', 'LATITUDE','LONGITUDE']]
complete_fires = complete_fires.append(wfigs[['UniqueID','FIRE_SIZE','discovery_date','cont_date', 'days_since', 'LATITUDE','LONGITUDE']])

service_area_db = gpd.read_file(base + 'data/Utility_Service_Areas.shp').to_crs(epsg=4326)
service_area_db = service_area_db[service_area_db['Acronym'].isin(['SCE','PG&E','SDG&E'])]

elevation_fp = base + 'data/gridmet/cal_elevationdata.nc'
elevation_ds = nc.Dataset(elevation_fp, 'r')
x_orig, y_orig = np.meshgrid(elevation_ds['lat'], elevation_ds['lon'], indexing='ij')
x, y = x_orig.flatten(), y_orig.flatten()
orig_shape = elevation_ds['elevation'].shape
s = pd.DataFrame(np.concatenate((x.reshape(-1,1),y.reshape(-1,1)), axis=1), columns = ['lat', 'lon'])
s.head()

"""
Read GridMET files into memory
"""
prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc','pdsi']
# prefixes = ['pdsi', 'sph', 'vpd', 'pr']
ds_dict = {}
time_series = None
for prefix in prefixes:
    start = time.time();
    ds = nc.Dataset(base + \
                    'data/gridmet/cal_{}.nc'.format(prefix + '_full' if prefix == 'pdsi' else prefix), 'r')
    if time_series is None:
        time_series = ds['day'][:]
    else:
        assert all(time_series == ds['day'][:])
    varname = list(ds.variables)[-1]
    ds_dict[prefix] = np.array(ds[varname][:])

out_fp = '/nobackup1/vilgalys/gridmet_fire_ignitions.csv'
with open(out_fp, 'w+', newline='') as outfile:
    fieldnames = ['UniqueID','FIRE_SIZE','discovery_date','cont_date', 'LATITUDE','LONGITUDE', 'elevation','num_matches', 'utility'] + prefixes +\
                [x + '_max' for x in prefixes] + [x + '_std' for x in prefixes]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    # Maybe for now, write to an ongoing csv file in nobackup (if we can even fit these things into memory )
    for i, row in complete_fires.iterrows():
        closest_points = ((np.abs(s.lat - row['LATITUDE']) <= geospatial_resolution ) & \
                       (np.abs(s.lon - row['LONGITUDE']) <= geospatial_resolution )).values
        multi_index = closest_points.reshape(orig_shape)
        weights = np.sqrt((s.lat - row['latitude'])**2 + (s.lon - row['LONGITUDE'])**2)[closest_points]
        x_matches, y_matches = np.where(multi_index)
        date_match = np.where(time_series == row['days_since'])[0][0]
        entry = {}
        for field in ['UniqueID','FIRE_SIZE','discovery_date','cont_date', 'LATITUDE','LONGITUDE']:
            entry[field] = row[field]
        if len(x_matches) == 0:
            entry['num_matches'] = 0 
            writer.writerow(entry)
        else:
            for prefix, ds in ds_dict.items():
                matches = ds[date_match,x_matches, y_matches]
                entry[prefix] = float(np.average(matches, weights=weights))
                entry[prefix + '_max'] = float(np.max(matches))
                entry[prefix + '_std'] = float(np.std(matches))
            entry['elevation'] = np.average(np.array(elevation_ds['elevation'])[...,x_matches,y_matches], weights=weights)
            entry['num_matches'] = len(matches)
            utility_matches = service_area_db.contains(Point(row['LONGITUDE'], row['LATITUDE'])).values
            if any(utility_matches):
                assert np.sum(utility_matches) == 1, "More than one match!"
                entry['utility'] = ['SCE','PG&E','SDG&E'][np.where(utility_matches)[0][0]]
            else:
                entry['utility'] = 'other'
            writer.writerow(entry)
