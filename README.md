###### SAMPLE PYTHON 3 CODE TO MAP HOPEWELL NATIVE AMERICAN MOUNDS USING LOCAL MAXIMA

    The Python 3 codes in this repository is a simple example of using Python 3's scikit-image
    library, and it's peak_local_max() utility, to attempt to count and map the Native-American
    Mounds (Hopewell Mounds) in Chillicothe, Ohio.

    To this end, lidar data (.laz file) is downloaded from the USGS:
    https://apps.nationalmap.gov/downloader/#/

    The data in this file (in the form of X, Y, and Z) is in the form of XYZ triplets. This data is filtered 
    so that only the XYZ points, inside a polygon enclosing the mounds themselves, are used (so that surrounding
    trees/woods are mostly filtered out). Later, the XYZ data are dumped into a .CSV file; this CSV file is then used
    by the gdal_grid utility to create an interpolated output Geotiff. 
    
    The data from this Geotiff is further filtered using a Gaussian blur, with a subsequent
    usage of the skimage.feature.peak_local_max(), to map the local maxima e.g. the "peaks" of the mounds.
    Final result is written out to a "points" shapefile. Visualization may be done in QGIS.
       
###### COMMAND-LINE USAGE:

    Install pre-requisites (if necessary). For example, on Ubuntu/Debian:
    
    $ pip3 install numpy
    $ pip3 install matplotlib
    $ pip3 install laspy
    $ pip3 install "laspy[laszip]"
    $ pip3 install scipy
    $ pip3 install GDAL

    *Also note the GDAL command-line utilities are required (e.g. gdalinfo, gdal2tiles.py, gdalwarp, etc.);
    here, the gdal_dem utility is required to take a CSV file containing Lidar XYZ points, and interpolate
    to dump out a Geotiff file.

    First make an output directory (call it "outputs"):
    $ mkdir outputs

    Then to run at command-line, pass in the name of the lidar data file (.laz):
    $ python3 hopewell_mounds_local_maxima.py data/USGS_LPC_OH_Statewide_Phase3_2021_B21_BS18250501.laz

###### INPUT DATA

    Input data file(s) can be downloaded from the U.S. Geological Survey's
    Earth Explorer Website:
      https://earthexplorer.usgs.gov/
    
###### Python version:
     
    Uses Python 3.8.x+
       
###### Sample Imagery

    Hopewell mounds visualization:
![Alt text](https://64.media.tumblr.com/01dfb3d951e4720dfcad68218f6795ee/5897fe13f3538212-04/s1280x1920/dce6eec6678410cc7418d1c900b93a07dffd6e4c.pnj)

    Hopewell mounds (not easily visible) with surrounding woods/forest:
![Alt text](https://64.media.tumblr.com/99b527de14ab0d3af13c8d82efd3a874/5897fe13f3538212-d8/s1280x1920/2e5c4b8add22287e8fdf3c136bf7f2f13c4548b7.pnj)
        
###### @author: 
    Gerasimos Michalitsianos
    gerasimosmichalitsianos@protonmail.com
    Lakithra@protonmail.com
    6 August 2025
