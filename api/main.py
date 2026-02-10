from fastapi import FastAPI
from pathlib import Path

from api.schemas import IDSLogRequest
from consumer.enrich import parse_ids_log_line, enrich_with_threat_intel
from threat_intel.loader import load_ipsum_feed

app = FastAPI(title="IDS Ingestion API")

# Load threat intel once at startup
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IPSUM_PATH = PROJECT_ROOT / "threat_intel" / "data" / "ipsum.txt"

THREAT_FEED = load_ipsum_feed(IPSUM_PATH)


@app.post("/ingest/ids")
def ingest_ids_log(request: IDSLogRequest):
    event = parse_ids_log_line(request.log_line)
    event = enrich_with_threat_intel(event, THREAT_FEED)
    return event
