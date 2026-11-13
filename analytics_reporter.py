from db_manager import DatabaseManager


class AnalyticsReporter:
  """A class dedicated to generating e-commerce business insights and reports."""

  def __init__(self):
    self.db = DatabaseManager()

  def report_daily_revenue_trends(self):
    """Fetches daily revenue and 7-day rolling averages."""
    query = """
        Select 
        date(o.order_date) as order_day,
        sum(oi.quantity * oi.item_price) as daily_revenue,
        avg(sum(oi.quantity * oi.item_price)) OVER (order by date(o.order_date) rows between 6 preceding and current row) as rolling_7_day_avg_revenue
        from orders o
        join order_items oi on o.order_id = oi.order_id
        group by date(o.order_date)
        order by order_day desc
        LIMIT 10;
        """

    self.db.connect()
    if not self.db.connection:
      return

    try:
      self.db.cursor.execute(query)
      rows = self.db.cursor.fetchall()

      print("\n--- RECENT DAILY REVENUE & 7-DAY ROLLING AVERAGE ---")
      print(f"{'Date':<15} | {'Daily Revenue ($)':<18} | {'7-Day Rolling Avg ($)':<20}")
      print("-" * 60)
      for row in rows:
        day, rev, roll_avg = row
        print(f"{str(day):<15} | ${float(rev):<17.2f} | ${float(roll_avg):<19.2f}")

    except Exception as e:
      print(f"Error fetching revenue report: {e}")
    finally:
      self.db.close()

  def report_top_vip_customers(self):
    """Fetches high-value customers based on order count and lifetime spend."""
    query = """
        select u.name, count(distinct o.order_id) as total_orders, sum(oi.quantity * oi.item_price) as lifetime_spend
        from users u 
        join orders o on u.user_id = o.user_id 
        join order_items oi on o.order_id = oi.order_id
        group by u.user_id, u.name
        HAVING COUNT(DISTINCT o.order_id) >= 3 AND SUM(oi.quantity * oi.item_price) > 200
        ORDER BY lifetime_spend DESC
        LIMIT 5;
        """

    self.db.connect()
    if not self.db.connection:
      return

    try:
      self.db.cursor.execute(query)
      rows = self.db.cursor.fetchall()

      print("\n--- TOP VIP CUSTOMERS REPORT ---")
      print(f"{'Customer Name':<25} | {'Total Orders':<12} | {'Lifetime Spend ($)'}")
      print("-" * 60)
      for row in rows:
        name, orders_count, spend = row
        print(f"{name:<25} | {orders_count:<12} | ${float(spend):.2f}")

    except Exception as e:
      print(f"Error fetching VIP report: {e}")
    finally:
      self.db.close()


if __name__ == "__main__":
  reporter = AnalyticsReporter()
  reporter.report_daily_revenue_trends()
  reporter.report_top_vip_customers()