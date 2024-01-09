#!/bin/bash
# GMT script to plot the USA
# gridding example 

# input argument xmin, xmax, ymin, ymax, grid_x, grid_y
xmin=$1
xmax=$2
ymin=$3
ymax=$4
grid_x=$5
grid_y=$6
R="-R${xmin}/${xmax}/${ymin}/${ymax}"
#J='-JX5i/5i'
I='-I1000'
grd="/gpfs/data1/vclgp/xiongl/GEDIglobal/result/X_${grid_x}_Y_${grid_y}.nc"
median="/gpfs/data1/vclgp/xiongl/GEDIglobal/result/X_${grid_x}_Y_${grid_y}.txt"
#cpt='/gpfs/data1/vclgp/xiongl/GEDIglobal/result/test.cpt'
#PS='/gpfs/data1/vclgp/xiongl/GEDIglobal/result/plot.ps'
tif="/gpfs/data1/vclgp/xiongl/GEDIglobal/result/X_${grid_x}_Y_${grid_y}.tif"
csv="/gpfs/data1/vclgp/xiongl/GEDIglobal/ease_data/GEDI02_A_X${grid_x}_Y${grid_y}.csv" # GEDI02_A_X158_Y108.csv'
# Beam,ShotNumber,Longitude,Latitude,QualityFlag,rh98,sensitivity, X,Y
# 0      1          2         3           4       5      6         7 8
echo $csv
gmt blockmedian $csv  $R $I -h -i7,8,5 > $median
gmt nearneighbor $median $R $I -G$grd -S3000 -N8/2
#gdal_translate NETCDF:$grd $tif
gdal_translate -of GTiff -a_srs EPSG:6933 NETCDF:$grd $tif

# how to use
# bash gmt_plot.sh -6053000   -5981000  -468000  -396000  158 108
# bash gmt_plot.sh -17295000 -17223000  5729000  5801000  2 22