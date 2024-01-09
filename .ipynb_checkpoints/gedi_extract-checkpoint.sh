#!/bin/bash
# activate the environment.
# | l2a       | rh_098                 | float   |
# rh_098  is in cm or m?
gh3_extract_shots -o /gpfs/data1/vclgp/xiongl/GEDIglobal/data_tiles/X4_Y4 -r /gpfs/data1/vclgp/xiongl/GEDIglobal/ease_tiles/X4_Y4.gpkg -l2a rh_098 --quality -q  "rh_098 >= 5 and rh_098 < 120"   -n 15  --geo --merge