#!/usr/bin/env python
# coding: utf-8
from pyproj import Transformer
import geopandas as gpd
from shapely.geometry import Polygon
import math
from shapely.geometry import Polygon
import shutil
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
def get_tiles_x_y(grid_x = 1, grid_y = 1):
        tilesize_x = 2481
        tilesize_y = 2438
        # 17367703.09
        ease2_origin = -17367000, 7314000
        ease2_nbins = int(34734 / tilesize_x ), int(14628 / tilesize_y )
        ease2_binsize = 1000*tilesize_x, 1000*tilesize_y
        x_up_left = ease2_origin[0] + (grid_x - 1)*ease2_binsize[0]
        y_up_left = ease2_origin[1] - (grid_y - 1)*ease2_binsize[1]
        xmin = x_up_left
        xmax = x_up_left + ease2_binsize[0]
        if grid_x == 12: xmax = xmax-0.1
        ymin = y_up_left - ease2_binsize[1]
        ymax = y_up_left
        return xmin, xmax, ymin, ymax
def ease_csv(data = '/gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/X4_Y4.parquet'):
    out_csv =  data.replace('.parquet', '.csv') 
    if os.path.exists(out_csv): return
    df = pd.read_parquet(data)
    transformer = Transformer.from_crs('epsg:4326', 'epsg:6933', always_xy=True)
    lon, lat = df['lon_lowestmode'], df['lat_lowestmode']
    x, y = transformer.transform(lon.to_numpy(), lat.to_numpy())
    csv_df = pd.DataFrame({
        'X': x,
        'Y': y,
        'rh_098': df['rh_098']
    })
    csv_df.to_csv(out_csv, index=False)
data_files = glob.glob('/gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/*.parquet')
print('number of data files from extraction:',len(data_files) )
for f in data_files:
    print('convert file to EASE...', f)
    ease_csv(f)

def gridding2tif(data = '/gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/X4_Y4.csv'):
        i = int(os.path.basename(data)[:-4].split('_')[0][1:])
        j = int(os.path.basename(data)[:-4].split('_')[1][1:])
        xmin, xmax, ymin, ymax = get_tiles_x_y(i, j)
        # Run the shell script
        subprocess.run(['bash', 'gmt_gridding.sh', str(xmin), str(xmax), str(ymin),str(ymax), str(i), str(j)])
data_files = glob.glob('/gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/*.csv')
print('number of csv files from extraction:',len(data_files) )
for f in data_files:
    gridding2tif(f)