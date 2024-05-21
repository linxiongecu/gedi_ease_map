#!/bin/bash
# GMT script to plot the USA
# gridding example 
plot_path='/gpfs/data1/vclgp/xiongl/GEDIglobal/plot/'
# -17367530.44	7314540.83 ease 2.0
# -17367000, 7314000 # [-180, 180]
# 7229000 # N80
# -6149000 # S57
# merge all grids 
#gmt grdblend ../result/X*.nc -G${plot_path}blend.nc -R-17367000/17367000/-6149000/7229000 -I1000 -V
#gdal_translate -of netCDF ${plot_path}GEDI_gridded_1km.tif ${plot_path}output.grd #-a_nodata none
# netCDF GMT
#gmt makecpt -Cseis -T0/60/5 -Z -F  -D -Iz> ${plot_path}elevation.cpt
# aspect ratio is maintained.
# -12750763E,5870964N   17336394,-5793702
gmt grdimage ${plot_path}output_1km.grd -JX8.22i/3.22i -I+  -R-12750000/17367000/-5871000/5871000 -C${plot_path}elevation.cpt   -K > ${plot_path}global_gedi.ps # -Baf -BWSen
gmt psscale -C${plot_path}elevation.cpt   -Dx4.2i/-0.2c+w6c/0.3c+jTC+h -Bxaf -By+lm -O >> ${plot_path}global_gedi.ps
gmt psconvert ${plot_path}global_gedi.ps -Tj -A -E3000

