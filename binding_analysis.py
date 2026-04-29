import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog
app = QApplication([])

# -----------------------------
# GLOBAL STYLE (IMPORTANT)
# -----------------------------
plt.rcParams.update({
    "font.size": 12,
    "font.family": "sans-serif",
    "axes.linewidth": 1,
    "xtick.major.width": 1,
    "ytick.major.width": 1
})


# -----------------------------
# Load + clean (your code unchanged)
# -----------------------------
file_path, _ = QFileDialog.getOpenFileName(
    None,
    "Select CSV file",
    "",
    "CSV Files (*.csv);;All Files (*)"
)

print("Selected file:", file_path)
base_name = os.path.splitext(os.path.basename(file_path))[0]
output_dir = os.path.dirname(file_path)

def read_csv_file(file_path):
    for enc in ['utf-16', 'cp1252', 'latin1']:
        try:
            df = pd.read_csv(file_path, skiprows=1, header=0, encoding=enc)
            print(f"Loaded with encoding: {enc}")
            return df
        except Exception:
            continue
    raise ValueError("Could not read file")

df = read_csv_file(file_path)

df = df.dropna(how='all')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.reset_index(drop=True)

df['start frame'] = pd.to_numeric(df['start frame'], errors='coerce')

if 'end frame' in df.columns:
    df['end frame'] = pd.to_numeric(df['end frame'], errors='coerce')
elif 'end frmae' in df.columns:
    df['end frame'] = pd.to_numeric(df['end frmae'], errors='coerce')

df['duration'] = df['end frame'] - df['start frame']
df['duration_time'] = df['duration'] * 0.2

duration_time = df['duration_time'].dropna().values

df['binding_number'] = pd.to_numeric(df['Binding number'], errors='coerce')
binding_values = df['binding_number'].dropna().values


# =========================================================
# 1. VIOLIN PLOT (Duration) — Publication Ready
# =========================================================
fig, ax = plt.subplots(figsize=(3, 5))

vp = ax.violinplot(
    duration_time,
    showmeans=False,
    showmedians=True,
    showextrema=False
)

# Style violin
for body in vp['bodies']:
    body.set_facecolor('lightgray')
    body.set_edgecolor('black')
    body.set_alpha(0.5)

vp['cmedians'].set_color('black')
vp['cmedians'].set_linewidth(2)

# Scatter all data (jitter)
x = np.random.normal(1, 0.04, size=len(duration_time))
ax.scatter(x, duration_time, color='black', alpha=0.25, s=12)

ax.set_ylabel("Duration (s)")
ax.set_xticks([])

# Clean look
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_ylim(0, 90)
ax.set_yticks(np.arange(0, 91, 10))
plt.tight_layout()

# Save
plt.savefig(os.path.join(output_dir, f"{base_name}_duration_violin.svg"))
plt.savefig(os.path.join(output_dir, f"{base_name}_duration_violin.png"), dpi=600)
plt.show()


# =========================================================
# 2. BOX PLOT (Binding Number) — Publication Ready
# =========================================================
fig, ax = plt.subplots(figsize=(3, 5))

box = ax.boxplot(
    binding_values,
    widths=0.4,
    patch_artist=True,
    showfliers=False
)

# Style box
for patch in box['boxes']:
    patch.set(facecolor='lightgray', alpha=0.4, edgecolor='black')

for median in box['medians']:
    median.set(color='black', linewidth=2)

for whisker in box['whiskers']:
    whisker.set(color='black', linewidth=1)

for cap in box['caps']:
    cap.set(color='black', linewidth=1)

# Scatter all data
x = np.random.normal(1, 0.04, size=len(binding_values))
ax.scatter(x, binding_values, color='black', alpha=0.25, s=12)

ax.set_ylabel("Number of Binding /200s")
ax.set_xticks([])

# Clean look
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)


ax.set_ylim(0, 40)
ax.set_yticks(np.arange(0, 41, 5))
plt.tight_layout()

# Save
plt.savefig(os.path.join(output_dir, f"{base_name}_binding_box.svg"))
plt.savefig(os.path.join(output_dir, f"{base_name}_binding_box.png"), dpi=600)

plt.show()


# =========================================================
# 3. STOICHIOMETRY (NUMERIC + NOT CLEAR HANDLING)
# =========================================================

# raw column preserved
df['Stoich_raw'] = df['Stoichiometry']

# numeric conversion
df['Stoich_num'] = pd.to_numeric(df['Stoichiometry'], errors='coerce')

# categorical handling
df['Stoich_cat'] = df['Stoich_raw'].astype(str).str.strip().str.lower()

df['Stoich_cat'] = df['Stoich_cat'].replace({
    'nan': np.nan,
    'not clear': 'not_clear',
    'unclear': 'not_clear'
})

# numeric stoichiometry distribution
stoich_int = df['Stoich_num'].dropna().round().astype(int)
stoich_int = stoich_int[stoich_int > 0]

counts_num = stoich_int.value_counts().sort_index()
fractions_num = stoich_int.value_counts(normalize=True).sort_index()

# NOT CLEAR fraction
not_clear_count = (df['Stoich_cat'] == 'not_clear').sum()

# combine
counts_all = counts_num.copy()
counts_all['not_clear'] = not_clear_count

fractions_all = counts_all / counts_all.sum()

print("\nStoichiometry distribution (including not clear):\n")
print(pd.DataFrame({
    "Count": counts_all,
    "Fraction": fractions_all
}))

# =========================================================
# 4. STOICHIOMETRY PLOT
# =========================================================
fig, ax = plt.subplots(figsize=(3, 5))

ax.bar(counts_all.index.astype(str),
       fractions_all.values,
       edgecolor='black',
       linewidth=1,
       alpha=0.6)

# scatter numeric points only
x = np.repeat(stoich_int.values, 1)
x_jitter = np.random.normal(0, 0.05, size=len(x))
ax.scatter(stoich_int.values + x_jitter,
           np.ones_like(stoich_int) * 0.02,
           color='black',
           alpha=0.25,
           s=12)

ax.set_xlabel("Stoichiometry")
ax.set_ylabel("Fraction")

ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_ylim(0, fractions_all.max() * 1.2)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"{base_name}_stoichiometry_fraction.svg"))
plt.savefig(os.path.join(output_dir, f"{base_name}_stoichiometry_fraction.png"), dpi=600)
plt.show()