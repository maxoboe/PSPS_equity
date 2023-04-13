import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
import matplotlib.colors as colors
from scipy import stats
import re
import os
if ('Users/maxv' in os.getcwd()):
    base = "/Users/maxv/Dropbox (MIT)/inferring_expectations/" 
else:
    base = '/pool001/vilgalys/inferring_expectations/'
out_fold = base + 'outputs/regression/'
rsquared_dict = {}


cmi = pd.read_csv(out_fold + 'cmi_regression.csv')
cmi = cmi.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
cmi = cmi.rename(columns=lambda x: x.replace('CMI_',''))
cmi = cmi.set_index('Unnamed: 0')
cmi = cmi.transpose()
rsquared_dict['CMI'] = cmi['R-sq'].dropna().astype(float).values

agg_cmi = pd.read_csv(out_fold + 'aggregate_cmi_regression.csv')
agg_cmi = agg_cmi.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
agg_cmi = agg_cmi.rename(columns=lambda x: x.replace('CMI_',''))
agg_cmi = agg_cmi.set_index('Unnamed: 0')
agg_cmi = agg_cmi.transpose()
agg_cmi = agg_cmi.rename(columns={'sens':'Aggregate_sens', 'socio':'Aggregate_socio'})
cmi = pd.merge(cmi, agg_cmi,  left_index=True, right_index=True, suffixes=('','_aggregate'))

customers = pd.read_csv(out_fold + 'customers_regression.csv')
customers = customers.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
customers = customers.rename(columns=lambda x: x.replace('customers_',''))
customers = customers.set_index('Unnamed: 0')
customers = customers.transpose()
rsquared_dict['Cust'] = customers['R-sq'].dropna().astype(float).values
agg_cust = pd.read_csv(out_fold + 'aggregate_customers_regression.csv')
agg_cust = agg_cust.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
agg_cust = agg_cust.rename(columns=lambda x: x.replace('customers_',''))
agg_cust = agg_cust.set_index('Unnamed: 0')
agg_cust = agg_cust.transpose()
agg_cust = agg_cust.rename(columns={'sens':'Aggregate_sens', 'socio':'Aggregate_socio'})
customers = pd.merge(customers, agg_cust,  left_index=True, right_index=True, suffixes=('','_aggregate'))

psps = pd.read_csv(out_fold + 'psps_logistic_regression.csv')
psps = psps.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
psps = psps.set_index('Unnamed: 0')
psps = psps.transpose()
rsquared_dict['PSPS'] = psps['pseudo R-sq'].dropna().astype(float).values

agg_psps = pd.read_csv(out_fold + 'aggregate_psps_logistic_regression.csv')
agg_psps = agg_psps.rename(columns={'Unnamed: 2':'community_se','Unnamed: 4':'population_se','Unnamed: 6':'primary_se','Unnamed: 8':'all_se'})
agg_psps = agg_psps.set_index('Unnamed: 0')
agg_psps = agg_psps.transpose()
agg_psps = agg_psps.rename(columns={'sens':'Aggregate_sens', 'socio':'Aggregate_socio'})
psps = pd.merge(psps, agg_psps,  left_index=True, right_index=True, suffixes=('','_aggregate'))

ignition = pd.read_csv(out_fold + 'ignition_second_stage.csv')
ignition['stat'] = ignition['Unnamed: 0'].apply(lambda x:x.split('_')[-1])
ignition['Unnamed: 0'] = ignition['Unnamed: 0'].apply(lambda x: x.split('_mean')[0].split('_std')[0])
ignition['Unnamed: 0'] = ignition['Unnamed: 0'].apply(lambda x: x.replace('&',''))
ignition = ignition.set_index('Unnamed: 0')
set_a = ignition[ignition.stat == 'mean'].drop(columns='stat')
set_b = ignition[ignition.stat == 'std'].drop(columns='stat')
set_a = set_a.rename(columns={'(1)':'community_','(2)':'population_','(3)':'primary_','(4)':'all_'})
set_b = set_b.rename(columns={'(1)':'community_se','(2)':'population_se','(3)':'primary_se','(4)':'all_se'})
ignition = set_a.transpose().append(set_b.transpose())
ignition = ignition.astype(float)

agg_ignition = pd.read_csv(out_fold + 'aggregate_ignition_second_stage.csv')
agg_ignition['stat'] = agg_ignition['Unnamed: 0'].apply(lambda x:x.split('_')[-1])
agg_ignition['Unnamed: 0'] = agg_ignition['Unnamed: 0'].apply(lambda x: x.split('_mean')[0].split('_std')[0])
agg_ignition['Unnamed: 0'] = agg_ignition['Unnamed: 0'].apply(lambda x: x.replace('&',''))
agg_ignition['Unnamed: 0'] = agg_ignition['Unnamed: 0'].apply(lambda x: x.replace('aggregate','Aggregate'))
agg_ignition = agg_ignition.set_index('Unnamed: 0')
set_a = agg_ignition[agg_ignition.stat == 'mean'].drop(columns='stat')
set_b = agg_ignition[agg_ignition.stat == 'std'].drop(columns='stat')
set_a = set_a.rename(columns={'(1)':'community_','(2)':'population_','(3)':'primary_','(4)':'all_'})
set_b = set_b.rename(columns={'(1)':'community_se','(2)':'population_se','(3)':'primary_se','(4)':'all_se'})
agg_ignition = set_a.transpose().append(set_b.transpose())
agg_ignition = agg_ignition.astype(float)
ignition = pd.merge(ignition, agg_ignition, left_index=True, right_index=True, suffixes=("",'_aggregate'))

