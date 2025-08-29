from studybuddy.app_configs import WEEKDAY_TO_INT

def hhmm_to_minutes(text: str) -> int:
    hours, minutes = map(int, text.split(":"))
    return hours * 60 + minutes

def minutes_to_hhmm(total: int) -> str:
    h, m = divmod(total, 60)
    return f"{h:02d}:{m:02d}"

def parse_range(text: str):
    """
    "Mon 13:00-15:30" -> (dow=0, start_min=780, end_min=930)
    """
    day_part, time_part = text.split(" ", 1)
    start_text, end_text = time_part.split("-", 1)
    dow = WEEKDAY_TO_INT[day_part.lower()[:3]]
    start_min = hhmm_to_minutes(start_text)
    end_min = hhmm_to_minutes(end_text)
    return dow, start_min, end_min