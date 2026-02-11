
from pathlib import Path
import json
import time
from kafka import KafkaProducer

from consumer.enrich import parse_ids_log_line, enrich_with_threat_intel
from threat_intel.loader import load_ipsum_feed


KAFKA_TOPIC = "ids-raw-logs"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"


def replay_ids_log(log_path: Path, ipsum_path: Path):
    threat_feed = load_ipsum_feed(ipsum_path)

    if not log_path.exists():
        raise FileNotFoundError(f"IDS log not found: {log_path.resolve()}")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 5, 0),
    )

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            event = parse_ids_log_line(line)
            event = enrich_with_threat_intel(event, threat_feed)

            producer.send(KAFKA_TOPIC, value=event)
            print("Sent to Kafka:", event)

            time.sleep(0.05)

    producer.flush()
    print("Replay finished.")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]

    replay_ids_log(
        log_path=project_root / "sample_logs" / "ids.log",
        ipsum_path=project_root / "threat_intel" / "data" / "ipsum.txt",
    )
