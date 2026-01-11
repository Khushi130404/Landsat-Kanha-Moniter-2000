import matplotlib.pyplot as plt
import numpy as np
from qgis.core import QgsProject

# ------------------------
# LOAD LAYER
# ------------------------
layer = QgsProject.instance().mapLayersByName("se_kanha_table")[0]

# ------------------------
# MONTH ORDER (Apr → Mar)
# ------------------------
month_order = [4,5,6,7,8,9,10,11,12,1,2,3]
month_names = {
    1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr",
    5:"May", 6:"Jun", 7:"Jul", 8:"Aug",
    9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"
}

month_index = {m:i+1 for i,m in enumerate(month_order)}

x_vals = []
y_vals = []

# ------------------------
# READ ALL VALID NDVI POINTS (2001)
# ------------------------
for f in layer.getFeatures():
    try:
        year = int(f["year"])
        month = int(f["month"])
        day = int(f["day"])
        ndvi = float(f["median_ndvi"])
    except:
        continue

    if year != 2001:
        continue

    if ndvi <= 0 or ndvi > 1:
        continue

    if month not in month_index:
        continue

    # Month position + small offset by day
    x = month_index[month] + (day / 31.0) * 0.3
    x_vals.append(x)
    y_vals.append(ndvi)

# ------------------------
# SORT BY X
# ------------------------
x_vals, y_vals = zip(*sorted(zip(x_vals, y_vals)))

# ------------------------
# PLOT
# ------------------------
plt.figure(figsize=(14,5))

plt.scatter(x_vals, y_vals, s=60)
plt.plot(x_vals, y_vals, alpha=0.6)

plt.xticks(
    ticks=range(1,13),
    labels=[month_names[m] for m in month_order]
)

plt.xlabel("Month (Apr → Mar)")
plt.ylabel("NDVI")
plt.title("NDVI Time Series — South East Zone (Kanha, 2001)")
plt.grid(True)
plt.tight_layout()
plt.show()
