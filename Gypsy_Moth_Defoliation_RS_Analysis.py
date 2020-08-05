#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
Title: Identfying Remote Sensing Indicators of & Classifying Gypsy Moth Defoliation
Date: July 13, 2020

Description: This script was developed alongside my Intermediate Quantiative Method course project.
The purpose of this project was to identify the most appropriate remote sensing indicators of Gypsy Moth defoliation and
compare two populer methods of binary classification, Logisitic Regression and Discriminant Analysis. The study area
for this study is an area of Gypsy Moth defoliation in New England (RI, CT, and Southern MA) from 2016. 
This project used the Landsat8 imagery (Bands1-7) and two raster layers provided by a doctoral student at Clark University. The first layer is a NLCD
landcover map of the study area. The second layer is a binary classification of defoliation derived from the S-CCD algorithm.

In this script, first I geoprocess the raster layers and prepare them for analysis. Then, I used TOC curves and Partial
Component Analysis to assess which remote sensing indicators were best for identifying defoliation. Finally, using Su's
binary classification as a "truth", I assessed whether Logistic Regression or Discriminant Analysis was better at
differentiatingbetween the two classes.

Note: This script uses R and Pythn simultaneously. This was done to access the TOC package available in R, but is not
available in Python.

''' 


#Import relevent libraries
import numpy as np
#Panda is a library for creating datframes
import pandas as pd
#SciKit learn is a library for scientific methods and tools
import sklearn
#matlpotlib is a library for data visualization
import matplotlib.pyplot as plt
#Seaborn is a library linked to matplotlib which makes nice graphics
import seaborn as sns
#Fiona is a library used to open and read geospatial files
from fiona.crs import from_epsg
#Geopandas is a library for making geographically referenced dataframe
import geopandas as gpd
#OS allows you to set a working folder. 
import os
#PyCrs is a library for converting between coordinate systems
import pycrs
#Rasterio is a library for processing geospatial data
import rasterio as rio
#Load R language into Python. I am doing this because I want to use a particular package
import rpy2.rinterface
#Set working folder here
dir = os.chdir("C:\\Users\\Emily\\Documents\\Summer_2020\\Py_DataScience_and_MachineLearning\\original\\Gypsy_Moth\\Landsat8Imagery")


# In[2]:


get_ipython().run_line_magic('load_ext', 'RWinOut')
#This ipython extension gets around display problems in the regular rpy2 extension


# # Geoprocessing of Raster Layers

# In[3]:


#Import TIF files - Landsat 8 and Gypsy Moth 
#Landsat 8 imagery for study area. The date of this imagery is July 13, 2016
tif1 = r"LC08_012031_20160713.tif"
#Hard classification of Gypsy Moth defoliation produced via SCCD 
tif2 = r"gm_esri_UTM.tif"
#Landcover types
tif3 = r"Mask_LC_UTM.tif"


# In[4]:


#Use rasterio to open tif files and set them to a variable. NOw one can maniplulate the data
raster1 = rio.open(tif1)
SY_Data = rio.open(tif2)
raster2 = rio.open(tif3)


# In[5]:


#Print metadata for each file to make sure images are functioning correctly. 
#This also reveals each layers size, projection, etc.
print(SY_Data.meta)
print(raster1.meta)
print(raster2.meta)


# In[6]:


#Display raster data. This is also a test to see if that data is functioning correctly and allows to compare how each layer overlaps.
from rasterio.plot import show
#Show Landsat 8 tif. This shows the composit image, but one can also look at each band. 
show(raster1)


# In[7]:


#Show hard classification
#Purpler = 0 (Foliated), Yellow = 1 (Defoliated). There are also some missing values here marked as "3".
show(SY_Data)


# In[8]:


#Show landuse data
#There are about 15 different landuse classes in this map. Eventually, I want to isolated 41 (Deciduous Forest) and 
#43 (Mixed Forest), so limit spectral outliers.
show(raster2)


# In[ ]:


#Here, I am reprojecting the TIF file to match the projection of the hard classification data. This code can be found 
#on the rasterio documentation.
#All of my files ave an original projection of the Landsat 8 imagery is EPSG3261 (UTM 19N). I am changing it to EPSG6350 
#(AlbersUS 1983). I did this because we're in a very small area and I want to ability to calculate area if necessary.

#Set variable with desired projection
dst_crs = 'EPSG:5070'

#This function changes the image metadata, reprojects & resamples each band of the image, and saves it as a new file.
#I turned this projection into a function so it can be used repeatedly. It takes four arguments - the input image name, the output
#image name, the new projection, and resample type.
def reproject(in_img, out_img, dst_crs, resample_type):
    import numpy as np
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    #The first section updates the image metadata
    #First, it opens the original image
    with rasterio.open(in_img) as src:
        #Then, it stores the transform, width, and height for the new image. This determined using the "calculate
        #_default_transform function". It calculates the transofrmation between the original projection and the new one
        #while maintaining the original image dimensions.
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        #Here, I used the variables above to update the metadata. Very important!
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        #The second section outputs the new reprojected and resampled image
        #First, I identify the new file and allow python to write to the file
        with rasterio.open(out_img, 'w', **kwargs) as dst:
            #Now, I iterate through every band of each image reprojecting and resampling
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=resample_type)


# In[ ]:


#Reproject the landuse map using Nearest Neighbor resampling
reproject("Mask_LC_UTM.tif", "Mask_LC_UTM_Albers83.tif", 'EPSG:5070', Resampling.nearest)


# In[ ]:


#Reproject the Gypsy Moth defoliation map using Nearest Neighbor resampling
reproject("gm_esri_UTM.tif", "gm_esri_UTM_Albers83.tif", 'EPSG:5070', Resampling.nearest)


# In[ ]:


#Reproject the Landsat8 Bands using Bilinear resampling
reproject("LC08_012031_20160713.tif", "LC08_012031_20160713_Reproj.tif", 'EPSG:5070', Resampling.bilinear)


# In[9]:


#Now I will mask all of image files to a specific polygon vector. 

#Import the polygon creation function
from shapely.geometry import Polygon
#Create a polygon and set the coordinate points. 
poly = Polygon([(1990000, 2331000), (1991000, 2353000), (1984000, 2353000), (1973000, 2352000), (1975000, 2328000), (1990000, 2331000)])
#I tested that this function worked by calculating the area
poly.area


# In[10]:


from shapely.geometry import box

GMbb = box(1991000, 2328000, 1973000, 2353000)


# In[11]:


#Here I create a geodataframe using GeoPandas to contain my polygon feature. This line inserts the polygon I created
#into a dataframe and assigns the projection.
geo = gpd.GeoDataFrame({'geometry': GMbb}, index=[0], crs=from_epsg(5070))
#I assigned the geometry column to the "geom" named column. Prior to this, json was having trouble identifying geomtries
#in my geopandas dataframe. Not sure if it's completely necessary now because I reinstalled the package since. 
#geo = geo.rename(columns={'geometry': 'geom'}).set_geometry('geom')
#Print dataframe
print (geo)


# In[12]:


#Checking that my geopandas dataframe is valid
from rasterio.features import is_valid_geom
is_valid_geom(geo.iloc[0]['geometry'])

#This funciton parses the geodataframe into a format which can be used for rasterio
def getFeatures(gdf):
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

#Here, I set the parsed coordinates to a variables and print them
coords = getFeatures(geo)
print(coords[0])


# In[13]:


#A function to mask each image
def mask_img(in_img, out_img, shape):
    #open the source image
    with rio.open(in_img) as src:
        from rasterio.mask import mask
        #crop the source image using the polygon shape and crop the image.
        out_image, out_transform = mask(src, shape, crop=True)
        #Originally, we will copy over the source metadata
        out_meta = src.meta
        #Update image size and transformation
        out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    #Write new image
    with rio.open(out_img, "w", **out_meta) as dest:
        dest.write(out_image)


# In[14]:


#Mask Landcover Data
mask_img("Mask_LC_UTM_Albers83.tif", "LC_masked.tif", coords)


# In[15]:


#Mask Gypsy Moth 2016 Data
mask_img("gm_esri_UTM_Albers83.tif", "GM_masked.tif", coords)


# In[16]:


#Mask Satellite Imagery
mask_img("LC08_012031_20160713_Reproj.tif", "LC08_012031_20160713_Masked.tif", coords)


# # Dataframe Preprocessing

# In[15]:


#Open and flatten all clipped layers as numpy arrays so they can be organized into a Pandas dataframe
#Here I use the package OSGEO (an open-source library for geogrpahic data) to convert my TIF imagery to numpy arrays. 
#I had issues trying to do this with rasterio hence why I used this other library.
from osgeo import gdal
#Open the masked landuse image
ds = gdal.Open("LC_masked.tif")
#Specify the band you want and read is as an array
Clip_LC = np.array(ds.GetRasterBand(1).ReadAsArray())
#I printed the shape as a check point - I want to make sure all of my files definitely have the same geometry
print (Clip_LC.shape)
#Here I flatten the 2-D array to a 1-D array
Clip_LC = Clip_LC.flatten()
#Print length of the 1-D array, i.e. the # of observations of per column in the dataframe
print (len(Clip_LC))

#Repeat the process for the Defoliation layer
ds = gdal.Open("GM_masked.tif")
Clip_GM = np.array(ds.GetRasterBand(1).ReadAsArray())
print(Clip_GM.shape)
Clip_GM = Clip_GM.flatten()
print (len(Clip_GM))

#For the final TIF, we will repeat the process for each band of the Landsat8 image
#The process is the same, except I alter the band number
ds = gdal.Open("LC08_012031_20160713_Masked.tif")
Band1 = np.array(ds.GetRasterBand(1).ReadAsArray())
print (Band1.shape)
Band1 = Band1.flatten()
print (len(Band1))
Band2 = np.array(ds.GetRasterBand(2).ReadAsArray())
Band2 = Band2.flatten()
Band3 = np.array(ds.GetRasterBand(3).ReadAsArray())
Band3 = Band3.flatten()
Band4 = np.array(ds.GetRasterBand(4).ReadAsArray())
Band4 = Band4.flatten()
Band5 = np.array(ds.GetRasterBand(5).ReadAsArray())
Band5 = Band5.flatten()
Band6 = np.array(ds.GetRasterBand(6).ReadAsArray())
Band6 = Band6.flatten()
Band7 = np.array(ds.GetRasterBand(7).ReadAsArray())
Band7 = Band7.flatten()
Band8 = np.array(ds.GetRasterBand(8).ReadAsArray())
Band8 = Band8.flatten()
               


# In[16]:


#Stack all data using Numpy. This allows each image to become a column in the dataframe
GM_Stack = np.column_stack([Clip_LC, Clip_GM, Band1, Band2, Band3, Band4, Band5, Band6, Band7, Band8])


# In[17]:


#A Pandas dataframe was then created from with the vertically stacked 2D array, GM_Data, and assigned column names.
GM_Data = pd.DataFrame(GM_Stack, columns=['Landcover', 'GM_Presence', 'Band1', 'Band2', 'Band3', 'Band4', 'Band5', 'Band6', 'Band7', 'Band8'])
#Get a description of data - a check to make sure it looks okay
GM_Data.describe()


# In[18]:


#Here I Replace Null values with Zero
GM_Data.fillna(0, inplace=True)
#Sum all the null values in each column to make sure it worked
GM_Data.isnull().sum()


# In[19]:


#Check what unique landcover types there are
GM_Data.Landcover.unique()


# In[20]:


# Replacing rows with 0 where Landcover is not 41 (Deciduous) and 43 (Mixed Forest)
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'GM_Presence'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band1'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band2'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band3'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band4'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band5'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band6'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band7'] = 0
GM_Data.loc[((GM_Data['Landcover'] != 43.0) & (GM_Data['Landcover'] != 41.0)), 'Band8'] = 0

# Replace rows with 0 where Cloudcover = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band1'] = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band2'] = 0             
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band3'] = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band4'] = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band5'] = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band6'] = 0
GM_Data.loc[(GM_Data['Band8'] == 0.0), 'Band7'] = 0

#This is the final form of my original dataframe - GM_Data


# In[21]:


#Drop rows which are not target landuses, where the GM layer hase no data, or if the rows are covered in clouds
indexNames = GM_Data[(GM_Data['Landcover'] != 41) & (GM_Data['Landcover'] != 43) | (GM_Data['GM_Presence'] == 3) | (GM_Data['Band8'] == 0)].index
#Make a new dataframe with only the select rows. However, this will maintain the original index
GM_Select = GM_Data.drop(indexNames)


# In[22]:


#Using the limited dataframe, I created new columns and calculated RS Indices
GM_Select['NDVI'] = (GM_Select['Band5'] - GM_Select['Band4'])/(GM_Select['Band5'] + GM_Select['Band4'])
GM_Select['SAVI'] = (GM_Select['Band4'] - GM_Select['Band3'])/((GM_Select['Band4'] + GM_Select['Band3'] + 0.5) * 1.5)
GM_Select['MSAVI'] = (2 * GM_Select['Band4'] + 1 - np.sqrt((2 * GM_Select['Band4'] + 1)**2 - 8*(GM_Select['Band4'] - GM_Select['Band3']))/2)
GM_Select['NDMI'] = (GM_Select['Band5'] - GM_Select['Band6'])/(GM_Select['Band5'] + GM_Select['Band6'])
GM_Select['TCBright'] = (0.3029*GM_Select['Band2'] + .2786*GM_Select['Band3'] + .4733*GM_Select['Band4'] + .5599*GM_Select['Band5'] + .508*GM_Select['Band6'] + .1872*GM_Select['Band7'])
GM_Select['TCGreen'] = (-.2941*GM_Select['Band2'] + -.243*GM_Select['Band3'] + -.5424*GM_Select['Band4'] + .7276*GM_Select['Band5'] + .0713*GM_Select['Band6'] + -.1608*GM_Select['Band7'])
GM_Select['TCWet'] = (0.1511*GM_Select['Band2'] + .1973*GM_Select['Band3'] + .3283*GM_Select['Band4'] + .3407*GM_Select['Band5'] + -.7117*GM_Select['Band6'] + -.4559*GM_Select['Band7'])
#Print to make sure it looks corect
print (GM_Select)
#I exported the limited dataframe to a a CSV in order to open it in the R cells more easliy. I was having trouble transferring the Python dataframe directly to R.
GM_Select.to_csv("C:\\Users\\Emily\\Documents\\Summer_2020\\Py_DataScience_and_MachineLearning\\original\\Gypsy_Moth\\Landsat8Imagery\\GM_Select.csv")


# # Multiple TOC Curve

# In[23]:


get_ipython().run_cell_magic('R', '', '#The symbol %%R calls R Magic and designates that this cell will use R, not Python\n#Here I am installing several packages that are dependencies for th TOC package, which is what I want to use\ninstall.packages(\'utils\', repos=\'http://cran.us.r-project.org\', quiet=TRUE )\nlibrary(utils)\ninstall.packages("Rcpp", repos=\'http://cran.us.r-project.org\', quiet=TRUE)\nlibrary(Rcpp)\ninstall.packages("sp", repos=\'http://cran.us.r-project.org\', quiet=TRUE)\nlibrary(sp)\ninstall.packages("bit", repos=\'http://cran.us.r-project.org\', quiet=TRUE)\nlibrary(bit)\ninstall.packages("rgdal", repos=\'http://cran.us.r-project.org\', quiet=TRUE)\nlibrary(rgdal)\ninstall.packages("raster", repos=\'http://cran.us.r-project.org\', quiet=TRUE)\nlibrary(raster)\ninstall.packages(\'TOC\',\'C:/Users/Emily/anaconda3/lib/R/library/\',type = \'source\')\nlibrary(TOC)')


# In[8]:


get_ipython().run_cell_magic('R', '', '##Set the working directory to appropriate folder\nsetwd("C:/Users/Emily/Documents/Summer_2020/Py_DataScience_and_MachineLearning/original/Gypsy_Moth/Landsat8Imagery/")\n##Open the CV+SV saved from the earlier portion of this code.\nGM_Select_r <- read.csv(file ="GM_Select.csv", header=TRUE, dec=".", stringsAsFactors=FALSE)')


# In[11]:


get_ipython().run_cell_magic('R', '', '##Create new numeric variables from dataframe columns. TOC requires this format in order to run. It will not intake columns as is.\nindexB1 <- (GM_Select_r$Band1)\nindexB2 <- (GM_Select_r$Band2)\nindexB3 <- (GM_Select_r$Band3)\nindexB4 <- (GM_Select_r$Band4)\nindexB5 <- (GM_Select_r$Band5)\nindexB6 <- (GM_Select_r$Band6)\nindexB7 <- (GM_Select_r$Band7)\nindexNDVI <- (GM_Select_r$NDVI)\nindexSAVI <- (GM_Select_r$SAVI)\nindexMSAVI <- (GM_Select_r$MSAVI)\nindexNDMI <- (GM_Select_r$NDMI)\nindexTCB <- (GM_Select_r$TCBright)\nindexTCG <- (GM_Select_r$TCGreen)\nindexTCW <- (GM_Select_r$TCWet)\n\n##Create reference boolean image for input into TOC\nboolean <- (GM_Select_r$GM_Presence)')


# In[12]:


get_ipython().run_cell_magic('R', '', '##Create TOC objects. These lines creates 100 equal intervals for each index variable. \n##For these TOC objects, only the Indices change.Ther is one TOC object per index variable.\ntocdB1 <- TOC(indexB1, boolean, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB2 <- TOC(indexB2, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB3 <- TOC(indexB3, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB4 <- TOC(indexB4, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB5 <- TOC(indexB5, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB6 <- TOC(indexB6, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdB7 <- TOC(indexB7, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdNDVI <- TOC(indexNDVI, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n                progress=FALSE, units=character(0))\ntocdSAVI <- TOC(indexSAVI, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n                progress=FALSE, units=character(0))\ntocdMSAVI <- TOC(indexMSAVI, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n                 progress=FALSE, units=character(0))\ntocdNDMI <- TOC(indexNDMI, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n                progress=FALSE, units=character(0))\ntocdTCB <- TOC(indexTCB, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n               progress=FALSE, units=character(0))\ntocdTCG <- TOC(indexTCG, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n               progress=FALSE, units=character(0))\ntocdTCW <- TOC(indexTCW, boolean, mask, nthres=100, thres=NULL, P=NA, Q=NA,\n               progress=FALSE, units=character(0))')


# In[13]:


get_ipython().run_cell_magic('R', '', '#In this cell, I am creating the multiple TOC Curve image\n#Here, I am designating a JPG file to export TOC plot\npng(file = "GM_Multi_TOC_Code.jpg", width = 550, height = 480)\n\n#Set the image plot to a square\npar(pty="s")\n#Create plot object and axes\ngraphics::plot(1, type="l", main = "TOC Curve", lty="dashed",xlab= "Hits+False Alarms (Pixels)", ylab="Hits (Pixels)",lwd=2, col=rgb(128,100,162, maxColorValue=255), xlim=c(0, 314346),ylim=c(0, 101575), bty=\'L\')\n\n#Plotting multiple lines to create multi-TOC plot\n#minimum line\nlines(c(0, 101575), c(0,101575), \n      lty="dotdash", lwd=2, col=rgb(50, 50,50, maxColorValue=255)) \n#maximum line\nlines(c(212771, 314346), c(0,101575), \n      lty="dotdash", lwd=2, col=rgb(50,50,50, maxColorValue=255)) \n\n#hits+misses line\nlines(c(0, 314346), c(101575, 101575), lwd=3, col=rgb(150,150,150, maxColorValue=255))\n\n#uniform line\nlines(c(0, 314346), c(0, 101575), lty="dotted", lwd=2, col=rgb(25,25,25, maxColorValue=255))\n\n#TOC object lines\n#Band1\nlines(tocdB1@table$"Hits+FalseAlarms", tocdB1@table$Hits, lwd=2, col=rgb(255,0,255, maxColorValue=255))\n#Band2\nlines(tocdB2@table$"Hits+FalseAlarms", tocdB2@table$Hits, lwd=2, col=rgb(0,0,255, maxColorValue=255))\n#Band3\nlines(tocdB3@table$"Hits+FalseAlarms", tocdB3@table$Hits, lwd=2, col=rgb(0,255,0, maxColorValue=255))\n#Band4\nlines(tocdB4@table$"Hits+FalseAlarms", tocdB4@table$Hits, lwd=2, col=rgb(255,0,0, maxColorValue=255))\n#Band5\nlines(tocdB5@table$"Hits+FalseAlarms", tocdB5@table$Hits, lwd=2, col=rgb(255,150,50, maxColorValue=255))\n#Band6\nlines(tocdB6@table$"Hits+FalseAlarms", tocdB6@table$Hits, lwd=2, col=rgb(150,150,150, maxColorValue=255))\n#Band7\nlines(tocdB7@table$"Hits+FalseAlarms", tocdB7@table$Hits, lwd=2, col=rgb(100,100,100, maxColorValue=255))\n#NDVI\nlines(tocdNDVI@table$"Hits+FalseAlarms", tocdNDVI@table$Hits, lty="dotted", lwd=2, col=rgb(255,100,255, maxColorValue=255))\n#SAVI\nlines(tocdSAVI@table$"Hits+FalseAlarms", tocdSAVI@table$Hits, lty="dotted", lwd=2, col=rgb(0,0,255, maxColorValue=255))\n#MSAVI\nlines(tocdMSAVI@table$"Hits+FalseAlarms", tocdMSAVI@table$Hits, lty="dotted", lwd=2, col=rgb(100,250,0, maxColorValue=255))\n#NDMI\nlines(tocdNDMI@table$"Hits+FalseAlarms", tocdNDMI@table$Hits, lty="dotted", lwd=2, col=rgb(200,0,0, maxColorValue=255))\n#TasseledCap Brightness\nlines(tocdTCB@table$"Hits+FalseAlarms", tocdTCB@table$Hits, lty="dotted", lwd=2, col=rgb(255,150,50, maxColorValue=255))\n#TasseledCap Greeness\nlines(tocdTCG@table$"Hits+FalseAlarms", tocdTCG@table$Hits, lty="dotted", lwd=2, col=rgb(10,150,0, maxColorValue=255))\n#TasseledCap Wetness\nlines(tocdTCW@table$"Hits+FalseAlarms", tocdTCW@table$Hits, lty="dotted", lwd=2, col=rgb(100,100,100, maxColorValue=255))\n\n#Set area outside plot for legend\npar(xpd=NA)\n#Set legend. Must define names, line color, and line patterns. \nlegend("topright", inset=c(-0.25, 0.2), c("Hits+Misses", "Minimum", "Maximum", "Uniform", "Band1", "Band2", "Band3", "Band4", "Band5", "Band6", "Band7", "NDVI", "SAVI", "MSAVI", "NDMI", "TCBrightness", "TCGreeness", "TCWetness"), \n       col = c(rgb(150,150,150, maxColorValue=255), rgb(50, 50,50, maxColorValue=255), rgb(50,50,50, maxColorValue=255), rgb(25,25,25, maxColorValue=255), rgb(255,0,255, maxColorValue=255), rgb(0,0,255, maxColorValue=255), rgb(0,255,0, maxColorValue=255), rgb(255,0,0, maxColorValue=255),rgb(255,150,50, maxColorValue=255), rgb(150,150,150, maxColorValue=255), rgb(100,100,100, maxColorValue=255), rgb(255, 100, 255, maxColorValue=255), rgb(0,0,255, maxColorValue=255), rgb(100,250,0, maxColorValue=255), rgb(200,0,0, maxColorValue=255), rgb(255,150,50, maxColorValue=255), rgb(10,150,0, maxColorValue=255), rgb(100,100,100, maxColorValue=255)),\n       lty = c(1, 4, 4, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3), merge = TRUE, bty="n", lwd=c(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2))\n\n#End image development. This will output the image.\ndev.off()')


# In[15]:


get_ipython().run_cell_magic('R', '', '#Saving AUC values. I will use these to rank the bands by AUC value\n#For the first part, I am setting the AUC values to variables\naucB1 <- tocdB1@AUC\naucB2 <- tocdB2@AUC\naucB3 <- tocdB3@AUC\naucB4 <- tocdB4@AUC\naucB5 <- tocdB5@AUC\naucB6 <- tocdB6@AUC\naucB7 <- tocdB7@AUC\naucNDVI <- tocdNDVI@AUC\naucSAVI <- tocdSAVI@AUC\naucMSAVI <- tocdMSAVI@AUC\naucNDMI <- tocdNDMI@AUC\naucTCB <- tocdTCB@AUC\naucTCG <- tocdTCG@AUC\naucTCW <- tocdTCW@AUC\n#Here, I am concerned with curviture rather than the raw AUC. \n#Therefore, I subtracted the AUC from 1 for those below the "uniform" line.\nopB5 <- 1.0-aucB5\nopNDMI <- 1.0-aucNDMI\nopNDVI <- 1.0-aucNDVI\nopTCB <- 1.0-aucTCB\nopTCG <- 1.0-aucTCG\nopTCW <- 1.0-aucTCW')


# In[16]:


get_ipython().run_cell_magic('R', '', '#Creating a dataframe for the input variables and their AUC values so I can rank the AUC values\nTOC_df <- data.frame("AUC" = c(aucB1, aucB2, aucB3, aucB4, opB5, aucB6, aucB7, opNDVI, aucSAVI, aucMSAVI, opNDMI, opTCB, opTCG, opTCW), "Name" = c("Band1","Band2", "Band3", "Band4", "Band5", "Band6", "Band7", "NDVI", "SAVI", "MSAVI", "NDMI", "TCB", "TCG", "TCW")) \n\n#Create a new column\nTOC_df$rank <- NA\n#Order the AUC values\norder.AUC <- order(TOC_df$AUC)\n#Create a new dataframe which is order by AUC\nTOC_df1 <- TOC_df[order.AUC,]\n#create a new column called "rank"\nTOC_df1$rank <- rank(TOC_df1$AUC)\n#Display that new dataframe\nTOC_df1')


# In[24]:


#Now I am back to using Python
#I am calling the GM_Select dataframe from before which contain select rows. 
#Remove non-variable bands - Gypsy Moth Presence, Landcover Type, Cloudmask, and Study Area Mask. This will be the independent variables for the classification methods.
Bands_only = GM_Select.drop(['GM_Presence', 'Landcover', 'Band8'], axis=1)
#Checking to make sure it worked
Bands_only.describe()


# # Partial Component Analysis

# In[25]:


#Standardizing independent variables for PCA
import sklearn
#Import scaler tool
from sklearn.preprocessing import StandardScaler
#Set the scaler object
scaler = StandardScaler()
#Standardize the bands
scaler.fit(Bands_only)
#Set transformed bands to a new variable
scaled_data = scaler.transform(Bands_only)


# In[26]:


#Now, I run PCA with the standardized indepenent variables
from sklearn.decomposition import PCA
#Here I designate that I want the first 5 components from PCA
pca = PCA(n_components = 5)
#I used the scaled data to fit PCA
pca.fit(scaled_data)
#Set outputs to new variable
x_pca = pca.transform(scaled_data)
x_pca.shape


# In[27]:


#Display PCA components - correlation for each variable
pca.components_


# In[28]:


#Here I calculate the percent explained variance from the eigenvalues becuase it's easier to interpret. 
#I divided each eigen value by the sum of all the eigenvalues.
C1 = pca.explained_variance_[0]/13.9446753*100
C2 = pca.explained_variance_[1]/13.9446753*100
C3 = pca.explained_variance_[2]/13.9446753*100
C4 = pca.explained_variance_[3]/13.9446753*100
C5 = pca.explained_variance_[4]/13.9446753*100


# In[29]:


#See percent variance explained for each component
#I make a datframe of each compoent, it's eigenvalue, anfd it's percent explained. Here I set the data
data ={'Component #':['1', '2', '3', '4', '5'], 
       'Eigenvalue':[format(pca.explained_variance_[0], '.2f'), format(pca.explained_variance_[1], '.2f'), format(pca.explained_variance_[2], '.2f'), format(pca.explained_variance_[3], '.2f'), format(pca.explained_variance_[4], '.2f')],
       'Percent Variance':[format(C1, '.2f'), format(C2, '.2f'), format(C3, '.2f'), format(C4, '.2f'), format(C5, '.2f')]}
#Then I bring the data into a dataframe and provide column names
PCA_data = pd.DataFrame(data, columns = ['Component #', 'Eigenvalue', 'Percent Variance'])
print(PCA_data)


# In[33]:


#Visualize PCA components
#This cell allows me to call graph the components againts each other. This was more for my own visualization purposes.
import matplotlib.pyplot as plt
import seaborn as sns
#Set figure size
plt.figure(figsize = (8,6))
#Here I graph component 1 vs Component 5
plt.scatter(x_pca[:,0], x_pca[:,4], c=GM_Select['GM_Presence'], cmap='coolwarm')


# In[34]:


#Make a heat map of components
#First I make dataframe of components
PCA_comp = pd.DataFrame(pca.components_)
#Then set column names
PCA_comp.columns = ['Band1', 'Band2', 'Band3', 'Band4', 'Band5', 'Band6', 'Band7', 'NDVI', 'SAVI', 'MSAVI', 'NDMI', 'TCBright','TCGreen','TCWet']
#Display dataframe
PCA_comp


# In[35]:


#Now, I will convert the dataframe of correlations to a heatmap
#Create plot object
plt1 = plt.axes()
#Create a heatmap from the component dataframe
sns.heatmap(PCA_comp, cmap="RdBu_r")
#Set titles and labels
plt1.set_title('Heat Map of PCA Components')
plt1.set_ylabel('Component #')
plt1.set_xlabel('Remote Sensing Indicators')
plt1.set_yticklabels(['1','2','3','4','5'])
#Ensure the labels don't get cutoff
plt.tight_layout()
#Save the figure s a jpeg
plt.savefig('PCA_Heat.jpeg')


# # Logistic Regression

# ### 1. Logistic Model with All Independent Variables

# In[37]:


#Set x & y variables for Logistic Regression
#The first set of x-variables includes all of the independent variables
x = GM_Select.drop(['GM_Presence', 'Landcover', 'Band8'], axis=1)
#The second set ot x-variables includes the select 4-variables (NDVI, NDMI, TCGreen, & TCWet)
x2 = GM_Select.drop(['GM_Presence', 'Landcover', 'Band8', 'Band1', 'Band2', 'Band3', 'Band4', 'Band5', 'Band6', 'Band7', 'SAVI', 'MSAVI', 'TCBright'], axis=1)
#Set dependent variable to Gypsy Moth presence
y = GM_Select['GM_Presence']


# In[38]:


#Split data for training and testin
from sklearn.model_selection import train_test_split
#Here we split the data - using all the independent variables. 70% of the data is used for training, 30% for training
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3)

#Here I create the first logistic regression model
from sklearn.linear_model import LogisticRegression
logModel = LogisticRegression()
#Fit the model with the training data
fit_modelLR = logModel.fit(x_train, y_train)

#Connect predictions back to dataframe
#Here, I create a dataframe of the logisitic model predictions. I set the column index to that from the GM_Select.
#This index will connect back to to large dataframe as well. 
df = pd.DataFrame(logModel.predict(x_test), columns=['LR_All_Pred'], index = x_test.index.copy())
#I merge the predictions to the GM_Select dataframe
df_out = pd.merge(GM_Select, df, how = 'left', left_index = True, right_index = True)
#I fill null values in the prediction column to 2 - these are training data
df_out.fillna(value=2, inplace=True)
print (df_out)


# In[40]:


#I get coefficents and intercept from LR model. This will be used for TOC Curves comparing the classification outcomes.

#Create a nw column with the calculations
df_out['LR_All'] = ((logModel.coef_[0][0]*df_out['Band1'])+
                     (logModel.coef_[0][1]*df_out['Band2'])+
                     (logModel.coef_[0][2]*df_out['Band3'])+
                     (logModel.coef_[0][3]*df_out['Band4'])+
                     (logModel.coef_[0][4]*df_out['Band5'])+
                     (logModel.coef_[0][5]*df_out['Band6'])+
                     (logModel.coef_[0][6]*df_out['Band7'])+
                     (logModel.coef_[0][7]*df_out['NDVI'])+
                     (logModel.coef_[0][8]*df_out['SAVI'])+
                     (logModel.coef_[0][9]*df_out['MSAVI'])+
                     (logModel.coef_[0][10]*df_out['NDMI'])+
                     (logModel.coef_[0][11]*df_out['TCBright'])+
                     (logModel.coef_[0][12]*df_out['TCGreen'])+
                     (logModel.coef_[0][13]*df_out['TCWet'])+logModel.intercept_)


# ### 2. Logistic Regression Model with Select Independent Variable

# In[41]:


#Split data for training and testing. In this case, I set the select variables as the independent variables
x2_train, x2_test, y2_train, y2_test = train_test_split(x2, y, test_size = 0.3)

#Create the second model
logModel2= LogisticRegression()
#Fit the second model using the new training data
fit_modelLR = logModel2.fit(x2_train, y2_train)

#Connect new predictions to a new dataframe
#Dataframe of 2nd LR Model
df = pd.DataFrame(logModel2.predict(x2_test), columns=['LR_Select_Pred'], index = x_test.index.copy())
print(df)
#Merge the dataframe from LR 1 to the new predictions.
df_out2 = pd.merge(df_out, df, how = 'left', left_index = True, right_index = True)
#Again, fill training data null values as 2
df_out2.fillna(value=2, inplace=True)
print (df_out2)


# In[42]:


#Get coefficents and intercept from second LR model.
df_out2['LR_Select'] = (logModel2.coef_[0][0]*df_out2['NDVI'])+(logModel2.coef_[0][1]*df_out2['NDMI'])+(logModel2.coef_[0][2]*df_out2['TCGreen'])+(logModel2.coef_[0][3]*df_out2['TCWet']+logModel2.intercept_)

print (df_out2)


# In[49]:


#This functin creates two coonfusion matrices. ONe not-normlaized and one normalized. It outputs the normalized one.
def confusion_matrix(mod, x, y, name, color):
    from sklearn.metrics import plot_confusion_matrix
    #Here 0 = Foliated, 1 = Foliated
    labels = ['0','1']
    #PLot titles
    titles_options = [("Confusion matrix, without normalization", None),
                      ("Normalized confusion matrix", 'true')]
    for title, normalize in titles_options:
        disp = plot_confusion_matrix(mod, x, y,
                                     display_labels= labels,
                                     cmap= color,
                                     normalize=normalize)
        disp.ax_.set_title(title)

        print(title)
        print(disp.confusion_matrix)
        plt.savefig(name)


# In[50]:


#Create confusion matrix for Logistic Model - All Variables
confusion_matrix(logModel, x_test, y_test, 'Confusion_Mat_LR_All.png', plt.cm.Blues)


# In[51]:


#Create confusion matrix for Logistic Model - Select Variables
confusion_matrix(logModel2, x2_test, y2_test, 'Confusion_Mat_LR_Select.png', plt.cm.Blues)


# # Discriminant Analysis

# ### 1. Discriminant Analysis with All Variables

# In[52]:


#import Discriminant Analysis
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
#Split data for training and testing. Again, 70% Training and 30% Testing.
da_x_train, da_x_test, da_y_train, da_y_test = train_test_split(x, y, test_size = 0.3)

#Create model obejct
daModel = LinearDiscriminantAnalysis()
#Fit model with training data
fit_modelDA = daModel.fit(da_x_train, da_y_train)

#Connect predictions to dataframe with Logistic Regression results
#Create dataframe of Discriminant Analysis prediction results
df = pd.DataFrame(daModel.predict(da_x_test), columns=['DA_All_Pred'], index = x_test.index.copy())
print(df)
#Merge with dataframe produced after the second DA Model
df_da = pd.merge(df_out2, df, how = 'left', left_index = True, right_index = True)
#Replace null values with 2 because that indicates training data.
df_da.fillna(value=2, inplace=True)
#Finally, add new columns with calculated DA linear equation
df_da['DA_All'] = ((daModel.coef_[0][0]*df_da['Band1'])+(daModel.coef_[0][1]*df_da['Band2'])+(daModel.coef_[0][2]*df_da['Band3'])+(daModel.coef_[0][3]*df_da['Band4'])+(daModel.coef_[0][4]*df_da['Band5'])+(daModel.coef_[0][5]*df_da['Band6'])+(daModel.coef_[0][6]*df_da['Band7'])+(daModel.coef_[0][7]*df_da['NDVI'])+(daModel.coef_[0][8]*df_da['SAVI'])+(daModel.coef_[0][9]*df_da['MSAVI'])+(daModel.coef_[0][10]*df_da['NDMI'])+(daModel.coef_[0][11]*df_da['TCBright'])+(daModel.coef_[0][12]*df_da['TCGreen'])+(daModel.coef_[0][13]*df_da['TCWet']+daModel.intercept_))

print (df_da)


# ### 2. Discriminant Analysis with Select Independent Variables

# In[46]:


#The final model I am running is Discriminant Analysis with select variables
#Split data for training and testin
da_x2_train, da_x2_test, da_y2_train, da_y2_test = train_test_split(x2, y, test_size = 0.3)

#Create model object
daModel2 = LinearDiscriminantAnalysis()
#
fit_modelDA = daModel2.fit(da_x2_train, da_y2_train)

#Connect predictions to data frame produced with first LR model
df = pd.DataFrame(daModel2.predict(da_x2_test), columns=['DA_Select_Pred'], index = x_test.index.copy())
GM_Full_Result = pd.merge(df_da, df, how = 'left', left_index = True, right_index = True)
GM_Full_Result.fillna(value=2, inplace=True)

#Finally, add new columns with second calculated DA linear equation
GM_Full_Result['DA_Select'] = ((daModel2.coef_[0][0]*GM_Full_Result['NDVI'])+(daModel2.coef_[0][1]*GM_Full_Result['NDMI'])+(daModel2.coef_[0][2]*GM_Full_Result['TCGreen'])+(daModel2.coef_[0][3]*GM_Full_Result['TCWet']+daModel2.intercept_))

#Again, I exported this dataframe to a CSV to open it in R. 
GM_Full_Result.to_csv("C:\\Users\\Emily\\Documents\\Summer_2020\\Py_DataScience_and_MachineLearning\\original\\Gypsy_Moth\\Landsat8Imagery\\GM_Full_Result.csv")


# In[53]:


#Create confusion matrix for Logistic Regression - All Indpendent Variables
confusion_matrix(daModel, da_x_test, da_y_test, 'Confusion_Mat_DA_All.png', plt.cm.Greens)


# In[54]:


#Create confusion matrix for Logistic Regression - Select Indpendent Variables
confusion_matrix(daModel2, da_x2_test, da_y2_test, 'Confusion_Mat_Da_Select.png', plt.cm.Greens)


# In[59]:


get_ipython().run_cell_magic('R', '', '#I am back to using R in this cell because I am making another TOC Curv diagram.\n##Open the CSV saved from the earlier portion of this code.\nGM_Full_Result <- read.csv(file ="GM_Full_Result.csv", header=TRUE, dec=".", stringsAsFactors=FALSE)')


# In[60]:


get_ipython().run_cell_magic('R', '', '##Create new numeric index variables from dataframe columns. I am using the calculated values from the coefficients/intercept for each model as the index.\nLR_All <- (GM_Full_Result$LR_All)\nLR_Select <- (GM_Full_Result$LR_Select)\nDA_All <- (GM_Full_Result$DA_All)\nDA_Select <- (GM_Full_Result$DA_Select)\n\n##Create reference.boolean image for input into TOC\nboolean <- (GM_Full_Result$GM_Presence)')


# In[61]:


get_ipython().run_cell_magic('R', '', '## These lines create TOC objects. This creates 100 equal intervals. \ntocdLA <- TOC(LR_All, boolean, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdLS <- TOC(LR_Select, boolean, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdDA <- TOC(DA_All, boolean, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))\ntocdDS <- TOC(DA_Select, boolean, nthres=100, thres=NULL, P=NA, Q=NA,\n              progress=FALSE, units=character(0))')


# In[62]:


get_ipython().run_cell_magic('R', '', '#Create a JPG file to export second TOC plot\npng(file = "GM_Classification_TOC.jpg", width = 550, height = 480)\n\n#Set the plot to a square\npar(pty="s")\n#Create plot object and axes\ngraphics::plot(1, type="l", main = "TOC Curve", lty="dashed",xlab= "Hits+False Alarms (Pixels)", ylab="Hits (Pixels)",lwd=2, col=rgb(128,100,162, maxColorValue=255), xlim=c(0, 314346),ylim=c(0, 101575), bty=\'L\')\n\n#PLot multiple lines to create multi-TOC plot\n#minimum line\nlines(c(0, 101575), c(0,101575), \n      lty="dotdash", lwd=2, col=rgb(50, 50,50, maxColorValue=255)) \n# maximum line\nlines(c(212771, 314346), c(0,101575), \n      lty="dotdash", lwd=2, col=rgb(50,50,50, maxColorValue=255)) \n\n# hits+misses line\nlines(c(0, 314346), c(101575, 101575), lwd=3, col=rgb(150,150,150, maxColorValue=255))\n\n# uniform line\nlines(c(0, 314346), c(0, 101575), lty="dotted", lwd=2, col=rgb(25,25,25, maxColorValue=255))\n\n#TOC object lines\n#Band1\nlines(tocdLA@table$"Hits+FalseAlarms", tocdLA@table$Hits, lwd=2, col=rgb(255,0,0, maxColorValue=255))\n#Band2\nlines(tocdLS@table$"Hits+FalseAlarms", tocdLS@table$Hits, lty="dotted", lwd=2, col=rgb(255,170,0, maxColorValue=255))\n#Band3\nlines(tocdDA@table$"Hits+FalseAlarms", tocdDA@table$Hits, lwd=2, col=rgb(0,150,150, maxColorValue=255))\n#Band4\nlines(tocdDS@table$"Hits+FalseAlarms", tocdDS@table$Hits, lty="dotted", lwd=2, col=rgb(100,255,100, maxColorValue=255))\n\n#Set not area for plot legend\npar(xpd=NA)\n#Set legend. Must define names, line color, and line patterns. \nlegend("topright", inset=c(-0.15, 0.6), c("Hits+Misses", "Minimum", "Maximum", "Uniform", "LR All", "LR Select", "DA All", "DA Select"), \n       col = c(rgb(150,150,150, maxColorValue=255), rgb(50, 50,50, maxColorValue=255), rgb(50,50,50, maxColorValue=255), rgb(25,25,25, maxColorValue=255), rgb(255,0,0, maxColorValue=255), rgb(255,170,0, maxColorValue=255), rgb(0,150,150, maxColorValue=255), rgb(100,255,100, maxColorValue=255)),\n       lty = c(1, 4, 4, 3, 1, 3, 1, 3), merge = TRUE, bty="n", lwd=c(2, 2, 2, 2, 2, 2, 2, 2))\n\n#End image development\ndev.off()')


# In[72]:


get_ipython().run_cell_magic('R', '', '#Saving AUC values. I will use these to rank the bands by AUC value.\naucLA <- tocdLA@AUC\naucLS <- tocdLS@AUC\naucDA <- tocdDA@AUC\naucDS <- tocdDS@AUC')


# In[73]:


get_ipython().run_cell_magic('R', '', '#Finally, I rank the AUC values.\n#Creating a dataframe for the input variables and their AUC values so I can rank the AUC values\nTOC_df <- data.frame("AUC" = c(aucLA, aucLS, aucDA, aucDS), "Name" = c("LR All","LR Select", "DA All", "DA Select")) \n\n#Create a new column\nTOC_df$rank <- NA\n#Order the AUC values\norder.AUC <- order(TOC_df$AUC)\n#Create a new dataframe which is order by AUC\nTOC_df1 <- TOC_df[order.AUC,]\n#create a new column called "rank"\nTOC_df1$rank <- rank(TOC_df1$AUC)\n#Display that new dataframe\nTOC_df1')


# In[74]:


#Add new columns to larger dataframe
crosstab = GM_Full_Result[["LR_All_Pred", "LR_All", "LR_Select_Pred", "LR_Select", "DA_All_Pred", "DA_All", "DA_Select_Pred", "DA_Select"]].copy()

GM_Data = GM_Data.join(crosstab,how='outer')


# In[75]:


GM_Data.describe()


# In[76]:


#Make new columns with for crosstab results. In this case, we're filling the columns with null values
GM_Data['Cross_LR_All'] = np.nan
GM_Data['Cross_LR_Select'] = np.nan
GM_Data['Cross_DA_All'] = np.nan
GM_Data['Cross_DA_Select'] = np.nan
print (GM_Data)


# In[97]:


#Assign crosstab values for DA select
def crosstab(x, y):

    GM_Data.loc[((GM_Data.GM_Presence == 0) & (x == 0)), y] = 4 #Correct Rejection
    GM_Data.loc[((GM_Data.GM_Presence == 1) & (x == 1)), y] = 1 #Hit
    GM_Data.loc[((GM_Data.GM_Presence == 0) & (x == 1)), y] = 2 #FA
    GM_Data.loc[((GM_Data.GM_Presence == 1) & (x == 0)), y] = 3 #Miss
    GM_Data.loc[((GM_Data.GM_Presence == 0) & (x == 2)), y] = 5 #Training Data - Foliated
    GM_Data.loc[((GM_Data.GM_Presence == 1) & (x == 2)), y] = 6 #Training Data - Defoliated
    GM_Data.loc[((GM_Data.GM_Presence == 3) & (x == 0)), y] = 0 #No Data
    GM_Data.loc[((GM_Data.GM_Presence == 3) & (x == 1)), y] = 0 #No Data
    GM_Data.loc[((GM_Data.GM_Presence == 3) & (x == 2)), y] = 0 #No Data
    GM_Data.describe()


# In[107]:


#Assign crosstab values for LR - All Model
crosstab(GM_Data.LR_All_Pred, 'Cross_LR_All')


# In[108]:


#Assign crosstab values for LR - Select Model
crosstab(GM_Data.LR_Select_Pred, 'Cross_LR_Select')


# In[109]:


#Assign crosstab values for DA - All Model
crosstab(GM_Data.DA_All_Pred, 'Cross_DA_All')


# In[101]:


#Assign crosstab values for DA - Select Model
crosstab(GM_Data.DA_Select_Pred, 'Cross_DA_Select')


# In[102]:


#Turn crostab column into an array and then to a raster image
def export_to_TIFF(x):
    Pred_array = GM_Data[[x]].to_numpy()
    Pred_array = Pred_array.astype('uint8')

    Pred_reshape = np.reshape(Pred_array, (835, 601))

    with rio.open("GM_masked.tif") as src:
        out_meta = src.meta 
        out_meta.update({"count": "1"})

    with rio.open(x+'.tif', 'w', **out_meta) as dst:
        dst.write(Pred_reshape, indexes=1)


# In[103]:


#Create raster for LR - All crosstab
export_to_TIFF('Cross_LR_All')


# In[104]:


#Create raster for LR - Select crosstab
export_to_TIFF('Cross_LR_Select')


# In[105]:


#Create raster for DA - All crosstab
export_to_TIFF('Cross_DA_All')


# In[106]:


#Create raster for DA - Select crosstab
export_to_TIFF('Cross_DA_Select')


# In[ ]:




