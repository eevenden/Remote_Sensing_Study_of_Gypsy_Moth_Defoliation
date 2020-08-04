# Evaluating Remote Sensing Indicators and Classification Methods of Gypsy Moth Defoliation
## Introduction

This script was developed alongside my Intermediate Quantiative Method course project.
The purpose of this project was to identify the most appropriate remote sensing indicators of Gypsy Moth defoliation and
compare two populer methods of binary classification, Logisitic Regression and Discriminant Analysis. The study area
for this study is an area of Gypsy Moth defoliation in New England (RI, CT, and Southern MA) from 2016. 
This project used the Landsat8 imagery (Bands1-7) and two raster layers provided by a doctoral student at Clark University. The first layer is a NLCD
landcover map of the study area. The second layer is a binary classification of defoliation derived from the S-CCD algorithm.

In this script, first I geoprocess the raster layers and prepare them for analysis. Then, I used TOC curves and Partial
Component Analysis to assess which remote sensing indicators were best for identifying defoliation. Finally, using th doctoral student's
binary classification as a "truth", I assessed whether Logistic Regression or Discriminant Analysis was better at
differentiating between the two classes.

Note: This script uses R and Python simultaneously. This was done to access the TOC package available in R, but is not
available in Python.

## Methods
### Geoprocessing

The Landsat8 imagery was sourced from Google Earth Engine. The javascript code is available in this repo. I downloaded Bands 1-7 as well as a cloud mask layer for one Landsat scene.

To geoprocess the imagery, first I reprojected the eight Landsat bands and the two provided data layers to the Albers Equal Area 1983 projection and updated their metadata. I chose this projection to perserve area in case I wanted to calculate area statistics. Next, I clipped each image to a bounding box and exported the clipped imagery as new TIF files. The final version of the data is shown below. Geoprocessing was done using the Rasterio library.

### Data Provided by PhD Student

![GM_Presence](https://user-images.githubusercontent.com/54719919/88695207-8ec05b00-d0cf-11ea-9677-c02417a57d3c.png)
![Land_Cover_2016](https://user-images.githubusercontent.com/54719919/88695208-8ec05b00-d0cf-11ea-8082-d962d5462edb.png)

### Landsat 8 Imagery

![Band1](https://user-images.githubusercontent.com/54719919/88695193-8d8f2e00-d0cf-11ea-8da8-7b1d400c459b.png)
![Band2](https://user-images.githubusercontent.com/54719919/88695194-8d8f2e00-d0cf-11ea-9aaa-d62ddd7ae751.png)
![Band3](https://user-images.githubusercontent.com/54719919/88695195-8e27c480-d0cf-11ea-94b3-182b0e430ac4.png)
![Band4](https://user-images.githubusercontent.com/54719919/88695198-8e27c480-d0cf-11ea-94d1-407aa6f9cd6e.png)
![Band5](https://user-images.githubusercontent.com/54719919/88695201-8e27c480-d0cf-11ea-8c79-bd3b8bd21ac1.png)
![Band6](https://user-images.githubusercontent.com/54719919/88695203-8ec05b00-d0cf-11ea-8411-997c1f0338cd.png)
![Band7](https://user-images.githubusercontent.com/54719919/88695204-8ec05b00-d0cf-11ea-8ca2-b720f22d5cf4.png)
![Band8](https://user-images.githubusercontent.com/54719919/88695322-b9121880-d0cf-11ea-8bee-4daf7258e4cc.png)


### Dataframe Preparation

Once my imagery is prepared, I flattened each raster layer to a 1D array and stacked them to create a pandas dataframe. By converting the raster data to a dataframe, I can apply a lot of statistical and machine learning methods which are otherwise limited to proprietary software. 

To further prepare the dataframe, I replaced all null values with zero. Additionally, I limited the data to only cloudless areas with either a deciduous or mixed forest landuse. Rows which are do not fall in these categories were replaced which zeros. I decided to do this to eliminate extranious information, but maintain the dataframe structure. I wanted to be able to match my final products to the original index in order to export new TIFs with the same dimensions and georeferencing.

Finally, I added several new columns and calculated remote sensing indices including: NDVI, SAVI, MSAVI, NDMI, Tassled Cap Brightness, Tasseled Cap Greenness, and Tasseled Cap Wetness. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88701222-b87d8000-d0d7-11ea-91c2-7414fea796cf.png">
</p>

### Partial Component Analysis
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841294-c00e5900-d1ab-11ea-9563-00ea97a2be04.jpeg">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841146-82113500-d1ab-11ea-9cfb-a37f4a770281.png">
</p>

### TOC Curve Comparison
![GM_Multi_TOC_Exported](https://user-images.githubusercontent.com/54719919/88701195-b3203580-d0d7-11ea-8139-420cbb8989a5.png)

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841144-81789e80-d1ab-11ea-860a-82ed29902193.png">
</p>

### Logistic Regression
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89209783-f9b8d880-d58c-11ea-8c46-f88b1e47739d.png">
  <img src="https://user-images.githubusercontent.com/54719919/89209785-fa516f00-d58c-11ea-8f42-197051325a4b.png">
</p>

### Discriminant Analysis
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89209781-f9b8d880-d58c-11ea-8596-96a3aa266716.png">
  <img src="https://user-images.githubusercontent.com/54719919/89209782-f9b8d880-d58c-11ea-8da3-b07e5a63f34d.png">
</p>

### TOC Classification Comparison
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89209172-c7f34200-d58b-11ea-9f01-6826e105f7f0.jpg">
  </p>
  
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89209039-88c4f100-d58b-11ea-8ba3-148a27647f62.png">
  </p>

### Classification Results
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89210238-c165ca00-d58d-11ea-8f61-88c2f821c621.png">
  <img src="https://user-images.githubusercontent.com/54719919/89210239-c1fe6080-d58d-11ea-8431-ed25eab199a1.png">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89210235-c0cd3380-d58d-11ea-87fc-3805131e0abc.png">
  <img src="https://user-images.githubusercontent.com/54719919/89210237-c165ca00-d58d-11ea-84a8-6a8a89347dad.png">
</p>
