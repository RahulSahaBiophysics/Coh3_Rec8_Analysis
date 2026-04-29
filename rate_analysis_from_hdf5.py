import os
import h5py
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

app = QApplication([])
root_dir = QFileDialog.getExistingDirectory(None, "Choose directory")


results = []

for dirpath, _, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith((".h5", ".hdf5")):
            file_path = os.path.join(dirpath, file)
            print(f"\nProcessing: {file_path}")

            try:
                with h5py.File(file_path, "r") as f:
                    
                    # Check if required path exists
                    if "symmetry_analysis" not in f:
                        print("No symmetry_analysis group, skipping")
                        continue
                    
                    sym = f["symmetry_analysis"]
                    
                    if "loop fits" not in sym:
                        print("No loop fits, skipping")
                        continue
                    
                    loop = sym["loop fits"]
                    
                    if "slope" not in loop:
                        print("No slope dataset, skipping")
                        continue
                    
                    # Read scalar slope
                    slope = loop["slope"][()]
                    
                    results.append({
                        "file": file,
                        "path": file_path,
                        "slope": slope
                    })
            except Exception as e:
                print(f"Error: {e}")

# Save results
results_df = pd.DataFrame(results)
output_path = os.path.join(root_dir, "rate summary.csv")
results_df.to_csv(output_path, index=False)

print(f"\nSaved results to: {output_path}")
print(results_df)


# PLOTTING SECTION


data = results_df["slope"].dropna().values
n = len(data)

fig, ax = plt.subplots()

# Transparent background
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Boxplot
ax.boxplot(
    [data],
    patch_artist=True,
    boxprops=dict(facecolor='lightsalmon', color='brown'),
    showmeans=True,
    meanprops=dict(marker='D', markerfacecolor='yellow',
                   markeredgecolor='black', markersize=4, zorder=3),
    whiskerprops=dict(color='darkred'),
    capprops=dict(color='black')
)

# Overlay all points (correct for single dataset)
x = np.random.normal(1, 0.01, size=len(data))
ax.plot(x, data, 'o', color='brown', markersize = 1)

# Labels
ymin, ymax = ax.get_ylim()
ax.set_xticks([])
ax.set_yticks(np.arange(0.0,ymax+0.1, 0.1))
ax.set_ylabel('Rate (kbp/s)')
ax.set_title(' Rate Distribution')

ax.text(
    0.95, 0.95,
    f'n = {n}',
    transform=ax.transAxes,
    ha='right',
    va='top'
)

# Save figure
plot_path_png = os.path.join(root_dir, "rate_boxplot.png")
plt.savefig(plot_path_png, transparent=True, dpi=600)

# Save figure (SVG - vector format)
plot_path_svg = os.path.join(root_dir, "rate_boxplot.svg")
plt.savefig(plot_path_svg, transparent=True)

print(f"Saved plot to: {plot_path_png}")
print(f"Saved plot to: {plot_path_svg}")
plt.show()