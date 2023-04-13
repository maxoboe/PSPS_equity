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
from shapely.geometry import Point, MultiPoint
base = '/pool001/vilgalys/inferring_expectations/'

geospatial_resolution = 0.041666666666666
min_dist = geospatial_resolution / np.sqrt(2)

state_fp = base + 'data/shapes/cb_2016_us_state_500k/cb_2016_us_state_500k.shp'
state_df = gpd.read_file(state_fp)
state_df = state_df[state_df.STUSPS.isin(['CA'])]
state_df = state_df.to_crs(epsg=4326)
service_area_db = gpd.read_file(base + 'data/Utility_Service_Areas.shp').to_crs(epsg=4326)
service_area_db = service_area_db[service_area_db['Acronym'].isin(['SCE','PG&E','SDG&E'])]

input_df = service_area_db[['Acronym','geometry']]
state_df['Acronym'] = 'ALL_CA'
input_df = input_df.append(state_df[['Acronym','geometry']])

# make geodatabase of all points in california 
elevation_fp = base + 'data/gridmet/cal_elevationdata.nc'
elevation_ds = nc.Dataset(elevation_fp, 'r')
x_orig, y_orig = np.meshgrid(elevation_ds['lat'], elevation_ds['lon'], indexing='ij')
x, y = x_orig.flatten(), y_orig.flatten()
orig_shape = elevation_ds['elevation'].shape
width = geospatial_resolution / 2
s = gpd.GeoSeries([MultiPoint([[_y - width, _x - width], [_y + width, _x + width]]).envelope for _x, _y in zip(x, y)])


prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc','pdsi']
# prefixes = ['pdsi', 'sph', 'vpd', 'pr']
ds_dict = {}
mask_dict = {}
time_series = None
for prefix in prefixes:
    ds = nc.Dataset(base + \
                    'data/gridmet/cal_{}.nc'.format(prefix + '_full' if prefix == 'pdsi' else prefix), 'r')
    if time_series is None:
        time_series = ds['day'][:]
    else:
        assert all(time_series == ds['day'][:])
    varname = list(ds.variables)[-1]
    mask_dict[prefix] = ds[varname][:].mask
    ds_dict[prefix] = np.array(ds[varname][:])
    ds.close()
time_series = pd.Series(time_series)

out_fp = '/nobackup1/vilgalys/gridmet_by_utility.csv'
if os.path.exists(out_fp):
    os.remove(out_fp)
file_exists = False
# Read all of the datasupply things separately! 
# Maybe get subsets of them since we started seeing records of Red Flag warnings? 
# The intersection of this plus red flags might be another whole big thing 

# Maybe for now, write to an ongoing csv file in nobackup (if we can even fit these things into memory )
for i, row in input_df.iterrows():
    overlap = s.intersection(row.geometry.buffer(0)).area.values.reshape(orig_shape)
    overall_df = None
    for prefix, ds in ds_dict.items():
        mask = mask_dict[prefix][0,...]
        mask_overlap = np.multiply(overlap.copy(), ~mask)
        mask_overlap = mask_overlap.flatten()
        flat_vals = ds.reshape((ds.shape[0], -1))
        means = np.tensordot(flat_vals, mask_overlap, axes=1) / np.sum(mask_overlap)
        means = means.reshape(-1,1)
        sub_df = pd.DataFrame(means, columns=[prefix])
        sub_df['date'] = [datetime.date(1900,1,1) + \
                datetime.timedelta(int(d)) for d in time_series]
        sub_df = sub_df.set_index('date')
        if overall_df is None:
            overall_df = sub_df
        else:
            overall_df = overall_df.merge(sub_df, left_index=True, right_index=True, how='outer')
    overall_df = overall_df.reset_index()
    overall_df['utility'] = row['Acronym']
    overall_df.to_csv(out_fp, mode='a',index=False, header=~file_exists)
    file_exists = True
