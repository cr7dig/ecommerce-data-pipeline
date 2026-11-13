import pandas as pd
import streamlit as st
from db_manager import DatabaseManager

# Page configuration
st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")
st.title("📊 E-Commerce Data Pipeline & Analytics")
st.markdown(
    "Filter and explore live PostgreSQL data without writing a single line of"
    " SQL."
)


# Helper function to run queries safely and return a Pandas DataFrame
def run_query(query, params=None):
  db = DatabaseManager()
  db.connect()
  if not db.connection:
    st.error(
        "Failed to connect to PostgreSQL. Check your .env file and server"
        " status."
    )
    return pd.DataFrame()
  try:
    df = pd.read_sql_query(query, db.connection, params=params)
    return df
  finally:
    db.close()


# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Interactive Filters")

# 1. Rolling window filter
rolling_days = st.sidebar.slider(
    "Revenue Rolling Average (Days)", min_value=3, max_value=30, value=7
)

# 2. Category filter
categories_df = run_query("SELECT DISTINCT category FROM products;")
category_list = (
    ["All"] + categories_df["category"].tolist()
    if not categories_df.empty
    else ["All"]
)
selected_category = st.sidebar.selectbox("Product Category", category_list)

# 3. VIP Customer Spend Filter
min_spend = st.sidebar.number_input(
    "Minimum VIP Customer Spend ($)", min_value=50, max_value=2000, value=200, step=50
)
min_orders = st.sidebar.slider(
    "Minimum Orders Placed", min_value=1, max_value=10, value=3
)

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns(2)

# Section 1: Dynamic Revenue Trends
with col1:
  st.subheader(f"📈 Daily Revenue & {rolling_days}-Day Rolling Avg")
  rev_query = f"""
        SELECT 
            DATE(o.order_date) AS order_day,
            SUM(oi.quantity * oi.item_price) AS daily_revenue,
            AVG(SUM(oi.quantity * oi.item_price)) OVER (
                ORDER BY DATE(o.order_date) 
                ROWS BETWEEN {rolling_days - 1} PRECEDING AND CURRENT ROW
            ) AS rolling_avg
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY DATE(o.order_date)
        ORDER BY order_day ASC;
    """
  rev_df = run_query(rev_query)

  if not rev_df.empty:
    rev_df.set_index("order_day", inplace=True)
    st.line_chart(rev_df[["daily_revenue", "rolling_avg"]])
  else:
    st.info("No revenue data found.")

# Section 2: Top Selling Products by Category
with col2:
  st.subheader(f"🏆 Top Selling Products ({selected_category})")
  if selected_category == "All":
    prod_query = """
            SELECT p.product_name, p.category, SUM(oi.quantity) AS units_sold
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_name, p.category
            ORDER BY units_sold DESC
            LIMIT 10;
        """
    prod_df = run_query(prod_query)
  else:
    prod_query = """
            SELECT p.product_name, p.category, SUM(oi.quantity) AS units_sold
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            WHERE p.category = %s
            GROUP BY p.product_name, p.category
            ORDER BY units_sold DESC;
        """
    prod_df = run_query(prod_query, params=(selected_category,))

  if not prod_df.empty:
    st.bar_chart(prod_df.set_index("product_name")["units_sold"])
    st.dataframe(prod_df, use_container_width=True)

# Section 3: Dynamic VIP Customer Lookup
st.divider()
st.subheader(
    f"💎 VIP Customers (Spend > ${min_spend} & Orders >= {min_orders})"
)

vip_query = """
    SELECT 
        u.name AS customer_name,
        u.email,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity * oi.item_price) AS lifetime_spend
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY u.user_id, u.name, u.email
    HAVING COUNT(DISTINCT o.order_id) >= %s AND SUM(oi.quantity * oi.item_price) > %s
    ORDER BY lifetime_spend DESC;
"""
vip_df = run_query(vip_query, params=(min_orders, min_spend))

if not vip_df.empty:
  st.dataframe(vip_df, use_container_width=True)
else:
  st.warning(
      "No customers match those filter criteria. Try lowering the thresholds in"
      " the sidebar!"
  )