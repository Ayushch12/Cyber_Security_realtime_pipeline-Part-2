
import json
import logging
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

from consumer.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    IDS_TOPIC,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_INDEX,
)

from core.logging_config import setup_logging

# logger = logging.getLogger("ids-consumer")

def main():
    setup_logging()
    logger = logging.getLogger("ids-consumer")

    logger.info("Starting Kafka consumer...")
    consumer = KafkaConsumer(
        IDS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # auto_offset_reset="earliest",
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="ids-group",
        #  api_version=(2, 5, 0),

    )
    # es = Elasticsearch(ELASTICSEARCH_URL)
    es = Elasticsearch(ELASTICSEARCH_URL)

    logger.info("Kafka consumer started. Waiting for IDS events...")

    for message in consumer:
        event = message.value

        try:
            es.index(index=ELASTICSEARCH_INDEX, document=event)

            logger.info(
                "Indexed event | src=%s dst=%s malicious=%s",
                event.get("source_ip"),
                event.get("destination_ip"),
                event.get("is_malicious"),
            )

        except Exception as e:
            logger.error("Failed to index event: %s", str(e))


if __name__ == "__main__":
    main()
