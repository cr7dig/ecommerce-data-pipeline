import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker
import psycopg2

#loading dotenv to access environment variables
load_dotenv()

# Initializing Faker for generating realistic mock data
fake = Faker()

# Database Connection Parameters
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def populate_database():
  try:
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    print("Successfully connected to PostgreSQL database!")

    # 1. Inserting Mock Users (50 users)
    print("Generating users...")
    user_ids = []
    for _ in range(50):
      name = fake.name()
      email = fake.unique.email()
      address = fake.address().replace("\n", ", ")
      cursor.execute(
          "INSERT INTO users (name, email, address) VALUES (%s, %s, %s) RETURNING"
          " user_id;",
          (name, email, address),
      )
      user_ids.append(cursor.fetchone()[0])

    # 2. Inserting Mock Products (20 products)
    print("Generating products...")
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Sports"]
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
      cursor.execute(
          "INSERT INTO products (product_name, category, price, stock_quantity)"
          " VALUES (%s, %s, %s, %s) RETURNING product_id;",
          (prod_name, cat, price, stock),
      )
      product_ids.append((cursor.fetchone()[0], price))

    # 3. Inserting Mock Orders & Order Items (Spread across the last 6 months)
    print("Generating orders and order items...")
    statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]

    for _ in range(200):  # Generating 200 orders
      user_id = random.choice(user_ids)
      # Random date within the last 180 days
      order_date = datetime.now() - timedelta(days=random.randint(0, 180))
      status = random.choice(statuses)

      cursor.execute(
          "INSERT INTO orders (user_id, status, order_date) VALUES (%s,"
          " %s, %s) RETURNING order_id;",
          (user_id, status, order_date),
      )
      
      order_id = cursor.fetchone()[0]

      # Adding 1 to 4 items per order
      num_items = random.randint(1, 4)
      chosen_products = random.sample(product_ids, num_items)

      for prod_id, prod_price in chosen_products:
        qty = random.randint(1, 3)
        # item_price locks in the price at time of order
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity,"
            " item_price) VALUES (%s, %s, %s, %s);",
            (order_id, prod_id, qty, prod_price),
        )

    # Commit changes to the database
    connection.commit()
    print("Data population completed successfully!")

  except Exception as error:
    print(f"Error while connecting to PostgreSQL: {error}")
  finally:
    if connection:
      cursor.close()
      connection.close()
      print("PostgreSQL connection is closed.")


if __name__ == "__main__":
  populate_database()