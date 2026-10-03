# Final results — actual calculated values

*Project owner and author: **Pranit Ajay Chaudhari**.*

Every figure below is computed by `python/01_clean_data.py` and `python/02_analysis.py` and is reproduced
consistently in MySQL and Excel (`docs/VERIFICATION.md`).
Data: US menus for McDonald's, Burger King and KFC, snapshot c. 2010–2013. **The dataset contains no prices.**

## Dataset

| Metric | Value |
|---|---|
| Rows in the raw source file | 1,147 |
| Rows for the three brands in scope | 736 |
| **Clean menu items analysed** | **713** |
| Distinct products across the three brands | 420 |
| Food items (excluding beverages and condiments) | 304 |
| Beverage rows | 356 |
| Brands | 3 |
| Categories (derived) | 8 |
| Items left uncategorised | 0 |
| Zero-calorie items (kept, flagged) | 56 |

## Brand comparison

| Brand | Menu rows | Distinct products | Food items | Drinks as % of rows |
|---|---|---|---|---|
| McDonald's | 328 | 184 | 123 | 55.2% |
| KFC | 213 | 123 | 86 | 52.6% |
| Burger King | 172 | 113 | 95 | 36.6% |

### Nutrition, food items only

| Brand | Avg calories | Median calories | Avg protein (g) | Avg fat (g) | Avg sugars (g) | Avg sodium (mg) |
|---|---|---|---|---|---|---|
| McDonald's | 458.1 | 420 | 17.3 | 19.3 | 26.2 | 707 |
| Burger King | 507.5 | 430 | 18.7 | 28.1 | 17.1 | 906 |
| KFC | 311.9 | 280 | 13.2 | 16.7 | 6.2 | 744 |

### Ratio measures (portion-size independent, items of 100 kcal or more)

| Brand | Protein per 100 kcal | Sodium per 100 kcal | % calories from fat |
|---|---|---|---|
| KFC | 4.55 | 235.2 | 48.5% |
| McDonald's | 3.92 | 163.7 | 37.8% |
| Burger King | 3.31 | 175.3 | 47.0% |

### Menu positioning

| Brand | Food under 400 kcal | Food 800 kcal or more |
|---|---|---|
| KFC | 75.6% | 3.5% |
| McDonald's | 42.3% | 8.1% |
| Burger King | 42.1% | 13.7% |

## Category results

| Category | Items | McDonald's | Burger King | KFC | Avg calories | Avg protein (g) | Avg sugars (g) | Avg sodium (mg) |
|---|---|---|---|---|---|---|---|---|
| Beverages | 356 | 181 | 63 | 112 | 186.1 | 3.0 | 38.2 | 101.2 |
| Chicken | 74 | 15 | 16 | 43 | 378.8 | 19.8 | 2.7 | 872.8 |
| Desserts & Shakes | 58 | 37 | 14 | 7 | 468.3 | 9.5 | 60.1 | 237.7 |
| Burgers & Sandwiches | 56 | 27 | 24 | 5 | 552.9 | 28.9 | 8.1 | 1,083.9 |
| Breakfast | 55 | 29 | 24 | 2 | 487.1 | 16.1 | 8.0 | 1,107.1 |
| Sauces & Condiments | 53 | 24 | 14 | 15 | 75.9 | 0.3 | 4.8 | 206.4 |
| Sides | 45 | 4 | 14 | 27 | 329.1 | 5.7 | 15.5 | 629.7 |
| Salads | 16 | 11 | 3 | 2 | 226.6 | 16.6 | 6.3 | 549.7 |

### Category share of each brand's menu (%)

| Category | McDonald's | Burger King | KFC |
|---|---|---|---|
| Beverages | 55.2 | 36.6 | 52.6 |
| Breakfast | 8.8 | 14.0 | 0.9 |
| Burgers & Sandwiches | 8.2 | 14.0 | 2.3 |
| Chicken | 4.6 | 9.3 | 20.2 |
| Desserts & Shakes | 11.3 | 8.1 | 3.3 |
| Sauces & Condiments | 7.3 | 8.1 | 7.0 |
| Sides | 1.2 | 8.1 | 12.7 |
| Salads | 3.4 | 1.7 | 0.9 |

## Overall figures

| Metric | Value |
|---|---|
| Average calories, food items | 432.2 |
| Median calories, food items | 390 |
| Average protein, food items | 16.6 g |
| Average sodium, food items | 780 mg |
| Average sugars, beverages | 38.2 g |
| Food items under 400 kcal | 51.6% |
| Food items 800 kcal or more | 8.6% |
| Highest-calorie item | Triple Whopper Sandwich with Cheese (Burger King), 1,220 kcal |

## Major business findings

1. **McDonald's carries 184 distinct products against 123 at KFC and 113 at Burger King** — about 50% more range than KFC and 63% more than Burger King.
2. **Burger King's food is the most calorie-dense (507.5 kcal average) and KFC's the least (311.9)** — but this is portion structure, not healthiness: KFC sells individual chicken pieces, Burger King sells composed sandwiches.
3. **On a per-calorie basis KFC is both the most protein-dense (4.55 g/100 kcal) and the most sodium-dense (235.2 mg/100 kcal)** of the three.
4. **Sugar sits in the drinks**: the average beverage carries 38.2 g, and beverages are half of all menu rows.
5. **Breakfast and burgers are the sodium hotspots**, at 1,107 mg and 1,084 mg per item — roughly half an adult's recommended daily intake in one item.
6. **Indulgence is concentrated at Burger King**: 13.7% of its food items are 800 kcal or more, against 8.1% at McDonald's and 3.5% at KFC.
7. **The light-end range barely exists**: salads are 16 items across all three brands, 2.2% of the menu.

## Not in this project

Prices, sales volumes, profitability, serving sizes, current menus, and the Indian market. The dataset
supports none of these; see `docs/BUSINESS_INSIGHTS.md` for the full list of limits.
