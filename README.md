# Cartopy backgrounds

This repository provides backgrounds from NASA's "Blue Marble" for usage with cartopy.

Cartopy expects the image files to be stored locally, and it references these images by their file paths.
Additional images need to be downloaded first and then referenced in the images.json file.

>  ## About NASA's Blue Marble 
>
> Next Generation images show Earth in true color. 
> The images show how the surface would look to a human in space if our world had no clouds and no atmosphere. 
> NASA's Terra satellite collected these images. 
> There is one Blue Marble image for each month of the year 2004. 
> These images allow us to explore changes on Earth's lands over time. 
> Notice how the patterns of green (trees and plants), brown (exposed land surface), and white (snow) change from winter through spring, summer, and fall.
> – from the [website](https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG)


## Update the data set
To keep the repository size small, only three resolutions of the BlueMarble images are provided.
However, there is a python script that can be run to retrieve the images from the web, including ultra-high resolution from https://visibleearth.nasa.gov/.

The script parses one of the following websites:
- https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG for BLUE MARBLE: NEXT GENERATION
- https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG-TB for BLUE MARBLE: NEXT GENERATION + TOPOGRAPHY AND BATHYMETRY

The div element with id "#timeline" holds divs with id's corresponding to the date of the dataset.
```js
document.querySelector("#timeline")
```
The link in that div has an onCLick target following the pattern `viewDataset('526308','2004-12-01');`. 
The first parameter is the dataset ID, the second parameter is the date.
The script makes use of these two parameters.

The rendered images can be retrieved from the following URL:
https://neo.gsfc.nasa.gov/servlet/RenderData?si=526306&cs=rgb&format=PNG&width=3600&height=1800
which accepts GET parameters in the form:
```
?si=<DATASET_ID>&cs=rgb&format=<FILE_FORMAT>&width=<WIDTH>&height=<HEIGHT>
```
with `<DATASET_ID>` being retrieved from the script before, `<FILE_FORMAT>` being one of JPEG, PNG, TIFF, KMZ.
Width and height can be chosen from the following dimension tuples:
- 360, 180
- 720, 360
- 1440, 720
- 3600, 1800

The script retrieves the three largest image sizes and saves them as PNG in the directory `BlueMarble`, named like `BlueMarble_<MONTH>_<WIDTH>x<HEIGHT>.png`.

## Update the images.json file
Once the download is complete, a JSON file following the cartopy format is generated
```JSON
{
    "__comment__": "JSON file specifying the images to use for a given type/name and resolution. Read in by cartopy.mpl.geoaxes.read_user_background_images.",
	
    "Blue Marble ${month}": {
        "__comment__": "Blue Marble ${month}",
        "__source__": "NASA Visible Earth",
        "__projection__": "PlateCarree",
        "low": "BlueMarble/BlueMarble_${month}_720x360.png",
        "mid": "BlueMarble/BlueMarble_${month}_1440x720.png",
        "high": "BlueMarble/BlueMarble_${month}_3600x1800.png",
        "ultrahigh": "BlueMarble/BlueMarle_${month}_21600x10800.jpg"
    },
    ...
}
```
This JSON file can then be merged with any other background entries.


## More datasets
- https://neo.gsfc.nasa.gov
- https://visibleearth.nasa.gov/images/73963/bathymetry
- https://visibleearth.nasa.gov/collection/1484   ← for clouds, topography, bathymetry, etc.

<!--
#TODO: Maybe using the images from VisibleEarth is even better since they provide even higher resolutions.
-->
