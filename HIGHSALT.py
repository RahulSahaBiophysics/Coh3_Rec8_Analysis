import matplotlib.pyplot as plt
import numpy as np

# ---- Input: multiple datasets ----
datasets = {
    " coh-3 (2nM) + Scc-2 (8 nM)": [0.05],
    " rec-8 (2nM) + Scc-2 (8nM)": [0.2,0.22],
    # add more datasets here
}

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
plt.ylabel('protein bound fraction after high salt wash')
plt.ylim(0, 1)
plt.title('High Salt wash experiment')

# Avoid duplicate legend entries (bars vs points)
handles, legend_labels = plt.gca().get_legend_handles_labels()
unique = dict(zip(legend_labels, handles))
plt.legend(unique.values(), unique.keys(), fontsize=8)

# ---- Save ----
plt.savefig("high_salt_remining.svg", format="svg", bbox_inches="tight")
plt.savefig("high_salt_remining.png", dpi=600, bbox_inches="tight")

plt.show()