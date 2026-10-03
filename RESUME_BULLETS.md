# Resume bullets — Project 2: Fast-Food Product & Nutrition Analytics

Author: **Pranit Ajay Chaudhari**. Every number below comes from `RESULTS.md` and is reproducible from the repository.

**Fast-Food Product & Nutrition Analytics — Python, SQL, Excel** · [GitHub repo]

- Cleaned and analysed a **713-item menu dataset covering McDonald's, Burger King and KFC** in **Python (pandas)**, repairing a broken parent/child structure that had left 42 Burger King drink rows labelled only "16 fl oz", and deriving an 8-category product taxonomy that classified **100% of items** with no missing nutrition values.
- Compared the three brands' **product portfolios and nutrition** across **14 MySQL queries** (CTEs, window functions, `CASE`) and a **1,638-formula Excel model**, establishing that McDonald's carries **184 distinct products against 123 at KFC and 113 at Burger King**, and that KFC's food is the most protein-dense per calorie (**4.55 g/100 kcal**) but also the most sodium-dense (**235 mg/100 kcal**).
- Built a reproducible **Python + SQL + Excel analytics workflow** covering brand overview, product mix, nutrition and business insights, with core figures reconciled across the tools and an independent audit used to fix data-cleaning, product-counting and Excel-reference defects.
- Translated the analysis into category recommendations: **reformulate breakfast first** (**1,107 mg sodium per item**, the saltiest category of all, in a smaller and less loyalty-sensitive daypart than burgers), and **treat sugar as a drinks problem** (**38.2 g average per beverage**, with drinks making up half of all menu rows) rather than a food-menu problem.

*Shorter variant (if space is tight):*

- Cleaned a 713-item fast-food menu dataset in Python, repairing 42 malformed product rows and deriving an 8-category taxonomy with zero items unclassified.
- Compared McDonald's, Burger King and KFC on portfolio breadth and nutrition using 14 MySQL queries and a 1,638-formula Excel model; McDonald's carries 184 distinct products against 113 and 123 at its rivals.
- Built a reproducible Python + SQL + Excel analytics workflow with core figures reconciled across the tools and documented verification checks.
- Recommended reformulating breakfast (1,107 mg sodium per item) and targeting sugar reduction at drinks (38.2 g average), based on category-level evidence.

## Talking points for an interview

- **The best story in this project is the cleaning.** Burger King's fountain drinks were stored as a name row followed by size rows, so 42 products had lost their names and looked like duplicates. Spotting and repairing that recovered real data instead of deleting it.
- **The most important judgement call** was excluding beverages from nutrition averages. Drinks are half the rows because every cup size is listed separately, so including them would have made McDonald's look both larger and lighter than it is.
- **The finding that sounds wrong until you explain it**: KFC has the lowest average calories per item. That is because KFC sells individual chicken pieces and Burger King sells whole sandwiches — which is why the analysis uses per-100-kcal ratios, where KFC is in fact the most fat- and sodium-dense.
- **The mistake I caught and fixed.** My first version of the "distinct products" rule only stripped some of the ways the source writes sizes, so "Chocolate Shake (12 fl oz cup)" and "(16 fl oz cup)" counted as two products. That overstated the headline figure by about 11% (468 rather than 420). An independent audit caught it, I fixed the rule and regenerated every downstream number rather than editing the write-up.
- **Be honest about what is missing**: there are no prices in the public data, so the project does not claim to analyse pricing, and the dataset is a US snapshot from roughly 2010–2013.
