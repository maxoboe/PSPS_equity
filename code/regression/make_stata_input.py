import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import datetime
from dateutil import parser
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import sys
if ('Users/maxv' in os.getcwd()):
    base = "/Users/maxv/Dropbox (MIT)/inferring_expectations/" 
else:
    base = '/pool001/vilgalys/inferring_expectations/'
sys.path.append(os.path.abspath(base + "code/"))
import global_constants
import read_write

out_folder = base + 'outputs/regressions/'
pd.options.mode.chained_assignment = None

ignition_db = read_write.read_ignitions(merge_community=False)
ignition_db['date_str'] = ignition_db.date.astype(str)
ignition_db = ignition_db.groupby(['identifier','date_str']).mean()
circuit_db = read_write.read_circuit(merge_community=True, red_flag=False)
circuit_db['date_str'] = circuit_db['date'].astype(str)
circuit_db = circuit_db[circuit_db.date_str > '2013-10-01']
circuit_db = circuit_db.set_index(['identifier','date_str'])

merged = pd.merge(circuit_db, ignition_db, how='left', 
    left_index=True, right_index=True, copy=False, indicator=True)
ignition_db = ignition_db.reset_index()
merged['ignition'] = (merged['_merge']=='both').astype(int)
merged = merged.drop(columns='_merge')

# red_flag_db = read_write.read_circuit(merge_community=False, red_flag=True)
# red_flag_db['date_str'] = red_flag_db['date'].astype(str)
# red_flag_db = red_flag_db[red_flag_db.date_str > '2013-10-01']
# red_flag_db = red_flag_db.set_index(['identifier','date_str'])
# merged = pd.merge(merged, red_flag_db[[]], how='left', left_index=True, right_index=True,
#                     copy=False, indicator=True)
# merged['red_flag'] = (merged['_merge']=='both').astype(int)
# merged = merged.drop(columns='_merge')

psps_db = read_write.read_psps(merge_community=False, return_db=True)
psps_db['date_str'] = psps_db['date'].astype(str)
psps_db = psps_db.groupby(['identifier','date_str']).sum()
# psps_db = psps_db.set_index(['identifier','date_str'])
merged = pd.merge(merged, psps_db[['CMI','TOTAL CUST', 'Outage Hou']], how='left', left_index=True, right_index=True,
                    copy=False, indicator=True)
merged['psps'] = (merged['_merge'] == 'both').astype(int)
merged = merged.drop(columns='_merge')
psps_db = psps_db.reset_index()
psps_db['Utility'] = psps_db.identifier.apply(lambda x: x.split('_')[-1])
merged = merged.reset_index()
has_year_utility = []
for year in range(2013, 2022):
    for Utility in psps_db.Utility.unique():
        if year in psps_db[psps_db.Utility == Utility].year.unique():
            has_year_utility.append('{}_{}'.format(year, Utility))
merged['year_utility'] = merged['year_x'].astype(str) + '_' + merged['Utility']
merged['has_year_utility'] = (merged.year_utility.isin(has_year_utility)).astype(int)
merged['shutoff_flag'] = (~merged.year_utility.isin(has_year_utility)).astype(int)
merged['shutoff_flag'] = np.where(merged.year_x >= 2014, merged['shutoff_flag'], 0)
merged['all_flag'] = 1
merged['red_flag'] = merged['red_flag'].astype(int)
merged['nonzero_ignition_flag'] = (merged.identifier.isin(ignition_db.identifier.unique())).astype(int)
merged['nonzero_psps_flag'] = (merged.identifier.isin(psps_db.identifier.unique())).astype(int)

population_frame = psps_db.groupby('identifier')[['TOTAL CUST']].mean()
population_frame = population_frame.rename(columns={'TOTAL CUST': 'average_customers'})
merged = pd.merge(merged, population_frame, left_on=['identifier'], right_index=True, how='left')

ica_gdb = gpd.read_file(base + 'data/all_ica_maps/')
ica_gdb = ica_gdb.to_crs("EPSG:4328")
ica_gdb['length'] = ica_gdb.geometry.length
ica_gdb['identifier'] = ica_gdb['clean_name'] + '_' + ica_gdb['Utility']
ica_gdb = ica_gdb[['identifier','length']]
merged = pd.merge(merged, ica_gdb, how='left', on='identifier', copy=False)
# merged['sdge_voll'] = (merged.psps + merged.TOTAL_CUST )/3
# merged['VoLL'] = np.where(merged.Utility == 'SDG&E', merged.sdge_voll, merged.CMI)

prefixes = global_constants.prefixes

for prefix in prefixes + ['elevation']: 
    merged[prefix] = merged[prefix].astype(float)

merged.to_stata("/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", write_index=False)

print(np.sum(merged['red_flag']))
