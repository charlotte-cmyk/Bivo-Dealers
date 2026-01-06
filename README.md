# Bivo Dealer Map Migration to Mapbox
**Last Updated:** 1/2/2026 Andrew Subach | <a href="https://andrewsubie.github.io">Contact</a>

## Overview

### Purpose

The Bivo dealer map was previously hosted as a custom map on Google Maps, which served it's purpose well but had several limitations. These included the inability to move the map's default display center, and inability to customize the popups when clicking on a dealer location. For these reasons, I decided that it would be best to migrate the map to Mapbox, and create custom JavaScript popups to display dealer information. Additionally, the heatmap feature on Mapbox matches Bivo's water camo theme well. 

### Repo Overview

`geojson` - This directory contains the .geosjon files used to store the dealers as a list of points in json format specified to work with mapbox's proprietary formating. File names match dataset names in the Mapbox online dashboard. 

`icons` - Contains custom point marker image files used in the map in various formats

`scripts` - Contains various python utilities used in transferring/completing the data. 

`.kml` files - Data exported from google maps

`mapbox_page.html` - HTML page and JS logic for popups to display the map to web users. Search for "GLOBAL SETTINGS" in this file and adjust the center coordinate and zoom level for various needs. This page can be duplicated into a different repo/hosting service in the future to make a EU-centered map when the EU is sufficiently populated with dealers. 

The actual map is hosted on Andrew's personal github at https://andrewsubie.github.io/mapbox-map/. This is a temporary band-aid fix that currently has no need to be updated, as a way to circumvent Shopify's restrictions on executing inline scripts. At some point this should be changed to a more robust/secure hosting service. 

## Adding New Dealers 

1. Login to console.mymapbox.com
2. Go to Data Manager -> Datasets
3. Draw a point in both the bivo_dealers dataset and the appropriate subset (roamer, REI, or unique for all other dealerss). 
4. Fill in all relevant fields (website, address, name etc.)
5. Set `icon-scale` and `icon-opacity` to 1
6. Set icon to `https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png`
7. Set styleUrl to `#icon-1899-DB4436-labelson`


REPEAT NEXT STEPS FOR EACH DATASET UPDATED

5. Click on the three dots next to the updated datasets. 
6. Click `Export to Tileset` in the menu. 
7. Click `Update a Connected Tileset` to update the appropriate tileset without overwriting. 

The new dealer point(s) should populate into the map within 15-30 minutes. 

## Duplicating Map for Other Markets

* Create a new GitHub page. See this tutorial: https://docs.github.com/en/pages/quickstart 
'Title it bivo-map-eu' or whatever. 

* Add an `index.html` file, and copy paste the contents of `mapbox_page.html`, changing the coordinates and zoom level as needed.

* Add, commit and push to main. The map should populate within 10-15 minutes.

### Links/Embedding Snippets to Live Maps

US Map: https://bivo-git.github.io/bivo-dealer-map-us/

```
<iframe
  src="https://bivo-git.github.io/bivo-dealer-map-us/"
  width="100%"
  height="600"
  style="border:0;"
  loading="lazy"
  allowfullscreen>
</iframe
```
EU Map: https://bivo-git.github.io/bivo-dealer-map-eu/

```
<iframe
  src="https://bivo-git.github.io/bivo-dealer-map-eu/"
  width="100%"
  height="600"
  style="border:0;"
  loading="lazy"
  allowfullscreen>
</iframe
```

