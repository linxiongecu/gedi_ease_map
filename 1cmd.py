import subprocess
import multiprocessing
import  time

# set the corners of your ROI in geographic coordinates - this example is for Maryland
lon_min = -125
lon_max = -65
lat_min = 25
lat_max = 50

# set your ROI name and GEDI data type
roi_name = 'US_'
GEDI_data = 'GEDI02_A_'

# list to store subsetting commands
cmd_list = []

# loop through latitudes
for lat in range(lat_min, lat_max, 1):
    # loop through longitudes
    for lon in range(lon_min, lon_max, 1):

        # make tile name using bottom left corner coordinate, removing negative sign and adding cardinal direction
        if lon >= 0:
            lon_label = 'E_'
        else:
            lon_label = 'W_'
        if lat >= 0:
            lat_label = 'N.csv'
        else:
            lat_label = 'S.csv'

        tile = str(abs(lon)) + lon_label + str(abs(lat)) + lat_label

        # make file name (and set a path if desired) based on GEDI data product and tile
        file_out = GEDI_data + roi_name + tile

        # make bbox coordinates from lon and lat
        xmin = lon
        xmax = lon + 1
        ymin = lat
        ymax = lat + 1

        # pass necessary info to subsetting command
        #cmd = 'issgedi_subset_orbits.py %s --product GEDI02 --level A --pgeversion 1 -b %f %f %f %f' % (file_out, xmin, ymax, xmax, ymin)
        cmd = 'python Export.py  -d var.txt --product GEDI02 --level A  --pgeversion 3 --type 02 --release 2 -b %f %f %f %f %s \n' % (xmin, ymax, xmax, ymin, file_out)
        #cmd = 'issgedi_subset_orbits.py -h'
        cmd_list.append(cmd)


# set up parallel processing
with open('cmd.txt', 'w') as f:
    f.writelines(cmd_list)    

