# kafka_consumer.py
import json
import uuid
from datetime import datetime

from cassandra.cluster import Cluster
from kafka import KafkaConsumer


def consume_events():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        "user_interactions",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="personalization_group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    # Connect to Cassandra
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect("personalization")

    # Prepare the insert statement for Cassandra
    insert_query = session.prepare(
        """
        INSERT INTO user_events (session_id, event_type, product_id, category_id, search_query, timestamp, additional_context)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    )

    # Process events from Kafka and store them in Cassandra
    for message in consumer:
        event = message.value
        session_id = event.get("session_id")
        event_type = event.get("event_type")
        product_id = str(event.get("product_id"))
        category_id = str(event.get("category_id"))
        search_query = event.get("search_query")
        timestamp = datetime.strptime(
            event.get("timestamp").replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
        )
        additional_context = event.get("additional_context", {})

        # Insert into Cassandra
        session.execute(
            insert_query,
            (
                uuid.UUID(session_id),
                event_type,
                product_id,
                category_id,
                search_query,
                timestamp,
                additional_context,
            ),
        )

        print(f"Stored event for session {session_id}: {event_type} at {timestamp}")


if __name__ == "__main__":
    consume_events()
