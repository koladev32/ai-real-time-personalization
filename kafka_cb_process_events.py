# kafka_cb_process_events.py
import json
from datetime import datetime

from kafka import KafkaConsumer
from engine.cb_engine import RecommendationEngine
from engine.redis_engine import (
    cache_user_profile,
    cache_recommendations,
    cache_recent_interactions,
    get_recent_interactions,
    cache_last_processed_timestamp,
    get_last_processed_timestamp,
)


def process_events_with_cb():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        "user_interactions",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="cb_processing_group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    # Process events from Kafka using Contextual Bandit and cache in Redis
    for message in consumer:
        event = message.value
        session_id = event.get("session_id")
        event_timestamp = datetime.strptime(
            event.get("timestamp").replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
        )
        # Retrieve the last processed timestamp for this session
        last_processed_timestamp = get_last_processed_timestamp(session_id)

        # Check if the event is new
        if last_processed_timestamp and event_timestamp <= datetime.strptime(
            last_processed_timestamp.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
        ):
            continue  # Skip this event as it's already processed

        # Cache the recent interaction and last processed timestamp
        cache_recent_interactions(session_id, event)
        cache_last_processed_timestamp(session_id, event.get("timestamp"))

        # Process only new events for recommendations
        recent_events = get_recent_interactions(session_id)

        score_data, recommendations = RecommendationEngine().process_event_batch(
            recent_events
        )

        # Cache the updated profile score in Redis
        cache_user_profile(session_id, score_data)


if __name__ == "__main__":
    process_events_with_cb()
