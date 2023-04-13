
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

out_folder = base + 'outputs/summary_stats/community_plots/'
psps_db = read_write.read_psps(merge_community=False, return_db=True)
psps_db['date_str'] = psps_db['date'].astype(str)
psps_db = psps_db.groupby(['identifier','date_str','clean_name','Utility']).sum().reset_index()
ignition_db = read_write.read_ignitions(merge_community=False)
community_db = read_write.read_community()
# indices = ['sens','socio','PopChar_P','Asthma_P','LowBirtWt_P','Cardiovas_P','Educatn_P','Ling_Isol_P', 'Poverty_P', 'Unempl_P', 'HousBurd_P']
# labels = ['Sensitive Population','Socioeconomic Factors','Overall','Asthma',
#         'Low Birth Weight','Cardiovascular','Education','Linguistic Isolation', 
#         'Poverty', 'Unemployment', 'House Burdened']
indices = ['sens','socio','PopChar_P']
labels = ['Health Risk','Socioeconomic Factors','Overall']

for index, _label in zip(indices, labels):

    psps_db['TOTAL CUST'] = psps_db['TOTAL CUST'].astype(int)
    merged = pd.merge(psps_db, community_db, on=['clean_name','Utility'], how='outer')

    grouped = merged.groupby('identifier')
    to_plot = grouped[[index,'clean_name','Utility']].first()
    to_plot['CMI'] = grouped['CMI'].sum()
    to_plot['log_CMI'] = np.log10(to_plot['CMI'])
    to_plot['Count'] = grouped['Utility'].count()
    to_plot.head()
    import matplotlib
    fig, ax = plt.subplots(figsize=(5,5))
    markers = ['.','^','d']
    utilities = ['SCE','PG&E','SDG&E']
    ax.set_yscale('log')
    for marker, utility in zip(markers, utilities):
        subset = to_plot[to_plot.Utility == utility]
        subset = subset[np.isfinite(subset[index])]
        subset = subset[np.isfinite(np.log(subset.CMI))]
        res = sm.OLS(np.log10(subset.CMI), sm.add_constant(subset[index])).fit()
        label = utility + '\n {:.4f} \n ({:.4f})'.format(res.params[1], res.bse[1])
        plt.scatter(subset[index], subset.CMI, marker=marker, label=label, alpha=0.7)
        x_init = np.linspace(0,100,300)
        y_init = res.params[0] + res.params[1] * x_init
        y_down = y_init - 1.96 * res.bse[1]
        y_up = y_init + 1.96 * res.bse[1]
        plt.plot(x_init, 10**y_init, linestyle='--')
    #     plt.fill_between(x_init, y_down, y_up, color='k', 
    #                      alpha=0.2, linestyle='--', facecolor='gainsboro')
    # plt.xlim((0,100))
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fontsize=12, ncol=3)
    ax.grid(b=True, which='major', color='k', linestyle='-', alpha=0.5)
    ax.grid(axis='x', which='minor', color='grey', linestyle='--', alpha=0.3)
    # ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.xlabel('{} Index'.format(_label), fontsize=13)
    plt.ylabel('Customer Minutes Interrupted', fontsize=14)
    plt.savefig(out_folder + '{}_vs_CMI.png'.format(index), dpi=200, bbox_inches='tight')
    plt.close()


    merged = pd.merge(ignition_db, community_db, on=['clean_name','Utility'], how='outer')
    merged['identifier'] = merged['clean_name'] + '_' + merged['Utility']
    grouped = merged.groupby('identifier')
    to_plot = grouped[[index,'clean_name','Utility']].first()
    to_plot['Count'] = grouped['year'].count()
    to_plot.head()

    fig, ax = plt.subplots(figsize=(5,5))
    markers = ['.','^','d']
    utilities = ['SCE','PG&E','SDG&E']
    ax.set_yscale('log')
    # ax.set_xscale('log')
    for marker, utility in zip(markers, utilities):
        subset = to_plot[to_plot.Utility == utility]
        subset = subset[np.isfinite(subset[index])]
        subset = subset[np.isfinite(np.log(subset.Count))]
        res = sm.OLS(np.log10(subset.Count), sm.add_constant(subset[index])).fit()
        label = utility + '\n {:.4f} \n ({:.4f})'.format(res.params[1], res.bse[1])
        plt.scatter(subset[index], subset.Count, marker=marker, label=label, alpha=0.7)
        x_init = np.linspace(0, 100, 300)
        y_init = res.params[0] + res.params[1] * x_init
        y_down = y_init - 1.96 * res.bse[1]
        y_up = y_init + 1.96 * res.bse[1]
        plt.plot(x_init, 10**y_init, linestyle='--', alpha=0.7)
    #     plt.fill_between(10**x_init, 10**y_down, 10**y_up, color='k', 
    #                      alpha=0.05, linestyle='--', facecolor='gainsboro')
    # plt.xlim((10**1.3, 10**2.6))
    # plt.ylim(bottom=0.45)
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fontsize=12, ncol=3)
    ax.grid(b=True, which='major', color='k', linestyle='-', alpha=0.5)
    ax.grid(axis='x', which='minor', color='grey', linestyle='--', alpha=0.3)
    # ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.xlabel('{} Index'.format(_label), fontsize=13)
    plt.ylabel('Number of Ignitions', fontsize=14)
    plt.savefig(out_folder + '{}_vs_ignitions.png'.format(index), dpi=200, bbox_inches='tight')
    plt.close()


    merged = pd.merge(psps_db, community_db, on=['clean_name','Utility'], how='outer')
    merged['identifier'] = merged['clean_name'] + '_' + merged['Utility']
    grouped = merged.groupby('identifier')
    to_plot = grouped[[index,'clean_name','Utility']].first()
    to_plot['Count'] = grouped['year'].count()
    to_plot.head()

    fig, ax = plt.subplots(figsize=(5,5))
    markers = ['.','^','d']
    utilities = ['SCE','PG&E','SDG&E']
    ax.set_yscale('log')
    # ax.set_xscale('log')
    for marker, utility in zip(markers, utilities):
        subset = to_plot[to_plot.Utility == utility]
        subset = subset[np.isfinite(subset[index])]
        subset = subset[np.isfinite(np.log(subset.Count))]
        res = sm.OLS(np.log10(subset.Count), sm.add_constant(subset[index])).fit()
        label = utility + '\n {:.4f} \n ({:.4f})'.format(res.params[1], res.bse[1])
        plt.scatter(subset[index], subset.Count, marker=marker, label=label, alpha=0.7)
        x_init = np.linspace(0, 100, 300)
        y_init = res.params[0] + res.params[1] * x_init
        y_down = y_init - 1.96 * res.bse[1]
        y_up = y_init + 1.96 * res.bse[1]
        plt.plot(x_init, 10**y_init, linestyle='--', alpha=0.7)
    #     plt.fill_between(10**x_init, 10**y_down, 10**y_up, color='k', 
    #                      alpha=0.2, linestyle='--', facecolor='gainsboro')
    # plt.xlim((10**1.3, 10**3))
    # plt.ylim(bottom=0.15)
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fontsize=12, ncol=3)
    ax.grid(b=True, which='major', color='k', linestyle='-', alpha=0.5)
    ax.grid(axis='x', which='minor', color='grey', linestyle='--', alpha=0.3)
    # ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.xlabel('{} Index'.format(_label), fontsize=13)
    plt.ylabel('Number of PSPS', fontsize=14)
    plt.savefig(out_folder + '{}_vs_PSPS.png'.format(index), dpi=200, bbox_inches='tight')
    plt.close()