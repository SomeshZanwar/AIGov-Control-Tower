from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.risk.scorer import run_risk_scoring


def main() -> None:
    risk_scores = run_risk_scoring()

    print("AI system risk scoring complete:")
    for score in risk_scores:
        print(
            f"- {score.system_key} | {score.system_name} | "
            f"score={score.risk_score} | tier={score.risk_tier}"
        )


if __name__ == "__main__":
    main()