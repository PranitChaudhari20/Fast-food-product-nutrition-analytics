# Data cleaning report

*Project owner and author: **Pranit Ajay Chaudhari**.*

Script: `python/01_clean_data.py` · Audit log: `data/cleaned/cleaning_log.csv`

## Before and after

| | Rows | Brands | Categories | Missing values |
|---|---|---|---|---|
| **Raw file** | 1,147 | 6 chains | none (no category column) | 232 in *Calories from Fat*, 11 rows fully blank |
| **In scope (3 brands)** | 736 | 3 | – | – |
| **Cleaned** | **713** | 3 | 8 (derived) | **0 nutrition values** * |

\* 168 cells are blank by design: protein/sodium per 100 kcal and % calories from fat are undefined for
the 56 zero-calorie items, which are kept and flagged rather than dropped.

## Step by step

| # | Step | Rows after | Change | Why |
|---|---|---|---|---|
| 1 | Loaded raw file | 1,147 | – | Column headers contained embedded line breaks; normalised |
| 2 | Kept McDonald's / Burger King / KFC | 736 | −411 | Taco Bell, Wendy's and Pizza Hut are out of scope. McDonald's is written with a curly apostrophe in the source and was standardised |
| 3 | **Re-attached drink names to size rows** | 736 | 0 | See below — 42 rows repaired |
| 4 | Dropped empty parent header rows | 725 | −11 | The drink-name rows carry no nutrition of their own |
| 5 | Cleaned item text | 725 | 0 | Removed ®, ™, ‡ marks; normalised curly quotes and dashes |
| 6 | Converted nutrition columns to numbers | 725 | 0 | 17 values were `<5` mg cholesterol or `<1` g fibre |
| 7 | Dropped two columns | 725 | 0 | *Calories from Fat* (232 of 736 missing, and derivable as fat × 9) and *Weight Watchers Pnts* (a third-party proprietary score, not a nutrition fact) |
| 8 | Removed rows with no calorie value | 725 | 0 | None remained after step 4 |
| 9 | Removed duplicate Brand + Item rows | **713** | −12 | Same product listed twice in the source |
| 10 | Derived the product category | 713 | 0 | 8 categories, 0 left uncategorised |
| 11 | Derived business metrics | 713 | 0 | `BaseItem`, protein per 100 kcal, sodium per 100 kcal, % calories from fat |

## The structural repair (step 3)

Burger King's fountain drinks are stored as a **parent row followed by child rows**:

```
Coca Cola classic®‡     <- drink name, every nutrition column blank
16 fl oz          210   <- the actual data, but the product name is lost
20 fl oz          270
29 fl oz          290
38 fl oz          510
```

Left alone this produces 11 unusable blank rows and 42 rows carrying only a size label. Those 42 rows use
just five distinct labels (`20 fl oz` ×11, `29 fl oz` ×11, `16 fl oz` ×9, `38 fl oz` ×9, `40 fl oz` ×2), so
37 of them would collide as duplicate Brand+Item pairs. Re-attaching the parent name — `Coca Cola classic (16 fl oz)` — recovers 42 real
products. Eleven header rows across the drinks block, each with 3 or 4 sizes beneath it, account for all
53 affected rows. McDonald's and KFC do not use this structure.

## Decisions worth defending in an interview

- **`<5` and `<1` became 0.** US labelling rules permit anything below those thresholds to be declared as
  zero, so this matches how the number would be read on a label. 17 values affected.
- **Zero-calorie items were kept.** 56 items (diet drinks, water, a salt packet) genuinely contain no
  calories. They are flagged with `IsZeroCalorie` and excluded from ratio measures, where dividing by zero
  is undefined — but they are real menu items and dropping them would understate menu breadth.
- **No category column existed, so one was derived** from the item name with a documented rule set applied
  in priority order. Order matters: *Chicken* is tested before *Desserts* so KFC's "Pot Pie" is a main
  course; *Desserts* before *Beverages* so a milkshake is not filed as a drink; branded drinks before
  *Chicken* so "Tropicana Twister" (a juice) does not collide with KFC's chicken "Twister". Every item
  that initially fell through was inspected and the rules corrected until nothing was left uncategorised.
- **`BaseItem` strips size and count suffixes.** "Diet Coke (Large)" and "Diet Coke (Small)" are one
  product in two sizes. The source writes sizes six different ways — `(32 fl oz cup)`, `- 12 fl oz`,
  `(Regular Size Biscuit)`, `(Family)`, a trailing bare `Large` and a leading `Large` — and all six are
  handled; an earlier version missed four of them and overstated distinct products by 11%. Without this, a brand that lists four cup sizes looks like it has four times the
  range. The analysis reports both menu rows and distinct products.
- **Nothing was deleted in bulk.** The largest removal is step 2, which is scope (other chains), not
  cleaning. Within the three brands, 736 rows became 713 — a 3.1% reduction, all of it duplicates and
  empty header rows.

## What was not fixed

- Serving sizes are absent from the source and could not be reconstructed.
- The vintage of the data is not documented; it is inferred from discontinued products (see `data/raw/README.md`).
- Trans fat is present but is 0 for most items, reflecting reformulation in that era; it is retained but not analysed.
