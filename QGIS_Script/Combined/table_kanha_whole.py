import os
import numpy as np
from osgeo import gdal

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsProject
)
from PyQt5.QtCore import QVariant

# ------------------------
# INPUT FOLDERS
# ------------------------
folders = [
    {
        "path": r"D:\Landsat_Kanha_Moniter_2000\USGS\Landsat_4_5\Mask\NDVI",
        "sensor": "Landsat4/5 (TM)"
    },
    {
        "path": r"D:\Landsat_Kanha_Moniter_2000\USGS\Landsat_7\Mask\NDVI",
        "sensor": "Landsat7 (ETM+)"
    }
]

# ------------------------
# CREATE MEMORY LAYER
# ------------------------
layer = QgsVectorLayer("None", "kanha_whole", "memory")
pr = layer.dataProvider()

pr.addAttributes([
    QgsField("date", QVariant.String),
    QgsField("year", QVariant.Int),
    QgsField("month", QVariant.Int),
    QgsField("day", QVariant.Int),
    QgsField("median_ndvi", QVariant.Double),
    QgsField("landsat", QVariant.String)
])
layer.updateFields()

# ------------------------
# PROCESS RASTERS
# ------------------------
for entry in folders:
    folder = entry["path"]
    sensor = entry["sensor"]

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".tif")])

    for file in files:
        try:
            # ------------------------
            # EXTRACT DATE FROM FILENAME
            # Example:
            # LT05_L2SP_143045_20010421_XXXX_NDVI.tif
            # ------------------------
            parts = file.split("_")
            date_part = parts[3]  # YYYYMMDD

            year = int(date_part[0:4])
            month = int(date_part[4:6])
            day = int(date_part[6:8])
            date_str = f"{day:02d}-{month:02d}-{year}"

            # ------------------------
            # READ RASTER
            # ------------------------
            path = os.path.join(folder, file)
            ds = gdal.Open(path)
            if ds is None:
                print("❌ Cannot open:", file)
                continue

            band = ds.GetRasterBand(1)
            arr = band.ReadAsArray().astype(float)

            # ------------------------
            # HANDLE NODATA
            # ------------------------
            nodata = band.GetNoDataValue()
            if nodata is not None:
                arr[arr == nodata] = np.nan

            # ------------------------
            # IGNORE NON-VEGETATION
            # NDVI <= 0 → water / soil / shadow
            # ------------------------
            arr[arr <= 0] = np.nan

            # ------------------------
            # MEDIAN NDVI (SAFE)
            # ------------------------
            if np.all(np.isnan(arr)):
                median_ndvi = np.nan
            else:
                median_ndvi = float(np.nanmedian(arr))

            print(f"{sensor} | {date_str} → Median NDVI: {median_ndvi}")

            # ------------------------
            # ADD FEATURE
            # ------------------------
            feature = QgsFeature()
            feature.setAttributes([
                date_str,
                year,
                month,
                day,
                median_ndvi,
                sensor
            ])
            pr.addFeature(feature)

        except Exception as e:
            print("❌ Error processing", file, e)

# ------------------------
# ADD LAYER TO QGIS
# ------------------------
QgsProject.instance().addMapLayer(layer)
print("✅ NDVI time-series table created successfully")
