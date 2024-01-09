#!/bin/bash

folder="/gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles"
# Loop through each file in the folder
for file in "$folder"/*
do
    if [ -f "$file" ]; then  # Check if it's a regular file
        echo "Processing file: $file"
    basename=$(basename "$file")
    # Remove the ".gpkg" extension
    reg="${basename%.gpkg}"  
    gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/$reg -r $file -l2a rh_098 --quality -q  "rh_098 >= 5 and rh_098 < 120"   -n 20  --geo --merge
    echo "#### $reg is done!!!"
    sleep 5
    fi
done