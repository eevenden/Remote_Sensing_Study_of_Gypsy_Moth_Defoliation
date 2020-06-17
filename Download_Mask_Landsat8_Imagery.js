//Set the geometry of a rectangular polygon to a variable
var aoi = geometry

//This function uses the Pixel_QA layer from Landsat 8 to mask out clouds
//This functions can be found on the GEE Information page about Landsat 8
function maskL8sr(image) {
  // Bits 3 and 5 are cloud shadow and cloud, respectively.
  var cloudShadowBitMask = (1 << 3);
  var cloudsBitMask = (1 << 5);
  // Get the pixel QA band.
  var qa = image.select('pixel_qa');
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
                 .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
  return image.updateMask(mask);
}

//Call the Landsat 8 Image collection for the bands and are I want. 
//I limited my data range to July 2016, peak foliation.
//I also limited the image search based on cloud cover, though I don't think there were any suitable imagery in this particulr month
//Then I applied the mask function
var L8 = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
  .select(['B1','B2','B3','B4','B5','B6','B7', 'pixel_qa'])
  .filterBounds(aoi)
  .filterDate('2016-07-01', '2016-07-31')  
  .filterMetadata('CLOUD_COVER', 'less_than', 5)
  .map(maskL8sr);
  
//I displayed the masked images
Map.addLayer(L8)

//Call a tool called 'Batch'
var batch = require('users/fitoprincipe/geetools:batch')

//Downloaded the images I selected to my GoogleDrive
batch.Download.ImageCollection.toDrive(L8, 'Landsat8Imagery', 
                {scale: 30, 
                 type: 'float'})