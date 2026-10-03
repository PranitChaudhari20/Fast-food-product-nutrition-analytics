"""
03_build_excel.py  -  Excel workbook for the fast-food analysis
================================================================
Output: excel/FastFood_Product_Nutrition_Analysis.xlsx

The workbook recalculates the analysis itself: Clean_Data holds the 713 menu items and every
summary sheet is COUNTIFS / AVERAGEIFS / SUMIFS on top of it. Change or filter the data and the
brand summary, category analysis, KPIs and charts all follow.

Run:  python python/03_build_excel.py

IMPORTANT after running: openpyxl writes formulas but cannot evaluate them, so the file it produces has
no cached values. Excel and LibreOffice recalculate on open, but GitHub's and Google Drive's previews do
not - they would show a blank grid. Open the file once in Excel or LibreOffice and save it before
committing, so the committed workbook carries its values. The copy in this repository has been through
that step.
"""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.formula import ArrayFormula

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "cleaned"
OUT = ROOT / "excel" / "FastFood_Product_Nutrition_Analysis.xlsx"
OUT.parent.mkdir(exist_ok=True)

FONT = "Arial"
F_BASE = Font(name=FONT, size=10)
F_BOLD = Font(name=FONT, size=10, bold=True)
F_TITLE = Font(name=FONT, size=14, bold=True, color="1F3864")
F_SUB = Font(name=FONT, size=10, italic=True, color="595959")
F_HDR = Font(name=FONT, size=10, bold=True, color="FFFFFF")
FILL_HDR = PatternFill("solid", fgColor="1F3864")
FILL_KPI = PatternFill("solid", fgColor="EAF1FB")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
N1, N0, PCT = "#,##0.0", "#,##0", "0.0%"

data = pd.read_csv(CLEAN / "menu_clean.csv")
NROW = len(data)
LAST = NROW + 1                                   # last data row on Clean_Data
BRANDS = ["McDonald's", "Burger King", "KFC"]
CATS = [("Burgers & Sandwiches", 1, 1), ("Chicken", 1, 2), ("Breakfast", 1, 3), ("Sides", 1, 4),
        ("Salads", 1, 5), ("Desserts & Shakes", 1, 6), ("Beverages", 0, 7), ("Sauces & Condiments", 0, 8)]

wb = Workbook()


def header_row(ws, row, ncols, start=1):
    for c in range(start, start + ncols):
        cell = ws.cell(row=row, column=c)
        cell.font = F_HDR; cell.fill = FILL_HDR; cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def widths(ws, w):
    for i, x in enumerate(w, start=1):
        ws.column_dimensions[get_column_letter(i)].width = x


def title(ws, text, sub=None):
    ws["A1"] = text; ws["A1"].font = F_TITLE
    if sub:
        ws["A2"] = sub; ws["A2"].font = F_SUB


# ===========================================================================
# Category_Lookup
# ===========================================================================
wl = wb.active; wl.title = "Category_Lookup"
title(wl, "Product categories", "IsFood = 0 for beverages and condiments. Nutrition averages use food items only.")
wl.append([]); wl.append(["Category", "IsFood", "DisplayOrder"]); header_row(wl, 4, 3)
for c, isf, order in CATS:
    wl.append([c, isf, order])
widths(wl, [26, 10, 14])
LK_CAT, LK_FOOD = f"Category_Lookup!$A$5:$A${4 + len(CATS)}", f"Category_Lookup!$B$5:$B${4 + len(CATS)}"

# ===========================================================================
# Clean_Data  (+ two formula helper columns)
# ===========================================================================
wd = wb.create_sheet("Clean_Data")
cols = list(data.columns) + ["IsFood", "IsFirstOfBaseProduct"]
wd.append(cols); header_row(wd, 1, len(cols))
# booleans are written as 1/0 rather than True/False: it matches the SQL TINYINT and the
# Category_Lookup convention, and stops a recalculating spreadsheet rewriting 1,426 literal
# booleans as =TRUE()/=FALSE() formulas
_bool_cols = [i for i, c in enumerate(data.columns) if data[c].dtype == bool]
for row in data.itertuples(index=False):
    vals = list(row)
    for i in _bool_cols:
        vals[i] = int(vals[i])
    wd.append(vals + [None, None])
