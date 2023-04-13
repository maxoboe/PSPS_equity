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
from shapely.geometry import MultiPoint
base = '/pool001/vilgalys/inferring_expectations/'

geospatial_resolution = 0.041666666666666
min_dist = geospatial_resolution / np.sqrt(2)

""" 
Read files from all utilities 
"""
ica_gdb = gpd.read_file(base + 'data/all_ica_maps/')
ica_gdb.head()
ica_lat_lon = ica_gdb.to_crs("EPSG:4326")
ica_lat_lon.head()

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

max_length = 0
min_length = 300
out_fp = '/nobackup1/vilgalys/gridmet_all_circuits.csv'
if os.path.exists(out_fp):
    os.remove(out_fp)
header=True
# Read all of the datasupply things separately! 
# Maybe get subsets of them since we started seeing records of Red Flag warnings? 
# The intersection of this plus red flags might be another whole big thing 
# Maybe for now, write to an ongoing csv file in nobackup (if we can even fit these things into memory )
for i, row in ica_lat_lon.iterrows():
    distances = s.distance(row.geometry)
    multi_index = (distances <= min_dist).values.reshape(orig_shape)
    x_matches, y_matches = np.where(multi_index)
    overall_df = None
    for prefix, ds in ds_dict.items():
        matches = ds[...,x_matches, y_matches]
        matches = matches[:,~mask_dict[prefix][0,x_matches, y_matches]]
        means = np.mean(matches, axis=1).reshape(-1,1)
        sub_df = pd.DataFrame(means,columns = [prefix])
        sub_df['date'] = [datetime.date(1900,1,1) + \
                datetime.timedelta(int(d)) for d in time_series]
        sub_df = sub_df[sub_df.date >= datetime.date(2013,1,1)]
        sub_df = sub_df.set_index('date')
        if overall_df is None:
            overall_df = sub_df
        else:
            overall_df = overall_df.merge(sub_df, left_index=True, right_index=True, how='outer')
    overall_df = overall_df.reset_index()
    overall_df['clean_name'] = row['clean_name']
    overall_df['Utility'] = row['Utility']
    overall_df['elevation'] = np.mean(np.array(elevation_ds['elevation'])[...,x_matches,y_matches])
    overall_df.to_csv(out_fp, mode='a',index=False, header=header)
    header=False
    if len(matches) > max_length: max_length = len(matches)
    if len(matches) < min_length: min_length = len(matches)
print(min_length, max_length)