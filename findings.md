## Olist Delivery and Review Analysis
## Unit of analysis

Headline results (late rate, review scores, state comparison) are counted per order (96,476 delivered orders). The seller analysis is counted per order item (110,196 rows), because one order can include several sellers. Early exploratory figures (delivery buckets, correlation, handling vs transit) were computed per order item and shift only slightly on a per-order basis.

## Data and cleaning (setup)
Olist e-commerce data: 99,441 orders, 8 tables.
customer_id is one per order, so any repeat-customer analysis must use customer_unique_id.
551 orders had duplicate reviews. I kept the latest review per order, which brought the row count back to exactly 99,441.
2,965 orders have no delivery date, so they were excluded from delivery analysis.
Merging order_items turns multi-product orders into several rows. Item-level analysis uses 110,196 delivered rows. Order-level analysis keeps one row per order, which gives 96,476 delivered orders.
## Delivery speed and reviews (per item)
Correlation between delivery days and review score is -0.30.
The average score falls from 4.39 (0-3 days) to 3.83 (10+ days), with the sharpest drop after 10 days.
46% of delivered items take more than 10 days.
## Sellers (per item)
Of 2,970 sellers, only 681 have 30+ orders. Averages for sellers with 1 to 5 orders are noise.
Among those 681, the seller-level correlation is -0.43, stronger than the item-level -0.30 because averaging removes noise.
Only 14 sellers average over 20 days, and they handle 2.3% of items. A seller blacklist would not fix the platform.
## Geography (per item)
Delivery time depends on location: SP averages 8.3 days, the remote northern states 20 to 28.
Slow does not mean low-rated. AP and AM wait about 27 days but score 4.1 to 4.3.
Late versus promised (per order, main finding)
8.1% of delivered orders arrive after the promised date.
Late orders average 2.57 stars against 4.29 for on-time ones, a 1.73-star gap.
This is much larger than the 0.56-star gap between fast and slow delivery (per item).
Customers judge delivery against the promise, not against a fixed number of days.
For reference, the first per-item version of these figures was 7.9%, 2.55 vs 4.21, and a 1.66-star gap. The conclusion did not change.
## Where the late orders are (per order)
RJ has a 13.5% late rate against 5.9% for SP and 5.6% for MG.
RJ has 1,664 late orders, second only to SP’s 2,387. That is 21% of all 7,827 late orders on the platform.
If RJ matched SP’s late rate, it would have about 730 late orders instead of 1,664. That is about 940 fewer, or roughly 12% of all late orders.
RR is the slowest state, but it has only 5 late orders out of 46 (per item).
## Why RJ is late (per item)
Seller handling takes 2.7 to 2.9 days in every major state, and RJ is only 0.17 days slower than SP.
RJ’s extra delay vs SP (about 6.4 days) is about 97% carrier transit (11.3 days vs 5.1).
Orders arrive earlier than the promised date on average in all four states (SP, MG, RJ, BA), so the problem is the minority of late orders, not the average.
RJ’s typical order is similar to MG’s (median 11 vs 10 days), but its slowest 10% are much slower (p90 28 vs 20 days). BA is slow across the board (median 16).
Transit (carrier and route) is therefore the stage to investigate, not the sellers.
## Limits
The data has no carrier names or routes, so “transit” covers the carrier, the route and local conditions.
Late orders are correlated with low scores, but I have not proven they cause them. Damaged or wrong items could also play a part.
Retention (do customers with a late order come back less?) was not analysed. It is a next step.
