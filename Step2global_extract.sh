#!/bin/bash
#module unload gdal
#conda activate /gpfs/data1/vclgp/decontot/environments/gedih3
folder="/gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles_v2"
# Loop through each file in the folder
for file in "$folder"/*
do

    echo "Processing file: $file"
    basename=$(basename "$file")
    # Remove the ".gpkg" extension
    reg="${basename%.gpkg}"  
    # Check if the file exists
    if [ -f "/gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/$reg.parquet" ]; then
   	     echo "File $reg.parquet exists."
    else
         echo "File $reg.parquet does not exist."
         # Donot any height filtering yet.
    	 # -q  "rh_098 >= 5 and rh_098 < 120"
    	 gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/$reg -r $file -l2a rh_098 --quality -n 15  --geo  --port 12510
    fi

    echo "#### $reg is done!!!"
    #sleep 5
done
