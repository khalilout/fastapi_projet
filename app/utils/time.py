from datetime import datetime, timezone


def maintenant_utc() -> datetime:
    return datetime.now(timezone.utc)