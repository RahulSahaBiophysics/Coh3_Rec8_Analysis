import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from qtpy.QtWidgets import QApplication, QFileDialog

# Choose folder

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

folder1 = QFileDialog.getExistingDirectory(
    None,
    "Select first folder containing CSV files"
)

if not folder1:
    raise SystemExit("First folder not selected.")

folder2 = QFileDialog.getExistingDirectory(
    None,
    "Select second folder"
)

if folder2 == "":
    folder2 = None


# PLotting Function 

def analyze(folder):
    all_durations = []
    durations_gt2 = []
    counts = []

    csv_files = sorted([
        f for f in os.listdir(folder) 
        if f.lower().endswith(".csv")
        and not f.startswith("Combined_")
    ])

    if len(csv_files) == 0:
        print(f"No csv files in {folder}")
        return None
    grouped = []
    labels = []

    for file in csv_files:

        filepath = os.path.join(folder, file)

        try:
            df = pd.read_csv(filepath)

            if "Duration (s)" not in df.columns:
                continue

            duration = pd.to_numeric(df["Duration (s)"],
            errors="coerce"
            ).dropna().values

            all_durations.extend(duration)
            durations_gt2.extend(duration[duration > 2.5])

            grouped.append(duration[duration> 2.5])
            labels.append(file)
        
            counts.append({
                "File": file,
                "Count": len(duration),
                "Count(>2s)": (duration > 2.5).sum(),
            })
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Save combined durations

    combined = pd.DataFrame({"duration (s)": all_durations})
    combined_csv = os.path.join(folder, "Combined_Duration.csv")
    combined.to_csv(combined_csv, index=False)


    # Save durations >2 s
    combined_gt2 = pd.DataFrame({"duration (s)": durations_gt2})
    combined_gt2_csv = os.path.join(folder, "Combined_Duration_GT2s.csv")
    combined_gt2.to_csv(combined_gt2_csv, index=False)

    # Figure 1: Violin plot (all durations)
    
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
    #plt.savefig(os.path.join(folder, "Violin_All_Duration.png"), dpi=600)
    #plt.savefig(os.path.join(folder, "Violin_All_Duration.svg"))

    # Figure 2: Violin plot (duration > 2 s)

    filtered = [d for d in all_durations if d > 2.5]

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
    #plt.savefig(os.path.join(folder, "Violin_Duration_more_than_2.png"), dpi=600)
    #plt.savefig(os.path.join(folder, "Violin_All_Duration_more_than_2.svg"))


    # Figure 3: Number of durations in each CSV

    count_df = pd.DataFrame(counts)

    plt.figure(figsize=(max(6, len(count_df)*0.6),5))

    plt.bar(count_df["File"], count_df["Count(>2s)"])

    plt.xticks(rotation=90)
    plt.ylabel("Number of bindings")
    plt.title("Number of Bindings per DNA")

    plt.tight_layout()
    #plt.savefig(os.path.join(folder, "Counts_per_CSV.png"), dpi=300)


    # Figure 4: Box plot of durations grouped by CSV
     

    plt.figure(figsize=(max(6, len(labels)*0.6),6))

    plt.boxplot(grouped, labels=labels, showfliers=True)

    plt.xticks(rotation=90)
    plt.ylabel("Duration (s)")
    plt.title("Duration Distribution per DNA")

    plt.tight_layout()
    #plt.savefig(os.path.join(folder, "Boxplot_Per_CSV.png"), dpi=300)



    count_values = [c["Count(>2s)"] for c in counts]

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
    #plt.savefig(os.path.join(folder, "Boxplot_number_bindings.png"),dpi=600)
    #plt.savefig(os.path.join(folder, "Boxplot_number_bindings.svg"),)
    #plt.show()

    return {
        "folder": os.path.basename(folder),
        "all": np.array(all_durations),
        "gt2": np.array(durations_gt2),
        "counts": counts
    }


result1 = analyze(folder1)

if folder2 is not None:
    result2 = analyze(folder2)
else:
    result2 = None


plt.figure(figsize=(6,7))

counts1 = [c["Count(>2s)"] for c in result1["counts"]]

datasets = [counts1]
labels = [result1["folder"]]

if result2 is not None:
    counts2 = [c["Count(>2s)"] for c in result2["counts"]]
    datasets.append(counts2)
    labels.append(result2["folder"])

positions = np.arange(1, len(datasets)+1)



# Boxplot on top
plt.boxplot(
    datasets,
    positions=positions,
    widths=0.5,
    patch_artist=True,
    showfliers=True
)

# Scatter
for i, data in enumerate(datasets):

    x = np.random.normal(
        positions[i],
        0.05,
        len(data)
    )

    plt.scatter(
        x,
        data,
        color="red",
        s=15,
        alpha=0.5,
        zorder=10
    )

plt.xticks(positions, labels)
plt.ylabel("Number of bindings")
plt.title("")

save_folder = QFileDialog.getExistingDirectory(
    None,
    "Select folder to save results"
)

plt.tight_layout()

plt.savefig(os.path.join(save_folder, "Comparison_Boxplot.png"),dpi=600)

plt.savefig(os.path.join(save_folder, "Comparison_Boxplot.svg"))

plt.show()