#!/bin/bash

echo "{\"__comment__\": \"JSON file specifying the images to use for a given type/name and resolution. Read in by cartopy.mpl.geoaxes.read_user_background_images. This file is generated.\"," > bm.json

for month in "January" "February" "March" "April" "May" "June" "July" "August" "September" "October" "November" "December"
do
    cat >>bm.json <<EOL
    "Blue Marble ${month}": {
        "__comment__": "Blue Marble ${month}",
        "__source__": "NASA Visible Earth",
        "__projection__": "PlateCarree",
        "low": "BlueMarble/BlueMarble_${month}_low.png",
        "mid": "BlueMarble/BlueMarble_${month}_mid.png",
        "high": "BlueMarble/BlueMarble_${month}_high.png"
    },

EOL
done

echo "}" >> bm.json
echo "Created bm.json"
