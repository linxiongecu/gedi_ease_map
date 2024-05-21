#!/bin/bash
<<com
 extract GEDI data tile by tile 
 06/06/2023
 i want lon, lat, rh98, time, landcover [make sure it is tree]
 currenlty select algorithm 1
module unload gdal
conda activate /gpfs/data1/vclgp/decontot/environments/gedih3
com
## extract

# run script in backgroud
# even after log out ; 
# nohup bash script.sh &

## create an empty file


####loop through files 
DIRECTORY="tilesFilter/data/"  # Specify the directory path here

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Loop through each file in the directory
for file in "$DIRECTORY"/*; do
    if [ -f "$file" ]; then
        #echo "Processing file: $file"
        # Extract string between "[" and "]"
        result=$(echo "$file" | grep -oP "(?<=\//).+?(?=\.)")
        #echo $result
        # Perform operations on the file
        # Add your code here
        gh3_extract_shots -o out/$result -r $file --merge  -l2a geolocation/rh_a1_098 delta_time  land_cover_data/landsat_treecover  --quality --geo
        #### output files should change. 
    fi
done


#gh3_extract_shots -o merge -r tiles/*.gpkg --merge  -l2a geolocation/rh_a1_098 delta_time  land_cover_data/landsat_treecover  --quality --geo

### aggregate 
#gh3_aggregate -i tiles/ -o tile_rh -m mean -r 8 -u geolocation/rh_a1_098 -g