for i in range(2, LAST + 1):
    wd.cell(row=i, column=20, value=f"=INDEX({LK_FOOD},MATCH(D{i},{LK_CAT},0))")
    # 1 the first time a brand+base product appears, so distinct products can be summed
    wd.cell(row=i, column=21, value=f"=IF(COUNTIFS($A$2:A{i},A{i},$C$2:C{i},C{i})=1,1,0)")
wd.freeze_panes = "B2"; wd.auto_filter.ref = f"A1:U{LAST}"
widths(wd, [14, 44, 38, 21, 9, 8, 10, 9, 12, 10, 9, 8, 9, 9, 11, 11, 11, 11, 12, 9, 12])
A = f"Clean_Data!$A$2:$A${LAST}"; D = f"Clean_Data!$D$2:$D${LAST}"; E = f"Clean_Data!$E$2:$E${LAST}"
FAT = f"Clean_Data!$F$2:$F${LAST}"; SOD = f"Clean_Data!$J$2:$J${LAST}"; CAR = f"Clean_Data!$K$2:$K${LAST}"
SUG = f"Clean_Data!$M$2:$M${LAST}"; PRO = f"Clean_Data!$N$2:$N${LAST}"
PPK = f"Clean_Data!$O$2:$O${LAST}"; SPK = f"Clean_Data!$P$2:$P${LAST}"; PCF = f"Clean_Data!$Q$2:$Q${LAST}"
FOOD = f"Clean_Data!$T$2:$T${LAST}"; FIRST = f"Clean_Data!$U$2:$U${LAST}"
SATF = f"Clean_Data!$G$2:$G${LAST}"; FIB = f"Clean_Data!$L$2:$L${LAST}"

# ===========================================================================
# Brand_Summary
# ===========================================================================
wb_ = wb.create_sheet("Brand_Summary")
title(wb_, "Brand summary", "Every figure is a formula over Clean_Data. Nutrition columns use food items only "
                            "(IsFood=1), so drinks and sauces do not distort the averages.")
hdr = ["Brand", "Menu rows", "Distinct products", "Food items", "Beverage rows", "% rows are drinks",
       "Avg calories", "Median calories", "Avg protein (g)", "Avg fat (g)", "Avg sugars (g)",
       "Avg sodium (mg)", "Protein per 100 kcal", "Sodium per 100 kcal", "% food under 400 kcal",
       "% food 800 kcal+"]
wb_.append([]); wb_.append(hdr); header_row(wb_, 4, len(hdr))
for i, b in enumerate(BRANDS):
    r = 5 + i
    q = f'$A${r}'
    wb_.cell(row=r, column=1, value=b)
    wb_.cell(row=r, column=2, value=f'=COUNTIFS({A},{q})').number_format = N0
    wb_.cell(row=r, column=3, value=f'=SUMIFS({FIRST},{A},{q})').number_format = N0
    wb_.cell(row=r, column=4, value=f'=COUNTIFS({A},{q},{FOOD},1)').number_format = N0
    wb_.cell(row=r, column=5, value=f'=COUNTIFS({A},{q},{D},"Beverages")').number_format = N0
    wb_.cell(row=r, column=6, value=f'=E{r}/B{r}').number_format = PCT
    wb_.cell(row=r, column=7, value=f'=AVERAGEIFS({E},{A},{q},{FOOD},1)').number_format = N1
    wb_.cell(row=r, column=8, value=ArrayFormula(f"H{r}", f'=MEDIAN(IF(({A}={q})*({FOOD}=1),{E}))')).number_format = N0
    wb_.cell(row=r, column=9, value=f'=AVERAGEIFS({PRO},{A},{q},{FOOD},1)').number_format = N1
    wb_.cell(row=r, column=10, value=f'=AVERAGEIFS({FAT},{A},{q},{FOOD},1)').number_format = N1
    wb_.cell(row=r, column=11, value=f'=AVERAGEIFS({SUG},{A},{q},{FOOD},1)').number_format = N1
    wb_.cell(row=r, column=12, value=f'=AVERAGEIFS({SOD},{A},{q},{FOOD},1)').number_format = N0
    wb_.cell(row=r, column=13, value=f'=AVERAGEIFS({PPK},{A},{q},{FOOD},1,{E},">=100")').number_format = "#,##0.00"
    wb_.cell(row=r, column=14, value=f'=AVERAGEIFS({SPK},{A},{q},{FOOD},1,{E},">=100")').number_format = N1
    wb_.cell(row=r, column=15, value=f'=COUNTIFS({A},{q},{FOOD},1,{E},"<400")/D{r}').number_format = PCT
    wb_.cell(row=r, column=16, value=f'=COUNTIFS({A},{q},{FOOD},1,{E},">=800")/D{r}').number_format = PCT
