# gedi_ease_map
using EASE grid to plot global canopy height map
# idea to make the plot
## Step 1 make ease tiles
binsize = 1000 , tilesize_x = 2481, tilesize_y = 2438, ease2_origin = -17367000, 7314000

https://nsidc.org/data/user-resources/help-center/guide-ease-grids

## Step 2 use h3 to extract gedi metrics in each tile
it takes one day to finish.
## Step 3 convert lat lon to X and Y in EASE grid.
## Step 4 gridding to Tif in each tile.
## Step 5 mosaic tif to a global map.