
from pathlib import Path
import json
import time
import os
import logging
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from consumer.enrich import parse_ids_log_line, enrich_with_threat_intel
from threat_intel.loader import load_ipsum_feed
from core.logging_config import setup_logging


# Environment-based configuration
KAFKA_TOPIC = os.getenv("IDS_TOPIC", "ids-raw-logs")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
LOG_PATH = os.getenv("LOG_PATH", "sample_logs/ids.log")
IPSUM_URL = os.getenv(
    "IPSUM_URL",
    "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt",
)


def create_kafka_producer(logger):
    """
    Retry until Kafka broker becomes available.
    """
    producer = None

    while True:
        try:
            logger.info("Connecting to Kafka at %s...", KAFKA_BOOTSTRAP_SERVERS)

            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

            logger.info("Connected to Kafka successfully.")
            break

        except NoBrokersAvailable:
            logger.warning("Kafka not available yet. Retrying in 5 seconds...")
            time.sleep(5)

    return producer


def tail_ids_log(log_path: Path):

    logger = logging.getLogger("ids-producer")

    # Load live IPSum feed
    threat_feed = load_ipsum_feed(IPSUM_URL)

    if not log_path.exists():
        raise FileNotFoundError(f"IDS log not found: {log_path.resolve()}")

    producer = create_kafka_producer(logger)

    logger.info("Tailing IDS log. Waiting for new events...")

    last_position = 0
    total_sent = 0

    try:
        while True:
            try:
                current_size = os.path.getsize(log_path)

                # Handle file rewrite
                if current_size < last_position:
                    logger.warning("Log file was rewritten. Resetting cursor.")
                    last_position = 0

                if current_size > last_position:
                    with open(log_path, "r", encoding="utf-8") as f:
                        f.seek(last_position)

                        for line in f:
                            line = line.strip()
                            if not line:
                                continue

                            try:
                                event = parse_ids_log_line(line)
                                event = enrich_with_threat_intel(event, threat_feed)
                                event["@timestamp"] = datetime.now(
                                    timezone.utc
                                ).isoformat()

                                producer.send(KAFKA_TOPIC, value=event)

                                total_sent += 1

                                if total_sent % 50 == 0:
                                    logger.info(
                                        "Sent %s events to Kafka", total_sent
                                    )

                            except Exception as e:
                                logger.error(
                                    "Error processing line: %s", str(e)
                                )

                        last_position = f.tell()

                time.sleep(1)

            except Exception as e:
                logger.error("Tail loop failure: %s", str(e))
                time.sleep(2)

    except KeyboardInterrupt:
        logger.info("Shutting down replay service...")

    finally:
        producer.close()
        logger.info("Kafka producer closed.")


if __name__ == "__main__":
    setup_logging()

    project_root = Path(__file__).resolve().parents[1]

    tail_ids_log(
        log_path=project_root / LOG_PATH,
    )
