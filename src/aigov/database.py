from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.aigov.config import get_database_config


def get_engine() -> Engine:
    config = get_database_config()
    return create_engine(config.sqlalchemy_url, future=True)


def execute_sql_file(sql_file_path: str | Path) -> None:
    path = Path(sql_file_path)

    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    sql_text = path.read_text(encoding="utf-8")

    if not sql_text.strip():
        raise ValueError(f"SQL file is empty: {path}")

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text(sql_text))