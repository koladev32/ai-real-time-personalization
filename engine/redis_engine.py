import json
from utils.redis_client import get_redis_connection

redis_conn = get_redis_connection()


def format_score_data_for_profile(score_data):
    """
    Transforms the score_data dictionary into the affinities format for caching as a user profile.
    Each product ID in score_data will be stored as an affinity with id, value, and score.
    """
    affinities = []

    # Assuming we have a function to get product names from the database
    for product_id, score in score_data.items():
        affinities.append({"id": product_id, "score": score})

    return {"affinities": affinities}


def cache_user_profile(session_id, score_data):
    """Caches the structured profile for a user in Redis."""
    profile_key = f"user:{session_id}:profile"
    formatted_profile = format_score_data_for_profile(score_data)
    redis_conn.set(profile_key, json.dumps(formatted_profile))


def get_user_profile_scores(session_id):
    """Retrieves and deserializes the cached profile for a user session."""
    profile_data = redis_conn.get(f"user:{session_id}:profile")
    return json.loads(profile_data) if profile_data else {}


def cache_recommendations(session_id, recommendations):
    """Caches recommended products for a user session."""
    # Serialize list as JSON before storing
    redis_conn.set(f"user:{session_id}:recommendations", json.dumps(recommendations))


def get_recommendations(session_id):
    """Retrieves cached recommendations for a user session."""
    recommendations = redis_conn.get(f"user:{session_id}:recommendations")
    # Deserialize JSON string back to list
    return json.loads(recommendations) if recommendations else []


def cache_categories_order(session_id, category_order):
    """Caches the category display order for a user session based on preferences."""
    # Serialize list as JSON before storing
    redis_conn.set(f"user:{session_id}:category_order", json.dumps(category_order))


def get_categories_order(session_id):
    """Retrieves the cached category order for a user session."""
    category_order = redis_conn.get(f"user:{session_id}:category_order")
    # Deserialize JSON string back to list
    return json.loads(category_order) if category_order else []


# In the Redis engine
def cache_recent_interactions(session_id, event):
    redis_conn.lpush(f"user:{session_id}:recent_interactions", json.dumps(event))
    redis_conn.ltrim(
        f"user:{session_id}:recent_interactions", 0, 9
    )  # Keep only last 10 interactions


def get_recent_interactions(session_id):
    interactions = redis_conn.lrange(f"user:{session_id}:recent_interactions", 0, 9)
    return [json.loads(event) for event in interactions]


def cache_last_processed_timestamp(session_id, timestamp):
    """Cache the last processed timestamp for a user's session."""
    redis_conn.set(f"user:{session_id}:last_processed_timestamp", timestamp)


def get_last_processed_timestamp(session_id):
    """Get the last processed timestamp for a user's session."""
    return redis_conn.get(f"user:{session_id}:last_processed_timestamp")
