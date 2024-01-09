#!/usr/bin/env python
# coding: utf-8

# import libraries
import os
import h5py
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy
from pyproj import Transformer
import glob
import os
import numpy
import subprocess
import sys
from dask.distributed import Client, progress
import dask
import re

def get_tile_id(longitude, latitude, tilesize=72): # lat, lon dataframe
    ease2_origin = -17367530.445161499083042, 7314540.830638599582016
    ease2_nbins = int(34704 / tilesize + 0.5), int(14616 / tilesize + 0.5)
    ease2_binsize = 1000.895023349556141*tilesize, 1000.895023349562052*tilesize

    valid = ~numpy.isnan(longitude) & ~numpy.isnan(latitude)
    xidx = numpy.zeros(valid.shape[0], dtype=numpy.int16)
    yidx = numpy.zeros(valid.shape[0], dtype=numpy.int16)

    if numpy.any(valid):
        transformer = Transformer.from_crs('epsg:4326', 'epsg:6933', always_xy=True)
        x,y = transformer.transform(longitude[valid],latitude[valid])
        xidx[valid] = numpy.int16( (x - ease2_origin[0]) / ease2_binsize[0]) + 1
        yidx[valid] = numpy.int16( (ease2_origin[1] - y) / ease2_binsize[1]) + 1
        numpy.clip(xidx, 0, ease2_nbins[0], out=xidx)
        numpy.clip(yidx, 0, ease2_nbins[1], out=yidx)
    return xidx, yidx
