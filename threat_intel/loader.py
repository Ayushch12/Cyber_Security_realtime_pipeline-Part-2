from pathlib import Path

def load_ipsum_feed(filepath: str) -> dict:
    """
    Load IPSum threat intelligence feed into memory.
    Returns: { ip -> confidence_score }
    """
    malicious_ips = {}

    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"IPSum file not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            ip, score = line.split()
            malicious_ips[ip] = int(score)

    return malicious_ips
