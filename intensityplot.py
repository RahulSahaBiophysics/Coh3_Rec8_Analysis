import sys
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.signal import savgol_filter

from qtpy.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
)

# ==========================================================
# Create Qt application
# ==========================================================
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# ==========================================================
# Choose CSV file
# ==========================================================
csv_file, _ = QFileDialog.getOpenFileName(
    None,
    "Select CSV file",
    "",
    "CSV Files (*.csv)"
)

if not csv_file:
    raise SystemExit("No CSV file selected.")

# ==========================================================
# Choose output folder
# ==========================================================
output_folder = QFileDialog.getExistingDirectory(
    None,
    "Select folder to save figure"
)

if not output_folder:
    raise SystemExit("No output folder selected.")

# ==========================================================
# Output filename
# ==========================================================
figure_name, ok = QInputDialog.getText(
    None,
    "Figure Name",
    "Enter output figure name:"
)

if not ok or figure_name.strip() == "":
    figure_name = "Intensity_plot"

# Remove extension if user typed one
figure_name = os.path.splitext(figure_name)[0]

# ==========================================================
# Starting index
# ==========================================================
start_index, ok = QInputDialog.getInt(
    None,
    "Start Index",
    "Start plotting from index:",
    value=0,
    min=0
)

if not ok:
    start_index = 0

# ==========================================================
# Choose end frame
# ==========================================================
end_index, ok = QInputDialog.getInt(
    None,
    "End Frame",
    "End plotting at frame:",
    value=start_index + 100,
    min=start_index
)

if not ok:
    raise SystemExit("Cancelled.")

# ==========================================================
# Read CSV
# ==========================================================
df = pd.read_csv(csv_file)

# Keep only desired range
df = df[(df["index"] >= start_index)].copy()

# Convert frame number to seconds
time = ((df["index"] - start_index) * 0.2).to_numpy()

intensity = df["smol"].to_numpy()

# ==========================================================
# Smooth signal
# ==========================================================
window = min(11, len(intensity))

# Window must be odd
if window % 2 == 0:
    window -= 1

if window >= 3:
    intensity_smooth = savgol_filter(intensity, window_length=31, polyorder=2)
else:
    intensity_smooth = intensity

# ==========================================================
# Plot
# ==========================================================
plt.figure(figsize=(8, 5))

plt.plot(
    time,
    intensity,
    color="lightgray",
    linewidth=1,
    label="Original"
)

plt.plot(
    time,
    intensity_smooth,
    color="red",
    linewidth=2,
    label="Smoothed"
)

plt.xlabel("Time (s)", fontsize=12)
plt.xticks([])
plt.ylabel("Intensity (AU)", fontsize=12)

plt.legend(frameon=False)
plt.tight_layout()
print("Click START time and END time on the plot.")

# Wait for two mouse clicks
pts = plt.ginput(2)
plt.close()

# Get selected time interval
t1, t2 = sorted([pts[0][0], pts[1][0]])

# Keep only selected range
mask = (time >= t1) & (time <= t2)

selected_intensity = intensity[mask]

plt.figure(figsize=(6, 5))

plt.hist(
    selected_intensity,
    bins="fd",          # Adjust number of bins as needed
    density=True,
    color="steelblue",
    edgecolor="black",
    alpha=0.8
)

# Gaussian fit
mu, sigma = norm.fit(selected_intensity)

# Generate fitted curve
x = np.linspace(selected_intensity.min(), selected_intensity.max(), 500)
y = norm.pdf(x, mu, sigma)

plt.plot(
    x,
    y,
    color="red",
    linewidth=2.5,
    label=f"Gaussian fit\nμ = {mu:.2f}\nσ = {sigma:.2f}"
)
plt.xlabel("Intensity (AU)", fontsize=12)
plt.ylabel("Probability Density", fontsize=12)


# ==========================================================
# Save figure
# ==========================================================


plt.savefig(os.path.join(output_folder, figure_name + ".png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(output_folder, figure_name + ".svg"), format="svg", bbox_inches="tight")

plt.show()