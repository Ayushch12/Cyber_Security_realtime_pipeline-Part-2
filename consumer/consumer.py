import json
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

from consumer.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    IDS_TOPIC,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_INDEX,
)
def main():
    consumer = KafkaConsumer(
        IDS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="ids-group",
         api_version=(2, 5, 0),

    )

    es = Elasticsearch(ELASTICSEARCH_URL)

    print("Kafka consumer started. Waiting for IDS events...")

    for message in consumer:
        event = message.value
        es.index(index=ELASTICSEARCH_INDEX, document=event)
        print("Indexed event:", event)


if __name__ == "__main__":
    main()
