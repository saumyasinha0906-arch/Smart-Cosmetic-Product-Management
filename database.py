import sqlite3
import pandas as pd

DATABASE_NAME = "cosmetic_products.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Product table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            brand TEXT NOT NULL,
            category TEXT,
            price REAL
        )
    """)

    # Review table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY,
            product_name TEXT,
            brand TEXT,
            category TEXT,
            rating INTEGER,
            review TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            aspects TEXT
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# PRODUCT FUNCTIONS
# --------------------------------------------------

def add_product(product_name, brand, category, price):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (product_name, brand, category, price)
        VALUES (?, ?, ?, ?)
    """, (
        product_name,
        brand,
        category,
        price
    ))

    connection.commit()
    connection.close()


def load_products():

    connection = get_connection()

    data = pd.read_sql_query(
        "SELECT * FROM products",
        connection
    )

    connection.close()

    return data


# --------------------------------------------------
# REVIEW FUNCTIONS
# --------------------------------------------------

def save_reviews(data):

    connection = get_connection()

    data.to_sql(
        "reviews",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()


def load_reviews():

    connection = get_connection()

    data = pd.read_sql_query(
        "SELECT * FROM reviews",
        connection
    )

    connection.close()

    return data