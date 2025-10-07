

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from SALib.analyze import sobol
from scipy.stats import spearmanr
from tools.analysis import display_table 

# ==== Cấu hình ====
RESULTS_FILE = "sobol_8params_results_3_OCT_sup.csv"

# ==== Danh sách tham số ====
param_names = [
    "acceleration",
    "deceleration",
    "minGap",
    "lcSpeedGain",
    "lcCooperative",
    "lcPushy",
    "lcStrategic",
    "lcAssertive",
]

# ==== Đọc CSV ====
if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"File Not Found Error: {RESULTS_FILE}")

df = pd.read_csv(RESULTS_FILE)

# Kiểm tra cột
expected_cols = param_names + ["PMx"]
missing = [c for c in expected_cols if c not in df.columns]
if missing:
    raise ValueError(f"Thiếu cột trong CSV: {missing}. Hiện có: {list(df.columns)}")

# Loại bỏ hàng NaN
df = df.dropna(subset=expected_cols).reset_index(drop=True)

# ==== Trích X và Y ====
X = df[param_names].to_numpy(dtype=float)
Y = df["PMx"].to_numpy(dtype=float)

# ==== Phân tích Sobol ====
problem = {
    "num_vars": len(param_names),
    "names": param_names,
    "bounds": [
        [4.0, 10.0],
        [6.0, 12.0],
        [0.3, 2.5],
        [0.0, 5.3],
        [0.0, 1.0],
        [0.0, 1.0],
        [0.0, 5.9],
        [0.0, 2.5],
    ],
}

Si = sobol.analyze(problem, Y, calc_second_order=True, print_to_console=False)

# ==== Bảng Sobol S1/ST ====
first_order_df = pd.DataFrame({
    "Parameter": param_names,
    "S1": Si["S1"],
    "S1_conf": Si["S1_conf"],
    "ST": Si["ST"],
    "ST_conf": Si["ST_conf"],
}).round(3)

# ==== Bảng Sobol S2 (non-zero) ====
second_order_rows = []
S2, S2c = Si.get("S2"), Si.get("S2_conf")
if S2 is not None:
    for i, ni in enumerate(param_names):
        for j in range(i+1, len(param_names)):
            s2 = S2[i, j]
            s2c_ij = S2c[i, j] if S2c is not None else np.nan
            if s2 is not None and np.isfinite(s2) and abs(s2) > 1e-4:
                second_order_rows.append({
                    "Param 1": ni,
                    "Param 2": param_names[j],
                    "S2": s2,
                    "S2_conf": s2c_ij
                })
second_order_df = pd.DataFrame(second_order_rows).round(3)

# ====  Sobol ====
try:
    display_table(first_order_df, title="Sobol Indices — First & Total Order (8 params)")
    if not second_order_df.empty:
        display_table(second_order_df, title="Sobol Indices — Second Order (non-zero)")
    else:
        print("No notable second-order interactions (|S2| <= 1e-4).")
except Exception:
    print(first_order_df)
    if not second_order_df.empty:
        print(second_order_df)

# ====  S1/ST ====
plt.figure(figsize=(9, 5))
x = np.arange(len(param_names))
w = 0.35
plt.bar(x - w/2, Si["S1"], w, label="Main Effect (S1)")
plt.bar(x + w/2, Si["ST"], w, label="Total Effect (ST)")
plt.xticks(x, param_names, rotation=15)
plt.ylabel("Sensitivity Index")
plt.title("Sobol Sensitivity Analysis (PMx) — 8 parameters")
plt.legend()
plt.tight_layout()
plt.show()

# ==== Scatter vs PMx + Spearman correlation ====
ncols = 4
nrows = int(np.ceil(len(param_names) / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 3.5*nrows))
axes = axes.flatten()

spearman_results = []

for i, name in enumerate(param_names):
    ax = axes[i]
    xv = df[name].to_numpy(float)
    yv = df["PMx"].to_numpy(float)
    
    # Scatter
    ax.scatter(xv, yv, alpha=0.4, color="tab:blue", label="Samples")
    
    # Linear fit
    if len(xv) >= 2 and np.ptp(xv) > 0:
        slope, intercept = np.polyfit(xv, yv, deg=1)
        xs = np.linspace(xv.min(), xv.max(), 100)
        ys = slope*xs + intercept
        ax.plot(xs, ys, color="red", linewidth=2, label=f"Linear fit (slope={slope:.2f})")
    
    # Spearman rank correlation
    rho, pval = spearmanr(xv, yv)
    spearman_results.append({
        "Parameter": name,
        "Spearman_r": round(rho, 3),
        "p-value": round(pval, 3)
    })
    
    # Title with Spearman info
    ax.set_title(f"{name} vs PMx\nSpearman r = {rho:.3f}, p = {pval:.3g}")
    ax.set_xlabel(name)
    ax.set_ylabel("PMx")
    ax.legend()


for j in range(i+1, len(axes)):
    axes[j].axis("off")

plt.tight_layout()
plt.show()

# ==== Spearman ====
spearman_df = pd.DataFrame(spearman_results)
print("\nSpearman rank correlation and p-values:")
print(spearman_df)
