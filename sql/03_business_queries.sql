-- ============================================================================
-- 03_business_queries.sql   14 business questions answered in SQL
-- Each block starts with "-- QUERY nn |" so python/run_sql_queries.py can run them
-- one at a time and save the output to sql/query_results/.
-- Techniques: GROUP BY, HAVING, CASE, JOIN, CTEs, window functions.
-- Nothing here exists to pad the file; every query answers a stated question.
-- ============================================================================
USE fastfood_analytics;

-- QUERY 01 | Portfolio size by brand | How big is each brand's menu, and how much of it is just cup sizes?
SELECT brand,
       COUNT(*)                                                     AS menu_rows,
       COUNT(DISTINCT base_item)                                    AS base_products,
       SUM(is_size_variant)                                         AS size_variant_rows,
       ROUND(SUM(is_size_variant) * 100.0 / COUNT(*), 1)            AS pct_rows_that_are_size_variants,
       COUNT(DISTINCT category)                                     AS categories_covered
FROM menu_items
GROUP BY brand
ORDER BY base_products DESC;

-- QUERY 02 | Menu composition | What share of each brand's menu sits in each category?
SELECT m.brand, m.category, c.is_food,
       COUNT(*)                                                     AS items,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY m.brand), 1) AS pct_of_brand_menu
FROM menu_items m
JOIN categories c ON c.category = m.category
GROUP BY m.brand, m.category, c.is_food
ORDER BY m.brand, items DESC;

-- QUERY 03 | Average calories by brand | Which brand's food is the most calorie-dense per item?
--           Drinks and condiments are excluded: a brand that lists four cup sizes would otherwise
--           look lighter simply because it lists more low-calorie rows.
SELECT m.brand,
       COUNT(*)                                                     AS food_items,
       ROUND(AVG(m.calories), 1)                                    AS avg_calories,
       ROUND(AVG(m.protein_g), 1)                                   AS avg_protein_g,
       ROUND(AVG(m.fat_g), 1)                                       AS avg_fat_g,
       ROUND(AVG(m.sugars_g), 1)                                    AS avg_sugars_g,
       ROUND(AVG(m.sodium_mg), 0)                                   AS avg_sodium_mg
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1
GROUP BY m.brand
ORDER BY avg_calories DESC;

-- QUERY 04 | Calorie range by brand | How wide is each brand's calorie range (food items)?
SELECT m.brand,
       MIN(m.calories)                                              AS min_calories,
       MAX(m.calories)                                              AS max_calories,
       MAX(m.calories) - MIN(m.calories)                            AS calorie_range,
       ROUND(AVG(m.calories), 1)                                    AS avg_calories,
       ROUND(STDDEV_SAMP(m.calories), 1)                            AS stdev_calories
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1
GROUP BY m.brand
ORDER BY calorie_range DESC;

-- QUERY 05 | Category nutrition profile | Which categories are the calorie and sodium hotspots?
SELECT c.display_order, m.category, c.is_food,
       COUNT(*)                                                     AS items,
       ROUND(AVG(m.calories), 1)                                    AS avg_calories,
       ROUND(AVG(m.protein_g), 1)                                   AS avg_protein_g,
       ROUND(AVG(m.sugars_g), 1)                                    AS avg_sugars_g,
       ROUND(AVG(m.sodium_mg), 0)                                   AS avg_sodium_mg
FROM menu_items m
JOIN categories c ON c.category = m.category
GROUP BY c.display_order, m.category, c.is_food
ORDER BY avg_calories DESC;

-- QUERY 06 | Highest-calorie items | Which single products carry the most calories?
SELECT RANK() OVER (ORDER BY calories DESC)                         AS calorie_rank,
       brand, item, category, calories, fat_g, sugars_g, sodium_mg
FROM menu_items
ORDER BY calories DESC
LIMIT 15;

-- QUERY 07 | Lightest food items | What does each brand offer at the low-calorie end?
WITH ranked AS (
    SELECT m.brand, m.item, m.category, m.calories, m.protein_g,
           ROW_NUMBER() OVER (PARTITION BY m.brand ORDER BY m.calories ASC, m.item) AS rn
    FROM menu_items m
    JOIN categories c ON c.category = m.category
    WHERE c.is_food = 1 AND m.calories > 0
)
SELECT brand, rn AS rank_in_brand, item, category, calories, protein_g
FROM ranked
WHERE rn <= 5
ORDER BY brand, rn;

-- QUERY 08 | Protein efficiency | Which items give the most protein per 100 calories?
--           This is the fairest cross-brand nutrition comparison: it removes portion size.
SELECT m.brand, m.item, m.category, m.calories, m.protein_g, m.protein_per_100kcal,
       RANK() OVER (ORDER BY m.protein_per_100kcal DESC)            AS protein_rank
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1 AND m.calories >= 100
ORDER BY m.protein_per_100kcal DESC
LIMIT 15;

