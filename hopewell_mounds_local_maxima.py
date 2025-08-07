#!/usr/bin/python3
import os
import sys
import json
import numpy as np

from lidar import lidar
from plot_utilities import * 
from geospatial_utilities import *

from skimage.feature import peak_local_max
from osgeo import osr, gdal
from scipy.interpolate import griddata
from skimage.filters import gaussian

# define constants
# ----------------
THIS_FILE = __name__
USAGE = f'USAGE: $ python3 {THIS_FILE} <lidar_filename|.laz>'
TREE_HEIGHT_THRESH = 670 
ELEVATION_THRESH_LOCAL_MAX = 646

def main():
  
  # get name of input lidar file
  # ----------------------------
  lidar_laz_filename = None
  try:
    lidar_laz_filename = sys.argv[1]
  except Exception as e:
    print(USAGE)
    sys.exit(1)

  lidar_ob = lidar(lidar_laz_filename)
  (lons_lats, z) = lidar_ob.xyz_to_wgs84()
  
  # read JSON file containing points enclosing mounds
  # -------------------------------------------------
  polygon_vertices = []
  with open('data/mounds_area_coordinates_polygon.json', 'r') as fpoints:
    polygon_coordinates = tuple(
            json.load(fpoints)['coordinates'][0])

  # let's filter the longitude-latitude points to ONLY
  # those inside the polygon enclosing the mounds (leaving out most of
  # the surrounding forest)
  # ------------------------------------------------------------------
  (lons_lats, polygon_indices) = lidar.filter_lng_lats_to_polygon(
          lons_lats, polygon_coordinates)
  
  lons = lons_lats[:, 0]
  lats = lons_lats[:, 1]
  z = z[polygon_indices]

  # now threshold to remove trees from the image (vertical threshold)
  # -----------------------------------------------------------------
  nontree_indices = np.where(z < TREE_HEIGHT_THRESH)[0]
  lons = lons[nontree_indices]
  lats = lats[nontree_indices]
  z = z[nontree_indices]

  # convert the 1D arrays of longitudes (X), latitudes (Y), and Z values
  # (elevation) to a re-gridded Geotiff
  # --------------------------------------------------------------------
  outname_png = 'outputs/hopewell_mounds.png'
  csv_filename = 'outputs/dem.csv'
  outname_tiff = 'outputs/hopewell_mounds.tif'

  visualize_mounds(lons, lats, z, outname_png)
  xyz_to_csv(lons, lats, z, csv_filename)
  csv_to_geotiff(csv_filename, outname_tiff)
 
  # now that we have geotiff, blur it out
  # -------------------------------------
  ds_tiff = gdal.Open(outname_tiff)
  geotiff_band = ds_tiff.GetRasterBand(1).ReadAsArray() 
  blurred = gaussian(geotiff_band, sigma = 2, preserve_range = True)
  plot_2d_birds_eye(blurred, 'outputs/blurred_mounds.png')
 
  row_column_max_coordinates = peak_local_max(blurred, 
          threshold_abs = ELEVATION_THRESH_LOCAL_MAX)
  lng_lat_max_coordinates = rows_columns_to_map_coordinates(
          outname_tiff, row_column_max_coordinates)
  write_pnts_shpfile('outputs/mound_locations.shp', lng_lat_max_coordinates)

if __name__ == '__main__':
  main()
