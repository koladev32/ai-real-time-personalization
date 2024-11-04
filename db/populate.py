import csv
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()

# Create the categories table with a popularity field
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    popularity REAL DEFAULT 0
)
"""
)

# Create the products table matching the CSV structure
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    imgUrl TEXT,
    productURL TEXT,
    stars REAL,
    reviews INTEGER,
    price REAL,
    listPrice REAL,
    category_id INTEGER,
    isBestSeller BOOLEAN,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
"""
)

# Create the cart table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- UUID or session identifier for the user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for cart creation
)
"""
)

# Create the cart_items table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,           -- Foreign key to the cart
    product_id INTEGER NOT NULL,         -- Foreign key to the product being added to the cart
    quantity INTEGER DEFAULT 1,          -- Quantity of the product in the cart
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
)
"""
)

# Create the orders table to log purchases
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,  -- UUID or identifier for the user
    total_amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE
)
"""
)

# Load and insert categories from amazon_categories.csv
with open("amazon_categories.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category_name = row["category_name"]
        category_id = row["id"]
        cursor.execute(
            "INSERT OR IGNORE INTO categories (id, category_name) VALUES (?, ?)",
            (category_id, category_name),
        )

# Commit categories to retrieve their IDs
conn.commit()

# Map category names to IDs for easy lookup
cursor.execute("SELECT id, category_name FROM categories")
category_map = {name: category_id for category_id, name in cursor.fetchall()}

# Load and insert products from amazon_products.csv
with open("amazon_products.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        asin = row["asin"]
        title = row["title"]
        imgUrl = row["imgUrl"]
        productURL = row["productURL"]
        stars = float(row["stars"]) if row["stars"] else 0
        reviews = int(row["reviews"]) if row["reviews"] else 0
        price = float(row["price"]) if row["price"] else 0
        listPrice = float(row["listPrice"]) if row["listPrice"] else 0
        category_id = row["category_id"]
        isBestSeller = row["isBestSeller"].lower() == "true"

        # Insert product into the database
        cursor.execute(
            """
            INSERT INTO products (
                asin, title, imgUrl, productURL, stars, reviews, price,
                listPrice, category_id, isBestSeller
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asin,
                title,
                imgUrl,
                productURL,
                stars,
                reviews,
                price,
                listPrice,
                category_id,
                isBestSeller,
            ),
        )

# Commit all product inserts
conn.commit()

# Calculate and update popularity scores for each category based on the average rating
for category_id in category_map.values():
    # Calculate the average stars for rated products in each category
    cursor.execute(
        """
        SELECT AVG(stars) as popularity
        FROM products
        WHERE category_id = ? AND stars > 0
        """,
        (category_id,),
    )
    result = cursor.fetchone()
    popularity = result[0] if result[0] is not None else 0

    # Update the popularity score in the categories table
    cursor.execute(
        "UPDATE categories SET popularity = ? WHERE id = ?",
        (popularity, category_id),
    )

# Commit all changes and close the connection
conn.commit()
conn.close()

print(
    "Database setup complete with categories, products, and popularity scores imported successfully."
)
