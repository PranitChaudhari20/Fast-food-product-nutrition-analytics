# How to collect the price data (about 40 minutes)

*Project owner and author: **Pranit Ajay Chaudhari**.*

The nutrition side of this project uses a real public dataset. **Menu prices are not published as open
data by any of the three brands**, and the only sources that carry them are paid commercial scrapers.
Rather than invent prices, you collect them yourself — which turns this part of the project into
genuine primary research, and is a stronger thing to talk about in an interview than a downloaded file.

## What to do

1. Open `data/raw/price_collection_template.csv` in Excel or Google Sheets.
2. It already has 30 rows: **10 comparable product slots × 3 brands**. The slots exist so that you are
   comparing like with like — a flagship burger against a flagship burger, a medium fries against a
   medium fries. Without that, a price comparison is meaningless.
3. For each row, open the brand's official India app or website and fill in:

| Column | What to put |
|---|---|
| `Item_Name_As_Listed` | The exact product name shown in the app (do not tidy it up) |
| `Size_Or_Variant` | e.g. "Medium", "2 pc", "500 ml" — leave blank if the item has no size |
| `Price_INR` | The listed price in rupees, numbers only (e.g. `219`, not `₹219`) |
| `Date_Collected` | The date you looked, e.g. `2026-09-30` |
| `Source` | e.g. `McDelivery India app` or the website URL |
| `Notes` | Anything odd — item unavailable, price differs by city, offer price, etc. |

4. If a brand genuinely has no item for a slot (for example, a brand with no wrap), write `NOT AVAILABLE`
   in `Item_Name_As_Listed` and leave the price blank. **Do not substitute a different product** — an
   empty slot is a real finding about the brand's menu.
5. Send the filled file back.

## Rules that keep the analysis honest

- **One city, one day.** Fast-food prices in India vary by city and by delivery platform. Collect
  everything from the same city and the same source on the same day, and record which. Mixing sources
  makes the comparison invalid.
- **List price, not offer price.** Skip combo discounts, app-only coupons and limited-time offers, or
  note them clearly in `Notes`.
- **Menu price, not delivery price.** Delivery apps add markups. Prefer the brand's own app/website.
- **Do not estimate.** If you cannot find a price, leave it blank. A blank is analysable; a guess is not.

## What happens once you send it back

The price data is loaded alongside the nutrition data and the project gains:

- price comparison across the three brands, by comparable slot
- price per 100 calories — the value-for-money measure that links price to the nutrition data
- a pricing section in Python, SQL and Excel
- README, RESULTS and resume bullets updated with the pricing findings

Until then the project stands on its own as a product portfolio and nutrition analysis, and nothing in
it claims to contain price data.
