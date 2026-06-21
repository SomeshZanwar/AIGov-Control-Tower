from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.evidence.review_scheduler import run_review_scheduling


def main() -> None:
    workflows, schedules = run_review_scheduling()

    print("Human review workflow scheduling complete:")
    for workflow in workflows:
        print(
            f"- {workflow.system_key} | {workflow.system_name} | "
            f"{workflow.review_status} | due={workflow.due_date.date()}"
        )

    print(f"Total human review workflows: {len(workflows)}")
    print(f"Total reassessment schedules: {len(schedules)}")


if __name__ == "__main__":
    main()