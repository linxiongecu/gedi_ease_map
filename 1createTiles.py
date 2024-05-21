#!/usr/bin/env python
# coding: utf-8

# Can I make a tile file in .gpkg format????

# Following code is created by chatGPT----

# In[1]:


import geopandas as gpd
from shapely.geometry import Polygon


# In[4]:


# Define the coordinates of the rectangle vertices
#xmin, ymin = -70, 0  # Minimum x and y coordinates
#xmax, ymax =  -69, 1 # Maximum x and y coordinates


# In[5]:


# Create the rectangle geometry using Shapely
#polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])


# In[6]:


# Create a GeoDataFrame with the rectangle geometry
#data = {'id': [1], 'geometry': [polygon]}
#gdf = gpd.GeoDataFrame(data, geometry='geometry')


# In[7]:


# Write the GeoDataFrame to the GeoPackage file
#gdf.to_file('tile.gpkg', driver='GPKG')


# In[9]:


### write a loop for global data tiles
# set the corners of your ROI in geographic coordinates - this example is for Maryland
lon_min = -180
lon_max = 180
lat_min = -90
lat_max = 90



#lon_min = -80
#lon_max = -75
#lat_min = 37
#lat_max = 50



# loop through latitudes
for lat in range(lat_min, lat_max, 30):
    # loop through longitudes
    for lon in range(lon_min, lon_max, 30):

        # make tile name using bottom left corner coordinate, removing negative sign and adding cardinal direction
        if lon >= 0:
            lon_label = 'E_'
        else:
            lon_label = 'W_'
        if lat >= 0:
            lat_label = 'N.gpkg'
        else:
            lat_label = 'S.gpkg'

        tile = str(abs(lon)) + lon_label + str(abs(lat)) + lat_label

        # make file name (and set a path if desired) based on GEDI data product and tile
        file_out = 'tiles/' +  tile

        # make bbox coordinates from lon and lat
        xmin = lon
        xmax = lon + 30
        ymin = lat
        ymax = lat + 30
        polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])
        data = {'id': [1], 'geometry': [polygon]}
        gdf = gpd.GeoDataFrame(data, geometry='geometry')
        gdf.to_file( file_out, driver='GPKG')
        # pass necessary info to subsetting command



