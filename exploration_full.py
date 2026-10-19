import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

orders = pd.read_csv("olist_orders_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")

# --- Clean reviews FIRST, before anything uses it ---
reviews_sorted = reviews.sort_values("review_creation_date")
reviews_dedup = reviews_sorted.drop_duplicates(subset="order_id", keep="last")
print("Reviews after dedup:", reviews_dedup.shape)
print("Remaining duplicate order_ids:", reviews_dedup["order_id"].duplicated().sum())

# Step 1: attach the real customer identity to each order
merged = orders.merge(customers[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="left")
print("After merging customers:", merged.shape)

# Step 2: attach review scores using the CLEANED reviews table
merged = merged.merge(reviews_dedup[["order_id", "review_score"]], on="order_id", how="left")
print("After merging reviews:", merged.shape)

items = pd.read_csv("olist_order_items_dataset.csv")

# Step 3: attach seller_id and price info
merged = merged.merge(items[["order_id", "seller_id", "price", "freight_value"]], on="order_id", how="left")
print("After merging order_items:", merged.shape)

merged["order_purchase_timestamp"] = pd.to_datetime(merged["order_purchase_timestamp"])
merged["order_delivered_customer_date"] = pd.to_datetime(merged["order_delivered_customer_date"])

merged["delivery_days"] = (merged["order_delivered_customer_date"] - merged["order_purchase_timestamp"]).dt.days

print(merged["delivery_days"].describe())

print(merged["delivery_days"].isna().sum())
delivery_review_data = merged.dropna(subset=["delivery_days"])
print(delivery_review_data.shape)

# Method 1 to check my hypothesis , does slow delivery affect review scores?
correlation = delivery_review_data["delivery_days"].corr(delivery_review_data["review_score"])
print("Correlation:", correlation)

# Method 2 grouped averages (explanation in pdf file)
delivery_review_data["delivery_bucket"] = pd.cut(
    delivery_review_data["delivery_days"],
    bins=[0, 3, 5, 7, 10, 300],
    labels=["0-3 days", "3-5 days", "5-7 days", "7-10 days", "10+ days"]
)

bucket_summary = delivery_review_data.groupby("delivery_bucket", observed=True)["review_score"].mean()
print(bucket_summary)

seller_summary = delivery_review_data.groupby("seller_id").agg(
    avg_delivery_days=("delivery_days", "mean"),
    avg_review_score=("review_score", "mean"),
    n_orders=("order_id", "count")
).reset_index()

print(seller_summary.shape)
print(seller_summary.sort_values("avg_delivery_days", ascending=False).head(10))

seller_big = seller_summary[seller_summary["n_orders"] >= 30]
print(seller_big.shape)
print(seller_big.sort_values("avg_delivery_days", ascending=False).head(10))
print(seller_big["avg_delivery_days"].describe())

print(seller_big["avg_delivery_days"].corr(seller_big["avg_review_score"]))

slow_sellers = seller_big[seller_big["avg_delivery_days"] > 20]
print(slow_sellers.shape)
print(slow_sellers["n_orders"].sum(), seller_big["n_orders"].sum())


print((delivery_review_data["delivery_days"] > 10).mean())

state_summary = delivery_review_data.groupby("customer_state").agg(
    avg_delivery_days=("delivery_days", "mean"),
    avg_review_score=("review_score", "mean"),
    n_orders=("order_id", "count")
).reset_index()
print(state_summary.sort_values("avg_delivery_days", ascending=False))

delivery_review_data["order_estimated_delivery_date"] = pd.to_datetime(delivery_review_data["order_estimated_delivery_date"])
delivery_review_data["is_late"] = delivery_review_data["order_delivered_customer_date"] > delivery_review_data["order_estimated_delivery_date"]

print(delivery_review_data["is_late"].mean())
print(delivery_review_data.groupby("is_late")["review_score"].mean())

state_late = delivery_review_data.groupby("customer_state").agg(
    late_rate=("is_late", "mean"),
    late_orders=("is_late", "sum"),
    avg_review_score=("review_score", "mean"),
    n_orders=("order_id", "count")
).reset_index()

print(state_late.sort_values("late_orders", ascending=False).head(10))
print(state_late[state_late["customer_state"] == "RR"])

print(state_late[state_late["n_orders"] >= 500].sort_values("late_rate", ascending=False))
print(state_late.sort_values("late_rate", ascending=False).head(10))
