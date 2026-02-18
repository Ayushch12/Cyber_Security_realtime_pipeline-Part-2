

# from pathlib import Path

# def load_ipsum_feed(filepath: str) -> dict:
#     """
#     Load IPSum threat intelligence feed into memory.
#     Returns: { ip -> confidence_score }
#     """
#     malicious_ips = {}

#     path = Path(filepath)

#     if not path.exists():
#         raise FileNotFoundError(f"IPSum file not found: {path.resolve()}")

#     with path.open("r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("#"):
#                 continue

#             ip, score = line.split()
#             malicious_ips[ip] = int(score)

#     return malicious_ips


import requests
import logging

logger = logging.getLogger("ipsum-loader")


def load_ipsum_feed(source: str) -> dict:
    """
    Load IPSum threat intelligence feed dynamically.
    'source' should be a URL.
    Returns: { ip -> confidence_score }
    """

    malicious_ips = {}

    logger.info("Downloading IPSum feed from %s", source)

    try:
        response = requests.get(source, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Failed to download IPSum feed: %s", str(e))
        raise

    for line in response.text.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        try:
            ip, score = line.split()
            malicious_ips[ip] = int(score)
        except ValueError:
            continue

    logger.info("Loaded %d malicious IPs from IPSum", len(malicious_ips))

    return malicious_ips

