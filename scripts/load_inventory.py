from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.ingestion.load_inventory import load_inventory_bundle


SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


def main() -> None:
    result = load_inventory_bundle(
        systems_csv_path=SAMPLE_DIR / "ai_system_inventory.csv",
        data_sources_csv_path=SAMPLE_DIR / "ai_data_sources.csv",
        evidence_mappings_csv_path=SAMPLE_DIR / "ai_risk_evidence_mappings.csv",
    )

    print("Loaded AI governance inventory bundle:")
    for key, value in result.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()