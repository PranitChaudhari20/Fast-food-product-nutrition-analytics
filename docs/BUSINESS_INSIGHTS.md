# Business insights

*Project owner and author: **Pranit Ajay Chaudhari**.*

All figures come from `data/cleaned/*.csv` and are reproduced identically in Python, SQL, Excel and
Python, SQL and Excel (see `docs/VERIFICATION.md`). Data: US menus, c. 2010–2013, 713 items. **No price data.**

## The one methodological point everything rests on

Beverages are **356 of the 713 menu rows**, because each cup size is listed separately. A brand that sells
four sizes of six drinks books 24 rows without adding a single new product. Two corrections run through
the whole analysis:

- Nutrition averages use **food items only** (304 items; beverages and condiments excluded).
- Portfolio size is reported as **distinct products** (`BaseItem`, size suffixes stripped) as well as menu rows.

Without these, McDonald's would look both larger and lighter than it is, purely because it lists more drinks.

---

## 1. Menu breadth is McDonald's structural difference

| Brand | Menu rows | Distinct products | Food items | Drinks as % of rows |
|---|---|---|---|---|
| McDonald's | 328 | **184** | 123 | 55.2% |
| KFC | 213 | 123 | 86 | 52.6% |
| Burger King | 172 | 113 | 95 | 36.6% |

**What it means.** McDonald's carries about 50% more distinct products than KFC and 63% more than Burger
King. Breadth is a marketing asset — more occasions covered, more reasons to visit — but it is also a
cost: more SKUs, more supplier lines, more prep stations, more waste risk, slower service. Burger King
runs the tightest range, which is the operationally cheaper position.

**What a manager would do with it.** Breadth is only worth its cost if the extra items actually sell. The
menu data cannot answer that — it has no sales figures — so the honest recommendation is to pair this with
item-level sales and cut the long tail that does not earn its place.

---

## 2. Calorie density differs, but it is portion structure, not healthiness

| Brand | Avg calories per food item | Median | % under 400 kcal | % 800 kcal or more |
|---|---|---|---|---|
| Burger King | **507.5** | 430 | 42.1% | **13.7%** |
| McDonald's | 458.1 | 420 | 42.3% | 8.1% |
| KFC | **311.9** | 280 | **75.6%** | 3.5% |

**The trap.** KFC looks like the lightest menu. It is not — KFC sells **individual chicken pieces**
(a wing is 170 kcal) while Burger King sells **composed sandwiches**. A customer does not order one wing.
Per-item calories compare packaging decisions, not diets.

**The fair comparison** is a ratio that removes portion size:

| Brand | Protein per 100 kcal | Sodium per 100 kcal | % calories from fat |
|---|---|---|---|
| KFC | **4.55** | **235.2** | 48.5 |
| McDonald's | 3.92 | 163.7 | 37.8 |
| Burger King | 3.31 | 175.3 | 47.0 |

On this basis KFC's food is the most protein-dense **and** the most sodium-dense per calorie. Both are
real, and they point in opposite marketing directions.

---

## 3. Positioning: each brand's menu states its strategy

- **KFC is the specialist.** 20.2% of its menu rows are Chicken — more than four times McDonald's 4.6% —
  and only 2.3% are Burgers & Sandwiches. Its protein density (4.55 g/100 kcal) is the highest of the
  three. That is a focused, protein-led position, and its menu structure backs the advertising.
- **Burger King is the indulgence brand.** Highest average calories, highest fat (28.1 g per food item),
  the highest share of 800 kcal-plus items (13.7%), and the single largest item on any of the three menus
  (Triple Whopper Sandwich with Cheese, 1,220 kcal). 14.0% of its rows are Burgers & Sandwiches, the
  highest of the three.
- **McDonald's is the breadth player.** No category dominates: Beverages 55.2%, Desserts 11.3%,
  Breakfast 8.8%, Burgers 8.2%. It competes on covering every occasion rather than on owning one.

---

## 4. Sugar is a drinks problem, not a food problem

The average beverage carries **38.2 g of sugar** — around nine teaspoons — against 17.1 g for an average
Burger King food item and 6.2 g for an average KFC one. Desserts & Shakes average 60.1 g, the highest of
any category, but they are only 58 items.

**Why it matters commercially.** Sugar taxes, front-of-pack labelling and reformulation pressure land on
drinks first. 56 items are already zero-calorie, so the zero-sugar range exists; the question is whether it
is priced and promoted hard enough to shift mix. This is the single clearest reformulation lever in the data.

---

## 5. Breakfast, not burgers, is the saltiest category

| Category | Items | Avg calories | Avg sodium (mg) | Avg protein (g) | Avg sugars (g) |
|---|---|---|---|---|---|
| Breakfast | 55 | 487.1 | **1,107.1** | 16.1 | 8.0 |
| Burgers & Sandwiches | 56 | 552.9 | **1,083.9** | 28.9 | 8.1 |
| Chicken | 74 | 378.8 | 872.8 | 19.8 | 2.7 |
| Sides | 45 | 329.1 | 629.7 | 5.7 | 15.5 |
| Salads | 16 | 226.6 | 549.7 | 16.6 | 6.3 |
| Desserts & Shakes | 58 | 468.3 | 237.7 | 9.5 | **60.1** |
| Sauces & Condiments | 53 | 75.9 | 206.4 | 0.3 | 4.8 |
| Beverages | 356 | 186.1 | 101.2 | 3.0 | 38.2 |

A single breakfast or burger item carries roughly **half an adult's recommended daily sodium**. That
breakfast edges ahead of burgers is the less obvious finding and the more actionable one — it is a
smaller, newer daypart where reformulation would be less visible to loyal customers than changing a
flagship burger.

---

## 6. The lightest offer is the thinnest part of every menu

Salads are **16 items across all three brands** — 2.2% of the menu. Every brand has a light-end story to
tell in its advertising and almost no product range to tell it with. If a brand wants to compete on the
health-conscious occasion, the data says the range does not currently exist.

---

## What this analysis cannot tell you

- **Nothing about price or value**, because the dataset has none. See `docs/PRICE_COLLECTION_GUIDE.md`.
- **Nothing about what sells.** Menu composition is not sales mix; a category with many items may
  contribute little revenue.
- **Nothing about today's menus, or about India.** This is a US snapshot from roughly 2010–2013.
- **Nothing about profitability**, portion sizes or ingredient cost.

Every recommendation above is therefore about menu *structure and positioning*, which is what the data
actually supports.
