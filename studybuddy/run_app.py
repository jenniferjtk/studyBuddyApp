from pathlib import Path
from studybuddy.app_configs import DB_PATH
from studybuddy.database.sql_storage import Storage
from studybuddy.application.services import StudyBuddyService
from studybuddy.application.cli.menu import handle_choice

def main():
    # init db (first run creates tables)
    db = Storage(DB_PATH)
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    db.execute_script(schema)

    svc = StudyBuddyService(db)
    handle_choice(svc)

if __name__ == "__main__":
    main()