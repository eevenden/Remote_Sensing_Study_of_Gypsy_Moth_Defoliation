# Evaluating Remote Sensing Indicators and Classification Methods of Gypsy Moth Defoliation
## Introduction

This script was developed alongside my Intermediate Quantiative Method course project.
The purpose of this project was to identify the most appropriate remote sensing indicators of Gypsy Moth defoliation and
compare two populer methods of binary classification, Logisitic Regression and Discriminant Analysis. The study area
for this study is an area of Gypsy Moth defoliation in New England (RI, CT, and Southern MA) from 2016. 
This project used the Landsat8 imagery (Bands1-7) and two raster layers provided by Su Ye at Clark University. The first layer is a NLCD
landcover map of the study area. The second layer is a binary classification of defoliation derived from the S-CCD algorithm.

In this script, first I geoprocess the raster layers and prepare them for analysis. Then, I used TOC curves and Partial
Component Analysis to assess which remote sensing indicators were best for identifying defoliation. Finally, using Su's
binary classification as a "truth", I assessed whether Logistic Regression or Discriminant Analysis was better at
differentiatingbetween the two classes.

Note: This script uses R and Pythn simultaneously. This was done to access the TOC package available in R, but is not
available in Python.

## Methods
### Geoprocessing
![Band1](https://user-images.githubusercontent.com/54719919/88694536-ad722200-d0ce-11ea-95c7-e6b6e43e3c6c.png)

![Band2](https://user-images.githubusercontent.com/54719919/88694538-ad722200-d0ce-11ea-98a5-ad41332528ff.png)

![Band3](https://user-images.githubusercontent.com/54719919/88694539-ad722200-d0ce-11ea-9afa-19a30ba76faa.png)

![Band4](https://user-images.githubusercontent.com/54719919/88694541-ae0ab880-d0ce-11ea-98da-cd1849dd0237.png)

![Band5](https://user-images.githubusercontent.com/54719919/88694542-ae0ab880-d0ce-11ea-9d63-1c75e67e7753.png)

![Band6](https://user-images.githubusercontent.com/54719919/88694543-aea34f00-d0ce-11ea-824b-7b6bcfd3e4e2.png)

![Band7](https://user-images.githubusercontent.com/54719919/88694544-aea34f00-d0ce-11ea-9af5-564fb4c0cad9.png)

![Band8](https://user-images.githubusercontent.com/54719919/88694545-aea34f00-d0ce-11ea-9110-c9e598ccc3c3.png)

![GM_Presence](https://user-images.githubusercontent.com/54719919/88694546-af3be580-d0ce-11ea-9c2d-474bd20f2bb5.png)

![Land_Cover_2016](https://user-images.githubusercontent.com/54719919/88694547-af3be580-d0ce-11ea-998e-7a922c192653.png)

### Dataframe Preparaion


### Partial Component Analysis


### TOC Curve Comparison


### Logistic Regression


### Discriminant Analysis


### TOC Classification Comparison
