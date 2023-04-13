import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import datetime
from dateutil import parser
base = '/pool001/vilgalys/inferring_expectations/'

label_dict = {'sph': 'specific humidity',
 'vpd': 'mean vapor pressure deficit',
 'pr': 'precipitation amount',
 'rmin': 'min relative humidity',
 'rmax': 'max relative humidity',
 'srad': 'surface downwelling shortwave flux in air',
 'tmmn': 'min air temperature',
 'tmmx': 'max air temperature',
 'vs': 'wind speed',
 'th': 'wind from direction',
 'pet': 'potential evapotranspiration',
 'etr': 'potential evapotranspiration',
 'fm100': 'dead fuel moisture 100hr',
 'fm1000': 'dead fuel moisture 1000hr',
 'bi': 'burning index',
 'erc': 'energy release component',
 'pdsi': 'palmer drought severity index'}

weather_db = pd.read_csv(base + 'data/gridmet/gridmet_by_utility.csv')
weather_db = weather_db[weather_db.date != 'date']
prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc','pdsi']
for prefix in prefixes:
    weather_db[prefix] = weather_db[prefix].astype(float)
from dateutil import parser
def parse_time(text):
    if text is None: return None
    return parser.parse(text, dayfirst=False)
weather_db['year'] = weather_db.date.apply(parse_time).dt.year

circuit_db = pd.read_csv(base + 'data/gridmet/gridmet_red_flag_circuits.csv')
circuit_db = circuit_db[circuit_db.date != 'date']
for pref in prefixes:
    circuit_db[pref] = circuit_db[pref].astype(float)
def parse_time(text):
    if text is None: return None
    return parser.parse(text, dayfirst=False)
circuit_db['year'] = circuit_db.date.apply(parse_time).dt.year

grouped= weather_db.groupby(['year', 'utility']).mean().reset_index()
prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc','pdsi']
for pref in prefixes:
    grouped[label_dict[pref]] = grouped[pref]
    p = sns.lmplot(x='year',y=label_dict[pref], hue='utility',data=grouped)
    plt.savefig(base + 'outputs/summary_stats/gridmet/{}.png'.format(pref))
    plt.close()

import statsmodels.api as sm
import statsmodels.formula.api as smf
service_results_dict = {}
for pref in prefixes:
    mod = smf.ols(formula='{} ~ year*utility - year'.format(pref), data=weather_db)
    res = mod.fit(cov_type='HC1')
    service_results_dict[pref] = {'params':res.params[-4:].values, 'pvalues': res.pvalues[-4:].values}
circuit_results_dict = {}
for pref in prefixes: 
    mod = smf.ols(formula='{} ~ year*Utility - year'.format(pref), data=circuit_db)
    res = mod.fit(cov_type='HC1')
    circuit_results_dict[pref] = {'params':res.params[-3:].values, 'pvalues': res.pvalues[-3:].values}

primary_variables = {'sph': 'specific humidity',
 'pr': 'precipitation amount',
 'rmin': 'min relative humidity',
 'rmax': 'max relative humidity',
 'srad': 'surface downwelling shortwave flux in air',
 'tmmn': 'min air temperature',
 'tmmx': 'max air temperature',
 'vs': 'wind speed',
 'th': 'wind from direction'}
derived_variables = {'vpd': 'mean vapor pressure deficit',
 'pet': 'potential evapotranspiration',
 'etr': 'potential evapotranspiration',
 'fm100': 'dead fuel moisture 100hr',
 'fm1000': 'dead fuel moisture 1000hr',
 'bi': 'burning index',
 'erc': 'energy release component',
 'pdsi': 'palmer drought severity index'}


def mywrite(outfile, string):
#     print(string)
    outfile.write(string.replace('_',' '))
def my_format(x, sig=3, drop_dec=False):
    if isinstance(x,str): return x
    if abs(x) > 100:
        sig = sig - int(np.log10(abs(x))) 
        sig = max(sig, 0)
    if drop_dec: return str(int(x))
    return format(x, ".{}f".format(sig))
for results_dict, data_label in zip([service_results_dict, circuit_results_dict], ['service_area', 'circuit']):
    num_fields = 4 if data_label == 'service_area' else 3
    for var_list, label in zip([primary_variables, derived_variables], ['primary','derived']):
        out_fp= base + 'outputs/summary_stats/{}_{}_table.tex'.format(data_label, label)
        with open(out_fp, 'w+') as outfile:
            mywrite(outfile,'\\begin{tabular}')
            mywrite(outfile,'{l' + 'c' * len(var_list) + '} ')
            mywrite(outfile,'\\toprule \n \\midrule \n')
            upper_strings = ["year by PG\\&E","year by SCE", "year by SDG\\&E", "year by CA overall"]
            lower_strings = [""] * num_fields
            header_string = [""] * 2
            for i, pref in enumerate(var_list):
                header_string[0] += '& ({})'.format(i)
                header_string[1] += '& {}'.format(pref)
                for j in range(num_fields):
                    upper_strings[j] += ' & {} '.format(my_format(results_dict[pref]['params'][j]))
                    lower_strings[j] += ' & ({}) '.format(my_format(results_dict[pref]['pvalues'][j]))
            mywrite(outfile, header_string[0] + '\\\\ \n')
            mywrite(outfile, header_string[1] + '\\\\ \n')
            mywrite(outfile, '\\midrule \n ')
            for j in range(num_fields):
                mywrite(outfile, upper_strings[j] + '\\\\ \n')
                mywrite(outfile, lower_strings[j] + '\\\\ \n')
            mywrite(outfile,'\\bottomrule \n')
            mywrite(outfile,'\\end{tabular}')