ignition = pd.read_csv(out_fold + 'logistic_regression_ignition_overall.csv')
ignition_r2 = ignition.set_index('Unnamed: 0')
ignition_r2 = ignition_r2.transpose()
ignition_r2 = ignition_r2.dropna(subset=['N','pseudo R-sq'])
ignition_r2['N'] = ignition_r2['N'].astype('float')
ignition_r2['pseudo R-sq'] = ignition_r2['pseudo R-sq'].astype('float')
ignition_r2['weighted_pseudo_r2'] = ignition_r2['N'] * ignition_r2['pseudo R-sq']
ignition_r2['group'] = [x.split('_')[0] for x in ignition_r2.index.astype(str)]
grouped = ignition_r2.groupby('group').sum()
grouped['weighted_pseudo_r2'] = grouped['weighted_pseudo_r2'] / grouped['N']
rsquared_dict['Ignition'] = grouped['weighted_pseudo_r2'][['community','population','primary','all']].values

ignition = ignition.rename(columns=lambda x: x + '_' if x[-1] == 'E' else x )
ignition = ignition.rename(columns={'Unnamed: 2':'community_SCE_se','Unnamed: 4':'community_PGE_se',
    'Unnamed: 6':'community_SDGE_se', 'Unnamed: 8':'population_SCE_se',
    'Unnamed: 10':'population_PGE_se', 'Unnamed: 12': 'population_SDGE_se',
    'Unnamed: 14':'primary_SCE_se','Unnamed: 16':'primary_PGE_se', 'Unnamed: 18': 'primary_SDGE_se',
    'Unnamed: 20':'all_SCE_se','Unnamed: 22':'all_PGE_se', 'Unnamed: 24': 'all_SDGE_se',})
ignition = ignition.set_index('Unnamed: 0')
agg_ignition = pd.read_csv(out_fold + 'aggregate_logistic_regression_ignition.csv')
agg_ignition = agg_ignition.rename(columns={'ignition_community_':'community_Aggregate_', 'Unnamed: 2': 'community_Aggregate_se',
    'ignition_population_': 'population_Aggregate_', 'Unnamed: 4': 'population_Aggregate_se',
    'ignition_primary_': 'primary_Aggregate_', 'Unnamed: 6': 'primary_Aggregate_se',
    'ignition_all_': 'all_Aggregate_', 'Unnamed: 8': 'all_Aggregate_se',
  })
agg_ignition = agg_ignition.set_index('Unnamed: 0')
ignition = pd.merge(ignition, agg_ignition, left_index=True, right_index=True, suffixes=('','_aggregate'))
print(ignition)

frame = None
for method in ['all','population','primary','community']:
    for utility in ['SCE','PGE','SDGE', 'Aggregate']:
        for field in ['sens','socio']:
            for mean_se, label in zip(['_','_se'],['mean','se']):
                entry = {'PSPS':float(psps[f'{utility}_{field}'][f'{method}{mean_se}']),
                        'Ignition':float(ignition[f'{method}_{utility}{mean_se}'][f'{field}']),
                        'CMI':float(cmi[f'{utility}_{field}'][f'{method}{mean_se}']),
                        'Cust':float(customers[f'{utility}_{field}'][f'{method}{mean_se}']),
                        'method':method, 'utility':utility, 'field':field}
                entry = pd.DataFrame(entry, index=[label])
                frame = entry if frame is None else frame.append(entry)
frame['utility'] = np.where(frame.utility == 'PGE', 'PG&E',frame.utility)
frame['utility'] = np.where(frame.utility == 'SDGE', 'SDG&E',frame.utility)

out_path = out_fold + 'coefficient_plots/'

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

for label in ['PSPS','Ignition','CMI','Cust']:
    for field in ['sens','socio']:
        fig, ax = plt.subplots(figsize=(6,4))
        for j, method in enumerate(['community','population','primary','all']):
            subset = frame[(frame.method == method) & (frame.field == field)]
            width = 0.2
            for i, utility in enumerate(subset.utility.unique()):
                means = subset[(subset.index == 'mean') & (subset.utility == utility)]
                stds = subset[(subset.index == 'se') & (subset.utility == utility)]
                y = means[label].values.flatten()
                y_err = 1.96 * stds[label].values.flatten()
                x = np.arange(len(y))
                plt.bar(x = j -0.3 + 0.2 * i, height = y, width=0.18, yerr = y_err, label=utility if j == 0 else None, 
                        alpha=0.8, capsize=3, ecolor='grey', fill=False, edgecolor=colors[i], linewidth=2)
        rsquared = rsquared_dict[label]
        # rsquared = [float(x) for x in rsquared]
        # print(rsquared)
        x_labels = ['no\ncontrols','\npopulation', 'primary\nweather','all\ncontrols']

        x_labels = [x + '\n({:.3f})'.format(y) for x,y in zip(x_labels, rsquared )]
        plt.xticks(np.arange(4), x_labels,
                  fontsize=14)
        plt.yticks(fontsize=13)
        _label = "log odds / index" if label in ['PSPS', 'Ignition'] else 'log change / index'
        plt.ylabel(_label, fontsize=13)
        ax.grid(axis='y', which='major', color='grey', linestyle='-', alpha=0.5)
        plt.legend()
        ax.legend(loc='center left', bbox_to_anchor=(0, -.31), ncol=4)
        plt.savefig(out_path + f'{label}_{field}.png', dpi=400, bbox_inches='tight')
        plt.close()