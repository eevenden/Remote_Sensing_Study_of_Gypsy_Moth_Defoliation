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
  <img src="https://user-images.githubusercontent.com/54719919/89051032-a2fb9680-d321-11ea-81fd-e156f03d85d4.png">
  <img src="https://user-images.githubusercontent.com/54719919/89051033-a2fb9680-d321-11ea-86ef-662a204bb0f2.png">
</p>

### Discriminant Analysis
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89051029-a2630000-d321-11ea-8af3-6014d248ae1a.png">
  <img src="https://user-images.githubusercontent.com/54719919/89051031-a2630000-d321-11ea-8b5b-5922f38d461f.png">
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
  <img src="https://user-images.githubusercontent.com/54719919/89191212-9a4ccf80-d570-11ea-885f-b7b7fcdb16ba.png">
  <img src="https://user-images.githubusercontent.com/54719919/89191223-9d47c000-d570-11ea-8a41-3bb06472b94d.png">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89191194-93be5800-d570-11ea-86e5-b98ee578d2a2.png">
  <img src="https://user-images.githubusercontent.com/54719919/89191202-9751df00-d570-11ea-9443-3cfd03e03326.png">
</p>
