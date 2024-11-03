# kafka_cb_process_events.py
import json
from kafka import KafkaConsumer
from engine.cb_engine import process_event_batch
from engine.redis_engine import cache_user_profile_score, cache_recommendations, cache_recent_interactions, \
    get_recent_interactions


def process_events_with_cb():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        'user_interactions',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='cb_processing_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # Process events from Kafka using Contextual Bandit and cache in Redis
    for message in consumer:
        event = message.value
        session_id = event.get('session_id')

        # Cache the recent interaction
        cache_recent_interactions(session_id, event)

        # Process the last 10 events for recommendations
        recent_events = get_recent_interactions(session_id)
        score_data, recommendations = process_event_batch(recent_events)

        # Cache the profile score and recommendations in Redis
        cache_user_profile_score(session_id, score_data)
        cache_recommendations(session_id, recommendations)

        print(f"Processed and cached recommendations for session {session_id}.")
if __name__ == "__main__":
    process_events_with_cb()