#!/usr/bin/python3
import laspy
import sys
import numpy as np

from matplotlib.path import Path
from pyproj import Proj, Transformer
from osgeo import osr
from functools import partial

class lidar(object):
 
  def __init__(self, filename) -> None:
    '''
    Initialize a lidar object.

    Args:
      filename: name of .laz file containing lidar data.
    '''
    self.filename = filename

  def get_proj_str(self) -> str:
    '''
    Get the projection string from the .laz
    lidar file.
    '''
    return self.get_header().vlrs[0].string

  def get_pnt_count(self) -> int:
    '''
    Retrun the number of points in the .laz lidar file.
    '''
    return self.get_header().point_count

  def get_xyz(self) -> tuple:
    '''
    Get the XYZ points from the lidar .laz file.
    '''
    with laspy.open(self.filename) as f:
      las = f.read()
      return (las.X, las.Y, las.Z)

  def get_header(self) -> str:
    '''
    Get the header from the lidar .laz file.
    '''
    with laspy.open(self.filename) as f:
      return f.header

  def get_scaling_factors(self) -> tuple:
    '''
    Get the scaling factors in e.g. (0.01, 0.01, 0.01)
    '''
    return self.get_header().scale

  @staticmethod
  def lat_lng_in_bbox(pnt, bbox) -> bool:
    '''
    Check if a longitude-latitude (e.g. X, Y) point
    is inside a rectangular bounding box.

    Args:
      pnt (tuple): longitude and latitude point.
      bbox (tuple): bounding box coordinates left, bottom, right, top.

    Returns:
      bool: if point is inside bounding-box or not.
    '''
    lng, lat = pnt 
    lon_min, lat_min, lon_max, lat_max = bbox 

    if lon_min <= lng <= lon_max and lat_min <= lat <= lat_max:
      return True
    return False

  @staticmethod
  def filter_lng_lats_to_polygon(lng_lats, polygon_coordinates) -> np.ndarray:
    '''
    Filter set of longitude-latitude points to only those inside a set of points
    defining a polygon.

    Args:
      lng_lats: Nx2 (2-column) NumPy array of longitudes and latitudes.
      polygon_coordinates (list): list of points, or list of tuples defining a polygon.

    Returns:
      np.ndarray: numpy array of indices where points are inside polygon.
    '''
    polygon_path = Path(polygon_coordinates)
    within_polygon_indices = polygon_path.contains_points(lng_lats).nonzero()
    out_lng_lats = lng_lats[within_polygon_indices, :][0]
    return (out_lng_lats, within_polygon_indices)

  @staticmethod
  def filter_lng_lats_to_bbox(lng_lats, bounding_box) -> np.ndarray:
    '''
    Get indices of where a set of longitude-latitude points (array)
    are inside a bounding box.

    Args:
      lng_lats (numpy.ndarray): Nx2 (2-column) NumPy array of longitudes and latitudes
      bounding_box (tuple): (left, bottom, right, top) - decimal degrees

    Returns:
      np.ndarray: numpy array of indices where points are inside bounding-box.
    '''
    partial_func = partial(
            lidar.lat_lng_in_bbox, bbox = bounding_box)
    result = list(map(partial_func, lng_lats.tolist()))
    result = np.array(result)
    return np.where(result == True)[0]

  def xyz_to_wgs84(self) -> tuple:
    '''
    Convert longitude-latitude coordinates from native projection from
    .laz lidar file to decimal degrees (WGS84).

    Returns:
      tuple: first element is Nx2 column array of longitudes-latitudes.
        Second element are scaled Z values.
    '''
    (X, Y, Z) = self.get_xyz()
    scale_factors = self.get_scaling_factors()
    X = X * scale_factors[0]
    Y = Y * scale_factors[1]
    Z = Z * scale_factors[2]

    proj_str = self.get_proj_str()
    inProj = osr.SpatialReference()
    inProj.ImportFromWkt(proj_str)
    inProj = Proj(inProj.ExportToProj4())
    outProj = Proj(proj = 'latlong', datum = 'WGS84')

    trans = Transformer.from_proj(inProj, outProj, always_xy = True)
    xx, yy = trans.transform(X, Y)
    XY = np.column_stack((xx, yy))
    return (XY, Z)
