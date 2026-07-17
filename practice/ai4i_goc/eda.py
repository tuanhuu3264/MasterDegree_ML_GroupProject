# -*- coding: utf-8 -*-
"""EDA for AI4I 2020 Predictive Maintenance dataset."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
OUT = "eda_out"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv("ai4i2020.csv")

def sep(t): print("\n" + "=" * 70 + f"\n {t}\n" + "=" * 70)

# ---------- 1. Basic structure ----------
sep("1. SHAPE & DTYPES")
print("Shape:", df.shape)
print(df.dtypes)
print("\nHead:\n", df.head())

sep("2. MISSING / DUPLICATES")
print("Missing per column:\n", df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("Duplicate Product IDs:", df["Product ID"].duplicated().sum())

# ---------- 3. Feature engineering names ----------
num_cols = ["Air temperature [K]", "Process temperature [K]",
            "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]
fail_modes = ["TWF", "HDF", "PWF", "OSF", "RNF"]
target = "Machine failure"

sep("3. NUMERIC SUMMARY")
print(df[num_cols].describe().T)

# ---------- 4. Target balance ----------
sep("4. TARGET / FAILURE MODES")
print("Machine failure rate: {:.2%} ({} of {})".format(
    df[target].mean(), df[target].sum(), len(df)))
print("\nType distribution:\n", df["Type"].value_counts())
print("\nFailure-mode counts:")
for c in fail_modes:
    print(f"  {c}: {df[c].sum()} ({df[c].mean():.2%})")

# overlap: rows flagged failure but no single mode, and vice versa
any_mode = df[fail_modes].sum(axis=1)
print("\nFailure=1 but no mode flagged:", ((df[target] == 1) & (any_mode == 0)).sum())
print("A mode flagged but failure=0:", ((df[target] == 0) & (any_mode > 0)).sum())
print("Rows with >1 mode flagged:", (any_mode > 1).sum())

# failure rate by Type
sep("5. FAILURE RATE BY TYPE")
print(df.groupby("Type")[target].agg(["mean", "sum", "count"]))

# ---------- Plots ----------
# target bar
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
df[target].value_counts().plot.bar(ax=ax[0], color=["#4c72b0", "#c44e52"])
ax[0].set_title(f"Machine failure (imbalance {df[target].mean():.2%})")
ax[0].set_xticklabels(["OK (0)", "Fail (1)"], rotation=0)
pd.Series({c: df[c].sum() for c in fail_modes}).plot.bar(ax=ax[1], color="#dd8452")
ax[1].set_title("Failure modes count")
plt.tight_layout(); plt.savefig(f"{OUT}/01_target.png", dpi=110); plt.close()

# numeric distributions
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, c in enumerate(num_cols):
    a = axes.flat[i]
    sns.histplot(df[c], kde=True, ax=a, color="#4c72b0")
    a.set_title(c)
axes.flat[-1].axis("off")
plt.tight_layout(); plt.savefig(f"{OUT}/02_distributions.png", dpi=110); plt.close()

# boxplots by failure
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, c in enumerate(num_cols):
    a = axes.flat[i]
    sns.boxplot(data=df, x=target, y=c, ax=a, palette=["#4c72b0", "#c44e52"])
    a.set_title(c); a.set_xlabel("Machine failure")
axes.flat[-1].axis("off")
plt.tight_layout(); plt.savefig(f"{OUT}/03_box_by_failure.png", dpi=110); plt.close()

# correlation heatmap
sep("6. CORRELATION WITH TARGET")
corr = df[num_cols + [target]].corr()
print(corr[target].sort_values(ascending=False))
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation matrix")
plt.tight_layout(); plt.savefig(f"{OUT}/04_corr.png", dpi=110); plt.close()

# engineered physics features
df["Power [W]"] = df["Torque [Nm]"] * df["Rotational speed [rpm]"] * 2 * np.pi / 60
df["Temp diff [K]"] = df["Process temperature [K]"] - df["Air temperature [K]"]
sep("7. ENGINEERED FEATURES vs FAILURE")
for c in ["Power [W]", "Temp diff [K]"]:
    print(f"\n{c}:")
    print(df.groupby(target)[c].describe()[["mean", "std", "min", "max"]])

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
sns.boxplot(data=df, x=target, y="Power [W]", ax=ax[0], palette=["#4c72b0", "#c44e52"])
ax[0].set_title("Mechanical power vs failure")
sns.boxplot(data=df, x=target, y="Temp diff [K]", ax=ax[1], palette=["#4c72b0", "#c44e52"])
ax[1].set_title("Temp difference vs failure")
plt.tight_layout(); plt.savefig(f"{OUT}/05_engineered.png", dpi=110); plt.close()

print("\nPlots saved to:", os.path.abspath(OUT))
