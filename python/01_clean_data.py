"""
01_clean_data.py  -  Data cleaning for the fast-food menu nutrition dataset
===========================================================================
Input : data/raw/fastfood_nutrition_menu_v3_source.csv   (see data/raw/README.md for provenance)
Output: data/cleaned/menu_clean.csv        one row per menu item, typed and categorised
        data/cleaned/cleaning_log.csv      rows remaining after every step (audit trail)
        data/cleaned/uncategorised.csv      any item the category rules could not place (should be empty)

Run:  python python/01_clean_data.py

Every rule is a documented decision, not a silent fix. The most important one is step 5:
Burger King's fountain drinks are stored as a parent row (drink name, no nutrition) followed by
child rows named only "16 fl oz", "20 fl oz"... Left alone, 11 rows are empty and 42 rows are
unusable duplicates. Re-attaching the parent name recovers 42 real products.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "fastfood_nutrition_menu_v3_source.csv"
OUT = ROOT / "data" / "cleaned"
OUT.mkdir(parents=True, exist_ok=True)

BRANDS = {"McDonald’s": "McDonald's", "McDonalds": "McDonald's", "McDonald's": "McDonald's",
          "Burger King": "Burger King", "KFC": "KFC"}
NUMERIC = ["Calories", "Total Fat (g)", "Saturated Fat (g)", "Trans Fat (g)", "Cholesterol (mg)",
           "Sodium (mg)", "Carbs (g)", "Fiber (g)", "Sugars (g)", "Protein (g)"]
RENAME = {"Calories": "Calories", "Total Fat (g)": "Fat_g", "Saturated Fat (g)": "SaturatedFat_g",
          "Trans Fat (g)": "TransFat_g", "Cholesterol (mg)": "Cholesterol_mg", "Sodium (mg)": "Sodium_mg",
          "Carbs (g)": "Carbs_g", "Fiber (g)": "Fiber_g", "Sugars (g)": "Sugars_g", "Protein (g)": "Protein_g"}

log = []


def step(name, df, prev, note=""):
    log.append({"step": name, "rows_after": len(df), "rows_changed": prev - len(df), "note": note})
    print(f"{name:<52} rows={len(df):>5}  change={prev - len(df):>+5}  {note}")
    return len(df)


# ---------------------------------------------------------------------------
# 1. LOAD + normalise column names (the header cells contain embedded newlines)
# ---------------------------------------------------------------------------
raw = pd.read_csv(RAW, dtype=str)
raw.columns = [re.sub(r"\s+", " ", c).strip() for c in raw.columns]
n = step("1. Loaded raw file", raw, len(raw), f"{raw.shape[1]} columns, header newlines removed")

# ---------------------------------------------------------------------------
# 2. KEEP ONLY THE THREE BRANDS IN SCOPE, and standardise the brand name
#    (the source writes McDonald's with a curly apostrophe)
# ---------------------------------------------------------------------------
df = raw[raw["Company"].isin(BRANDS)].copy()
df["Brand"] = df["Company"].map(BRANDS)
n = step("2. Kept McDonald's / Burger King / KFC", df, n, "other chains in the file are out of scope")

# ---------------------------------------------------------------------------
# 3. REPAIR Burger King's parent/child drink rows.
#    A row whose Item is only a size ("16 fl oz") belongs to the drink named above it.
# ---------------------------------------------------------------------------
df = df.reset_index(drop=True)
size_only = df["Item"].str.match(r"^\s*\d+\s*(fl\s*oz|oz)\s*$", case=False, na=False)
blank_nutrition = df["Calories"].fillna("").str.strip().eq("")
parent = df["Item"].where(~size_only).ffill()
n_repaired = int(size_only.sum())
df.loc[size_only, "Item"] = parent[size_only].str.strip() + " (" + df.loc[size_only, "Item"].str.strip() + ")"
step("3. Re-attached drink names to size rows", df, n, f"{n_repaired} size rows now carry their drink name")

# ---------------------------------------------------------------------------
# 4. DROP the now-empty parent header rows (they carry no nutrition of their own)
# ---------------------------------------------------------------------------
df = df[~blank_nutrition].copy()
n = step("4. Dropped empty parent header rows", df, n, "11 drink names that held no nutrition data")

# ---------------------------------------------------------------------------
# 5. CLEAN ITEM TEXT: trademark marks, footnote daggers, curly quotes, spacing
# ---------------------------------------------------------------------------
df["Item"] = (df["Item"].str.replace(r"[®™©‡†]", "", regex=True)
                        .str.replace("’", "'", regex=False)
                        .str.replace(r"\s*[–—]\s*", " - ", regex=True)
                        .str.replace(r"\s+", " ", regex=True).str.strip())
step("5. Cleaned item text", df, n, "removed (R)/(TM)/dagger marks, normalised quotes and dashes")

# ---------------------------------------------------------------------------
# 6. NUMERIC CONVERSION.  Labels use "<5" mg cholesterol and "<1" g fibre.
#    US labelling rules let anything under those thresholds be declared as 0,
#    so "<5" -> 0 and "<1" -> 0. This is recorded rather than done silently.
# ---------------------------------------------------------------------------
less_than = 0
for c in NUMERIC:
    s = df[c].fillna("").str.strip()
    less_than += int(s.str.startswith("<").sum())
    df[c] = pd.to_numeric(s.str.replace(r"^<.*$", "0", regex=True).replace("", pd.NA), errors="coerce")
df = df.rename(columns=RENAME)
step("6. Converted nutrition columns to numbers", df, n, f'{less_than} "<5"/"<1" label values set to 0')

# ---------------------------------------------------------------------------
# 7. DROP two columns that cannot support the analysis
#    Calories from Fat: missing for ~30% of rows and fully derivable from fat grams
#    Weight Watchers Pnts: a third-party proprietary score, not a nutrition fact
# ---------------------------------------------------------------------------
dropped = [c for c in ["Calories from Fat", "Weight Watchers Pnts", "Company"] if c in df.columns]
df = df.drop(columns=dropped)
step("7. Dropped unusable columns", df, n, ", ".join(dropped))

# ---------------------------------------------------------------------------
# 8. REMOVE rows with no calorie value, then exact duplicates
# ---------------------------------------------------------------------------
df = df[df["Calories"].notna()].copy()
n = step("8. Removed rows with no calorie value", df, n)
df = df.drop_duplicates(subset=["Brand", "Item"], keep="first")
n = step("9. Removed duplicate Brand+Item rows", df, n, "same product listed twice in the source")

# ---------------------------------------------------------------------------
# 9. DERIVE the product category from the item name.
#    The source has no category column, so this is a documented rule set applied in
#    priority order (first match wins). Breakfast is tested before Chicken so that
#    "Sausage Biscuit" is Breakfast, not Chicken.
# ---------------------------------------------------------------------------
# Rules are applied in priority order, first match wins. The order matters and was set by
# inspecting what fell through: "Pot Pie" must be tested as Chicken before Desserts, a milkshake
# as Dessert before Beverages, and a salad before Sauces or the "no dressing" ones land wrongly.
RULES = [
    # 0. condiment packets first: "Lemon Juice Packet" is a condiment, not a beverage
    # standalone condiments only: "Hotcake Syrup" is a condiment, "Latte with Vanilla Syrup" is a drink
    ("Sauces & Condiments", r"packet|sweetener|creamer|dipping sauce|^(hotcake|breakfast|pancake|maple) syrup"),
    # branded drinks resolved early: "Tropicana Twister" is a juice, not KFC's chicken Twister
    ("Beverages", r"tropicana|capri sun|minute maid|powerade|gatorade|dasani|aquafina|"
                  r"mountain dew|\bpepsi\b|7up|lipton|brisk|nestea|mug root beer"),
    ("Breakfast", r"mcmuffin|mcgriddle|biscuit|croissan|burrito|hotcake|pancake|oatmeal|hash brown|"
                  r"bagel|egg white|sunrise|platter|french toast|cinnabon|cinnamon roll|danish|"
                  r"english muffin|sausage, egg|ham, egg|bacon, egg|egg & cheese|breakfast"),
    # 1. these are side dishes despite being called "salad"
    ("Sides", r"potato salad|macaroni salad|cole ?slaw|apple slices|apple dippers"),
    ("Salads", r"salad"),
    # 2. chicken before desserts so KFC's "Pot Pie" is a main course
    ("Chicken", r"chicken|nugget|tender|wing|strip|popcorn|drumstick|thigh|breast|"
                r"original recipe|extra crispy|grilled filet|mcchicken|selects|pot pie|famous bowl|"
                r"twister|snacker|littles|gizzard|liver"),
    # 3. desserts before beverages so a milkshake is not filed as a drink
    ("Desserts & Shakes", r"shake|mcflurry|sundae|\bcone\b|\bpie\b|cookie|brownie|cheesecake|"
                          r"soft serve|dessert|parfait|donut|ice cream|\bcake\b|float|cinnamon melt"),
    ("Burgers & Sandwiches", r"burger|big mac|whopper|quarter pounder|mcdouble|mcrib|sandwich|"
                             r"filet-o-fish|\bfish\b|angus|stacker|rodeo|\bmelt\b|wrap|slider|"
                             r"big n'? tasty|\btaco\b|steakhouse|king\b|\bjr\.?\b"),
    ("Sides", r"fries|onion ring|potato|mashed|corn|beans|mac & cheese|macaroni|\bside\b|"
              r"yogurt|chips|applesauce|jamwich|rice|gravy|\broll\b|tater|hush pupp|okra|greens|"
              r"\bapple\b|fruit"),
    ("Beverages", r"coca.?cola|diet coke|\bcoke\b|sprite|dr\.? pepper|root beer|fanta|hi-c|lemonade|"
                  r"sweet tea|unsweetened tea|iced tea|\btea\b|coffee|latte|mocha|cappuccino|espresso|"
                  r"frappe|americano|juice|\bmilk\b|water|dasani|soft drink|soda|smoothie|slushie|"
                  r"capri sun|hot chocolate|powerade|gatorade|pepsi|mountain dew|7up|brisk|"
                  r"fl oz\)|\(child\)|\(small\)|\(medium\)|\(large\)"),
    ("Sauces & Condiments", r"sauce|dressing|vinaigrette|ketchup|mayo|mustard|syrup|jam|jelly|preserves|"
                            r"cream cheese|margarine|butter|honey|salt\b|croutons|\bdip\b|"
                            r"american cheese|\bcheese \(slice\)"),
]


def categorise(item):
    s = item.lower()
    for name, pattern in RULES:
        if re.search(pattern, s):
            return name
    return "Uncategorised"


# A product sold in four cup sizes is four rows in the source. BaseItem strips the size/count
# suffix so the analysis can report distinct products as well as menu rows. The source writes sizes
# six different ways - "(32 fl oz cup)", "- 12 fl oz", "(Regular Size Biscuit)", "(Family)",
# "POPCORN NUGGETS Large" and "Large French Fries" - so all six are handled.
SIZE_WORD = r"child|kids?|small|medium|large|snack|value|regular|extra large|x-?large|family|unsalted|king"
SIZE_SUFFIX = re.compile(
    r"\s*("
    r"\(\s*\d+\s*(fl\s*oz|oz|pc|piece)s?(\s*cup)?\s*\)"          # (32 fl oz cup), (9 pc)
    r"|\(\s*(" + SIZE_WORD + r")(\s+size\s+biscuit)?\s*\)"          # (Large), (Regular Size Biscuit)
    r"|\(\s*\d+\s*slices?\s*\)|\(\s*each\s*\)|\(\s*1\s*pat\s*\)"
    r"|[-\u2013]\s*\d+\s*(fl\s*oz|oz|pc|piece)s?\.?"                # - 12 fl oz, - 9 pc.
    r"|[-\u2013]\s*(" + SIZE_WORD + r")\.?"                            # - small, - value
    r"|\b\d+\s*(pc|piece)s?\.?"                                       # 6pc
    r"|\s(" + SIZE_WORD + r")"                                           # trailing bare: "... Large"
    r")\s*$", re.I)
LEADING_SIZE = re.compile(r"^\s*(" + SIZE_WORD + r")\s+(?=[A-Za-z])", re.I)


def base_item(item):
    prev = None
    s = item.strip()
    while prev != s:                      # repeat: "French Fries - value (unsalted)" needs two passes
        prev = s
        s = SIZE_SUFFIX.sub("", s).strip(" -\u2013,")
    stripped = LEADING_SIZE.sub("", s).strip()
    return stripped or s or item.strip()


df["Category"] = df["Item"].map(categorise)
unc = df[df["Category"] == "Uncategorised"]
step("10. Derived product category from item name", df, n,
     f"{df['Category'].nunique()} categories, {len(unc)} uncategorised")

# ---------------------------------------------------------------------------
# 10. DERIVED BUSINESS METRICS (all computed from the cleaned columns)
# ---------------------------------------------------------------------------
df["ProteinPer100kcal"] = (df["Protein_g"] / df["Calories"] * 100).round(2)
df["SodiumPer100kcal"] = (df["Sodium_mg"] / df["Calories"] * 100).round(1)
df["PctCaloriesFromFat"] = (df["Fat_g"] * 9 / df["Calories"] * 100).round(1)
for c in ["ProteinPer100kcal", "SodiumPer100kcal", "PctCaloriesFromFat"]:
    df.loc[df["Calories"] == 0, c] = pd.NA          # zero-calorie drinks: ratio undefined
df["IsZeroCalorie"] = df["Calories"] == 0
df["BaseItem"] = df["Item"].map(base_item)
df["IsSizeVariant"] = df.duplicated(subset=["Brand", "BaseItem"], keep=False)

cols = ["Brand", "Item", "BaseItem", "Category", "Calories", "Fat_g", "SaturatedFat_g", "TransFat_g",
        "Cholesterol_mg", "Sodium_mg", "Carbs_g", "Fiber_g", "Sugars_g", "Protein_g",
        "ProteinPer100kcal", "SodiumPer100kcal", "PctCaloriesFromFat", "IsZeroCalorie", "IsSizeVariant"]
clean = df[cols].sort_values(["Brand", "Category", "Item"]).reset_index(drop=True)
step("11. Final clean menu table", clean, n, f"{clean.shape[1]} columns")

clean.to_csv(OUT / "menu_clean.csv", index=False)
pd.DataFrame(log).to_csv(OUT / "cleaning_log.csv", index=False)
unc.to_csv(OUT / "uncategorised.csv", index=False)

print("\nSUMMARY")
print(f"  raw rows in file         : {len(raw):>5}")
print(f"  clean items (3 brands)   : {len(clean):>5}")
print(f"  items per brand          : {dict(clean.Brand.value_counts())}")
print(f"  categories               : {dict(clean.Category.value_counts())}")
print(f"  distinct base products   : {clean.groupby('Brand').BaseItem.nunique().to_dict()}")
print(f"  zero-calorie items kept  : {int(clean.IsZeroCalorie.sum())}")
print(f"  missing values remaining : {int(clean[['Calories','Fat_g','Sodium_mg','Protein_g']].isna().sum().sum())}")
