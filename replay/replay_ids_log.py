from pathlib import Path
import json
import time
import os
from datetime import datetime
from kafka import KafkaProducer
import logging

from consumer.enrich import parse_ids_log_line, enrich_with_threat_intel
from threat_intel.loader import load_ipsum_feed
from core.logging_config import setup_logging
from datetime import datetime, timezone


KAFKA_TOPIC = "ids-raw-logs"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

setup_logging()
logger = logging.getLogger("ids-producer")


def tail_ids_log(log_path: Path, ipsum_path: Path):
    threat_feed = load_ipsum_feed(ipsum_path)

    if not log_path.exists():
        raise FileNotFoundError(f"IDS log not found: {log_path.resolve()}")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 5, 0),
    )

    logger.info("Tailing IDS log. Waiting for new events...")

    last_position = 0

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
                            # event["@timestamp"] = datetime.utcnow().isoformat()
                            event["@timestamp"] = datetime.now(timezone.utc).isoformat()

                            producer.send(KAFKA_TOPIC, value=event)

                            logger.info(
                                "Event sent | src=%s dst=%s malicious=%s confidence=%s",
                                event["source_ip"],
                                event["destination_ip"],
                                event["is_malicious"],
                                event["confidence"],
                            )

                        except Exception as e:
                            logger.error("Error processing line: %s", str(e))

                    last_position = f.tell()

            time.sleep(1)

        except Exception as e:
            logger.error("Tail loop failure: %s", str(e))
            time.sleep(2)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]

    tail_ids_log(
        log_path=project_root / "sample_logs" / "ids.log",
        ipsum_path=project_root / "threat_intel" / "data" / "ipsum.txt",
    )
