#!/usr/bin/env python
# coding: utf-8
from pyproj import Transformer
import geopandas as gpd
from shapely.geometry import Polygon
import math
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import shutil
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import glob
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
for grid_x in range(1,15):
    for grid_y in range(1,7):
        #print(grid_x,grid_y)
        xmin, xmax, ymin, ymax = get_tiles_x_y(grid_x, grid_y)
        #print(xmin, xmax, ymin, ymax)
        transformer = Transformer.from_crs('epsg:6933', 'epsg:4326', always_xy=True)
        lon_min, lat_min = transformer.transform(xmin,ymin)    
        lon_max, lat_max = transformer.transform(xmax,ymax)
        #print(lon_min, lon_max,lat_min, lat_max)
        out_folder = '/gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles'
        tile = 'X' + str(grid_x) + '_Y' + str(grid_y) + '.gpkg'
        # make file name (and set a path if desired) based on GEDI data product and tile
        file_out = out_folder + '/' +  tile
        # make bbox coordinates from lon and lat
        polygon = Polygon([(lon_min, lat_min), (lon_max, lat_min), (lon_max, lat_max), (lon_min, lat_max)])
        data = {'id': [1], 'geometry': [polygon]}
        gdf = gpd.GeoDataFrame(data, geometry='geometry', crs='EPSG:4326')
        gdf.to_file( file_out, driver='GPKG')

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
directory = '/gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles'
# List all files in the directory
files = os.listdir(directory)
print('all tiles: ', len(files ))
for file in files:
    f = directory +'/' +file
    data = gpd.read_file(f)
    if not data.intersects(world.unary_union).any():
      print(f)
      os.remove(f)
files = os.listdir(directory)
print('all land tiles: ', len(files ))