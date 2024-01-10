#!/bin/bash
# activate the environment.
# | l2a       | rh_098                 | float   |
# rh_098  is in cm or m?
gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/X7_Y3 -r /gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles/X7_Y3.gpkg -l2a rh_098 --quality -q  "rh_098 >= 5 and rh_098 < 120"   -n 15  --geo --merge

gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/X9_Y5 -r /gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles/X9_Y5.gpkg -l2a rh_098 --quality -q  "rh_098 >= 5 and rh_098 < 120"   -n 15  --geo --merge