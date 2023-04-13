
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

psps_db = read_write.read_psps(merge_community=False, return_db=True)
psps_db['TOTAL CUST'] = psps_db['TOTAL CUST'].astype(int)

overall_df = None

for utility in psps_db.Utility.unique():
    to_print = psps_db[psps_db.Utility == utility].groupby(['year']).sum()[['TOTAL CUST','CMI']]
    to_print['CMI'] = to_print['CMI'] / 1e6


    to_print['CMI'] = to_print['CMI'].apply('{:.3g}'.format).astype(float).apply('{:,}'.format).apply(lambda x: x[:-2] if x[-2:]=='.0' else x).astype(str)
    to_print['Count'] = psps_db[psps_db.Utility == utility].groupby(['year']).count()['TOTAL CUST']
    to_print['Count'] = to_print['Count'].apply(lambda x: '{:,}'.format(x))
    to_print['TOTAL CUST'] = to_print['TOTAL CUST'].astype(int).apply(lambda x: '{:,}'.format(x))
    
    to_print = to_print.rename(columns={'TOTAL CUST': 'Customers', 'CMI':'Million CMI', 'Count':'\# PSPS Events'})
    # to_print = to_print.reset_index()
    to_print = to_print.transpose()
    to_print['Utility'] = utility.replace('&','\&')
    to_print = to_print.reset_index()
    to_print = to_print.rename(columns={'index':'\ '})
    to_print = to_print.set_index(['Utility','\ '])
    if overall_df is None:
        overall_df = to_print
    else:
        overall_df = overall_df.append(to_print)
overall_df.to_latex(base + 'outputs/summary_stats/psps_summary_table.tex', 
                        multirow=True, multicolumn_format='c', na_rep='--',
                        column_format='ll'+'c'*len(overall_df.transpose()),
                         float_format = '{:,}'.format, escape=False)