import geopandas as gpd
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
import datetime
from dateutil import parser
import statsmodels.api as sm
import statsmodels.formula.api as smf
from collections import OrderedDict

from sklearn.model_selection import cross_val_predict
from patsy import dmatrix
from sklearn.metrics import r2_score
from sklearn.metrics import confusion_matrix
from patsy import dmatrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
if ('Users/maxv' in os.getcwd()):
    base = "/Users/maxv/Dropbox (MIT)/inferring_expectations/" 
else:
    base = '/pool001/vilgalys/inferring_expectations/'
sys.path.append(os.path.abspath(base + "code/"))
import global_constants
import read_write

out_folder = base + 'outputs/summary_stats/fire_size/'
prefixes = global_constants.prefixes
dep_var_string = list(prefixes)[0]
for var in list(prefixes)[1:]:
    dep_var_string += ' + ' + var

fire_db = read_write.read_fire()

def my_append(_dict, method, key, value):
    if method in _dict.keys():
        entry = _dict[method]
        entry[key] = value
        _dict[method] = entry
    else:
        entry = OrderedDict()
        entry[key] = value
        _dict[method] = entry
    return _dict

def regression_trial(method, out_results, verbose=False):
    X = dmatrix('C(year) + C(utility) + {}'.format(dep_var_string), data=fire_db)
    y = np.log10(fire_db['FIRE_SIZE'].values)
    kf = KFold(n_splits=5, random_state = global_constants.random_seed, shuffle=True)
    if method == 'Linear':
        mod = smf.ols(formula='np.log10(FIRE_SIZE) ~ + C(year) + C(utility) + {}'.format(dep_var_string), data=fire_db)
        res = mod.fit(cov_type='HC1')
        y_pred = res.predict()
        y_actual = y
    elif method == 'Linear Interacted':
        mod = smf.ols(formula='np.log10(FIRE_SIZE) ~ + (C(year) + C(utility) + {})**2'.format(dep_var_string), data=fire_db)
        res = mod.fit(cov_type='HC1')
        y_pred = res.predict()
        y_actual = y
    elif method == 'Random Forest':
        y_pred = []
        y_actual = []
        for train, test in kf.split(y):
            _y_actual = y[test]
            clf = RandomForestRegressor(random_state=global_constants.random_seed)
            clf.fit(X[train,:], y[train])
            _y_pred = clf.predict(X[test,:])
            y_pred = y_pred + list(_y_pred)
            y_actual = y_actual + list(_y_actual)
    score = r2_score(y_actual, y_pred)
    read_write.plot_predictions(y_actual, y_pred, fire_db['utility'],
                     "fire size", "(log acres)", "{}_regressors.png".format(method))
    out_results = my_append(out_results, method, ("Regression","R squared"), score)
    return out_results

def classification_trial(method, out_results, verbose=False):
    for threshold, label in  zip([300, 500, 'top .02'], ["300 acres", "500 acres", "top 2\%"]):
        fire_subset = fire_db.copy()
        if threshold == 'top .02':
            utility_thresholds = fire_subset[['utility','FIRE_SIZE']].groupby('utility').quantile(0.98)
            threshold = fire_db['utility'].apply(lambda x: float(utility_thresholds.loc[x]))
        fire_subset['large_fire'] = fire_subset['FIRE_SIZE'] >= threshold
        fire_subset['large_fire'] = fire_subset['large_fire'].astype(int)
        X = dmatrix('C(year) + C(utility) + {}'.format(dep_var_string), data=fire_db)
        y = np.array(fire_subset['large_fire'])
        first_mean = 1 / fire_subset.large_fire.mean()
        second_mean = 1 / ( 1 - fire_subset.large_fire.mean())
        weights = np.array([first_mean if x else second_mean for x in fire_subset.large_fire])
        if method == 'Linear':
            clf = LogisticRegression(penalty="none", max_iter=10000)
            y_pred = clf.fit(X, y, sample_weight=weights).predict(X)
            y_actual = y
        elif method == 'Linear Interacted':
            X = dmatrix('(C(year) + C(utility) + {})**2'.format(dep_var_string), data=fire_db)
            clf = LogisticRegression(penalty="none", max_iter=10000)
            y_pred = clf.fit(X, y, sample_weight=weights).predict(X)
            y_actual = y
        elif method == 'Random Forest':
            kf = KFold(n_splits=5, random_state = global_constants.random_seed, shuffle=True)
            y_pred = []
            y_actual = []
            for train, test in kf.split(y):
                _y_actual = y[test]
                clf = RandomForestClassifier(random_state=1234)
                clf.fit(X[train,:], y[train], sample_weight = weights[train])
                _y_pred = clf.predict(X[test,:])
                y_pred = y_pred + list(_y_pred)
                y_actual = y_actual + list(_y_actual)
        tn, fp, fn, tp = confusion_matrix(y_actual, y_pred).ravel()
        sensitivity = tn / (tn + fp)
        specificity = tp / (tp + fn)
        if verbose:
            print('Sensitivity: ', sensitivity, 'Specificity: ', specificity)
            print("True negatives:", tn, ", False positives:", fp, ", False negatives:", fn, ', True positives:', tp)
            print('-'*20)
        out_results = my_append(out_results, method, ("Fire size $\geq$ " + label, "Specificity"), specificity)
        out_results = my_append(out_results, method, ("Fire size $\geq$ " + label, "Sensitivity"), sensitivity)
    return out_results

out_results = OrderedDict()
method_list = ['Linear','Linear Interacted','Random Forest']
for method in method_list:
    out_results = regression_trial(method, out_results)
    out_results = classification_trial(method,out_results)
out_frame = pd.DataFrame(out_results).transpose()
out_frame.to_latex(out_folder + 'fire_size_prediction.tex', escape=False,  multirow=True, multicolumn_format='c',
            column_format='l'+'c'*len(out_frame.transpose()), float_format = '{:.4g}'.format)
