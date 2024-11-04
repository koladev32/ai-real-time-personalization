import datetime
import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS

from engine.redis_engine import get_user_profile_scores
from utils.collections import send_to_kafka
from utils.redis_client import get_redis_connection

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})
redis_conn = get_redis_connection()


# Utility functions
def get_db_connection():
    conn = sqlite3.connect("db/ecommerce.db")
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn


def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result


def insert_and_get_id(query, args=()):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# Category Endpoints
@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = query_db(
        "SELECT id, category_name FROM categories ORDER BY popularity DESC"
    )
    return jsonify([dict(row) for row in categories])


# Product Endpoints
@app.route("/api/products", methods=["GET"])
def get_products():
    params = get_product_query_params(request)
    products = query_db(params["query"], tuple(params["args"]))
    total_count = query_db(
        params["count_query"], tuple(params["count_args"]), one=True
    )["count"]

    return jsonify(
        {
            "products": [dict(row) for row in products],
            "total": total_count,
            "skip": params["skip"],
            "limit": params["limit"],
        }
    )


def get_product_query_params(request):
    # Helper function to generate query parameters for /api/products
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))
    sort_by = request.args.get("sortBy", "id")
    order = request.args.get("order", "asc").lower()
    select_fields = request.args.get("select", "*")
    category_id = request.args.get("category", None)
    search_query = request.args.get("search", None)

    base_query = f"SELECT {select_fields} FROM products"
    count_query = "SELECT COUNT(*) as count FROM products"
    conditions, args = [], []

    if search_query:
        conditions.append("(title LIKE ?)")
        args.append(f"%{search_query}%")
    if category_id:
        conditions.append("category_id = ?")
        args.append(category_id)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"{base_query}{where_clause} ORDER BY {sort_by} {order.upper()} LIMIT ? OFFSET ?"
    args.extend([limit, skip])

    return {
        "query": query,
        "count_query": f"{count_query}{where_clause}",
        "args": args,
        "count_args": args[:-2],
        "limit": limit,
        "skip": skip,
    }


@app.route("/api/products/search", methods=["GET"])
def search_products():
    search_query = request.args.get("q", "")
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))

    query = """
    SELECT * FROM products
    WHERE title LIKE ? OR description LIKE ?
    LIMIT ? OFFSET ?
    """
    search_results = query_db(
        query, (f"%{search_query}%", f"%{search_query}%", limit, skip)
    )

    return jsonify(
        {
            "products": [dict(row) for row in search_results],
            "total": len(search_results),
            "skip": skip,
            "limit": limit,
        }
    )


@app.route("/api/products/category/<category_slug>", methods=["GET"])
def get_products_by_category(category_slug):
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))

    query = """
    SELECT p.* FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE c.slug = ?
    LIMIT ? OFFSET ?
    """
    products = query_db(query, (category_slug, limit, skip))

    total_count = query_db(
        """
        SELECT COUNT(*) as count FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE c.slug = ?
        """,
        (category_slug,),
        one=True,
    )["count"]

    return jsonify(
        {
            "products": [dict(row) for row in products],
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }
    )


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if product:
        return jsonify(dict(product))
    return jsonify({"error": "Product not found"}), 404


# Cart Endpoints
@app.route("/api/cart", methods=["GET"])
def get_cart():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    cart, cart_id = get_or_create_cart(session_id)
    cart_items = query_db(
        """
        SELECT ci.product_id, ci.quantity, p.title, p.price, p.imageURL
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?
    """,
        (cart_id,),
    )

    return jsonify(
        {
            "cart_id": cart_id,
            "session_id": session_id,
            "items": [dict(item) for item in cart_items],
        }
    )


@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    session_id, product_id = data.get("session_id"), data.get("product_id")
    quantity = data.get("quantity", 1)

    if not session_id or not product_id:
        return jsonify({"error": "Session ID and Product ID are required"}), 400

    cart, cart_id = get_or_create_cart(session_id)
    update_or_insert_cart_item(cart_id, product_id, quantity)

    return jsonify({"status": "success", "message": "Item added to cart"}), 201


def get_or_create_cart(session_id):
    cart = query_db("SELECT * FROM cart WHERE session_id = ?", (session_id,), one=True)
    if not cart:
        cart_id = insert_and_get_id(
            "INSERT INTO cart (session_id) VALUES (?)", (session_id,)
        )
    else:
        cart_id = cart["id"]
    return cart, cart_id


def update_or_insert_cart_item(cart_id, product_id, quantity):
    existing_item = query_db(
        "SELECT * FROM cart_items WHERE cart_id = ? AND product_id = ?",
        (cart_id, product_id),
        one=True,
    )
    conn = get_db_connection()
    cur = conn.cursor()
    if existing_item:
        cur.execute(
            "UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND product_id = ?",
            (existing_item["quantity"] + quantity, cart_id, product_id),
        )
    else:
        cur.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
            (cart_id, product_id, quantity),
        )
    conn.commit()
    conn.close()


# Tracking and Profile Endpoints
@app.route("/api/track", methods=["POST"])
def track_event():
    data = request.get_json()
    if data.get("event_type") not in {
        "view_product",
        "click_category",
        "search",
        "add_to_cart",
        "purchase",
    }:
        return jsonify({"error": "Invalid event type"}), 400

    data["timestamp"] = data.get(
        "timestamp", datetime.datetime.now(datetime.UTC).isoformat()
    )
    send_to_kafka("user_interactions", data)

    return jsonify({"status": "success", "session_id": data["session_id"]}), 200


@app.route("/api/user_profile", methods=["GET"])
def get_user_profile():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    profile_data = get_user_profile_scores(session_id)
    if not profile_data:
        return jsonify({"error": "User profile not found"}), 404

    return jsonify(profile_data), 200


# Recommendations Endpoint
@app.route("/api/categories/top_products", methods=["GET"])
def get_top_categories_with_top_products():
    categories = query_db(
        """
        SELECT id, category_name
        FROM categories
        ORDER BY popularity DESC
        LIMIT 5
    """
    )

    categories_with_top_products = [
        {
            "id": category["id"],
            "category_name": category["category_name"],
            "products": [
                {
                    "id": product["id"],
                    "title": product["title"],
                    "imgUrl": product["imgUrl"],
                }
                for product in query_db(
                    "SELECT id, title, imgUrl FROM products WHERE category_id = ? ORDER BY stars DESC LIMIT 5",
                    (category["id"],),
                )
            ],
        }
        for category in categories
    ]

    return jsonify(categories_with_top_products)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
