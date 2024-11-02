from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Utility function to execute queries
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('db/ecommerce.db')
    conn.row_factory = sqlite3.Row  # Enables column access by name
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Endpoint to list all categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = query_db("SELECT id, name, slug FROM categories")
    return jsonify([dict(row) for row in categories])

# Endpoint to list all products with pagination, sorting, and field selection
@app.route('/api/products', methods=['GET'])
def get_products():
    # Query parameters for pagination, sorting, and field selection
    limit = int(request.args.get('limit', 10))  # Default limit is 10
    skip = int(request.args.get('skip', 0))  # Default skip is 0
    sort_by = request.args.get('sortBy', 'id')  # Default sort by id
    order = request.args.get('order', 'asc').lower()  # Default order is ascending
    select_fields = request.args.get('select', '*')  # Fields to select

    # Validate order
    if order not in ['asc', 'desc']:
        return jsonify({"error": "Invalid order parameter. Use 'asc' or 'desc'."}), 400

    # Build the query
    query = f"SELECT {select_fields} FROM products ORDER BY {sort_by} {order.upper()} LIMIT ? OFFSET ?"
    products = query_db(query, (limit, skip))

    # Get total count of products for pagination info
    total_count = query_db("SELECT COUNT(*) as count FROM products", one=True)['count']

    # Format the response
    response = {
        "products": [dict(row) for row in products],
        "total": total_count,
        "skip": skip,
        "limit": limit if limit != 0 else total_count  # If limit is 0, fetch all products
    }
    return jsonify(response)

# Endpoint to search for products by title or description
@app.route('/api/products/search', methods=['GET'])
def search_products():
    search_query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    skip = int(request.args.get('skip', 0))

    # Build the search query
    query = """
    SELECT * FROM products
    WHERE title LIKE ? OR description LIKE ?
    LIMIT ? OFFSET ?
    """
    search_results = query_db(query, (f'%{search_query}%', f'%{search_query}%', limit, skip))

    # Format the response
    response = {
        "products": [dict(row) for row in search_results],
        "total": len(search_results),
        "skip": skip,
        "limit": limit
    }
    return jsonify(response)

# Endpoint to get products by category
@app.route('/api/products/category/<category_slug>', methods=['GET'])
def get_products_by_category(category_slug):
    limit = int(request.args.get('limit', 10))
    skip = int(request.args.get('skip', 0))

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
    total_count = query_db(count_query, (category_slug,), one=True)['count']

    # Format the response
    response = {
        "products": [dict(row) for row in products],
        "total": total_count,
        "skip": skip,
        "limit": limit
    }
    return jsonify(response)

# Endpoint to fetch a single product by ID
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if product:
        return jsonify(dict(product))
    else:
        return jsonify({"error": "Product not found"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)