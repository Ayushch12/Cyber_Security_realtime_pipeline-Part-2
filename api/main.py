from fastapi import FastAPI
from pathlib import Path
import json
from kafka import KafkaProducer

from api.schemas import IDSLogRequest
from api.config import KAFKA_BOOTSTRAP_SERVERS, IDS_TOPIC
from consumer.enrich import parse_ids_log_line, enrich_with_threat_intel
from threat_intel.loader import load_ipsum_feed

app = FastAPI(title="IDS Ingestion API")

# All the Load threat intel is here
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IPSUM_PATH = PROJECT_ROOT / "threat_intel" / "data" / "ipsum.txt"

THREAT_FEED = load_ipsum_feed(IPSUM_PATH)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.post("/ingest/ids")
def ingest_ids_log(request: IDSLogRequest):
    event = parse_ids_log_line(request.log_line)
    event = enrich_with_threat_intel(event, THREAT_FEED)

    producer.send(IDS_TOPIC, value=event)

    return {"status": "sent to kafka"}
