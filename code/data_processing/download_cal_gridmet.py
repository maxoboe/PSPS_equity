import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import netCDF4 as nc
import urllib.request
base = '/pool001/vilgalys/inferring_expectations/'
raw_directory = '/nobackup1/vilgalys/raw_wget/'

state_fp = base + 'data/shapes/cb_2016_us_state_500k/cb_2016_us_state_500k.shp'
state_df = gpd.read_file(state_fp)
state_df = state_df[state_df.STUSPS.isin(['CA'])]
minx, miny, maxx, maxy = state_df.to_crs(epsg=4326).bounds.values[0]
minx = minx - 0.05
miny = miny - 0.05
maxx = maxx + 0.05
maxy = maxy + 0.05
year_range = np.arange(1979, 2022)
prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc']


# Special case: download for elevation data, which does not change yearly
url = 'https://climate.northwestknowledge.net/METDATA/data/metdata_elevationdata.nc'
fp = '/nobackup1/vilgalys/raw_wget/metdata_elevationdata.nc'
urllib.request.urlretrieve(url,fp)
ds = nc.Dataset(fp)
lat=np.array(ds['lat'])
lon = np.array(ds['lon'])
outfile = base + 'data/gridmet/cal_elevationdata.nc'
cal_subset = nc.Dataset(outfile, 'w', clobber=True)
lat_subset = ds['lat'][(lat <= maxy) & (lat >= miny)]
lon_subset = ds['lon'][(lon <= maxx) & (lon >= minx)]
_lat = cal_subset.createDimension("lat", len(lat_subset))
_lon = cal_subset.createDimension("lon", len(lon_subset))
cal_lat = cal_subset.createVariable("lat","f8",("lat",))
cal_lon = cal_subset.createVariable("lon","f8",("lon",))
cal_elevation = cal_subset.createVariable("elevation","i4",("lat","lon",))
cal_lat[:] = lat_subset
cal_lon[:] = lon_subset
cal_elevation[:] = ds['elevation'][...,(lat <= maxy) & (lat >= miny), (lon <= maxx) & (lon >= minx)]
cal_subset.close()
ds.close()

# special download for pdsi 
url = 'https://www.northwestknowledge.net/metdata/data/pdsi.nc'
fp = raw_directory + 'pdsi.nc'
# urllib.request.urlretrieve(url,fp)
ds = nc.Dataset(fp, 'r')
lat=ds['lat']
lon = ds['lon']
outfile = base + 'data/gridmet/cal_pdsi_float.nc'
cal_subset = nc.Dataset(outfile, 'w', clobber=True)
lat_subset = ds['lat'][(lat <= maxy) & (lat >= miny)]
lon_subset = ds['lon'][(lon <= maxx) & (lon >= minx)]
_lat = cal_subset.createDimension("lat", len(lat_subset))
_lon = cal_subset.createDimension("lon", len(lon_subset))
_day = cal_subset.createDimension("day", None)
cal_lat = cal_subset.createVariable("lat","f8",("lat",))
cal_lon = cal_subset.createVariable("lon","f8",("lon",))
cal_day = cal_subset.createVariable("day","i8",("day",))
cal_pdsi = cal_subset.createVariable("pdsi","f8",("day","lat","lon",))
cal_lat[:] = lat_subset
cal_lon[:] = lon_subset
cal_day[:] = ds['day'][:]
cal_pdsi[:] = ds['pdsi'][...,(lat <= maxy) & (lat >= miny), (lon <= maxx) & (lon >= minx)]
cal_subset.close()
ds.close()

for prefix in prefixes:
    outfile = base + 'data/gridmet/cal_{}.nc'.format(prefix)
    year = year_range[0]
    if os.path.exists(outfile):
        os.remove(outfile)
    url = 'http://www.northwestknowledge.net/metdata/data/{}_{}.nc'.format(prefix, year)
    fp = raw_directory + '{}_{}.nc'.format(prefix, year)
    urllib.request.urlretrieve(url,fp) 
    ds = nc.Dataset(fp,'r')
    assert len(ds.variables) == 5
    varname = list(ds.variables)[-1]
    assert varname not in ['lat','lon','day','crs']
    dtype = ds[varname].datatype
    ds.close()
    cal_subset = nc.Dataset(outfile, 'w')
    _lat = cal_subset.createDimension("lat", len(lat_subset))
    _lon = cal_subset.createDimension("lon", len(lon_subset))
    _day = cal_subset.createDimension("day", None)
    cal_lat = cal_subset.createVariable("lat","f8",("lat",))
    cal_lon = cal_subset.createVariable("lon","f8",("lon",))
    cal_day = cal_subset.createVariable("day","i8",("day",))
    out_var = cal_subset.createVariable(varname,"f8",("day","lat","lon",))
    cal_lat[:] = lat_subset
    cal_lon[:] = lon_subset
    for year in year_range:
        url = 'http://www.northwestknowledge.net/metdata/data/{}_{}.nc'.format(prefix, year)
        fp = raw_directory + '{}_{}.nc'.format(prefix, year)
        urllib.request.urlretrieve(url,fp)
        ds = nc.Dataset(fp, 'r')
        time_start = out_var.shape[0]
        time_end = time_start + ds[varname].shape[0]
        cal_day[time_start:time_end] = ds['day'][:]
        out_var[time_start:time_end,:,:] = ds[varname][...,(lat <= maxy) & (lat >= miny), (lon <= maxx) & (lon >= minx)]
        ds.close()
    cal_subset.close()


"""
Interpolation between values in PDSI to generate the full time series
"""
pdsi = nc.Dataset(base + 'data/gridmet/cal_{}.nc'.format('pdsi'), 'r')
tmmn = nc.Dataset(base + 'data/gridmet/cal_{}.nc'.format('tmmn'), 'r')

lat=pdsi['lat']
lon = pdsi['lon']
outfile = base + 'data/gridmet/cal_{}.nc'.format('pdsi_full')
pdsi_full = nc.Dataset(outfile, 'w', clobber=True)
_lat = pdsi_full.createDimension("lat", len(lat))
_lon = pdsi_full.createDimension("lon", len(lon))
_day = pdsi_full.createDimension("day", None)
cal_lat = pdsi_full.createVariable("lat","f8",("lat",))
cal_lon = pdsi_full.createVariable("lon","f8",("lon",))
cal_day = pdsi_full.createVariable("day","i8",("day",))
cal_pdsi = pdsi_full.createVariable("pdsi","f8",("day","lat","lon",))
cal_lat[:] = lat[:]
cal_lon[:] = lon[:]
cal_day[:] = tmmn['day'][:]
blank_output = np.zeros(tmmn['air_temperature'].shape)
for i, _ in enumerate(pdsi['lat']):
    for j, _ in enumerate(pdsi['lon']):
        masked = pdsi['pdsi'][:,i,j].mask
        values = np.interp(tmmn['day'][:], pdsi['day'][:], pdsi['pdsi'][:,i,j])
        if isinstance(masked, np.bool_) and masked == False:
            blank_output[:,i,j] = values
        else:
            masked = np.interp(tmmn['day'][:], pdsi['day'][:], masked) > 0
            blank_output[:,i,j] = np.ma.masked_array(values, masked)
cal_pdsi[:] = blank_output
pdsi_full.close()