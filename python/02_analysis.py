"""
02_analysis.py  -  Product portfolio and nutrition analysis
============================================================
Input : data/cleaned/menu_clean.csv
Output: data/cleaned/*.csv   summary tables used by Excel and SQL checks
        screenshots/*.png    charts

Run:  python python/02_analysis.py

METHOD NOTE that drives everything below: beverages are 356 of the 713 menu rows, and a brand that
lists every cup size separately looks bigger and sweeter than one that does not. So every nutrition
comparison is run on FOOD ITEMS (everything except Beverages and Sauces & Condiments) and the
beverage numbers are reported on their own. Portfolio size is reported twice: menu rows, and
distinct base products with size variants stripped.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "cleaned"
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)

BRAND_ORDER = ["McDonald's", "Burger King", "KFC"]
COLOURS = {"McDonald's": "#2a78d6", "Burger King": "#eb6834", "KFC": "#1baf7a"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
plt.rcParams.update({"figure.dpi": 110, "font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#c3c2b7", "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
                     "axes.titlesize": 12, "axes.titleweight": "600", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "legend.frameon": False})


# SQL's ROUND() rounds a half away from zero; numpy/Python rounds a half to even, so an exact
# value like 26.25 becomes 26.3 in MySQL and 26.2 in pandas. Every published figure therefore goes
# through r() so the Python, SQL and Excel numbers are identical rather than nearly so.
from decimal import Decimal, ROUND_HALF_UP


def r(x, dp=1):
    if pd.isna(x):
        return x
    q = Decimal(1).scaleb(-dp)
    return float(Decimal(str(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def rs(series, dp=1):
    return series.map(lambda v: r(v, dp))


df = pd.read_csv(CLEAN / "menu_clean.csv")
df["Brand"] = pd.Categorical(df["Brand"], BRAND_ORDER, ordered=True)
NON_FOOD = ["Beverages", "Sauces & Condiments"]
food = df[~df["Category"].isin(NON_FOOD)].copy()
bev = df[df["Category"] == "Beverages"].copy()
print(f"all items {len(df)} | food items {len(food)} | beverages {len(bev)}")


def save(name):
    plt.tight_layout(); plt.savefig(SHOTS / name, bbox_inches="tight"); plt.close()
    print("  chart ->", name)


# ===========================================================================
# 1. PORTFOLIO SIZE AND SHAPE
# ===========================================================================
brand = (df.groupby("Brand", observed=True)
           .agg(MenuRows=("Item", "size"), BaseProducts=("BaseItem", "nunique"),
                Categories=("Category", "nunique"), FoodItems=("Item", lambda s: 0))
           .reset_index())
brand["FoodItems"] = food.groupby("Brand", observed=True)["Item"].size().values
brand["BeverageRows"] = df[df.Category == "Beverages"].groupby("Brand", observed=True)["Item"].size().values
brand["SizeVariantRows"] = df[df.IsSizeVariant].groupby("Brand", observed=True)["Item"].size().values
brand["PctBeverageRows"] = (brand.BeverageRows / brand.MenuRows * 100).round(1)
f = food.groupby("Brand", observed=True)
brand["AvgCalories_Food"] = rs(f["Calories"].mean(), 1).values
brand["MedianCalories_Food"] = f["Calories"].median().values
brand["AvgProtein_Food"] = rs(f["Protein_g"].mean(), 1).values
brand["AvgFat_Food"] = rs(f["Fat_g"].mean(), 1).values
brand["AvgCarbs_Food"] = rs(f["Carbs_g"].mean(), 1).values
brand["AvgSugars_Food"] = rs(f["Sugars_g"].mean(), 1).values
brand["AvgSodium_Food"] = rs(f["Sodium_mg"].mean(), 0).values
# ratio metrics use a 100 kcal floor so that a 20 kcal condiment cannot dominate the average
fr = food[food.Calories >= 100].groupby("Brand", observed=True)
brand["AvgProteinPer100kcal_Food"] = rs(fr["ProteinPer100kcal"].mean(), 2).values
brand["AvgSodiumPer100kcal_Food"] = rs(fr["SodiumPer100kcal"].mean(), 1).values
brand["PctCaloriesFromFat_Food"] = rs(fr["PctCaloriesFromFat"].mean(), 1).values
brand["MaxCalories_Food"] = f["Calories"].max().values
brand["PctFoodUnder400kcal"] = (food.assign(u=food.Calories < 400).groupby("Brand", observed=True)["u"].mean() * 100).round(1).values
brand["PctFood800kcalPlus"] = (food.assign(o=food.Calories >= 800).groupby("Brand", observed=True)["o"].mean() * 100).round(1).values
brand.to_csv(CLEAN / "brand_summary.csv", index=False)

# category mix
cat = (df.groupby(["Brand", "Category"], observed=True)
         .agg(Items=("Item", "size"), BaseProducts=("BaseItem", "nunique"),
              AvgCalories=("Calories", "mean"), AvgProtein=("Protein_g", "mean"),
              AvgSodium=("Sodium_mg", "mean"), AvgSugars=("Sugars_g", "mean"))
         .reset_index())
for _c in ["AvgCalories", "AvgProtein", "AvgSodium", "AvgSugars"]:
    cat[_c] = rs(cat[_c], 1)
cat["PctOfBrandMenu"] = rs(cat.Items / cat.groupby("Brand", observed=True).Items.transform("sum") * 100, 1)
cat.to_csv(CLEAN / "brand_category_summary.csv", index=False)

catall = (df.groupby("Category")
            .agg(Items=("Item", "size"), Brands=("Brand", "nunique"), AvgCalories=("Calories", "mean"),
                 AvgProtein=("Protein_g", "mean"), AvgSodium=("Sodium_mg", "mean"),
                 AvgSugars=("Sugars_g", "mean"), AvgFat=("Fat_g", "mean"))
            .sort_values("Items", ascending=False).reset_index())
for _c in ["AvgCalories", "AvgProtein", "AvgSodium", "AvgSugars", "AvgFat"]:
    catall[_c] = rs(catall[_c], 1)
catall.to_csv(CLEAN / "category_summary.csv", index=False)

# ===========================================================================
# 2. NUTRITION DETAIL (food items only)
# ===========================================================================
nutr = (food.groupby("Brand", observed=True)[["Calories", "Fat_g", "SaturatedFat_g", "Carbs_g",
                                              "Sugars_g", "Fiber_g", "Protein_g", "Sodium_mg"]]
            .agg(["mean", "median", "min", "max"]).round(1))
nutr.to_csv(CLEAN / "nutrition_by_brand.csv")

top_cal = df.nlargest(15, "Calories")[["Brand", "Item", "Category", "Calories", "Fat_g", "Sugars_g", "Sodium_mg"]]
top_cal.to_csv(CLEAN / "top_calorie_items.csv", index=False)
top_sod = food.nlargest(15, "Sodium_mg")[["Brand", "Item", "Category", "Sodium_mg", "Calories", "SodiumPer100kcal"]]
top_sod.to_csv(CLEAN / "top_sodium_items.csv", index=False)
top_pro = food[food.Calories >= 100].nlargest(15, "ProteinPer100kcal")[
    ["Brand", "Item", "Category", "Protein_g", "Calories", "ProteinPer100kcal"]]
top_pro.to_csv(CLEAN / "top_protein_efficiency_items.csv", index=False)

# ===========================================================================
# 3. HEADLINE KPIs
# ===========================================================================
kpi = pd.DataFrame([
    ("Menu rows analysed", len(df)),
    # a product name shared by two brands is two products, so count brand+product pairs
    ("Distinct products across the three brands", df.groupby(["Brand", "BaseItem"]).ngroups),
    ("Food items (excl. beverages & condiments)", len(food)),
    ("Beverage rows", len(bev)),
    ("Brands", df.Brand.nunique()),
    ("Categories", df.Category.nunique()),
    ("Average calories, food items", round(food.Calories.mean(), 1)),
    ("Median calories, food items", food.Calories.median()),
    ("Highest-calorie item (kcal)", int(df.Calories.max())),
    ("Highest-calorie item", df.loc[df.Calories.idxmax(), "Item"]),
    ("Average protein, food items (g)", round(food.Protein_g.mean(), 1)),
    ("Average sodium, food items (mg)", round(food.Sodium_mg.mean(), 0)),
    ("Average sugars, beverages (g)", round(bev.Sugars_g.mean(), 1)),
    ("Zero-calorie items", int(df.IsZeroCalorie.sum())),
    ("Food items under 400 kcal (%)", round((food.Calories < 400).mean() * 100, 1)),
    ("Food items of 800 kcal or more (%)", round((food.Calories >= 800).mean() * 100, 1)),
], columns=["Metric", "Value"])
kpi.to_csv(CLEAN / "kpis.csv", index=False)

# ===========================================================================
# 4. CHARTS
# ===========================================================================
def brandbar(series, title, ylab, fmt="{:,.0f}", fname="x.png"):
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    vals = [series[b] for b in BRAND_ORDER]
    ax.bar(BRAND_ORDER, vals, color=[COLOURS[b] for b in BRAND_ORDER], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_title(title); ax.set_ylabel(ylab); ax.set_ylim(0, max(vals) * 1.18)
    save(fname)


brandbar(brand.set_index("Brand").BaseProducts, "Distinct products on the menu",
         "products", fname="01_products_by_brand.png")
brandbar(brand.set_index("Brand").AvgCalories_Food, "Average calories per food item",
         "kcal", fname="02_avg_calories_by_brand.png")

# product mix: grouped bars, three brand colours only (eight shades of one hue blur together)
piv = (df.pivot_table(index="Category", columns="Brand", values="Item", aggfunc="size", observed=True)
         .fillna(0))
pct = piv.div(piv.sum(axis=0), axis=1) * 100
pct = pct.loc[pct.mean(axis=1).sort_values().index]
fig, ax = plt.subplots(figsize=(8.6, 5.0))
h = 0.26
ypos = np.arange(len(pct))
for k, b in enumerate(BRAND_ORDER):
    ax.barh(ypos + (1 - k) * h, pct[b], height=h, color=COLOURS[b], label=b)
    for y, v in zip(ypos + (1 - k) * h, pct[b]):
        if v > 0:
            ax.text(v + 0.6, y, f"{v:.0f}%", va="center", fontsize=8.2, color=INK2)
ax.set_yticks(ypos); ax.set_yticklabels(pct.index)
ax.set_xlabel("% of that brand's menu rows"); ax.set_title("Menu composition by category")
ax.set_xlim(0, pct.values.max() * 1.16); ax.legend(ncol=3, loc="lower right")
save("03_menu_composition.png")

# calorie distribution, food items
fig, ax = plt.subplots(figsize=(7.4, 3.8))
data = [food[food.Brand == b].Calories.values for b in BRAND_ORDER]
bp = ax.boxplot(data, tick_labels=BRAND_ORDER, patch_artist=True, widths=0.5,
                medianprops=dict(color=INK, linewidth=1.6), flierprops=dict(marker="o", markersize=3,
                markerfacecolor="#898781", markeredgecolor="none", alpha=.6))
for patch, b in zip(bp["boxes"], BRAND_ORDER):
    patch.set_facecolor(COLOURS[b]); patch.set_alpha(.35); patch.set_edgecolor(COLOURS[b])
ax.set_title("Calorie spread of food items"); ax.set_ylabel("kcal per item")
save("04_calorie_distribution.png")

# protein efficiency vs sodium: positioning scatter
fig, ax = plt.subplots(figsize=(7.4, 4.6))
for b in BRAND_ORDER:
    s = food[(food.Brand == b) & food.ProteinPer100kcal.notna()]
    ax.scatter(s.Calories, s.Protein_g, s=26, alpha=.62, color=COLOURS[b], label=b,
               edgecolors="white", linewidths=.6)
ax.set_xlabel("calories per item"); ax.set_ylabel("protein (g)")
ax.set_title("Calories vs protein, food items"); ax.legend()
save("05_calories_vs_protein.png")

# average nutrition profile by brand
fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.3))
for ax, (col, lab) in zip(axes, [("AvgProtein_Food", "Protein (g)"), ("AvgFat_Food", "Fat (g)"),
                                 ("AvgSugars_Food", "Sugars (g)"), ("AvgSodium_Food", "Sodium (mg)")]):
    v = [brand.set_index("Brand")[col][b] for b in BRAND_ORDER]
    ax.bar([b.split()[0] for b in BRAND_ORDER], v, color=[COLOURS[b] for b in BRAND_ORDER], width=0.55)
    for i, x in enumerate(v):
        ax.text(i, x, f"{x:,.0f}" if col == "AvgSodium_Food" else f"{x:,.1f}",
                ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_title(lab, fontsize=11); ax.set_ylim(0, max(v) * 1.2)
fig.suptitle("Average nutrition per food item", y=1.04, fontsize=12, fontweight="600")
save("06_nutrition_profile.png")

# category calories
fig, ax = plt.subplots(figsize=(7.4, 4.0))
cc = catall[~catall.Category.isin(NON_FOOD)].sort_values("AvgCalories")
ax.barh(cc.Category, cc.AvgCalories, color="#2a78d6", height=0.6)
for y, v in enumerate(cc.AvgCalories):
    ax.text(v + 6, y, f"{v:,.0f}", va="center", fontsize=9, color=INK)
ax.set_title("Average calories by category (food items)"); ax.set_xlabel("kcal")
ax.invert_yaxis()
ax.set_xlim(0, cc.AvgCalories.max() * 1.18)
save("07_calories_by_category.png")

# top calorie items
fig, ax = plt.subplots(figsize=(8.6, 4.2))
t = top_cal.head(12).sort_values("Calories")
ax.barh([f"{r.Item[:38]}  ({r.Brand.split()[0]})" for r in t.itertuples()], t.Calories,
        color=[COLOURS[b] for b in t.Brand], height=0.62)
for y, v in enumerate(t.Calories):
    ax.text(v + 10, y, f"{v:,.0f}", va="center", fontsize=9, color=INK)
ax.set_title("Highest-calorie items on the menu"); ax.set_xlabel("kcal")
ax.set_xlim(0, t.Calories.max() * 1.2)
save("08_top_calorie_items.png")

pd.set_option("display.width", 200, "display.max_columns", 40)
print("\nBRAND SUMMARY\n", brand.to_string(index=False))
print("\nCATEGORY SUMMARY\n", catall.to_string(index=False))
print("\nKPIs\n", kpi.to_string(index=False))
