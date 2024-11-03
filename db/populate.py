import sqlite3
import json
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()

# Create the categories table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
)
"""
)

# Create the products table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    price REAL NOT NULL,
    discountPercentage REAL,
    rating REAL,
    stock INTEGER,
    brand TEXT,
    sku TEXT,
    weight REAL,
    dimensions TEXT,
    warrantyInformation TEXT,
    shippingInformation TEXT,
    availabilityStatus TEXT,
    returnPolicy TEXT,
    minimumOrderQuantity INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    barcode TEXT,
    thumbnail TEXT,
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

# Load and insert categories from JSON
with open("categories.json") as f:
    categories = json.load(f)

for category in categories:
    slug = category.get("slug")
    name = category.get("name")
    cursor.execute(
        "INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)", (name, slug)
    )

# Commit the categories to get their IDs
conn.commit()

# Map category slugs to IDs for easy lookup
cursor.execute("SELECT id, slug FROM categories")
category_map = {slug: category_id for category_id, slug in cursor.fetchall()}

# Load and insert products from JSON
with open("products.json") as f:
    products_data = json.load(f)

for product in products_data["products"]:
    # Extract product fields
    title = product.get("title")
    description = product.get("description")
    price = product.get("price")
    discountPercentage = product.get("discountPercentage")
    rating = product.get("rating")
    stock = product.get("stock")
    brand = product.get("brand")
    sku = product.get("sku")
    weight = product.get("weight")

    # Dimensions as a single string
    dimensions = product.get("dimensions", {})
    dimensions_str = f"{dimensions.get('width', 0)}x{dimensions.get('height', 0)}x{dimensions.get('depth', 0)}"

    warrantyInformation = product.get("warrantyInformation")
    shippingInformation = product.get("shippingInformation")
    availabilityStatus = product.get("availabilityStatus")
    returnPolicy = product.get("returnPolicy")
    minimumOrderQuantity = product.get("minimumOrderQuantity")

    # Timestamps
    created_at = product.get("meta", {}).get("createdAt")
    updated_at = product.get("meta", {}).get("updatedAt")
    created_at = (
        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if created_at
        else None
    )
    updated_at = (
        datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if updated_at
        else None
    )

    # Barcode and thumbnail
    barcode = product.get("meta", {}).get("barcode")
    thumbnail = product.get("thumbnail")

    # Get the category ID from the category slug
    category_slug = product.get("category")
    category_id = category_map.get(category_slug)

    # Insert product into the database
    cursor.execute(
        """
    INSERT INTO products (
        title, description, category_id, price, discountPercentage, rating,
        stock, brand, sku, weight, dimensions, warrantyInformation,
        shippingInformation, availabilityStatus, returnPolicy,
        minimumOrderQuantity, created_at, updated_at, barcode, thumbnail
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            title,
            description,
            category_id,
            price,
            discountPercentage,
            rating,
            stock,
            brand,
            sku,
            weight,
            dimensions_str,
            warrantyInformation,
            shippingInformation,
            availabilityStatus,
            returnPolicy,
            minimumOrderQuantity,
            created_at,
            updated_at,
            barcode,
            thumbnail,
        ),
    )

# Commit all changes and close the connection
conn.commit()
conn.close()

print("Database setup complete with categories and products imported successfully.")
