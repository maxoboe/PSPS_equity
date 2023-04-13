import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
if ('Users/maxv' in os.getcwd()):
    base = "/Users/maxv/Dropbox (MIT)/inferring_expectations/" 
else:
    base = '/pool001/vilgalys/inferring_expectations/'
sys.path.append(os.path.abspath(base + "code/"))
import global_constants
import datetime
from dateutil import parser

def read_income():
    income_db = pd.read_csv(base + 'data/circuit_income.csv')
    income_db['Utility'] = np.where(income_db.Utility == 'PGE', 'PG&E', income_db.Utility)
    income_db['Utility'] = np.where(income_db.Utility == 'SDGE', 'SDG&E', income_db.Utility)
    return income_db
def read_community():
    community_db = pd.read_csv(base + 'data/community_with_circuit.csv')
    community_db['clean_name'] = community_db['clean_name'].astype(str)
    community_db['Utility'] = np.where(community_db.Utility == 'PGE', 'PG&E', community_db.Utility)
    community_db['Utility'] = np.where(community_db.Utility == 'SDGE', 'SDG&E', community_db.Utility)
    return community_db

def read_psps(merge_community=False, return_db = True):
    psps_gdb = gpd.read_file(base + 'data/psps_events/psps_events.shp')
    def parse_time(text):
        if text is None: return None
        if str(text) == 'NaT': return None
        text = text.split(' ')[0]
        return parser.parse(text, dayfirst=False)
    psps_gdb['date'] = psps_gdb['Outage Sta'].apply(parse_time)
    psps_gdb['year'] = psps_gdb.date.dt.year
    psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'PGE', 'PG&E', psps_gdb.Utility)
    psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'SDGE', 'SDG&E', psps_gdb.Utility)
    psps_gdb['TOTAL CUST'] = psps_gdb['TOTAL CUST'].apply(lambda x: str(x).replace(',',''))
    psps_gdb['TOTAL CUST'] = psps_gdb['TOTAL CUST'].apply(lambda x: 0 if x == 'None' else x)
    psps_gdb['TOTAL CUST'] = psps_gdb['TOTAL CUST'].astype(int)
    psps_gdb['CMI'] = psps_gdb['TOTAL CUST'].astype(float) * psps_gdb['Outage Hou'] * 60
    psps_gdb['clean_name'] = psps_gdb['clean_name'].astype(str)
    psps_gdb['identifier'] = psps_gdb['clean_name']+ '_' + psps_gdb['Utility']
    if merge_community:
        psps_gdb = psps_gdb.merge(read_community(), on=['clean_name','Utility'], how='left')

    if return_db:
        return pd.DataFrame(psps_gdb).drop(columns=['geometry'])
    else:
        return psps_gdb

def read_ignitions(merge_community=False):
    ignition_db = pd.read_csv(base + 'data/cpuc_with_circuit.csv')
    def parse_time(text):
        text = text.split(' ')[0]
        text = text.replace('116','16') #typo from CPUC files 
        return parser.parse(text, dayfirst=False)
    ignition_db['date'] = ignition_db['Date'].apply(parse_time)
    ignition_db['year'] = ignition_db.date.dt.year
    ignition_db['clean_name'] = ignition_db['closest_circuit'].astype(str)
    ignition_db['Utiliy'] = ignition_db['utility_match']
    ignition_db['Utility'] = np.where(ignition_db.Utility == 'PGE', 'PG&E', ignition_db.Utility)
    ignition_db['Utility'] = np.where(ignition_db.Utility == 'SDGE', 'SDG&E', ignition_db.Utility)
    if merge_community:
        ignition_db = ignition_db.merge(read_community(), on=['clean_name','Utility'], how='left')
        ignition_db = ignition_db[['date','clean_name','Utility','weighted_mean_AGI','year']]
    else:
        ignition_db = ignition_db[['date','clean_name','Utility','year']]
    ignition_db['identifier'] = ignition_db['clean_name'] + '_' + ignition_db['Utility']
    return ignition_db

def read_circuit(merge_community=False, red_flag=True):
    circuit_db = pd.read_csv(base + 'data/gridmet/gridmet_red_flag_circuits.csv')
    circuit_db = circuit_db[circuit_db.date != 'date']
    circuit_db['red_flag'] = np.where(circuit_db.red_flag == 'True', 1, circuit_db.red_flag)
    circuit_db['red_flag'] = np.where(circuit_db.red_flag == 'False', 0, circuit_db.red_flag)
    circuit_db['red_flag'] = circuit_db['red_flag'].astype(int)
    if red_flag: 
        circuit_db = circuit_db[circuit_db.red_flag]
        # circuit_db = pd.read_csv('/nobackup1/vilgalys/gridmet_all_circuits.csv')
    circuit_db['clean_name'] = circuit_db['clean_name'].astype(str)
    circuit_db['Utility'] = np.where(circuit_db.Utility == 'PGE', 'PG&E', circuit_db.Utility)
    circuit_db['Utility'] = np.where(circuit_db.Utility == 'SDGE', 'SDG&E', circuit_db.Utility)
    if merge_community:
        circuit_db = circuit_db.merge(read_community(), on=['clean_name','Utility'],
                        how='left')
    for pref in global_constants.prefixes:
        circuit_db[pref] = circuit_db[pref].astype(float)
    def parse_time(text):
        if text is None: return None
        return parser.parse(text, dayfirst=False)
    circuit_db['year'] = circuit_db.date.apply(parse_time).dt.year
    circuit_db['identifier'] = circuit_db['clean_name']+ '_' + circuit_db['Utility']
    # circuit_subset['date_str'] = circuit_subset['date'].astype(str)
    #     psps_subset['date_str'] = psps_subset['date'].astype(str)
    return circuit_db

def read_fire():
    fire_db = pd.read_csv(base + 'data/gridmet/gridmet_fire_ignitions.csv')
    def parse_time(text):
        if text is None: return None
        if str(text) == 'NaT': return None
        text = text.split(' ')[0]
        return parser.parse(text, dayfirst=False)
    fire_db = fire_db[np.isfinite(fire_db.FIRE_SIZE)]
    fire_db = fire_db[np.isfinite(fire_db[global_constants.prefixes[0]])]
    fire_db['discovery_date'] = fire_db['discovery_date'].apply(parse_time)
    fire_db['cont_date'] = fire_db['cont_date'].apply(parse_time)
    for prefix in global_constants.prefixes:
        fire_db[prefix] = fire_db[prefix].astype(float)
    fire_db['year'] = fire_db['discovery_date'].dt.year
    return fire_db

def plot_predictions(true_val, predicted, marker, value="value",unit="", fp=None, 
                    out_folder=base + 'outputs/summary_stats/'):
    f, ax = plt.subplots(figsize=(7, 7))
    sns.scatterplot(x=predicted, y=true_val, hue=marker)
    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    ]
    ax.set_ylabel("true {} {}".format(value, unit))
    ax.set_xlabel("predicted {} {}".format(value, unit))
    ax
    # now plot both limits against eachother
    ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    if fp is None:
        plt.show()
    else:
        plt.savefig(out_folder + fp, dpi=200)
        plt.close()
