#!/bin/bash

folder="/path/to/folder"  # Replace with your folder path
folder="/gpfs/data1/vclgp/xiongl/GEDIglobal/pythonTiles/tilesFilter/data"
# Loop through each file in the folder
for file in "$folder"/*
do
    if [ -f "$file" ]; then  # Check if it's a regular file
        echo "Processing file: $file"
    basename=$(basename "$file")
    # Remove the ".gpkg" extension
    reg="${basename%.gpkg}"
    
    # rh98 in cm ----    
    gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/global/global_bash_2year/sub_$reg   -r $file  -l2a geolocation/rh_a1_098 -t0 2021-01-01 -t1 2022-12-31  --quality --geo  
        # Add your code here to perform operations on each file
    echo "#### one region is done!!!"
    sleep 5

    fi
done

# test
# /gpfs/data1/vclgp/xiongl/GEDIglobal/pythonTiles/tiles/90W_30S.gpkg
#gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/global/global_bash/sub_90W_30S   -r /gpfs/data1/vclgp/xiongl/GEDIglobal/pythonTiles/tiles/90W_30S.gpkg  -l2a geolocation/rh_a1_098 -t0 2022-01-01 -t1 2022-12-31  --quality --geo -q '`geolocation/rh_a1_098` >= 200 and `geolocation/rh_a1_098` < 20000' 
