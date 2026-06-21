from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.ingestion.load_incidents import load_incidents_from_csv


DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "sample" / "ai_risk_evidence.csv"


def main() -> None:
    inserted_count = load_incidents_from_csv(DEFAULT_CSV_PATH)
    print(f"Loaded {inserted_count} incident evidence records from {DEFAULT_CSV_PATH}")


if __name__ == "__main__":
    main()