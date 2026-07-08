import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog


app = QApplication([])
save_dir = QFileDialog.getExistingDirectory(
    None,
    "Select folder to save figure"
)

if not save_dir:
    raise RuntimeError("No directory selected. Aborting save.")
# Data
labels = ['0', '1', '2', '>2']
values = [11.7, 39.3, 34, 14.8]

colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2']


# Create figure
fig, ax = plt.subplots(figsize=(5, 4))

# Bar plot
bars = ax.bar(labels, 
              values, width=0.4, color=colors,
    edgecolor='black',
    linewidth=0.8)  # thin
# Add values on top of bars
'''for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f'{height:.1f}',
        ha='center',
        va='bottom'
    )'''

# Labels
ax.set_ylabel('Fraction (%)')
ax.set_xlabel('Number of dyes')
ax.set_title('Distribution of Number of Dyes')

# Modify y-axis
ax.set_ylim(0, 50)                    # y-axis range
ax.set_yticks(range(0, 51, 10))       # ticks: 0,10,20,30,40,50

plt.tight_layout()

plt.savefig(os.path.join(save_dir,"stoichiometry.svg"), format="svg", bbox_inches="tight")
plt.savefig(os.path.join(save_dir,"stoichiometry.png"), dpi=600, bbox_inches="tight")

plt.show()