BR_LAST = 4 + len(BRANDS)
for rr in range(5, BR_LAST + 1):
    for cc in range(1, len(hdr) + 1):
        wb_.cell(row=rr, column=cc).font = F_BASE
wb_.conditional_formatting.add(f"G5:G{BR_LAST}", DataBarRule(start_type="min", end_type="max", color="5B9BD5"))
wb_.conditional_formatting.add(f"L5:L{BR_LAST}", DataBarRule(start_type="min", end_type="max", color="ED7D31"))
widths(wb_, [15, 11, 15, 11, 12, 14, 12, 13, 13, 12, 13, 13, 16, 16, 16, 15])

# ===========================================================================
# Category_Analysis
# ===========================================================================
wc = wb.create_sheet("Category_Analysis")
title(wc, "Category analysis", "Item counts per brand and the nutrition profile of each category.")
hdr2 = ["Category", "Is food", "Total items", "McDonald's", "Burger King", "KFC",
        "Avg calories", "Avg protein (g)", "Avg sugars (g)", "Avg sodium (mg)", "% of all items"]
wc.append([]); wc.append(hdr2); header_row(wc, 4, len(hdr2))
for i, (c, isf, _o) in enumerate(CATS):
    r = 5 + i
    q = f'$A${r}'
    wc.cell(row=r, column=1, value=c)
    wc.cell(row=r, column=2, value=isf).number_format = N0
    wc.cell(row=r, column=3, value=f'=COUNTIFS({D},{q})').number_format = N0
    for j, b in enumerate(BRANDS):
        wc.cell(row=r, column=4 + j, value=f'=COUNTIFS({D},{q},{A},"{b}")').number_format = N0
    wc.cell(row=r, column=7, value=f'=AVERAGEIFS({E},{D},{q})').number_format = N1
    wc.cell(row=r, column=8, value=f'=AVERAGEIFS({PRO},{D},{q})').number_format = N1
    wc.cell(row=r, column=9, value=f'=AVERAGEIFS({SUG},{D},{q})').number_format = N1
    wc.cell(row=r, column=10, value=f'=AVERAGEIFS({SOD},{D},{q})').number_format = N0
    wc.cell(row=r, column=11, value=f'=C{r}/SUM($C$5:$C${4 + len(CATS)})').number_format = PCT
CAT_LAST = 4 + len(CATS)
wc.cell(row=CAT_LAST + 1, column=1, value="TOTAL").font = F_BOLD
wc.cell(row=CAT_LAST + 1, column=3, value=f"=SUM(C5:C{CAT_LAST})").number_format = N0
for j in range(3):
    wc.cell(row=CAT_LAST + 1, column=4 + j,
            value=f"={get_column_letter(4 + j)}5+{get_column_letter(4 + j)}6+{get_column_letter(4 + j)}7+"
                  f"{get_column_letter(4 + j)}8+{get_column_letter(4 + j)}9+{get_column_letter(4 + j)}10+"
                  f"{get_column_letter(4 + j)}11+{get_column_letter(4 + j)}12").number_format = N0
