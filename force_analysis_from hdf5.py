import os
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

app = QApplication([])
root_dir = QFileDialog.getExistingDirectory(None, "Choose directory")

def force_wlc(rel_ext, Plen=36):
    kbT = 4.114
    rel_ext = np.clip(rel_ext, 0, 0.99)
    sqt = 1 / (4 * (1 - rel_ext)**2)
    return (kbT / Plen) * (sqt - 0.25 + rel_ext)

results = []

for dirpath, _, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith((".h5", ".hdf5")):
            file_path = os.path.join(dirpath, file)
            print(f"\nProcessing: {file_path}")

            try:
                df = pd.read_hdf(file_path, key="df_loop_with_force")

                if not all(col in df.columns for col in ["NonPeakRelativeExtension", "FrameNumber"]):
                    print("Missing required columns, skipping")
                    continue

                df["Time_ms"] = df["FrameNumber"] * 0.2

                wl = min(31, len(df)//2*2 - 1)
                df["smoothed_ext"] = savgol_filter(
                    df["NonPeakRelativeExtension"], window_length=wl, polyorder=2
                )

                df["Force"] = force_wlc(df["smoothed_ext"].values)

                wl_force = min(51, len(df)//2*2 - 1)
                df["smoothed_force"] = savgol_filter(
                    df["Force"], window_length=wl_force, polyorder=1
                )

                stalling_force = df["smoothed_force"].values

                threshold = np.percentile(stalling_force, 95)
                top_5_percent = stalling_force[stalling_force >= threshold]
                median_top_5 = np.mean(top_5_percent)

                results.append({
                    "file": file,
                    "path": file_path,
                    "median_top_5_force": median_top_5,
                    "threshold_95": threshold
                })

            except Exception as e:
                print(f"Error: {e}")

# Save results
results_df = pd.DataFrame(results)
output_path = os.path.join(root_dir, "stalling_force_summary.csv")
results_df.to_csv(output_path, index=False)

print(f"\nSaved results to: {output_path}")
print(results_df)


# PLOTTING SECTION


data = results_df["median_top_5_force"].dropna().values
n = len(data)

fig, ax = plt.subplots()

# Transparent background
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Boxplot
ax.boxplot(
    [data],
    patch_artist=True,
    boxprops=dict(facecolor='limegreen', color='green'),
    showmeans=True,
    meanprops=dict(marker='D', markerfacecolor='yellow',
                   markeredgecolor='black', markersize=5),
    whiskerprops=dict(color='darkred'),
    capprops=dict(color='black')
)

# Overlay points (jitter)
x = np.random.normal(1, 0.01, size=len(data))
ax.plot(x, data, 'o', color='blue', markersize=1, alpha=0.7)

# Labels
ymin, ymax = ax.get_ylim()
ax.set_xticks([])
ax.set_yticks(np.arange(0,ymax+0.04, 0.04))
ax.set_ylabel('Stalling Force (pN)')
ax.set_title('Stalling Force Distribution')

# Sample size
ax.text(
    0.95, 0.95,
    f'n = {n}',
    transform=ax.transAxes,
    ha='right',
    va='top'
)

# Save figure
plot_path_png = os.path.join(root_dir, "stalling_force_boxplot.png")
plt.savefig(plot_path_png, transparent=True, dpi=600)

# Save figure (SVG - vector format)
plot_path_svg = os.path.join(root_dir, "stalling_force_boxplot.svg")
plt.savefig(plot_path_svg, transparent=True)

print(f"Saved plot to: {plot_path_png}")
print(f"Saved plot to: {plot_path_svg}")

plt.show()