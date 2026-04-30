import os 
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog

# ---- Input: multiple datasets ----
datasets = {
    " coh-3 (1nM) + Scc-2 (2.5 nM)": [0.02,0.01,0.03],
    " coh-3 (1.5nM) + Scc-2 (3.75 nM)": [0.05, 0.06,0.05],
    " coh-3 (2nM) + Scc-2 (5 nM)": [0.11, 0.12,0.17],
    " coh-3 (3nM) + Scc-2 (7.5 nM)": [0.3, 0.4],
    # add more datasets here
}

app = QApplication([])
save_dir = QFileDialog.getExistingDirectory(
    None,
    "Select folder to save figure"
)
# Optional: define colors (auto-extend if fewer than datasets)
bar_colors = ['green', 'darkred', 'steelblue', 'purple', 'teal']
point_colors = ['darkblue', 'orange', 'black', 'brown', 'gray']

labels = list(datasets.keys())
data_values = list(datasets.values())

# ---- Compute stats ----
mean_vals = [np.mean(d) for d in data_values]
std_vals = [np.std(d) for d in data_values]

# ---- X positions ----
x_positions = np.arange(len(datasets))

# ---- Plot bars ----
plt.figure(figsize=(6,4))
plt.bar(
    x_positions,
    mean_vals,
    yerr=std_vals,
    capsize=8,
    width=0.4,
    alpha=0.7,
    color=bar_colors[:len(datasets)]
)

# ---- Overlay individual points ----
for i, d in enumerate(data_values):
    plt.scatter(
        np.full(len(d), x_positions[i]),
        d,
        color=point_colors[i % len(point_colors)],
        zorder=5,
        s=25,
        label=labels[i]
    )

# ---- Formatting ----
plt.xticks(x_positions, labels, rotation=20, ha='right')
plt.ylabel('Fraction of loops')
plt.ylim(0, 1)
plt.title('Loop Extrusion Activity')

# Avoid duplicate legend entries (bars vs points)
handles, legend_labels = plt.gca().get_legend_handles_labels()
unique = dict(zip(legend_labels, handles))
plt.legend(unique.values(), unique.keys(), fontsize=8)

# ---- Save ----
plt.savefig(os.path.join(save_dir,"loop_extrusion_activity_coh3_scc2.svg"), format="svg", bbox_inches="tight")
plt.savefig(os.path.join(save_dir,"loop_extrusion_activity_coh3_scc2.png"), dpi=600, bbox_inches="tight")

plt.show()