import datetime

from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

from utils.collections import send_to_kafka

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})


# Utility function to execute queries
def query_db(query, args=(), one=False):
    conn = sqlite3.connect("db/ecommerce.db")
    conn.row_factory = sqlite3.Row  # Enables column access by name
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


# Utility function to insert and retrieve last inserted ID
def insert_and_get_id(query, args=()):
    conn = sqlite3.connect("db/ecommerce.db")
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# Endpoint to list all categories
@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = query_db("SELECT id, name, slug FROM categories")
    return jsonify([dict(row) for row in categories])


# Endpoint to list all products with pagination, sorting, field selection, and search functionality
@app.route("/api/products", methods=["GET"])
def get_products():
    # Query parameters for pagination, sorting, field selection, category, and search
    limit = int(request.args.get("limit", 10))  # Default limit is 10
    skip = int(request.args.get("skip", 0))  # Default skip is 0
    sort_by = request.args.get("sortBy", "id")  # Default sort by 'id'
    order = request.args.get("order", "asc").lower()  # Default order is 'asc'
    select_fields = request.args.get("select", "*")  # Fields to select
    category_id = request.args.get("category", None)
    search_query = request.args.get("search", None)  # Search keyword

    # Validate order
    if order not in ["asc", "desc"]:
        return jsonify({"error": "Invalid order parameter. Use 'asc' or 'desc'."}), 400

    # Base query
    base_query = f"SELECT {select_fields} FROM products"
    count_query = "SELECT COUNT(*) as count FROM products"

    # Building conditions
    conditions = []
    params = []

    # Add search condition
    if search_query:
        conditions.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Add category filter condition
    if category_id:
        conditions.append("category_id = ?")
        params.append(category_id)

    # Combine conditions into WHERE clause if there are any
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
        base_query += where_clause
        count_query += where_clause

    # Add sorting and pagination to the main query
    base_query += f" ORDER BY {sort_by} {order.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    # Execute the main query to fetch products
    products = query_db(base_query, tuple(params))

    # Execute the count query to get the total count of products
    total_count = query_db(count_query, tuple(params[: len(params) - 2]), one=True)[
        "count"
    ]

    # Format the response
    response = {
        "products": [dict(row) for row in products],
        "total": total_count,
        "skip": skip,
        "limit": limit
        if limit != 0
        else total_count,  # If limit is 0, fetch all products
    }
    return jsonify(response)


# Endpoint to search for products by title or description
@app.route("/api/products/search", methods=["GET"])
def search_products():
    search_query = request.args.get("q", "")
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))

    # Build the search query
    query = """
    SELECT * FROM products
    WHERE title LIKE ? OR description LIKE ?
    LIMIT ? OFFSET ?
    """
    search_results = query_db(
        query, (f"%{search_query}%", f"%{search_query}%", limit, skip)
    )

    # Format the response
    response = {
        "products": [dict(row) for row in search_results],
        "total": len(search_results),
        "skip": skip,
        "limit": limit,
    }
    return jsonify(response)


# Endpoint to get products by category
@app.route("/api/products/category/<category_slug>", methods=["GET"])
def get_products_by_category(category_slug):
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))

    # Query to get products by category
    query = """
    SELECT p.* FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE c.slug = ?
    LIMIT ? OFFSET ?
    """
    products = query_db(query, (category_slug, limit, skip))

    # Get total count of products in the category
    count_query = """
    SELECT COUNT(*) as count FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE c.slug = ?
    """
    total_count = query_db(count_query, (category_slug,), one=True)["count"]

    # Format the response
    response = {
        "products": [dict(row) for row in products],
        "total": total_count,
        "skip": skip,
        "limit": limit,
    }
    return jsonify(response)


# Endpoint to fetch a single product by ID
@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if product:
        return jsonify(dict(product))
    else:
        return jsonify({"error": "Product not found"}), 404


################################################################################
# Cart Endpoints
################################################################################


# Endpoint to retrieve the cart with items for a specific session
@app.route("/api/cart", methods=["GET"])
def get_cart():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    # Retrieve the cart ID based on session_id
    cart = query_db("SELECT * FROM cart WHERE session_id = ?", (session_id,), one=True)
    if not cart:
        return jsonify({"cart": [], "message": "Cart is empty"}), 200

    cart_id = cart["id"]

    # Retrieve all items in the cart
    cart_items = query_db(
        """
        SELECT ci.product_id, ci.quantity, p.title, p.price, p.thumbnail
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?
    """,
        (cart_id,),
    )

    # Format response
    response = {
        "cart_id": cart_id,
        "session_id": session_id,
        "items": [dict(item) for item in cart_items],
    }
    return jsonify(response)


# Endpoint to add items to the cart
@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    session_id = data.get("session_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not session_id or not product_id:
        return jsonify({"error": "Session ID and Product ID are required"}), 400

    # Check if a cart exists for this session_id
    cart = query_db("SELECT * FROM cart WHERE session_id = ?", (session_id,), one=True)
    if not cart:
        # Create a new cart for this session_id if it doesn't exist
        cart_id = insert_and_get_id(
            "INSERT INTO cart (session_id) VALUES (?)", (session_id,)
        )
    else:
        cart_id = cart["id"]

    # Check if the product is already in the cart
    existing_item = query_db(
        "SELECT * FROM cart_items WHERE cart_id = ? AND product_id = ?",
        (cart_id, product_id),
        one=True,
    )
    if existing_item:
        # Update quantity if the product is already in the cart
        new_quantity = existing_item["quantity"] + quantity
        conn = sqlite3.connect("db/ecommerce.db")
        cur = conn.cursor()
        cur.execute(
            "UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND product_id = ?",
            (new_quantity, cart_id, product_id),
        )
        conn.commit()
        conn.close()
    else:
        # Add the new item to the cart
        insert_and_get_id(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
            (cart_id, product_id, quantity),
        )

    return jsonify({"status": "success", "message": "Item added to cart"}), 201


# Endpoint to track user interactions
@app.route("/api/track", methods=["POST"])
def track_event():
    data = request.get_json()

    # Validate event type
    valid_event_types = {
        "view_product",
        "click_category",
        "search",
        "add_to_cart",
        "purchase",
    }
    event_type = data.get("event_type")

    if event_type not in valid_event_types:
        return jsonify({"error": "Invalid event type"}), 400

    # Validate session_id
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    # Add timestamp if not provided
    if "timestamp" not in data:
        data["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()

    # Send to Kafka
    topic = "user_interactions"
    send_to_kafka(topic, data)

    return jsonify({"status": "success", "session_id": data['session_id']}), 200


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
