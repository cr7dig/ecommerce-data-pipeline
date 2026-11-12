import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

class DatabaseManager:
    
    def __init__(self):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.connection = None
        self.cursor = None

    def connect(self):
        # establishing a connection to the PostgreSQL database
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Successfully connected to the database using OOP!")
        except Exception as error:
            print(f"Connection error: {error}")

    def execute_query(self, query, params=None):
        """Method to safely execute queries using parameters."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully.")
        except Exception as error:
            self.connection.rollback()
            print(f"Query failed: {error}")

    def close(self):
        """Method to cleanly close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed safely.")

# --- Testing the Class ---
if __name__ == "__main__":
    # Create an object (instance) of our DatabaseManager class
    db = DatabaseManager()
    
    # Call methods on that object
    db.connect()
    db.close()