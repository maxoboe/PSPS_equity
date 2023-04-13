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

""" 
Read files from all utilities 
"""
ica_gdb = gpd.read_file(base + 'data/all_ica_maps/')
ica_gdb.head()
ica_lat_lon = ica_gdb.to_crs("EPSG:4326")
ica_lat_lon.head()

nws = gpd.read_file(base + 'data/nws_gdb')
def contime(text):
    """Convert text into a UTC datetime."""
    if text is None: return None
    # The 0000 is the standard VTEC undefined time
    if text.startswith("0000"):
        return None
    ts = datetime.datetime.strptime(text, "%Y%m%d%H%M")
    # NWS has a bug sometimes whereby 1969 or 1970s timestamps are emitted
    return ts
nws = nws[nws.PHENOM == 'FW']
nws['issued'] = nws['ISSUED'].apply(contime)
nws['expired'] = nws['EXPIRED'].apply(contime)
nws['init_exp'] = nws['INIT_EXP'].apply(contime)
nws['init_iss'] = nws['INIT_ISS'].apply(contime)
nws = nws.to_crs(epsg=4326)
nws['start_date'] = (np.minimum(nws.init_iss.dt.date, nws.issued.dt.date).apply(pd.to_datetime) - datetime.datetime(1900,1,1)).dt.days
nws['end_date'] = (np.maximum(nws.init_exp.dt.date, nws.expired.dt.date).apply(pd.to_datetime) - datetime.datetime(1900,1,1)).dt.days
nws.head()

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

out_fp = '/nobackup1/vilgalys/gridmet_red_flag_circuits.csv'
if os.path.exists(out_fp):
    os.remove(out_fp)
file_exists = False
# Read all of the datasupply things separately! 
# Maybe get subsets of them since we started seeing records of Red Flag warnings? 
# The intersection of this plus red flags might be another whole big thing 

for i, row in ica_lat_lon.iterrows():
    fire_warnings = nws[nws.intersects(row.geometry)]
    if len(fire_warnings) == 0: 
        fire_dates = []
    else:
        fire_dates = np.arange(np.min(fire_warnings['start_date']), np.max(fire_warnings['end_date'] + 1))
        fire_dates = fire_dates[[any((date >= fire_warnings.start_date) & (date <= fire_warnings.end_date)) for date in fire_dates]]
    zero_dist_matches = np.where(s.distance(row.geometry) == 0)
    overlap = np.zeros(len(s))
    overlap[zero_dist_matches] = s.iloc[zero_dist_matches].intersection(row.geometry).length
    overlap = overlap.reshape(orig_shape)
    overall_df = None
    date_range = time_series.isin(fire_dates).values
    for prefix, ds in ds_dict.items():
        mask = mask_dict[prefix][0,...]
        mask_overlap = np.multiply(overlap.copy(), ~mask)
        mask_overlap = mask_overlap.flatten()
        flat_vals = ds.reshape((ds.shape[0], -1))
        means = np.tensordot(flat_vals, mask_overlap, axes=1) / np.sum(mask_overlap)
        means = means.reshape(-1,1)
        # means = means[date_range, ...]
        sub_df = pd.DataFrame(means,columns = [prefix])
        sub_df['date'] = time_series
        sub_df = sub_df[sub_df['date'] >= 41273] # Excludes values before 1/1/2013
        # sub_df['date'] = [datetime.date(1900,1,1) + \
        #         datetime.timedelta(int(d)) for d in time_series]# [date_range]]
        # sub_df = sub_df[sub_df.date >= datetime.date(2013,1,1)]
        sub_df = sub_df.set_index('date')
        if overall_df is None:
            overall_df = sub_df
        else:
            overall_df = overall_df.merge(sub_df, left_index=True, right_index=True, how='outer')
    overall_df = overall_df.reset_index()
    overall_df['red_flag'] = overall_df.date.isin(fire_dates).values
    overall_df['date'] = [datetime.date(1900,1,1) + \
                datetime.timedelta(int(d)) for d in overall_df['date']]
    overall_df['clean_name'] = row['clean_name']
    overall_df['Utility'] = row['Utility']
    overall_df['elevation'] = np.dot(elevation_ds['elevation'][...].reshape(-1), mask_overlap) / np.sum(mask_overlap)
    overall_df.to_csv(out_fp, mode='a',index=False, header=~file_exists)
    file_exists = True
