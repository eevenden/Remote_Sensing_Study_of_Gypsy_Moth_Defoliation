# Evaluating Remote Sensing Indicators and Classification Methods of Gypsy Moth Defoliation
## Introduction

This script was developed alongside my Intermediate Quantiative Method course project.
The purpose of this project was to identify the most appropriate remote sensing indicators of Gypsy Moth defoliation and
compare two popular methods of binary classification, Logisitic Regression and Discriminant Analysis. The study area
for this project is a widespread incident of Gypsy Moth defoliation which occured in New England (RI, CT, and Southern MA) in 2016. 
This project used the Landsat8 imagery (Bands1-7) and two raster layers provided by a doctoral student at Clark University. The first layer is a NLCD
landcover map of the study area. The second layer is a binary classification of defoliation derived from the S-CCD algorithm.

In this script, first I geoprocess the raster layers and prepare them for analysis. Then, I used TOC curves and Partial
Component Analysis to assess which remote sensing indicators were best for identifying defoliation. Finally, using the doctoral student's
binary classification as a "truth", I assessed whether Logistic Regression or Discriminant Analysis was better at
differentiating between the two classes.

Note: This script uses R and Python simultaneously. This was done to access the TOC package available in R, but is not
available in Python.

## Methods
### Geoprocessing

The Landsat8 imagery was sourced from Google Earth Engine. The javascript code is available in this repo. I downloaded Bands 1-7 as well as a cloud mask layer for one Landsat scene in July, 2016.

To geoprocess the imagery, first I reprojected the eight Landsat bands and the two provided raster layers to the Albers Equal Area US 1983 projection and updated their metadata. I chose this projection to perserve area in case I wanted to calculate area statistics. Next, I clipped each image to a bounding box and exported the clipped imagery as new TIF files. The final version of the data is shown below. Geoprocessing was done using the rasterio library.

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

Once my imagery was prepared, I flattened each raster layer to a 1D array and stacked them to create a pandas dataframe. By converting the raster data to a dataframe, I can apply a lot of statistical and machine learning methods which are otherwise limited to proprietary software. 

To further prepare the dataframe, I limited the data to cloudless areas with either a deciduous or mixed forest landcover. The rows which didn't fall in these categories were replaced which all zeros. I decided to do this to eliminate extranious information, but maintain the dataframe structure. I wanted to be able to match my final products to the original index in order to export new TIFs with the same dimensions and georeferencing.

Finally, I created a new dataframe of only the target rows while maintaining the original index. Within this limited dataframe, I created several new columns and calculated remote sensing indices including: Normalized Difference Vegetation Index (NDVI), Soil adjusted Vegetation Index (SAVI), Modified Soil Adjusted Vegetation Index (MSAVI), Normalized Difference Moisture Index (NDMI), Tassled Cap Brightness, Tasseled Cap Greenness, and Tasseled Cap Wetness. Not all columns are seen in the image below.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88701222-b87d8000-d0d7-11ea-91c2-7414fea796cf.png">
</p>


### Partial Component Analysis (PCA)

For this study, I utilized PCA and the Total Operating Characteristic (TOC) Curves to identify remote sensing indicators best for discriminating defoliation. PCA is a method of reducing data dimensionality by creating orthogonal linear axes to describe "components" of a dataset. TOC Curves are similar to Receiving Operating Characteristic (ROC) Curves and evaluate the ability of index variables to identify presence or absence of a charactertisitic. 

The image below shows the first five components produced from PCA. Red-colors indicate a positive correlation between a variable and component, while blue-colors indicate a negative correlation. In this case, I think the most important component to examine is Component 1, especically when compared to the the TOC results in the next section. I think this component differentiates between the Foliated and Defoliated pixel. More specifically, I think NDVI, NDMI, Tasseled Cap Greeness, and Tasseled Cap Wetness are the most important variables for differentiating Defoliation. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841294-c00e5900-d1ab-11ea-9563-00ea97a2be04.jpeg">
</p>

This table shows the eigenvalues and percent variance explained by each component. Component 1 explains approximately 74% of the data variance.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841146-82113500-d1ab-11ea-9cfb-a37f4a770281.png">
</p>

### TOC Curve Comparison

In this TOC curve, the x-axis is Hits + False Alarms, where the maximum x-value is the size of the study area (limited to cloudless Deciduous and Mixed forest). The y-axis is Hits, where the maximum value is the size of defoliation. The most important take away from these graphs is the steepness and Area Under the Curve (AUC) values of the TOC curves. Steeper curves with higher AUC values indicate that a particular variable can discriminate defoliated areas better than less-steep curves with lower AUC values. 

The graph below displays the TOC curves for each variable. All TOC curves in this study will be descending, meaning the highest index values (i.e. the brightest Band value or the highest Remote Sensing index value) will be closest to the origin. Notice that some TOC curves are convex (above the Uniform line) and some are concave (below the Uniform line). Normally, a concave TOC curve has a low AUC value because it identifies presence of a characterisitic later than other variables. However, for this study, I am not concerned with whether a variable identifies presence first or last. Therefore, I subtracted AUC values below 0.50 from 1 to find the area "above the curve". This allows me to identify the steepest TOC curves without penalizing whether high or low brightness or index values are associated with defoliation.

