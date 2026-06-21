from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.evidence.document_checker import (
    calculate_document_summary,
    run_document_completeness_check,
)


def main() -> None:
    documents = run_document_completeness_check()
    summary = calculate_document_summary(documents)

    print("Documentation completeness check complete:")
    for system_key, values in sorted(summary.items()):
        print(
            f"- {system_key} | completed={values['completed']}/"
            f"{values['required']} | rate={values['completion_rate']}"
        )

    print(f"Total required document records: {len(documents)}")


if __name__ == "__main__":
    main()