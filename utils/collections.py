import json

from kafka import KafkaProducer

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


# Utility function to send events to Kafka
def send_to_kafka(topic, data):
    producer.send(topic, value=data)
    producer.flush()
