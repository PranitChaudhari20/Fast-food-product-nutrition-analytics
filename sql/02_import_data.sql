-- ============================================================================
-- 02_import_data.sql   Load the cleaned menu produced by python/01_clean_data.py
--
-- HOW TO RUN (MySQL 8):
--   mysql --local-infile=1 -u root -p
--   SET GLOBAL local_infile = 1;            -- only if the server refuses
--   Replace the path below with the full path on YOUR machine (forward slashes
--   work on Windows too), then:  SOURCE sql/02_import_data.sql;
-- ============================================================================
USE fastfood_analytics;

LOAD DATA LOCAL INFILE 'data/cleaned/menu_clean.csv'
INTO TABLE menu_items
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(brand, item, base_item, category, calories, fat_g, saturated_fat_g, trans_fat_g,
 cholesterol_mg, sodium_mg, carbs_g, fiber_g, sugars_g, protein_g,
 @ppk, @spk, @pcf, @zero, @variant)
SET protein_per_100kcal   = NULLIF(@ppk, ''),
    sodium_per_100kcal    = NULLIF(@spk, ''),
    pct_calories_from_fat = NULLIF(@pcf, ''),
    is_zero_calorie       = IF(@zero = 'True', 1, 0),
    is_size_variant       = IF(@variant = 'True', 1, 0);

-- Expected: 713 menu items across 3 brands and 8 categories
SELECT COUNT(*) AS menu_items, COUNT(DISTINCT brand) AS brands,
       COUNT(DISTINCT category) AS categories, COUNT(DISTINCT CONCAT(brand, '|', base_item)) AS base_products
FROM menu_items;
