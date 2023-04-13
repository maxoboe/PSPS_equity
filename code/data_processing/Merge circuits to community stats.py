import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
base = '/Users/maxv/Dropbox (MIT)/inferring_expectations/'
community = gpd.read_file(base + 'data/calenviroscreen40shpf2021shp/')
community = community.to_crs("EPSG:4328")
sensitive_pop = ['Asthma','LowBirtWt','Cardiovas']
socioecon_pop = ['Educatn','Ling_Isol', 'Poverty', 'Unempl', 'HousBurd']
all_factors = sensitive_pop + socioecon_pop + ['TotPop19']
ica_db = gpd.read_file(base + 'data/all_ica_maps/').to_crs("EPSG:4328")
out_df = None
for i, row in ica_db.iterrows():
    cbg_matches = community[community.intersects(row.geometry)]
    row = pd.DataFrame(row).transpose().drop(columns=['geometry'])
    if len(cbg_matches) == 0:
        print("0 matches: ", row.clean_name, row.Utility)
    else:
        length = cbg_matches.length.values.flatten()
        for var in all_factors:
            if all(cbg_matches[var] == -999):
                row[var] = np.nan
                continue
            not_nan = cbg_matches[var] != -999
            row[var] = np.average(cbg_matches[var][not_nan], weights=length[not_nan])
    if out_df is None:
        out_df = row
    else:
        out_df = out_df.append(row)
for var in sensitive_pop + socioecon_pop:
    out_df[var + '_P'] = 100 * out_df[var].rank(pct=True)
out_df['sens'] = np.mean(out_df[[var + '_P' for var in sensitive_pop]], axis=1)
out_df['socio'] = np.mean(out_df[[var + '_P' for var in socioecon_pop]], axis=1)
out_df['PopChar'] = np.mean(out_df[['sens','socio']], axis=1)
out_df['PopChar_P'] = 100 * out_df['PopChar'].rank(pct=True)
out_df['Utility'] = np.where(out_df.Utility == 'PGE', 'PG&E', out_df.Utility)
out_df['Utility'] = np.where(out_df.Utility == 'SDGE', 'SDG&E', out_df.Utility)
out_df.to_csv(base + 'data/community_with_circuit.csv', index=False)

print(np.sum(np.isfinite(out_df[all_factors])))
psps_gdb = gpd.read_file(base + 'data/psps_events/psps_events.shp')
psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'PGE', 'PG&E', psps_gdb.Utility)
psps_gdb['Utility'] = np.where(psps_gdb.Utility == 'SDGE', 'SDG&E', psps_gdb.Utility)
psps_gdb['identifier'] = psps_gdb['clean_name'] + '_' + psps_gdb['Utility']
psps_ids = psps_gdb['identifier'].unique()
out_df['identifier'] = out_df['clean_name'] + '_' + out_df['Utility']
thing = out_df[out_df.identifier.isin(psps_ids)]
print(np.sum(np.isfinite(thing[all_factors + ['PopChar','socio','sens']])))