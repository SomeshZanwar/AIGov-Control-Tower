from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.reports.audit_report import generate_all_audit_reports


OUTPUT_DIR = PROJECT_ROOT / "docs" / "audit_reports"


def main() -> None:
    output_paths = generate_all_audit_reports(OUTPUT_DIR)

    print("Generated AI governance audit reports:")
    for path in output_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()