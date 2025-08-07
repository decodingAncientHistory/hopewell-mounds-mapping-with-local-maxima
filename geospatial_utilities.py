#!/usr/bin/python3
import os
import subprocess
import numpy as np
import rasterio
from osgeo import osr, ogr

def write_pnts_shpfile(outname_shp: str, coordinates: np.ndarray) -> None:
  '''
  Method to write a points shapefile.

  Args:
    outname_shp (str): name of output shapefile containing points
    coordinates (numpy.ndarray): Nx2 array of decimal degrees -- coordinates
  '''
  spatial_ref = osr.SpatialReference()
  prj = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
  spatial_ref.ImportFromProj4(prj)
  spatial_ref.MorphToESRI()
   
  drv = ogr.GetDriverByName("ESRI Shapefile")
  if os.path.exists(outname_shp): 
    drv.DeleteDataSource(outname_shp)
        
  shapeData = drv.CreateDataSource(outname_shp)
  pntLayer = shapeData.CreateLayer(outname_shp, spatial_ref, \
          geom_type = ogr.wkbPoint)

  layerDefn = pntLayer.GetLayerDefn()
  pnt = ogr.Geometry(ogr.wkbPoint)

  row_index = 0
  while row_index < coordinates.shape[0]:

    lng, lat = coordinates[row_index, 0], coordinates[row_index, 1]
    pnt.AddPoint(float(lng), float(lat))
    
    feature = ogr.Feature(layerDefn)
    feature.SetGeometry(pnt)
    feature.SetFID(row_index)
    
    pntLayer.CreateFeature(feature)
    row_index += 1
       
  proj = open(outname_shp.replace('shp', 'prj'),"w")
  proj.write(spatial_ref.ExportToWkt())
  proj.close()
  shapeData.Destroy()

def rows_columns_to_map_coordinates(tiff_filename: str, rows_columns: np.ndarray) -> np.ndarray:
  '''
  Convert Nx2 NumPy array with row-column pairs to map coordinates in
  decimal degrees. Use a Geotiff file to this end.

  Args:
    tiff_filename (str): name of Geotiff file.
    rows_columns (numpy.ndarray): Nx2 array of rows and column pairs
    
  Returns:
    numpy.ndarray: output coordinates in decimal degrees.
  '''
  output_coordinate_pairs = []

  with rasterio.open(tiff_filename) as src:
    
    transform = src.transform
    nrows = rows_columns.shape[0]
    row_index = 0
    
    while row_index < nrows:
      row, column = rows_columns[row_index, 0], rows_columns[row_index, 1]
      lon, lat = rasterio.transform.xy(transform, row, column)
      output_coordinate_pairs.append([lon, lat])
      row_index += 1
  return np.array(output_coordinate_pairs, dtype = np.float32)

def csv_to_geotiff(csv_filename: str, outname_tiff: str) -> None:
  '''
  Take a CSV file with 3 columns (easting, northing, and elevation e.g. longitude,
  latitude, and height, and use the gdal_grid command-line tool, from the GDAL
  suite, to dump out a gridded geotiff file.

  It is also REQUIRED to have the gdal_grid command-line tool installed (part of
  GDAL command-line tools suite e.g. /usr/bin/gdal_grid)

  Args:
    csv_filename (str): input CSV filename. MUST end with ".csv" for this to work
    outname_tiff (std): output filename for geotiff to be created
  '''
  # if the output geotiff file already exists, remove it
  # ----------------------------------------------------
  if os.path.isfile(outname_tiff):
    os.remove(outname_tiff)

  # write out the .vrt file to be used for gridding
  # -----------------------------------------------
  outname_vrt = csv_filename.replace('.csv', '.vrt')
  if os.path.isfile(outname_vrt):
    os.remove(outname_vrt)

  # write out the VRT file
  # ----------------------
  with open(outname_vrt, 'w') as f_vrt:
    f_vrt.write('%s\n' % '<OGRVRTDataSource>')
    f_vrt.write('%s\n' % '  <OGRVRTLayer name="dem">')
    f_vrt.write('%s\n' % (    '<SrcDataSource>' + csv_filename + '</SrcDataSource>'))
    f_vrt.write('%s\n' % '     <GeometryType>wkbPoint</GeometryType>')
    f_vrt.write('%s\n' % '     <GeometryField encoding="PointFromColumns" x="Easting" y="Northing" z="Elevation"/>')
    f_vrt.write('%s\n' % '  </OGRVRTLayer>')
    f_vrt.write('%s\n' % '</OGRVRTDataSource>')

  # finally, use gdal_grid to write out geotiff ... 
  #   e.g. gdal_grid dem.vrt out_mounds.tif
  # -----------------------------------------------
  geotiff_regrid_cmd = ' '.join(['gdal_grid', '-q', outname_vrt, outname_tiff])
  proc = subprocess.Popen(geotiff_regrid_cmd, shell = True, 
          text = True, stdout = subprocess.PIPE)
  stdout, stderr = proc.communicate()

  # clearn up and remove the .vrt file
  # ----------------------------------
  if os.path.isfile(outname_vrt):
    os.remove(outname_vrt)

def xyz_to_csv(x: np.ndarray, y: np.ndarray, z: np.ndarray, csv_filename: str) -> None:
  '''
  Simple method to take 3 NumPy arrays and write a 3-column
  CSV file. To be used later by gdal_dem (possibly).

  Args:
    csv_filename (str): output filename of CSV
    x (numpy.ndarray): longitude coordinates
    y (numpy.ndarray): latitude coordinates
    z (numpy.ndarray): elevation coordinates
  '''
  # if the CSV file already exists, remove it (so we overwrite)
  # -----------------------------------------------------------
  if os.path.isfile(csv_filename):
    os.remove(csv_filename)

  # open up file object for CSV file for writing and write header
  # -------------------------------------------------------------
  f_csv = open(csv_filename, 'w')
  f_csv.write('%s\n' % 'Easting,Northing,Elevation')

  # iterate through points, write out as comma-separated string
  # -----------------------------------------------------------
  for x_pnt, y_pnt, z_pnt in zip(x, y, z):
    out_str = ','.join([str(x_pnt), str(y_pnt), str(z_pnt)])
    f_csv.write('%s\n' % out_str)

  # close out the dataset
  # ---------------------
  f_csv.close()
