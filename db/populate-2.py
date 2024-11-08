import re
import sqlite3
import json
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()


def is_image_url_valid(url):
    """
    Check if a URL is well-formed and appears to point to an image file.
    """
    # Regular expression for basic URL structure
    url_pattern = re.compile(
        r"^(https?://)"  # Starts with http:// or https://
        r"([A-Za-z0-9.-]+)"  # Domain name
        r"(\.[A-Za-z]{2,6})"  # Top-level domain (e.g., .com, .net)
        r"(/[A-Za-z0-9._~:/?#@!$&\'()*+,;=-]*)*"  # Path and query params
        r"\.(jpg|jpeg|png|gif|webp)$",  # Valid image extensions
        re.IGNORECASE,
    )

    # Match the URL pattern and check for valid image extensions
    return bool(url_pattern.match(url))


# Load new product data from JSON file
with open("new_products.json") as f:
    new_products = json.load(f)

# Insert categories and products into the existing tables
for product in new_products:
    # Extract category information and insert into categories table if not already present
    if "new" in product.get("title").lower():
        continue
    if "new" in product.get("category", {}).get("name").lower():
        continue

    if (
        "products.com" in product.get("images", [None])[0]
        or "example.com" in product.get("images", [None])[0]
        or "placeimg" in product.get("images", [None])[0]
    ):
        continue

    category_data = product.get("category", {})
    category_name = category_data.get("name")
    if category_name:
        category_slug = category_name.lower().replace(" ", "-")
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)",
            (category_name, category_slug),
        )

    # Retrieve category_id for the product (assuming category exists now)
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_row = cursor.fetchone()
    category_id = category_row[0] if category_row else None

    # Extract product information
    title = product.get("title")
    description = product.get("description", None)
    price = product.get("price", None)
    created_at = (
        datetime.fromisoformat(product.get("creationAt", "").replace("Z", "+00:00"))
        if product.get("creationAt")
        else None
    )
    updated_at = (
        datetime.fromisoformat(product.get("updatedAt", "").replace("Z", "+00:00"))
        if product.get("updatedAt")
        else None
    )
    thumbnail = product.get("images", [None])[
        0
    ]  # Use the first image as the thumbnail if available
    if is_image_url_valid(thumbnail):
        thumbnail = thumbnail
    else:
        thumbnail = None

    # Insert product into the database, using only existing fields and ignoring others
    cursor.execute(
        """
    INSERT INTO products (
        title, description, category_id, price, created_at, updated_at, thumbnail
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (title, description, category_id, price, created_at, updated_at, thumbnail),
    )

# Commit all changes and close the connection
conn.commit()
conn.close()

print("Data imported successfully into the existing tables.")
