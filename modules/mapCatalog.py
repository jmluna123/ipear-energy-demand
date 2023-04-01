from pystac.extensions.item_assets import ItemAssetsExtension
from matplotlib.colors import ListedColormap
from pystac_client import Client
import planetary_computer as pc
import rasterio.features
import rioxarray as rx
import numpy as np
import rasterio


catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")


def obtain_map_classificate(aoi):
    search = catalog.search(
        collections=["io-lulc-9-class"],
        intersects=aoi,
        datetime=["2021-01-01"],
    )
    return list(search.get_items())


def get_classes():
    collection = catalog.get_collection("io-lulc-9-class")
    ia = ItemAssetsExtension.ext(collection)
    x = ia.item_assets["data"]
    class_names = {x["summary"]: x["values"][0]
                   for x in x.properties["file:values"]}
    return class_names


def get_cmap(item):
    class_names = get_classes()
    with rasterio.open(pc.sign(item.assets["data"].href)) as src:
        colormap_def = src.colormap(1)  # get metadata colormap for band 1
        colormap = [
            np.array(colormap_def[i]) / 255 for i in range(max(class_names.values()))
        ]  # transform to matplotlib color format
    return ListedColormap(colormap)


temp_ec = rx.open_rasterio("files/Ecuador/tmp_ecuador.tif")
rad_ec = rx.open_rasterio("files/Ecuador/rad_ecuador.tif")