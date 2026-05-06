import os
import h5py
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

plotting_fractions = True
colors = ['#ED3E73', '#4581C3', "#99CA3E"]


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
                    
                    if "down fits" not in sym:
                        print("No loop fits, skipping")
                        continue
                    
                    loop = sym["down fits"]
                    
                    if "slope" not in loop:
                        print("No slope dataset, skipping")
                        continue
                    
                    # Read scalar slope
                    rate_down = loop["slope"][()]
                    rate_up = f["symmetry_analysis/up fits/slope"][()]

                    if np.abs(rate_down)> np.abs(rate_up):
                        rate_ratio = rate_up/rate_down
                    else:
                        rate_ratio = rate_down/rate_up

                    if rate_ratio>0.1:
                        category = 'sym'
                    elif rate_ratio<-0.1:
                        category = 'asym_slippage'
                    else:
                        category = 'asym'
                    
                    results.append({
                        "file": file,
                        "path": file_path,
                        "rate down": rate_down,
                        "rate up": rate_up,
                        "rate ratio": rate_ratio,
                        "category": category
                    })
            except Exception as e:
                print(f"Error: {e}")

       
results_df = pd.DataFrame(results)
print(results_df[['rate up', 'rate down']].describe())
fig, ax = plt.subplots()
#h = ax.hist2d(results_df['rate up'], results_df['rate down'], bins = 50, cmap = 'gist_heat_r')
ax.scatter(results_df['rate up'], results_df['rate down'], s = 2, color = 'red')
ax.set_xlabel('Rate I (kbps)')
ax.set_ylabel('Rate II (kbps)')
max_abs_val = np.max(np.abs([results_df['rate down'], results_df['rate up']]))
#max_abs_val = np.max(np.abs(results_df[['rate down', 'rate up']].values))
ax.set_xlim(-max_abs_val, max_abs_val)
ax.set_ylim(-max_abs_val, max_abs_val)
ax.axhline(0, color='black', linestyle='--', alpha=0.5)
ax.axvline(0, color='black', linestyle='--', alpha=0.5)
# set number of ticks to 5
ax.locator_params(nbins=5)
ax.set_aspect('equal')
#plt.colorbar(h[3], ax=ax, label='Counts')

plot_png = os.path.join(root_dir, "quadrant_plot.png")
plot_svg = os.path.join(root_dir, "quadrant_plot.svg")

plt.savefig(plot_png, transparent=True, dpi=600)
plt.savefig(plot_svg, transparent=True)

print(f"Saved plot to: {plot_png}")
print(f"Saved plot to: {plot_svg}")
plt.show()

output_path = os.path.join(root_dir, "symmetry_summary.csv")
results_df.to_csv(output_path, index=False)

print(f"\nSaved results to: {output_path}")
print(results_df)


# Save results
categories = ["sym", "asym", "asym_slippage"]

counts = results_df["category"].value_counts().reindex(categories,fill_value=0)
fractions = results_df["category"].value_counts(normalize=True).reindex(categories,fill_value=0)

print("\nCounts:")
print(counts)

print("\nFractions:")
print(fractions)



# Extract values
symm_fractions = fractions["sym"]
asymm_fractions = fractions["asym"]
asymmslip_fractions = fractions["asym_slippage"]


# PLOTTING

if plotting_fractions:

    fig, ax = plt.subplots(figsize=(5,3))

    phase_label = ['initial growth']

    asymm = np.atleast_1d(asymm_fractions)
    asymmslip = np.atleast_1d(asymmslip_fractions)
    symm = np.atleast_1d(symm_fractions)

    ax.bar(phase_label, asymm,
           label='Asymmetric',
           color=colors[0],
           edgecolor='black', linewidth=0.5, width=0.3)

    ax.bar(phase_label, asymmslip,
           bottom=asymm,
           label='Asymmetric Slippage',
           color=colors[1],
           edgecolor='black', linewidth=0.5, width=0.3)

    ax.bar(phase_label, symm,
           bottom=asymm + asymmslip,
           label='Symmetric',
           color=colors[2],
           edgecolor='black', linewidth=0.5, width=0.3)

    ax.set_ylabel('Fraction')
    ax.set_ylim(0, 1)
    ax.set_xlim(-0.5, 0.5)

    ax.set_xticks([0])
    ax.set_xticklabels(['initial growth'], rotation=45, ha='right')
   
    ax.legend(
    loc='center left',
    bbox_to_anchor=(1, 0.5),
    frameon=False,
    fontsize=12,
    handlelength=2,
    markerscale=1.3
    )
    plt.tight_layout()

    

    # Save plots
    plot_png = os.path.join(root_dir, "category_fractions.png")
    plot_svg = os.path.join(root_dir, "category_fractions.svg")

    plt.savefig(plot_png, transparent=True, dpi=600)
    plt.savefig(plot_svg, transparent=True)

    print(f"Saved plot to: {plot_png}")
    print(f"Saved plot to: {plot_svg}")

    plt.show()
