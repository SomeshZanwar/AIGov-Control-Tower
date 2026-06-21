from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aigov.policy.evaluator import (
    run_policy_evaluation,
    strongest_decision_for_system,
)


POLICY_FILE = PROJECT_ROOT / "policies" / "ai_governance_policies.yml"


def main() -> None:
    decisions = run_policy_evaluation(POLICY_FILE)
    strongest = strongest_decision_for_system(decisions)

    print("AI governance policy evaluation complete:")
    for system_key, decision in sorted(strongest.items()):
        print(
            f"- {system_key} | {decision.system_name} | "
            f"{decision.decision} | {decision.policy_name}"
        )

    print(f"Total policy matches: {len(decisions)}")


if __name__ == "__main__":
    main()