for cc in range(1, len(hdr2) + 1):
    wc.cell(row=CAT_LAST + 1, column=cc).font = F_BOLD
    wc.cell(row=CAT_LAST + 1, column=cc).fill = FILL_KPI
wc.conditional_formatting.add(f"G5:G{CAT_LAST}", ColorScaleRule(start_type="min", start_color="FFFFFF",
                              end_type="max", end_color="5B9BD5"))
widths(wc, [24, 9, 12, 13, 13, 9, 13, 15, 15, 15, 13])

# ===========================================================================
# Nutrition_Analysis
# ===========================================================================
wn = wb.create_sheet("Nutrition_Analysis")
title(wn, "Nutrition analysis", "Food items only. Min / average / max per nutrient, per brand.")
NUTRIENTS = [("Calories", E, N0), ("Fat (g)", FAT, N1), ("Saturated fat (g)", SATF, N1),
             ("Carbs (g)", CAR, N1), ("Sugars (g)", SUG, N1), ("Fibre (g)", FIB, N1),
             ("Protein (g)", PRO, N1), ("Sodium (mg)", SOD, N0)]
wn.append([]); wn.append(["Nutrient", "Brand", "Minimum", "Average", "Median", "Maximum"])
header_row(wn, 4, 6)
r = 5
for name, rng, fmt in NUTRIENTS:
    for b in BRANDS:
        wn.cell(row=r, column=1, value=name if b == BRANDS[0] else "")
        wn.cell(row=r, column=2, value=b)
        wn.cell(row=r, column=3, value=f'=_xlfn.MINIFS({rng},{A},B{r},{FOOD},1)').number_format = fmt
        wn.cell(row=r, column=4, value=f'=AVERAGEIFS({rng},{A},B{r},{FOOD},1)').number_format = N1
        wn.cell(row=r, column=5, value=ArrayFormula(f"E{r}", f'=MEDIAN(IF(({A}=B{r})*({FOOD}=1),{rng}))')).number_format = N1
        wn.cell(row=r, column=6, value=f'=_xlfn.MAXIFS({rng},{A},B{r},{FOOD},1)').number_format = fmt
        r += 1
widths(wn, [20, 15, 12, 12, 12, 12])

# ===========================================================================
# KPIs
# ===========================================================================
wk = wb.create_sheet("KPIs", 1)
title(wk, "Headline figures", "All formulas. Food items exclude beverages and condiments.")
kpis = [
    ("Menu rows analysed", f'=COUNTA({A})', N0),
    ("Distinct base products", f'=SUM({FIRST})', N0),
    ("Food items", f'=COUNTIFS({FOOD},1)', N0),
    ("Beverage rows", f'=COUNTIFS({D},"Beverages")', N0),
    ("Brands", f'=3', N0),
    ("Categories", f'={len(CATS)}', N0),
    ("Average calories, food items", f'=AVERAGEIFS({E},{FOOD},1)', N1),
    ("Median calories, food items", "ARRAY:=MEDIAN(IF(%s=1,%s))" % (FOOD, E), N0),
    ("Highest-calorie item (kcal)", f'=MAX({E})', N0),
    ("Average protein, food items (g)", f'=AVERAGEIFS({PRO},{FOOD},1)', N1),
    ("Average sodium, food items (mg)", f'=AVERAGEIFS({SOD},{FOOD},1)', N0),
    ("Average sugars, beverages (g)", f'=AVERAGEIFS({SUG},{D},"Beverages")', N1),
    ("Zero-calorie items", f'=COUNTIFS({E},0)', N0),
    ("Food items under 400 kcal", f'=COUNTIFS({FOOD},1,{E},"<400")/COUNTIFS({FOOD},1)', PCT),
    ("Food items 800 kcal or more", f'=COUNTIFS({FOOD},1,{E},">=800")/COUNTIFS({FOOD},1)', PCT),
]
wk.append([]); wk.append(["Metric", "Value"]); header_row(wk, 4, 2)
for i, (m, f_, fmt) in enumerate(kpis):
    r = 5 + i
    wk.cell(row=r, column=1, value=m).font = F_BASE
    val = ArrayFormula(f"B{r}", f_.replace("ARRAY:", "")) if str(f_).startswith("ARRAY:") else f_
    c = wk.cell(row=r, column=2, value=val); c.font = F_BOLD; c.fill = FILL_KPI; c.border = BORDER
    c.number_format = fmt; c.alignment = Alignment(horizontal="right")
