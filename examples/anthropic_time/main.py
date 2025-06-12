from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional
from fastapi import HTTPException

async def handler(params: dict) -> dict:
    """
    Returns the current time in the specified timezone.
    
    params:
      timezone: str (optional) - IANA-compliant timezone name. Defaults to UTC.
    """
    try:
        tz_name = params.get("timezone") or "UTC"
        
        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timezone: '{tz_name}'. Please use a valid IANA timezone identifier (e.g. 'America/New_York', 'UTC', 'Europe/London')."
            )
        
        now = datetime.now(tz)
        
        return {
            "iso_8601": now.isoformat(),
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "timezone": str(tz)
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Local debug
if __name__ == "__main__":
    # Test with default timezone (UTC)
    print(handler({}))
    # Test with a specific timezone
    print(handler({"timezone": "America/New_York"})) 