import redis

def get_redis_connection():
    return redis.Redis(
        host='localhost',  # or your Redis host
        port=6379,         # Redis default port
        db=0,              # Redis default database
        decode_responses=True  # Ensures responses are in a readable format
    )