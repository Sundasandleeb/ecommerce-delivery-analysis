import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

orders = pd.read_csv("olist_orders_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
items = pd.read_csv("olist_order_items_dataset.csv")

# --- Clean reviews: keep only the latest review per order ---
reviews_sorted = reviews.sort_values("review_creation_date")
reviews_dedup = reviews_sorted.drop_duplicates(subset="order_id", keep="last")

# --- Build the merged table ---
merged = orders.merge(customers[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="left")
merged = merged.merge(reviews_dedup[["order_id", "review_score"]], on="order_id", how="left")
merged = merged.merge(items[["order_id", "seller_id", "price", "freight_value"]], on="order_id", how="left")

# --- Convert text to dates and calculate delivery days ---
merged["order_purchase_timestamp"] = pd.to_datetime(merged["order_purchase_timestamp"])
merged["order_delivered_customer_date"] = pd.to_datetime(merged["order_delivered_customer_date"])
merged["delivery_days"] = (merged["order_delivered_customer_date"] - merged["order_purchase_timestamp"]).dt.days

# --- Keep only delivered orders ---
delivery_review_data = merged.dropna(subset=["delivery_days"])
delivery_review_data = delivery_review_data.drop_duplicates(subset="order_id")

# --- Late vs promised ---
delivery_review_data["order_estimated_delivery_date"] = pd.to_datetime(delivery_review_data["order_estimated_delivery_date"])
delivery_review_data["is_late"] = delivery_review_data["order_delivered_customer_date"] > delivery_review_data["order_estimated_delivery_date"]

# --- Late orders by state ---
state_late = delivery_review_data.groupby("customer_state").agg(
    late_rate=("is_late", "mean"),
    late_orders=("is_late", "sum"),
    avg_review_score=("review_score", "mean"),
    n_orders=("order_id", "count")
).reset_index()

print(state_late.sort_values("late_orders", ascending=False).head(10))

# --- Where does the delay happen: seller handling or carrier transit? ---
delivery_review_data["order_delivered_carrier_date"] = pd.to_datetime(delivery_review_data["order_delivered_carrier_date"])

delivery_review_data["handling_days"] = (delivery_review_data["order_delivered_carrier_date"] - delivery_review_data["order_purchase_timestamp"]).dt.days
delivery_review_data["transit_days"] = (delivery_review_data["order_delivered_customer_date"] - delivery_review_data["order_delivered_carrier_date"]).dt.days

# stage_by_state = delivery_review_data.groupby("customer_state").agg(
#     avg_handling_days=("handling_days", "mean"),
#     avg_transit_days=("transit_days", "mean")
# ).reset_index()
#
# print(stage_by_state[stage_by_state["customer_state"].isin(["SP", "RJ", "MG", "BA"])])

# --- Is the promised delivery time realistic? ---
# delivery_review_data["promised_days"] = (delivery_review_data["order_estimated_delivery_date"] - delivery_review_data["order_purchase_timestamp"]).dt.days
#
# promise_by_state = delivery_review_data.groupby("customer_state").agg(
#     avg_promised_days=("promised_days", "mean"),
#     avg_actual_days=("delivery_days", "mean")
# ).reset_index()
#
# promise_by_state["gap_days"] = promise_by_state["avg_actual_days"] - promise_by_state["avg_promised_days"]
#
# print(promise_by_state[promise_by_state["customer_state"].isin(["SP", "RJ", "MG", "BA"])])

# --- How spread out are delivery times? ---
# spread_by_state = delivery_review_data.groupby("customer_state").agg(
#     avg_actual_days=("delivery_days", "mean"),
#     std_actual_days=("delivery_days", "std"),
#     max_actual_days=("delivery_days", "max"),
#     late_rate=("is_late", "mean")
# ).reset_index()
#
# print(spread_by_state[spread_by_state["customer_state"].isin(["SP", "RJ", "MG", "BA"])])

# --- How slow are the slowest orders? ---
# days_by_state = delivery_review_data.groupby("customer_state")["delivery_days"]
#
# tail_by_state = pd.DataFrame({
#     "median_days": days_by_state.median(),
#     "p90_days": days_by_state.quantile(0.90),
#     "p95_days": days_by_state.quantile(0.95)
# }).reset_index()
#
# tail_by_state["p90_vs_median"] = tail_by_state["p90_days"] - tail_by_state["median_days"]
#
# print(tail_by_state[tail_by_state["customer_state"].isin(["SP", "RJ", "MG", "BA"])])

# --- Final headline numbers ---
print("Delivered orders:", len(delivery_review_data))
print("Late rate:", delivery_review_data["is_late"].mean())
print(delivery_review_data.groupby("is_late")["review_score"].mean())

state_final = delivery_review_data.groupby("customer_state").agg(
    late_rate=("is_late", "mean"),
    late_orders=("is_late", "sum"),
    n_orders=("order_id", "count")
).reset_index()
print(state_final[state_final["customer_state"].isin(["SP", "RJ", "MG", "BA"])])

import matplotlib.pyplot as plt

# --- Chart 1: review score, on time vs late ---
score_by_late = delivery_review_data.groupby("is_late")["review_score"].mean()
plt.figure(figsize=(6, 4))
plt.bar(["On time", "Late"], [score_by_late[False], score_by_late[True]], color=["#4c9f70", "#d9534f"])
plt.ylabel("Average review score")
plt.title("Late orders score 1.7 stars lower")
plt.ylim(0, 5)
plt.tight_layout()
plt.savefig("chart1_late_vs_ontime.png", dpi=150)
plt.close()

# --- Chart 2: late rate by state (states with 1,000+ orders) ---
big_states = state_final[state_final["n_orders"] >= 1000].sort_values("late_rate")
bar_colors = ["#d9534f" if s == "RJ" else "#9aa5b1" for s in big_states["customer_state"]]
plt.figure(figsize=(7, 6))
plt.barh(big_states["customer_state"], big_states["late_rate"] * 100, color=bar_colors)
plt.xlabel("Late orders (%)")
plt.title("Share of orders delivered late, by state")
plt.tight_layout()
plt.savefig("chart2_late_rate_by_state.png", dpi=150)
plt.close()

# --- Chart 3: number of late orders, top 10 states ---
top_late = state_final.sort_values("late_orders", ascending=False).head(10).sort_values("late_orders")
bar_colors = ["#d9534f" if s == "RJ" else "#9aa5b1" for s in top_late["customer_state"]]
plt.figure(figsize=(7, 5))
plt.barh(top_late["customer_state"], top_late["late_orders"], color=bar_colors)
plt.xlabel("Number of late orders")
plt.title("Where the late orders are: RJ is second only to SP")
plt.tight_layout()
plt.savefig("chart3_late_orders_by_state.png", dpi=150)
plt.close()