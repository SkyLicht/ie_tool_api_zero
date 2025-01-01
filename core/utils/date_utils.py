from datetime import datetime

def get_iso_week_number(date_str: str) -> int:
    """Return the ISO week number for a given date in YYYY-MM-DD format."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    # isocalendar() returns a tuple (iso_year, iso_week_number, iso_weekday)

    _, iso_week_num, _ = date_obj.isocalendar()
    return iso_week_num