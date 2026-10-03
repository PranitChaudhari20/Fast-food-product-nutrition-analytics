# SQL version of the project (MySQL 8 / MariaDB 10.5+)

*Project owner and author: **Pranit Ajay Chaudhari**.*

The SQL layer rebuilds the comparison in a database and answers 14 business questions. Every script was
executed against MariaDB 10.11 and the results match the Python and Excel figures exactly
(see `../docs/VERIFICATION.md`).

## Files

| File | Purpose |
|---|---|
| `01_create_schema.sql` | Creates database `fastfood_analytics`, the `menu_items` table and the `categories` lookup (with the food / non-food flag) |
| `02_import_data.sql` | `LOAD DATA LOCAL INFILE` for `data/cleaned/menu_clean.csv` |
| `03_business_queries.sql` | The 14 queries |
| `query_results/` | The actual output of each query as CSV |

## How to run

```bash
mysql -u root -p < sql/01_create_schema.sql
mysql --local-infile=1 -u root -p fastfood_analytics < sql/02_import_data.sql   # edit the CSV path first
# then run any query in 03_business_queries.sql, or run everything and export:
python python/run_sql_queries.py --user root --password "yourpassword"
```

If the import fails with *"Loading local data is disabled"*, run `SET GLOBAL local_infile = 1;` as an
administrator, or use MySQL Workbench's **Table Data Import Wizard**.

## Query index

| # | Business question | SQL features |
|---|---|---|
| 01 | How big is each brand's menu, and how much of it is just cup sizes? | aggregates, ratio |
| 02 | What share of each brand's menu sits in each category? | `JOIN`, window `SUM() OVER (PARTITION BY)` |
| 03 | Which brand's food is the most calorie-dense per item? | `JOIN`, filtered aggregate |
| 04 | How wide is each brand's calorie range? | `MIN`/`MAX`/`STDDEV_SAMP` |
| 05 | Which categories are the calorie and sodium hotspots? | `JOIN`, `GROUP BY` |
| 06 | Which single products carry the most calories? | `RANK()` window |
| 07 | What does each brand offer at the low-calorie end? | CTE, `ROW_NUMBER() PARTITION BY` |
| 08 | Which items give the most protein per 100 calories? | `RANK()`, ratio column |
| 09 | Which brand's food delivers the most protein per calorie? | filtered aggregate |
| 10 | How is each brand's food split across calorie bands? | `CASE` bucketing |
| 11 | How much sugar does a typical drink carry? | conditional aggregates |
| 12 | Which products sit at more than double their brand's average? | CTE + join back to the aggregate |
| 13 | Where is each brand deep, and where is it barely present? | `CASE` pivot, `HAVING` |
| 14 | On shared categories, which brand is heaviest? | nested window over an aggregate |

## Schema

```
categories (8 rows)                 menu_items (713 rows)
  category       VARCHAR(30) PK       item_id              INT PK
  is_food        TINYINT(1)           brand                VARCHAR(20)
  display_order  TINYINT              item / base_item     VARCHAR(120)
                                      category             VARCHAR(30) -> categories.category
                                      calories             INT
                                      fat_g, saturated_fat_g, trans_fat_g, carbs_g,
                                      fiber_g, sugars_g, protein_g      DECIMAL(6,1)
                                      cholesterol_mg, sodium_mg         INT
                                      protein_per_100kcal, sodium_per_100kcal,
                                      pct_calories_from_fat             DECIMAL (NULL if 0 kcal)
                                      is_zero_calorie, is_size_variant  TINYINT(1)
```

`is_food = 0` marks Beverages and Sauces & Condiments. Every nutrition query joins `categories` and filters
`is_food = 1`, because beverages are 356 of the 713 rows and would otherwise dominate the averages.
