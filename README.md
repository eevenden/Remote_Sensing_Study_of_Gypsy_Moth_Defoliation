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

Finally, I created a new dataframe which only includes the rows from the cloudless land-uses I'm targeting, but maintains the original index. Within this limited dataframe, I created several new columns and calculated remote sensing indices including: NDVI, SAVI, MSAVI, NDMI, Tassled Cap Brightness, Tasseled Cap Greenness, and Tasseled Cap Wetness. Not all columns are seen in the image below.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88701222-b87d8000-d0d7-11ea-91c2-7414fea796cf.png">
</p>


### Partial Component Analysis (PCA)

For this study, I utilized PCA and the Total Operating Characteristic (TOC) Curves to identify remote sensing indicators best for discriminating defoliation. PCA is a method of reducing data dimensionality by creating orthogonal linear axes to describe "components" of a dataset. TOC Curves are similar to Receiving Operatign Characteristic (ROC) Curves and evaluate the ability of index variables to identify presence or absence of a charactertisitic. 

The image below shows the first five components produced from PCA. Red-colors indicate a positive correlation between a variable and component, while blue-colors indicate a negative correlation. In this case, I think the most important component to examine is Component 1, especically when compared to the the TOC results in the next section. I think this component differentiates between the Foliated and Defoliated pixel. More specifically, I think Band 5, NDVI, NDMI, TC Greeness, and TC Wetness are the variables most important variables for differentiating Defoliation. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841294-c00e5900-d1ab-11ea-9563-00ea97a2be04.jpeg">
</p>

This table shows the eigenvalues and percent variance explained by each component. Component 1 explains approximately 74% of the data variance.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841146-82113500-d1ab-11ea-9cfb-a37f4a770281.png">
</p>

### TOC Curve Comparison

In this TOC curve, the x-axis is Hits + False Alarms, where the maximum x-value is the size of the study area (limited to cloudless Deciduous and Mixed forest) where defoliation is theoretically possible. The y-axis is Hits, where the maximum value on the y-axis is the size of defoliation as indicating by the data provided by the doctoral student. The most important take away from these graphs is the steepness and Area Under the Curve (AUC) values of the TOC curves. Steeper curves with a higher AUC values indicate that a particular variable can discriminate defoliated areas better than less-steep curves with lower AUC values. 

The graph below displays the TOC curves for each variable. All TOC curves in this study will be descending, meaning the highest index values (i.e. the brightest Band value or the highest Remote Sensing index value) will be closest to the origin. Notice that some TOC curves are convex (above the Uniform line) and some are concave (below the Uniform line). Normally, a concave TOC curve has a low AUC value because it identifies presence of a characterisitic later than other variables. However, for this study, I am not concerned with whether a variable identifies presence first or last. Therefore, I subtracted AUC values below 0.50 from 1 to find the area above the curve. This allows me to identify the steepest TOC curves without penalizing whether high or low brightness or index values are associated with defoliation.

![GM_Multi_TOC_Exported](https://user-images.githubusercontent.com/54719919/88701195-b3203580-d0d7-11ea-8139-420cbb8989a5.png)

This table ranks each variable according to its corrected AUC value. Notice, the variables identified as having a strong negative correlation with Defoliation in PCA had the highest corrected AUC values when using TOC. Using this information, one can corroberate that NDVI, NDMI, and Tasseled Cap Wetness are helpful variables for identifying defoliation. It's debatable whether all of these variables are needed to model defoliation because they are correlated with each other. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841144-81789e80-d1ab-11ea-860a-82ed29902193.png">
</p>

### Logistic Regression
Thes second portion of this project compares two binary parametric classification techniques, Logisitic Regression and Discriminant Analysis, and determines whether either method is better at identifying defoliation. For both methods, I created two models: the first contains all of the potential independent variables and the second includes three independent variables with the highest corrected AUC values (i.e. NDMI, Tassled Cap Wetness, NDVI, and Tasseled Cap Greeness). 

The normalized correlation matrices below show the relative success of each model when classifying defoliation using Logistic Regression.

                              Model 1 Results (All)                                Model 2 Results (Select Variables)
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327893-972e0e00-d65a-11ea-92e4-68f547a1f4d7.png">
  <img src="https://user-images.githubusercontent.com/54719919/89327894-972e0e00-d65a-11ea-9df4-04cf067ad196.png">
</p>

### Discriminant Analysis
The normalized correlation matrices below show the relative success of each model when classifying defoliation using Discriminant Analysis.

                              Model 1 Results (All)                                Model 2 Results (Select Variables)
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327891-96957780-d65a-11ea-86df-8a0a77a13f0a.png">
  <img src="https://user-images.githubusercontent.com/54719919/89327892-972e0e00-d65a-11ea-9c30-b5e3adc8f138.png">
</p>

Based on these four matrices, the "Discriminant Analysis - Select" Variables model has the most success when identifying defoliated pixels. However, it does not perform as well as the "Discriminant Analysis - All" model or the "Logistic Regression - All" model when identifying foliated pixels. As a result, it's somewhat difficult to evaluate which model is the best. One way we can rank the performance of each model is using TOC curves. 

### TOC Classification Comparison
Like the previous TOC curve, TOC curve, the x-axis is Hits + False Alarms, where the maximum x-value is the size of the study area (limited to cloudless Deciduous and Mixed forest) where defoliation is theoretically possible. The y-axis is Hits, where the maximum value on the y-axis is the size of defoliation as indicating by the data provided by the doctoral student. In this case, the index variables are the outputs from the linear equations produced by the the Logisitic Regression and Discriminant Analysis models.
Based on the TOC curve we see that all models perform relatively equal when discriminating between Foliated and Defoliated Trees.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327920-a1500c80-d65a-11ea-9e23-2ac71da8848e.jpg">
  </p>

When ranking the AUC values for each model, we see that "Discriminant Analysis - All" model performs the best (marginally). Followed by "Logistic Regression - All" model. However, when comparing model performance using select variables, Discriminant Analysis outperforms Logistic Regression. This could suggest the two method perform similarly when given many independent variables. However, discriminant analysis may be more robust when the user reduces the number of independent variables. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327889-96957780-d65a-11ea-936d-a9651102312c.png">
  </p>

### Classification Results
These final maps showcase the classification results from each model. "Hits" represent pixels which were correctly identified as Defoliated. "False Alarms" are pixels labeled as Foliated in the "true" layer, but classified as Defoliated in the models. "Misses" are pixels which were labeled as Defoliated in the "true" layer, but classified as Foliated in the model. Finally, "Correct Rejections" are pixels correctly identified as Foliated. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89339284-e466ab80-d66b-11ea-8f74-5afd816c10b1.png">
  <img src="https://user-images.githubusercontent.com/54719919/89339286-e4ff4200-d66b-11ea-8025-38dc65951d43.png">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89339280-e3ce1500-d66b-11ea-8556-3ba5937a9738.png">
  <img src="https://user-images.githubusercontent.com/54719919/89339282-e466ab80-d66b-11ea-8b0d-39b59c091d4a.png">
</p>

It's very interesting to compare the "Discriminant Ananlysis - All" and "Logistic Regression - All" because they perform similarly in the confusion matrix, but show very different spatial patterns in the classication results. 
