# Remote Sensing Analysis of Gypsy Moth Defoliation
## Introduction

Description: This script was developed alongside my Intermediate Quantiative Method course project.
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
