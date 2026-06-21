from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.database import execute_sql_file


SCHEMA_FILE = PROJECT_ROOT / "sql" / "001_create_full_schema.sql"


def main() -> None:
    execute_sql_file(SCHEMA_FILE)
    print(f"Applied schema file: {SCHEMA_FILE}")


if __name__ == "__main__":
    main()