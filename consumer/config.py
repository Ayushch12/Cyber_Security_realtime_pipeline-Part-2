import os

# KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
# IDS_TOPIC = "ids-raw-logs"
# ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
# ELASTICSEARCH_INDEX = "ids-events"



KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
IDS_TOPIC = os.getenv("IDS_TOPIC", "ids-raw-logs")

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "ids-events")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")