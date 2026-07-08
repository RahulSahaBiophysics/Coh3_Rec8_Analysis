import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from qtpy.QtWidgets import QApplication, QFileDialog

# ============================================
# Choose folder
# ============================================

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

folder = QFileDialog.getExistingDirectory(
    None,
    "Select folder containing CSV files"
)

if not folder:
    raise SystemExit("No folder selected.")

# ============================================
# Read all CSV files
# ============================================
all_durations = []
counts = []

csv_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".csv")])

if len(csv_files) == 0:
    raise SystemExit("No CSV files found.")

for file in csv_files:

    filepath = os.path.join(folder, file)

    try:
        df = pd.read_csv(filepath)

        if "Duration (s)" not in df.columns:
            print(f"Skipping {file}: column 'Duration (s)' not found.")
            continue

        duration = (
            pd.to_numeric(df["Duration (s)"], errors="coerce")
            .dropna()
            .values
        )

        all_durations.extend(duration)

        counts.append({
            "File": file,
            "Count": len(duration)
        })

        print(f"{file}: {len(duration)} events")

    except Exception as e:
        print(f"Error reading {file}: {e}")

# ============================================
# Save combined durations
# ============================================
combined = pd.DataFrame({"duration (s)": all_durations})

combined_csv = os.path.join(folder, "Combined_Duration.csv")
combined.to_csv(combined_csv, index=False)

print(f"\nCombined CSV saved to:\n{combined_csv}")

# ============================================
# Figure 1: Violin plot (all durations)
# ============================================
plt.figure(figsize=(5,6))
plt.violinplot(all_durations, showmeans=True, showmedians=True)

# Random horizontal jitter
x = np.random.normal(1, 0.05, len(all_durations))

plt.scatter(
    x,
    all_durations,
    s=18,
    color="black",
    alpha=0.6,
    zorder=10
)
median_val = np.median(all_durations)
n = len(all_durations)

# Mark the median
plt.scatter(
    1,
    median_val,
    color="red",
    s=60,
    marker="_",
    linewidths=3,
    zorder=20,
    label="Median"
)

# Display median and n
ymax = max(all_durations)
yrange = ymax - min(all_durations)

plt.text(
    1.05,
    ymax + 0.05 * yrange,
    f"Median = {median_val:.2f} s\nn = {n}",
    fontsize=10,
    ha="left",
    va="bottom"
)

plt.ylabel("Duration (s)")
plt.title("All Durations")
plt.xticks([1], ["All"])

plt.tight_layout()
plt.savefig(os.path.join(folder, "Violin_All_Duration.png"), dpi=300)

# ============================================
# Figure 2: Violin plot (duration > 2 s)
# ============================================
filtered = [d for d in all_durations if d > 2]

plt.figure(figsize=(5,6))

if len(filtered) > 0:
    plt.violinplot(filtered, showmeans=True, showmedians=True)

    x = np.random.normal(1, 0.05, len(filtered))

    plt.scatter(
        x,
        filtered,
        s=18,
        color="black",
        alpha=0.6,
        zorder=10
    )

    median_val = np.median(filtered)
    n = len(filtered)

    # Mark the median
    plt.scatter(
        1,
        median_val,
        color="red",
        s=60,
        marker="_",
        linewidths=3,
        zorder=20,
        label="Median"
    )

    # Display median and n
    ymax = max(all_durations)
    yrange = ymax - min(all_durations)

    plt.text(
        1.05,
        ymax + 0.05 * yrange,
        f"Median = {median_val:.2f} s\nn = {n}",
        fontsize=10,
        ha="left",
        va="bottom"
    )

plt.ylabel("Duration (s)")
plt.title("Duration > 2 s")
plt.xticks([1], [">2 s"])

plt.tight_layout()
plt.savefig(os.path.join(folder, "Violin_Duration_GT2.png"), dpi=300)

# ============================================
# Figure 3: Number of durations in each CSV
# ============================================
count_df = pd.DataFrame(counts)

plt.figure(figsize=(max(6, len(count_df)*0.6),5))

plt.bar(count_df["File"], count_df["Count"])

plt.xticks(rotation=90)
plt.ylabel("Number of durations")
plt.title("Number of Events per CSV")

plt.tight_layout()
plt.savefig(os.path.join(folder, "Counts_per_CSV.png"), dpi=300)

# ============================================
# Figure 4: Box plot of durations grouped by CSV
# ============================================
grouped = []
labels = []

for file in csv_files:

    filepath = os.path.join(folder, file)

    try:
        df = pd.read_csv(filepath)

        if "Duration (s)" not in df.columns:
            continue

        duration = (
            pd.to_numeric(df["Duration (s)"], errors="coerce")
            .dropna()
            .values
        )

        if len(duration) > 0:
            grouped.append(duration)
            labels.append(file)

    except:
        pass

plt.figure(figsize=(max(6, len(labels)*0.6),6))

plt.boxplot(grouped, labels=labels, showfliers=True)

plt.xticks(rotation=90)
plt.ylabel("Duration (s)")
plt.title("Duration Distribution per CSV")

plt.tight_layout()
plt.savefig(os.path.join(folder, "Boxplot_Per_CSV.png"), dpi=300)



count_values = [c["Count"] for c in counts]

plt.figure(figsize=(4,6))

plt.boxplot(
    count_values,
    widths=0.4,
    showfliers=True
)

# Overlay every CSV as a jittered point
x = np.random.normal(1, 0.04, len(count_values))

plt.scatter(
    x,
    count_values,
    s=35,
    color="red",
    zorder=10
)

plt.ylabel("Number of bindingss")
plt.xticks([1], [" "])
plt.title("")

plt.tight_layout()
plt.savefig(
    os.path.join(folder, "Boxplot_Event_Counts.png"),
    dpi=300
)

plt.show()
print("\nFinished!")