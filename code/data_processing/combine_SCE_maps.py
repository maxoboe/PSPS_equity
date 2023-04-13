import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
base = '/Users/maxv/Dropbox (MIT)/inferring_expectations/'
import os
root = base + 'data/SCE_raw/'
directories = [os.path.join(root, f) for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]
out_df = None
for path in directories:
    print(path)
    gdb = gpd.read_file(path)
    if out_df is None:
        out_df = gdb
    else:
        out_df = out_df.append(gdb)
    print(out_df.shape)
out_df.to_file(base + 'data/SCE/SCE.shp')
gdb = gpd.read_file(base + 'data/SCE')
print(gdb.shape)
print(gdb.head())
gdb.plot()
plt.show()
