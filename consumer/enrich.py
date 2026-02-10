from datetime import datetime


def parse_ids_log_line(line: str) -> dict:
    """
    Parse a single IDS log line into a structured dictionary.
    """

    parts = line.strip().split(" - ")

    timestamp_str = parts[0]
    logger = parts[1]
    severity = parts[2]
    protocol = parts[3]
    connection = parts[4]
    tcp_flag = parts[5]
    attack_type = parts[6]

    # Parse timestamp
    timestamp = datetime.strptime(
        timestamp_str, "%Y-%m-%d %H:%M:%S,%f"
    ).isoformat()

    # Parse connection: src_ip:port --> dst_ip:port
    src, dst = connection.split(" --> ")

    source_ip, source_port = src.split(":")
    destination_ip, destination_port = dst.split(":")

    return {
        "@timestamp": timestamp,
        "log_type": "ids",
        "severity": severity,
        "protocol": protocol,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "attack_type": attack_type,
    }
