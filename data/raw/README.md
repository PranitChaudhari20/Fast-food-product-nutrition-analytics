# Raw data — provenance and limitations

*Project owner and author: **Pranit Ajay Chaudhari**.*

## The file

`fastfood_nutrition_menu_v3_source.csv` — 1,147 rows × 14 columns, nutrition facts for menu items at six
US fast-food chains. This project uses the three in scope: **McDonald's, Burger King and KFC** (736 of
those rows, 713 after cleaning).

| | |
|---|---|
| **Underlying source** | Nutrition data compiled from **fastfoodnutrition.org**, which republishes the nutrition information the chains themselves publish |
| **Obtained from** | Public GitHub repository `tturne21/Capstone`, file `Data/FastFoodNutritionMenuV3.csv` |
| **Date obtained** | 30 September 2026 |
| **SHA-256** | `20ac70d3d580f44c0326d6a7095f5dae289577e0bd9d06795741984d793caa62` |
| **Market** | United States |
| **Columns** | Company, Item, Calories, Calories from Fat, Total Fat, Saturated Fat, Trans Fat, Cholesterol, Sodium, Carbs, Fiber, Sugars, Protein, Weight Watchers Pnts |

## Limitations — read these before using any number from this project

1. **It is a historical snapshot, roughly 2010–2013.** The file contains products that have since been
   discontinued — McDonald's *Triple Thick Shake* and *Angus* burgers, for example. The analysis is
   therefore a comparison of these menus **as they were**, not as they are today. No claim is made about
   current menus.
2. **It is a third-party compilation.** The compiler and the exact collection date are not documented in
   the source repository. The data is internally consistent and matches the nutrition figures the chains
   published at the time, but it has not been certified by the brands.
3. **US menus only.** McDonald's, Burger King and KFC sell different products in different countries. In
   India, for example, none of the three sells beef. Nothing here transfers to the Indian market.
4. **There are no prices in this file, and none were added.** Menu prices are not published as open data
   by any of the three brands, and the only sources carrying them are paid commercial scrapers. Rather
   than invent prices, the project ships `price_collection_template.csv` for first-hand collection —
   see `docs/PRICE_COLLECTION_GUIDE.md`.
5. **Serving sizes are not given**, so "per item" comparisons mix a single chicken wing with a triple
   burger. This is why the analysis leans on ratio measures (protein per 100 kcal, sodium per 100 kcal),
   which are independent of portion size.
6. **Menu rows are not products.** Each cup size of a drink is its own row, so brands that list more
   sizes look larger. The cleaning step derives a `BaseItem` so distinct products can be counted properly.

## How to reproduce

The cleaned file is committed, so the project runs without re-downloading anything. To start from the
original source:

```bash
git clone --depth 1 https://github.com/tturne21/Capstone.git
cp Capstone/Data/FastFoodNutritionMenuV3.csv data/raw/fastfood_nutrition_menu_v3_source.csv
python python/01_clean_data.py
```

## Other file in this folder

`price_collection_template.csv` — a blank 30-row template (10 comparable product slots × 3 brands) for
collecting India menu prices first-hand. It contains no data yet.
