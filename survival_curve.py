import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

from qtpy.QtWidgets import QApplication, QFileDialog

# ==========================================================
# Create Qt application
# ==========================================================
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


folder = QFileDialog.getExistingDirectory(
    None,
    "Select folder to save figure"
)
# ==========================================================
# Select CSV files
# ==========================================================
control_file, _ = QFileDialog.getOpenFileName(
    None,
    "Select Control CSV",
    "",
    "CSV Files (*.csv)"
)

if not control_file:
    raise SystemExit("No Control CSV selected.")

A_file, _ = QFileDialog.getOpenFileName(
    None,
    "Select Condition A CSV",
    "",
    "CSV Files (*.csv)"
)

if not A_file:
    raise SystemExit("No Condition A CSV selected.")

# ==========================================================
# Read duration column
# ==========================================================
control_df = pd.read_csv(control_file)
A_df = pd.read_csv(A_file)

column_name = "duration (s)"

if column_name not in control_df.columns:
    raise ValueError(f"'{column_name}' not found in Control CSV.")

if column_name not in A_df.columns:
    raise ValueError(f"'{column_name}' not found in Condition A CSV.")

control_times = control_df[column_name].dropna().to_numpy()
A_times = A_df[column_name].dropna().to_numpy()

# Assume all events are observed
control_event = [1] * len(control_times)
A_event = [1] * len(A_times)

# ==========================================================
# Kaplan-Meier analysis
# ==========================================================
kmf = KaplanMeierFitter()

plt.figure(figsize=(7, 6))

kmf.fit(
    control_times,
    event_observed=control_event,
    label=f"without SCC-2 (n={len(control_times)})"
)
kmf.plot_survival_function(ci_show=True)

kmf.fit(
    A_times,
    event_observed=A_event,
    label=f"+ SCC2 (n={len(A_times)})"
)
kmf.plot_survival_function(ci_show=True)

plt.xlabel("Binding duration (s)")
plt.ylabel("Probability of Remaining Bound")
plt.title("Kaplan–Meier Survival Analysis")

plt.xlim(0, 100)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(folder, "Kaplan_Meier_100s.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.savefig(
    os.path.join(folder, "Kaplan_Meier_100s.svg"),
    bbox_inches="tight"
)

plt.show()

# ==========================================================
# Log-rank test
# ==========================================================
results = logrank_test(
    control_times,
    A_times,
    event_observed_A=control_event,
    event_observed_B=A_event
)

print("\n========== Log-rank Test ==========")
print(results.summary)
print(f"\np-value = {results.p_value:.6g}")