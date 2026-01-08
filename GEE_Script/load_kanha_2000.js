// ======================================================
// Kanha Reserved Forest - Harmonized Landsat Red/NIR
// Year: 2000
// Landsat 5 TM + Landsat 7 ETM+
// Harmonize L5 to L7
// Export to Google Drive per image
// ======================================================

// AOI: Kanha Reserved Forest
var kanha = ee.Geometry.Rectangle([80.53, 22.05, 81.2, 22.45]);
Map.centerObject(kanha, 9);
Map.addLayer(kanha, { color: "red" }, "Kanha AOI");

// Date range for 2000
var startDate = "2000-01-01";
var endDate = "2000-12-31";

// -------------------------------
// Harmonization function for Landsat 5 → Landsat 7
// -------------------------------
function harmonizeL5toL7(image) {
  var red = image.select("Red").multiply(1.016).add(-0.001).rename("Red");
  var nir = image.select("NIR").multiply(0.996).add(0.002).rename("NIR");
  return image
    .addBands(red)
    .addBands(nir)
    .select(["Red", "NIR"])
    .copyProperties(image, ["system:time_start"]);
}

// -------------------------------
// Load Landsat 5 TM (Surface Reflectance)
var l5 = ee
  .ImageCollection("LANDSAT/LT05/C02/T1_L2")
  .filterBounds(kanha)
  .filterDate(startDate, endDate)
  .select(["SR_B3", "SR_B4"], ["Red", "NIR"])
  .map(harmonizeL5toL7);

// Load Landsat 7 ETM+ (Surface Reflectance)
var l7 = ee
  .ImageCollection("LANDSAT/LE07/C02/T1_L2")
  .filterBounds(kanha)
  .filterDate(startDate, endDate)
  .select(["SR_B3", "SR_B4"], ["Red", "NIR"]);

// Merge L5 + L7
var merged = l5.merge(l7).sort("system:time_start");
print("Total images for 2000:", merged.size());

// -------------------------------
// Export each image individually
// -------------------------------
var imageList = merged.toList(merged.size());
var mainFolder = "NDVI_Time_Series_0_5_10_15_20_25";
var yearFolder = "NDVI_Time_Series_2000";

for (var i = 0; i < merged.size().getInfo(); i++) {
  var img = ee.Image(imageList.get(i));
  var d = ee.Date(img.get("system:time_start"));

  var year = d.get("year").getInfo();
  var month = ee.Number(d.get("month")).format("%02d").getInfo();
  var day = ee.Number(d.get("day")).format("%02d").getInfo();
  var date = year + "_" + month + "_" + day;

  Export.image.toDrive({
    image: img,
    description: "Kanha_RED_NIR_" + date,
    folder: mainFolder + "/" + yearFolder,
    fileNamePrefix: "Kanha_RED_NIR_" + date,
    region: kanha,
    scale: 30,
    crs: "EPSG:4326",
    maxPixels: 1e13,
  });
}

print("Export tasks for 2000 created!");