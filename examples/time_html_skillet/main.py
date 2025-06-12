from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def handler(params: dict) -> dict:
    """
    Returns the current time in the specified timezone.
    
    params:
      timezone: str (optional) - IANA-compliant timezone name. Defaults to UTC.
    """
    tz_name = params.get("timezone") or "UTC"

    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        # This is a simplified error handling.
        # In a real skill, you might return a specific error object or status.
        raise ValueError(f"Invalid timezone: '{tz_name}'")

    now = datetime.now(tz)

    return {
        "iso_8601": now.isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "timezone": str(tz),
    }

# Local debug
if __name__ == "__main__":
    # Test with default timezone (UTC)
    print(handler({}))
    # Test with a specific timezone
    print(handler({"timezone": "America/New_York"})) 