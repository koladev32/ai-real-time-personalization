import json
from utils.redis_client import get_redis_connection

redis_conn = get_redis_connection()

def cache_user_profile_score(session_id, score_data):
    """Caches the score for a user profile in Redis."""
    # Convert dictionary to JSON string before storing
    redis_conn.hmset(f"user:{session_id}:score", {k: str(v) for k, v in score_data.items()})

def get_user_profile_score(session_id):
    """Fetches the cached score for a user profile."""
    score_data = redis_conn.hgetall(f"user:{session_id}:score")
    # Convert values back to their original type if needed
    return {k.decode('utf-8'): float(v) for k, v in score_data.items()}

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
    redis_conn.ltrim(f"user:{session_id}:recent_interactions", 0, 9)  # Keep only last 10 interactions


def get_recent_interactions(session_id):
    interactions = redis_conn.lrange(f"user:{session_id}:recent_interactions", 0, -1)
    return [json.loads(event) for event in interactions]