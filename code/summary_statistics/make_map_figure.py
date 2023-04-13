import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
import seaborn as sns
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import re
import os
if ('Users/maxv' in os.getcwd()):
    base = "/Users/maxv/Dropbox (MIT)/inferring_expectations/" 
else:
    base = '/pool001/vilgalys/inferring_expectations/'

state_fp = base + 'data/shapes/cb_2016_us_state_500k/cb_2016_us_state_500k.shp'
state_df = gpd.read_file(state_fp)
state_df = state_df[state_df.STUSPS.isin(['CA'])]
state_df = state_df.to_crs(epsg=2163)
service_area_db = gpd.read_file(base + 'data/Utility_Service_Areas.shp').to_crs(epsg=2163)
service_area_db = service_area_db[service_area_db['Acronym'].isin(['SCE','PG&E','SDG&E'])]
service_area_db['coords'] = service_area_db['geometry'].apply(lambda x: x.representative_point().coords[:][0])

psps_gdb = gpd.read_file(base + 'data/psps_events/psps_events.shp')
psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'PGE', 'PG&E', psps_gdb.Utility)
psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'SDGE', 'SDG&E', psps_gdb.Utility)
overall_circuits = gpd.read_file(base + 'data/all_ica_maps/')
overall_circuits['identifier'] = overall_circuits.clean_name + '_' + overall_circuits.Utility
psps_gdb['identifier'] = psps_gdb.clean_name + '_' + psps_gdb.Utility
overall_circuits['psps_flag'] = np.where(overall_circuits.identifier.isin(psps_gdb.identifier.unique()), 
                                        1, 0)
overall_circuits['psps'] = np.where(overall_circuits.identifier.isin(psps_gdb.identifier.unique()), 
                                        'PSPS', 'No PSPS')
fire_db = pd.read_csv(base + 'data/cpuc_with_circuit.csv')
overall_circuits['fire_flag'] = np.where(overall_circuits.identifier.isin(fire_db.identifier.unique()), 
                                        1, 0)
overall_circuits['fire'] = np.where(overall_circuits.identifier.isin(fire_db.identifier.unique()), 
                                        'Ignition', 'No Ignition')
overall_circuits['flag'] = np.where(overall_circuits.fire_flag, 'Ignition only', 'Neither')
overall_circuits['flag'] = np.where(overall_circuits.psps_flag, 'PSPS only', overall_circuits.flag)
overall_circuits['flag'] = np.where(overall_circuits.psps_flag & overall_circuits.fire_flag,
                                    'Ignition & PSPS', overall_circuits.flag)

fig, ax = plt.subplots(1, figsize=(15, 9))
state_df.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
ax.axis('off');
cmap=ListedColormap(['#D81B60', '#FFC107'])
service_area_db.plot(ax=ax,color='none',edgecolor='gray',alpha=0.8, legend=True);
overall_circuits.plot(ax=ax,column='psps',alpha=0.9, linewidth=0.2, legend=True, cmap=cmap, 
                                categories = ['PSPS','No PSPS'])
for idx, row in service_area_db.iterrows():
    plt.annotate(text=row['Acronym'], xy=row['coords'],
                horizontalalignment='center', fontsize=12)
plt.savefig(base + 'outputs/summary_stats/circuit_map_psps.png',bbox_inches='tight', dpi=200)
plt.close()

fig, ax = plt.subplots(1, figsize=(15, 9))
state_df.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
ax.axis('off');
cmap=ListedColormap(['#D81B60', '#FFC107'])
service_area_db.plot(ax=ax,color='none',edgecolor='gray',alpha=0.8, legend=True);
overall_circuits.plot(ax=ax,column='fire',alpha=0.9, linewidth=0.2, legend=True, cmap=cmap, 
                                categories = ['Ignition','No Ignition'])
for idx, row in service_area_db.iterrows():
    plt.annotate(text=row['Acronym'], xy=row['coords'],
                horizontalalignment='center', fontsize=12)
plt.savefig(base + 'outputs/summary_stats/circuit_map_ignition.png',bbox_inches='tight', dpi=200)
plt.close()