![GM_Multi_TOC_Exported](https://user-images.githubusercontent.com/54719919/88701195-b3203580-d0d7-11ea-8139-420cbb8989a5.png)

This table ranks each variable according to its corrected AUC value. Notice, the variables identified as having a strong negative correlation with Defoliation in the first PCA component had the highest corrected AUC values when using TOC. Using this information, one can corroberate that NDMI, Tassled Cap Wetness, NDVI, and Tasseled Cap Greeness are helpful variables for identifying defoliation. It's debatable whether all of these variables are needed to model defoliation because they are correlated with each other. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/88841144-81789e80-d1ab-11ea-860a-82ed29902193.png">
</p>

### Logistic Regression
The second portion of this project compares two binary classification techniques, Logisitic Regression and Discriminant Analysis, and determines whether either method is better at identifying defoliation. For both methods, I created two models: the first contains all of the potential independent variables and the second includes the four independent variables with the highest corrected AUC values (i.e. NDMI, Tassled Cap Wetness, NDVI, and Tasseled Cap Greeness). 

The normalized correlation matrices below show the relative success of each model when classifying defoliation using Logistic Regression.

                              Model 1 Results (All)                                
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327893-972e0e00-d65a-11ea-92e4-68f547a1f4d7.png">
</p>

                              Model 2 Results (Select Variables)
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327894-972e0e00-d65a-11ea-9df4-04cf067ad196.png">
</p>

### Discriminant Analysis
The normalized correlation matrices below show the relative success of each model when classifying defoliation using Discriminant Analysis.

                              Model 1 Results (All)
<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327891-96957780-d65a-11ea-86df-8a0a77a13f0a.png">
</p>

                              Model 2 Results (Select Variables)
<p align="center">
<img src="https://user-images.githubusercontent.com/54719919/89327892-972e0e00-d65a-11ea-9c30-b5e3adc8f138.png">
</p>

Based on these four matrices, the "Discriminant Analysis - Select" Variables model has the most success when identifying defoliated pixels. However, it does not perform as well as the "Discriminant Analysis - All" model or the "Logistic Regression - All" model when identifying foliated pixels. As a result, it's somewhat difficult to evaluate which model is the best. One way we can rank the performance of each model is using TOC curves. 

### TOC Classification Comparison
Like the previous TOC curve, the x-axis is Hits + False Alarms, where the maximum x-value is the size of the study area (limited to cloudless Deciduous and Mixed forest). The y-axis is Hits, where the maximum value is the size of defoliation. In this case, the index variables are the outputs from the linear equations produced by the Logisitic Regression and Discriminant Analysis models.
Based on the TOC curve, we see that all models perform relatively equally when discriminating between Foliated and Defoliated pixels.

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327920-a1500c80-d65a-11ea-9e23-2ac71da8848e.jpg">
  </p>

When ranking the AUC values for each model, we see that "Discriminant Analysis - All" model performs the best (marginally). Followed by "Logistic Regression - All" model. However, when comparing select variable models, Discriminant Analysis outperforms Logistic Regression. This could suggest the two methods perform similarly when given many independent variables. However, discriminant analysis may be more robust when the user reduces the number of independent variables. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89327889-96957780-d65a-11ea-936d-a9651102312c.png">
  </p>

### Classification Results
These final maps showcase the classification results from each model. "Hits" represent pixels which were correctly identified as Defoliated. "False Alarms" are pixels labeled as Foliated in the "true" layer, but classified as Defoliated in the model. "Misses" are pixels which were labeled as Defoliated in the "true" layer, but classified as Foliated in the model. Finally, "Correct Rejections" are pixels correctly identified as Foliated. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89339284-e466ab80-d66b-11ea-8f74-5afd816c10b1.png">
  <img src="https://user-images.githubusercontent.com/54719919/89339286-e4ff4200-d66b-11ea-8025-38dc65951d43.png">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54719919/89339280-e3ce1500-d66b-11ea-8556-3ba5937a9738.png">
  <img src="https://user-images.githubusercontent.com/54719919/89339282-e466ab80-d66b-11ea-8b0d-39b59c091d4a.png">
</p>

It's very interesting to compare the "Discriminant Analysis - All" and "Logistic Regression - All"maps because the models perform similarly in the confusion matrix, but show very different spatial patterns in the classication results. Specifically, the "Logistic Regresion - All" model shows clusters of False Alarms and Misses and identifies more Hits near the Defoliated training data. Meanwhile, the same categories seem to be more dispersed in the classification results produced by the "Discriminant Analysis - All" model.

## Conclusions
Some of the most important remote sensing indicators of defoliation are NDMI, NDVI, Tasseled Cap Greeness, and Tasseled Cap Wetness. Based on my remote sensing knowledge, these indices can be sorted into two groups: Vegetation & Moisture. NDVI and Tasseled Cap Greeneness both attempt to highlight vegetation, while NDMI and Tasseled Cap Wetness attempt to contrast moist and dry areas. This is important when discussing Foliated and Defoliated trees because leaves are generally positively correlated with vegetation and mositure indices, whereas non-photosynthetic vegetation (like bark) is generally negatively correlated with vegetation and moisture indices.

There is very little difference between Logistic Regression and Discriminant Analysis model performance when one examines the correlation matrices. However, the models which utilize all of the independent variables slightly outperform the models with select variables. This underscores a known concept that adding many variables does not necessarily produce better model outcomes. 

Perhaps more noteably, the spatial distribution of the classification results differ when one examines the maps. For example, it would be interesting  to further explore why the "Logistic Regression - All" model produces noticeable spatial clusters of False Alarms & Misses, but the same pattern isn't apparent in the outcomes from the "Discriminant Ananlysis - All" model. Additionally, the two models identify Hits is very different regions.