widths(wk, [40, 18])

# ===========================================================================
# Business_Insights
# ===========================================================================
wi = wb.create_sheet("Business_Insights")
title(wi, "Business insights", "Each line references the sheets above, so the numbers update with the data.")
wi.append([]); wi.append(["#", "Finding", "Figure", "Why it matters"]); header_row(wi, 4, 4)
INSIGHTS = [
    ("Widest menu", '=Brand_Summary!C5', "McDonald's lists the most distinct products; menu breadth is a cost and complexity decision as well as a choice decision."),
    ("Narrowest menu", '=Brand_Summary!C6', "Burger King runs the tightest range of the three, which simplifies kitchen operations."),
    ("Heaviest food per item", '=Brand_Summary!G6', "Burger King's average food item carries the most calories, consistent with a burger-led menu."),
    ("Lightest food per item", '=Brand_Summary!G7', "KFC's average is lowest because it sells individual chicken pieces rather than composed sandwiches - a portion-structure difference, not a health claim."),
    ("Most protein per 100 kcal", '=Brand_Summary!M7', "KFC gets the most protein out of each calorie, which supports a protein-led marketing message."),
    ("Drinks as a share of the menu", '=Brand_Summary!F5', "Over half of McDonald's menu rows are drinks, mostly the same product in different cup sizes."),
    ("Average sugar in a drink (g)", '=KPIs!B16', "Beverages are where the sugar sits; this is the clearest reformulation and labelling exposure."),
    ("Sodium in burgers (mg)", '=Category_Analysis!J5', "Burgers and sandwiches carry the most sodium per item of any category."),
]
for i, (name, formula, why) in enumerate(INSIGHTS):
    r = 5 + i
    wi.cell(row=r, column=1, value=i + 1)
    wi.cell(row=r, column=2, value=name).font = F_BOLD
    c = wi.cell(row=r, column=3, value=formula); c.font = F_BOLD; c.fill = FILL_KPI; c.number_format = N1
    c.border = BORDER
    cell = wi.cell(row=r, column=4, value=why); cell.font = F_BASE
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    wi.row_dimensions[r].height = 30
widths(wi, [5, 30, 14, 96])

# ===========================================================================
# Charts
# ===========================================================================
wch = wb.create_sheet("Charts", 3)
title(wch, "Charts", "Built on Brand_Summary and Category_Analysis, so they follow the data.")


def bar(title_, cats, vals, anchor, ylab, colour, horizontal=False, w=15, h=8):
    ch = BarChart(); ch.type = "bar" if horizontal else "col"; ch.title = title_; ch.style = 10
    ch.add_data(vals, titles_from_data=True); ch.set_categories(cats)
    ch.y_axis.title = ylab; ch.legend = None; ch.width = w; ch.height = h
    ch.series[0].graphicalProperties.solidFill = colour
    ch.dataLabels = DataLabelList(); ch.dataLabels.showVal = True
    wch.add_chart(ch, anchor)


bcat = Reference(wb_, min_col=1, min_row=5, max_row=BR_LAST)
bar("Distinct products by brand", bcat, Reference(wb_, min_col=3, min_row=4, max_row=BR_LAST),
    "A4", "products", "2A78D6")
