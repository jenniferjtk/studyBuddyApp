from pathlib import Path

# creates a quick reference to the database file
DB_PATH = Path(__file__).resolve().parent / "studybuddy.db"

WEEKDAY_TO_INT = {"mon":0,"tue":1,"wed":2,"thu":3,"fri":4,"sat":5,"sun":6}
INT_TO_WEEKDAY = {v:k.capitalize() for k,v in WEEKDAY_TO_INT.items()}

MIN_MATCH_MINUTES = 30 #only counts overlap betwewen sessions as valid if its 
#at least 30 Min. So, a user can't book a session if their and the other person's
#schedule don't have at least 30 min of overlap