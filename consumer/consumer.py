
# import json
# import logging
# from kafka import KafkaConsumer
# from elasticsearch import Elasticsearch
# from kafka.errors import NoBrokersAvailable
# import time

# from consumer.config import (
#     KAFKA_BOOTSTRAP_SERVERS,
#     IDS_TOPIC,
#     ELASTICSEARCH_URL,
#     ELASTICSEARCH_INDEX,
# )

# from core.logging_config import setup_logging

# # logger = logging.getLogger("ids-consumer")

# def main():
#     setup_logging()
#     logger = logging.getLogger("ids-consumer")

#     logger.info("Starting Kafka consumer...")
#     consumer = KafkaConsumer(
#         IDS_TOPIC,
#         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#         auto_offset_reset="earliest",
#         # auto_offset_reset="latest",
#         value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#         group_id="ids-group",
#         #  api_version=(2, 5, 0),

#     )
#     # es = Elasticsearch(ELASTICSEARCH_URL)
#     es = Elasticsearch(ELASTICSEARCH_URL)

#     logger.info("Kafka consumer started. Waiting for IDS events...")

#     for message in consumer:
#         event = message.value

#         try:
#             es.index(index=ELASTICSEARCH_INDEX, document=event)

#             logger.info(
#                 "Indexed event | src=%s dst=%s malicious=%s",
#                 event.get("source_ip"),
#                 event.get("destination_ip"),
#                 event.get("is_malicious"),
#             )

#         except Exception as e:
#             logger.error("Failed to index event: %s", str(e))


# if __name__ == "__main__":
#     main()


import json
import logging
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch

from consumer.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    IDS_TOPIC,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_INDEX,
)

from core.logging_config import setup_logging


def create_kafka_consumer(logger):
    """
    Retry until Kafka broker becomes available.
    """
    while True:
        try:
            logger.info("Connecting to Kafka at %s...", KAFKA_BOOTSTRAP_SERVERS)

            consumer = KafkaConsumer(
                IDS_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset="earliest",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="ids-group",
            )

            logger.info("Connected to Kafka successfully.")
            return consumer

        except NoBrokersAvailable:
            logger.warning("Kafka not available yet. Retrying in 5 seconds...")
            time.sleep(5)


def create_es_client(logger):
    """
    Retry until Elasticsearch becomes available.
    """
    while True:
        try:
            logger.info("Connecting to Elasticsearch at %s...", ELASTICSEARCH_URL)

            es = Elasticsearch(ELASTICSEARCH_URL)

            if es.ping():
                logger.info("Connected to Elasticsearch successfully.")
                return es

            logger.warning("Elasticsearch ping failed. Retrying in 5 seconds...")

        except Exception as e:
            logger.warning(
                "Elasticsearch not ready yet (%s). Retrying in 5 seconds...",
                str(e),
            )

        time.sleep(5)


def main():
    setup_logging()
    logger = logging.getLogger("ids-consumer")

    logger.info("Starting IDS Kafka consumer service...")

    # Wait for dependencies
    consumer = create_kafka_consumer(logger)
    es = create_es_client(logger)

    logger.info("Consumer started. Waiting for IDS events...")

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
            time.sleep(2)


if __name__ == "__main__":
    main()