bar("Average calories per food item", bcat, Reference(wb_, min_col=7, min_row=4, max_row=BR_LAST),
    "J4", "kcal", "EB6834")
bar("Average sodium per food item (mg)", bcat, Reference(wb_, min_col=12, min_row=4, max_row=BR_LAST),
    "A22", "mg", "1BAF7A")
ccat = Reference(wc, min_col=1, min_row=5, max_row=CAT_LAST)
bar("Average calories by category", ccat, Reference(wc, min_col=7, min_row=4, max_row=CAT_LAST),
    "J22", "kcal", "2A78D6", horizontal=True, w=16, h=9)

# ===========================================================================
# README
# ===========================================================================
wr = wb.create_sheet("README", 0)
title(wr, "Fast-Food Product & Nutrition Analytics",
      "McDonald's vs Burger King vs KFC - menu portfolio and nutrition comparison")
rows = [
    ("Owner", "Pranit Ajay Chaudhari"),
    ("Data source", "fastfood_nutrition_menu_v3_source.csv - see data/raw/README.md for full provenance"),
    ("Market / vintage", "United States menus, snapshot of approximately 2010-2013 (contains discontinued items)"),
    ("Scope", f"{NROW} menu items across 3 brands and {len(CATS)} categories"),
    ("", ""),
    ("How the workbook works", ""),
    ("Clean_Data", f"The {NROW} cleaned menu items, produced by python/01_clean_data.py. Two formula columns are "
                   "added here: IsFood (from Category_Lookup) and IsFirstOfBaseProduct (used to count distinct products)."),
    ("KPIs", "Headline figures, all formulas."),
    ("Brand_Summary", "Portfolio size and nutrition averages per brand."),
    ("Category_Analysis", "Item counts per brand and nutrition profile per category."),
    ("Nutrition_Analysis", "Min / average / median / max per nutrient per brand."),
    ("Business_Insights", "The findings, each pointing at the cell that produced it."),
    ("Charts", "Native Excel charts, built on the summary sheets."),
    ("Category_Lookup", "The eight categories and the food / non-food flag."),
    ("", ""),
    ("Important method note", ""),
    ("", "Beverages are 356 of the 713 rows because each cup size is listed separately. Every nutrition "
         "average therefore uses food items only (IsFood = 1). Portfolio size is reported both as menu rows "
         "and as distinct base products, so a brand is not credited for listing four sizes of one drink."),
    ("", ""),
    ("Note on prices", "This workbook contains no price data. Menu prices are not published as open data by "
                       "any of the three brands; see docs/PRICE_COLLECTION_GUIDE.md."),
]
r = 4
for k, v in rows:
    wr.cell(row=r, column=1, value=k).font = F_BOLD if v else F_BOLD
    c = wr.cell(row=r, column=2, value=v); c.font = F_BASE
    c.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
widths(wr, [24, 118])

for sh in wb.worksheets:
    for row in sh.iter_rows():
        for c in row:
            if c.value is not None and c.font.name != FONT:
                c.font = Font(name=FONT, size=c.font.size or 10, bold=c.font.bold,
                              italic=c.font.italic, color=c.font.color)

wb.properties.creator = "Pranit Ajay Chaudhari"
wb.properties.lastModifiedBy = "Pranit Ajay Chaudhari"
wb.properties.title = "Fast-Food Product & Nutrition Analytics"
wb.properties.subject = "McDonald's vs Burger King vs KFC menu portfolio and nutrition comparison"
wb.properties.description = "Portfolio project by Pranit Ajay Chaudhari."
wb._sheets = [wb[n] for n in ["README", "KPIs", "Brand_Summary", "Category_Analysis", "Nutrition_Analysis",
                              "Business_Insights", "Charts", "Clean_Data", "Category_Lookup"]]
wb.save(OUT)
print("saved", OUT, "|", NROW, "items")
