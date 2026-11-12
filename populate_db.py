import random
from datetime import datetime, timedelta
from faker import Faker
from db_manager import DatabaseManager  # Import your custom OOP class

# Initialize Faker
fake = Faker()


def populate_database():
  # Instantiate the DatabaseManager object
  db = DatabaseManager()

  # Connect using the object's method
  db.connect()

  if not db.connection:
    print("Stopping population due to connection failure.")
    return

  try:
    # 1. Insert Mock Users (50 users)
    print("Generating users...")
    user_ids = []
    for _ in range(50):
      name = fake.name()
      email = fake.unique.email()
      address = fake.address().replace("\n", ", ")

      # Use the connection's cursor directly
      db.cursor.execute(
          "INSERT INTO users (name, email, address) VALUES (%s, %s, %s) RETURNING"
          " user_id;",
          (name, email, address),
      )
      user_ids.append(db.cursor.fetchone()[0])

    # 2. Insert Mock Products (10 products)
    print("Generating products...")
    product_data = [
        ("Wireless Mouse", "Electronics", 29.99, 150),
        ("Mechanical Keyboard", "Electronics", 89.99, 80),
        ("Running Shoes", "Apparel", 59.99, 200),
        ("Cotton T-Shirt", "Apparel", 19.99, 500),
        ("Blender", "Home & Kitchen", 49.99, 60),
        ("Coffee Maker", "Home & Kitchen", 79.99, 40),
        ("Python Programming Book", "Books", 39.99, 120),
        ("Sci-Fi Novel", "Books", 14.99, 300),
        ("Yoga Mat", "Sports", 25.00, 150),
        ("Dumbbell Set", "Sports", 99.99, 30),
    ]

    product_ids = []
    for prod_name, cat, price, stock in product_data:
      db.cursor.execute(
          "INSERT INTO products (product_name, category, price, stock_quantity)"
          " VALUES (%s, %s, %s, %s) RETURNING product_id;",
          (prod_name, cat, price, stock),
      )
      product_ids.append((db.cursor.fetchone()[0], price))

    # 3. Insert Mock Orders & Order Items
    print("Generating orders and order items...")
    statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]

    for _ in range(200):
      user_id = random.choice(user_ids)
      order_date = datetime.now() - timedelta(days=random.randint(0, 180))
      status = random.choice(statuses)

      db.cursor.execute(
          "INSERT INTO orders (user_id, status, order_date) VALUES (%s,"
          " %s, %s) RETURNING order_id;",
          (user_id, status, order_date),
      )
      order_id = db.cursor.fetchone()[0]

      num_items = random.randint(1, 4)
      chosen_products = random.sample(product_ids, num_items)

      for prod_id, prod_price in chosen_products:
        qty = random.randint(1, 3)
        db.cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity,"
            " item_price) VALUES (%s, %s, %s, %s);",
            (order_id, prod_id, qty, prod_price),
        )

    # Commit changes through the connection managed by our class
    db.connection.commit()
    print("Data population completed successfully using OOP architecture!")

  except Exception as error:
    print(f"Error during population: {error}")
    if db.connection:
      db.connection.rollback()
  finally:
    # Safely close down using the class method
    db.close()


if __name__ == "__main__":
  populate_database()