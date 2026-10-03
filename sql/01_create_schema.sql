-- ============================================================================
-- 01_create_schema.sql   (MySQL 8.0 / MariaDB 10.5+)
-- Fast-Food Product & Nutrition Analytics - McDonald's vs Burger King vs KFC
--
-- Two tables:
--   menu_items  one row per menu item, as produced by python/01_clean_data.py
--   categories  the eight derived product categories, with the food/non-food flag
--               that the analysis uses to keep drinks and condiments out of the
--               per-item nutrition averages
-- ============================================================================

CREATE DATABASE IF NOT EXISTS fastfood_analytics
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fastfood_analytics;

DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category        VARCHAR(30)  NOT NULL,
    is_food         TINYINT(1)   NOT NULL,   -- 0 = beverage or condiment, excluded from food averages
    display_order   TINYINT      NOT NULL,
    PRIMARY KEY (category)
) ENGINE = InnoDB;

INSERT INTO categories (category, is_food, display_order) VALUES
('Burgers & Sandwiches', 1, 1),
('Chicken',              1, 2),
('Breakfast',            1, 3),
('Sides',                1, 4),
('Salads',               1, 5),
('Desserts & Shakes',    1, 6),
('Beverages',            0, 7),
('Sauces & Condiments',  0, 8);

CREATE TABLE menu_items (
    item_id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    brand                VARCHAR(20)  NOT NULL,
    item                 VARCHAR(120) NOT NULL,   -- product name as listed, cleaned
    base_item            VARCHAR(120) NOT NULL,   -- name with the size/count suffix removed
    category             VARCHAR(30)  NOT NULL,
    calories             INT          NOT NULL,
    fat_g                DECIMAL(6,1) NOT NULL,
    saturated_fat_g      DECIMAL(6,1) NOT NULL,
    trans_fat_g          DECIMAL(6,1) NOT NULL,
    cholesterol_mg       INT          NOT NULL,
    sodium_mg            INT          NOT NULL,
    carbs_g              DECIMAL(6,1) NOT NULL,
    fiber_g              DECIMAL(6,1) NOT NULL,
    sugars_g             DECIMAL(6,1) NOT NULL,
    protein_g            DECIMAL(6,1) NOT NULL,
    protein_per_100kcal  DECIMAL(6,2) NULL,       -- NULL for zero-calorie items
    sodium_per_100kcal   DECIMAL(8,1) NULL,
    pct_calories_from_fat DECIMAL(6,1) NULL,
    is_zero_calorie      TINYINT(1)   NOT NULL,
    is_size_variant      TINYINT(1)   NOT NULL,   -- product also sold in another size
    PRIMARY KEY (item_id),
    INDEX idx_brand (brand),
    INDEX idx_category (category),
    CONSTRAINT fk_menu_category FOREIGN KEY (category) REFERENCES categories (category)
) ENGINE = InnoDB;
