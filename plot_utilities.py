import os
from matplotlib.pylab import *
import matplotlib.pyplot as plt

def plot_2d_birds_eye(array2d, outname_png):
  if os.path.isfile(outname_png):
    os.remove(outname_png)

  ioff()
  plt.title('')
  matshow(array2d)
  colorbar()
  plt.savefig(outname_png, dpi = 200)
  plt.close()

def plot_surface_xyz(xx, yy, zz, outname_png):
  
  ioff()
  if os.path.isfile(outname_png):
    os.remove(outname_png)
  fig = plt.figure()
  
  ax = fig.add_subplot(111, projection = '3d')
  ax.view_init(elev = 70)
  surf = ax.plot_surface(xx, yy, zz, cmap = plt.cm.terrain)
  
  ax.set_xlabel('longitude', fontsize = 4)
  ax.set_ylabel('latitude', fontsize = 4)
  ax.set_zlabel('height', fontsize = 8)
  
  fig.colorbar(surf)
  plt.savefig(outname_png, dpi = 200)
  plt.close()

def visualize_mounds(x, y, z, outname_png):

  ioff()
  fig = plt.figure()
  ax = fig.add_subplot(111, projection = '3d')
  ax.view_init(elev = 70)

  surf = ax.plot_trisurf(x, y, z, cmap = plt.cm.terrain,
                         linewidth = 0, antialiased = True, shade = True)
  ax.set_xlabel('longitude', fontsize = 4)
  ax.set_ylabel('latitude', fontsize = 4)
  ax.set_zlabel('height', fontsize = 8)

  ax.tick_params(axis = 'both', which = 'major', labelsize = 4)
  fig.colorbar(surf)
  
  if os.path.isfile(outname_png):
    os.remove(outname_png)
  plt.savefig(outname_png, dpi = 200)
  plt.close()
