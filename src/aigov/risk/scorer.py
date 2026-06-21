from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from src.aigov.database import get_engine


@dataclass(frozen=True)
class RiskScore:
    system_id: int
    system_key: str
    system_name: str
    risk_score: float
    risk_tier: str
    business_impact_score: int
    data_sensitivity_score: int
    autonomy_score: int
    exposure_score: int
    vendor_risk_score: int
    documentation_risk_score: int
    risk_factors: str


def score_business_impact(decision_impact: str, production_critical: bool) -> int:
    score_map = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
    }
    score = score_map.get((decision_impact or "").upper(), 1)

    if production_critical:
        score += 1

    return min(score, 4)


def score_data_sensitivity(system: dict) -> int:
    score = 0

    if system["uses_personal_data"]:
        score += 1
    if system["uses_sensitive_data"]:
        score += 2
    if system["uses_financial_data"]:
        score += 1
    if system["uses_health_data"]:
        score += 1
    if system["uses_children_data"]:
        score += 2

    return min(score, 5)


def score_autonomy(autonomy_level: str, human_review_present: bool) -> int:
    autonomy_map = {
        "ASSISTIVE": 1,
        "HUMAN_IN_THE_LOOP": 2,
        "DECISION_SUPPORT": 3,
        "AUTONOMOUS": 5,
    }

    score = autonomy_map.get((autonomy_level or "").upper(), 1)

    if not human_review_present and score >= 3:
        score += 1

    return min(score, 5)


def score_exposure(customer_facing: bool, external_user_facing: bool, employee_facing: bool) -> int:
    if external_user_facing:
        return 4
    if customer_facing:
        return 3
    if employee_facing:
        return 2
    return 1


def score_vendor(third_party_vendor: bool, vendor_name: str | None) -> int:
    if third_party_vendor and vendor_name:
        return 3
    if third_party_vendor:
        return 4
    return 1


def score_documentation_placeholder(approval_status: str) -> int:
    status = (approval_status or "").upper()

    if status == "APPROVED_WITH_CONTROLS":
        return 1
    if status == "REQUIRES_REVIEW":
        return 3
    if status == "NOT_REVIEWED":
        return 4
    if status == "BLOCKED":
        return 5

    return 3


def determine_risk_tier(risk_score: float, prohibited_use_case: bool) -> str:
    if prohibited_use_case:
        return "BLOCKED"

    if risk_score >= 4.0:
        return "HIGH"
    if risk_score >= 2.5:
        return "MODERATE"
    return "LOW"


def build_risk_factors(system: dict, scores: dict[str, int]) -> str:
    factors: list[str] = []

    if system["prohibited_use_case"]:
        factors.append("Prohibited use case")

    if scores["business_impact_score"] >= 3:
        factors.append("High business or decision impact")

    if scores["data_sensitivity_score"] >= 3:
        factors.append("Sensitive or regulated data usage")

    if scores["autonomy_score"] >= 4:
        factors.append("High autonomy or missing human review")

    if scores["exposure_score"] >= 3:
        factors.append("Customer or external user exposure")

    if scores["vendor_risk_score"] >= 3:
        factors.append("Third-party vendor dependency")

    if scores["documentation_risk_score"] >= 3:
        factors.append("Incomplete or pending governance review")

    return "; ".join(factors) if factors else "Low governance risk profile"


def fetch_ai_systems() -> list[dict]:
    query = text(
        """
        SELECT
            system_id,
            system_key,
            system_name,
            decision_impact,
            production_critical,
            uses_personal_data,
            uses_sensitive_data,
            uses_children_data,
            uses_financial_data,
            uses_health_data,
            autonomy_level,
            human_review_present,
            customer_facing,
            external_user_facing,
            employee_facing,
            third_party_vendor,
            vendor_name,
            prohibited_use_case,
            approval_status
        FROM inventory.ai_systems
        ORDER BY system_key
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query).mappings().all()

    return [dict(row) for row in rows]


def calculate_risk_score(system: dict) -> RiskScore:
    business_impact_score = score_business_impact(
        decision_impact=system["decision_impact"],
        production_critical=system["production_critical"],
    )
    data_sensitivity_score = score_data_sensitivity(system)
    autonomy_score = score_autonomy(
        autonomy_level=system["autonomy_level"],
        human_review_present=system["human_review_present"],
    )
    exposure_score = score_exposure(
        customer_facing=system["customer_facing"],
        external_user_facing=system["external_user_facing"],
        employee_facing=system["employee_facing"],
    )
    vendor_risk_score = score_vendor(
        third_party_vendor=system["third_party_vendor"],
        vendor_name=system["vendor_name"],
    )
    documentation_risk_score = score_documentation_placeholder(
        approval_status=system["approval_status"],
    )

    risk_score = round(
        (
            business_impact_score
            + data_sensitivity_score
            + autonomy_score
            + exposure_score
            + vendor_risk_score
            + documentation_risk_score
        )
        / 6,
        2,
    )

    scores = {
        "business_impact_score": business_impact_score,
        "data_sensitivity_score": data_sensitivity_score,
        "autonomy_score": autonomy_score,
        "exposure_score": exposure_score,
        "vendor_risk_score": vendor_risk_score,
        "documentation_risk_score": documentation_risk_score,
    }

    risk_tier = determine_risk_tier(
        risk_score=risk_score,
        prohibited_use_case=system["prohibited_use_case"],
    )

    return RiskScore(
        system_id=system["system_id"],
        system_key=system["system_key"],
        system_name=system["system_name"],
        risk_score=risk_score,
        risk_tier=risk_tier,
        business_impact_score=business_impact_score,
        data_sensitivity_score=data_sensitivity_score,
        autonomy_score=autonomy_score,
        exposure_score=exposure_score,
        vendor_risk_score=vendor_risk_score,
        documentation_risk_score=documentation_risk_score,
        risk_factors=build_risk_factors(system, scores),
    )


def save_risk_scores(risk_scores: list[RiskScore]) -> None:
    delete_sql = text("DELETE FROM governance.risk_assessments")

    insert_sql = text(
        """
        INSERT INTO governance.risk_assessments (
            system_id,
            risk_score,
            risk_tier,
            business_impact_score,
            data_sensitivity_score,
            autonomy_score,
            exposure_score,
            vendor_risk_score,
            documentation_risk_score,
            risk_factors
        )
        VALUES (
            :system_id,
            :risk_score,
            :risk_tier,
            :business_impact_score,
            :data_sensitivity_score,
            :autonomy_score,
            :exposure_score,
            :vendor_risk_score,
            :documentation_risk_score,
            :risk_factors
        )
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(delete_sql)
        for score in risk_scores:
            connection.execute(
                insert_sql,
                {
                    "system_id": score.system_id,
                    "risk_score": score.risk_score,
                    "risk_tier": score.risk_tier,
                    "business_impact_score": score.business_impact_score,
                    "data_sensitivity_score": score.data_sensitivity_score,
                    "autonomy_score": score.autonomy_score,
                    "exposure_score": score.exposure_score,
                    "vendor_risk_score": score.vendor_risk_score,
                    "documentation_risk_score": score.documentation_risk_score,
                    "risk_factors": score.risk_factors,
                },
            )


def run_risk_scoring() -> list[RiskScore]:
    systems = fetch_ai_systems()
    risk_scores = [calculate_risk_score(system) for system in systems]
    save_risk_scores(risk_scores)
    return risk_scores