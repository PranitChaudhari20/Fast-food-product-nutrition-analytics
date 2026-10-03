# Verification — Python, SQL and Excel

*Project owner and author: **Pranit Ajay Chaudhari**.*

This project intentionally excludes Power BI. The verification below covers the tools and deliverables that are actually included in the final repository.

## 1. Source integrity

| Check | Result |
|---|---|
| Raw file rows / columns | 1,147 × 14 |
| SHA-256 of the source CSV | `20ac70d3d580f44c0326d6a7095f5dae289577e0bd9d06795741984d793caa62` |
| Rows for the three brands | 736 → 713 after cleaning |
| Missing nutrition values after cleaning | 0 (ratio cells are blank by design for zero-calorie items) |
| Items left uncategorised | 0 |

## 2. Python vs SQL

The SQL outputs in `sql/query_results/` were checked against the Python summary tables. **39 of 39 brand metrics were identical** after the documented fixes to calorie-band boundaries, ratio filtering and rounding convention.

## 3. Python vs Excel

`excel/FastFood_Product_Nutrition_Analysis.xlsx` contains **1,638 formulas** and was checked for formula errors and agreement with the published Python/SQL summary values. The workbook uses formula-driven summary sheets rather than pasted result tables.

A product-counting definition issue was identified during the project audit: distinct products must be counted per brand so identically named products from different brands are not silently merged. The Python logic and downstream outputs were corrected to use that definition.

## 4. Independent audit fixes

The project audit identified and fixed issues in the reproducible code/workbook rather than editing the final numbers by hand, including: size-suffix handling in the base-product rule, three condiment classifications, an Excel business-insights cell reference, and SQL presentation/query logic.

## 5. Final verification scope

The final repository contains **Python, SQL and Excel**. No Power BI files, DAX measures, PBIP/PBIX files, or Power BI verification claims are included. Therefore this project makes no claim that Power BI Desktop was opened, refreshed or visually verified.

## 6. Known limitations

- US menus, snapshot of roughly 2010–2013.
- No prices, sales volumes, serving sizes or profitability.
- Categories are derived from item names by documented rules, not supplied by the brands.
- The source is a third-party compilation of nutrition information; see `data/raw/README.md` for provenance.