-- QUERY 09 | Protein efficiency by brand | Which brand's food delivers the most protein per calorie?
SELECT m.brand,
       ROUND(AVG(m.protein_per_100kcal), 2)                         AS avg_protein_per_100kcal,
       ROUND(AVG(m.sodium_per_100kcal), 1)                          AS avg_sodium_per_100kcal,
       ROUND(AVG(m.pct_calories_from_fat), 1)                       AS avg_pct_calories_from_fat
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1 AND m.calories >= 100
GROUP BY m.brand
ORDER BY avg_protein_per_100kcal DESC;

-- QUERY 10 | Indulgent vs lighter menu | How is each brand's food split across calorie bands?
SELECT m.brand,
       SUM(CASE WHEN m.calories < 200                      THEN 1 ELSE 0 END) AS under_200,
       SUM(CASE WHEN m.calories BETWEEN 200 AND 399        THEN 1 ELSE 0 END) AS band_200_399,
       SUM(CASE WHEN m.calories BETWEEN 400 AND 599        THEN 1 ELSE 0 END) AS band_400_599,
       SUM(CASE WHEN m.calories BETWEEN 600 AND 799        THEN 1 ELSE 0 END) AS band_600_799,
       SUM(CASE WHEN m.calories >= 800                     THEN 1 ELSE 0 END) AS over_800,
       ROUND(SUM(CASE WHEN m.calories < 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_under_400,
       ROUND(SUM(CASE WHEN m.calories >= 800 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_over_800
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1
GROUP BY m.brand
ORDER BY pct_over_800 DESC;

-- QUERY 11 | Sugar in drinks | How much sugar does a typical beverage carry, and who sells the sweetest?
SELECT brand,
       COUNT(*)                                                     AS beverage_rows,
       SUM(is_zero_calorie)                                         AS zero_calorie_options,
       ROUND(SUM(is_zero_calorie) * 100.0 / COUNT(*), 1)            AS pct_zero_calorie,
       ROUND(AVG(sugars_g), 1)                                      AS avg_sugars_g,
       MAX(sugars_g)                                                AS max_sugars_g
FROM menu_items
WHERE category = 'Beverages'
GROUP BY brand
ORDER BY avg_sugars_g DESC;

-- QUERY 12 | Items at double their brand's average | Which products pull a brand's calorie average up?
WITH brand_avg AS (
    SELECT m.brand, AVG(m.calories) AS avg_cal
    FROM menu_items m JOIN categories c ON c.category = m.category
    WHERE c.is_food = 1
    GROUP BY m.brand
)
SELECT m.brand, m.item, m.category, m.calories,
       ROUND(b.avg_cal, 0)                                          AS brand_avg_calories,
       ROUND(m.calories - b.avg_cal, 0)                             AS kcal_above_brand_avg
FROM menu_items m
JOIN categories c ON c.category = m.category
JOIN brand_avg  b ON b.brand = m.brand
WHERE c.is_food = 1 AND m.calories > b.avg_cal * 2      -- more than double the brand average
ORDER BY kcal_above_brand_avg DESC, m.item          -- item breaks ties so the output is stable
LIMIT 15;

-- QUERY 13 | Category breadth | Where is each brand deep, and where is it barely present?
SELECT m.category,
       SUM(CASE WHEN m.brand = 'McDonald''s'  THEN 1 ELSE 0 END)    AS mcdonalds,
       SUM(CASE WHEN m.brand = 'Burger King'  THEN 1 ELSE 0 END)    AS burger_king,
       SUM(CASE WHEN m.brand = 'KFC'          THEN 1 ELSE 0 END)    AS kfc,
       COUNT(*)                                                     AS total_items
FROM menu_items m
GROUP BY m.category
HAVING COUNT(*) >= 20        -- drops the smallest categories; Salads (16) falls out here
ORDER BY total_items DESC;

-- QUERY 14 | Core-category comparison | On the categories all three brands compete in, who is heaviest?
SELECT m.category, m.brand,
       COUNT(*)                                                     AS items,
       ROUND(AVG(m.calories), 0)                                    AS avg_calories,
       ROUND(AVG(m.sodium_mg), 0)                                   AS avg_sodium_mg,
       -- compared with the unweighted mean of the brand averages in this category, not the item-weighted mean
       ROUND(AVG(m.calories) - AVG(AVG(m.calories)) OVER (PARTITION BY m.category), 0) AS vs_mean_of_brand_avgs
FROM menu_items m
JOIN categories c ON c.category = m.category
WHERE c.is_food = 1
GROUP BY m.category, m.brand
HAVING COUNT(*) >= 3
ORDER BY m.category, avg_calories DESC;
