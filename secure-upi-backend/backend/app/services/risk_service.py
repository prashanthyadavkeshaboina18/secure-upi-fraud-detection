"""
Turns a raw model probability into the score/level/decision triple the rest
of the app works with. Thresholds are configurable (app/config.py) rather
than hardcoded, per the project's requirement that band boundaries be
justified and adjustable rather than arbitrary magic numbers.
"""
from app.config import get_settings
from app.models.transaction import Decision, RiskLevel

settings = get_settings()


def score_from_probability(probability: float) -> int:
    return round(max(0.0, min(1.0, probability)) * 100)


def level_from_score(score: int) -> RiskLevel:
    if score <= settings.RISK_LOW_MAX:
        return RiskLevel.LOW
    if score <= settings.RISK_MEDIUM_MAX:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def decision_from_level(level: RiskLevel) -> Decision:
    return {
        RiskLevel.LOW: Decision.APPROVED,
        RiskLevel.MEDIUM: Decision.REVIEW,
        RiskLevel.HIGH: Decision.BLOCKED,
    }[level]


def evaluate(probability: float) -> tuple[int, RiskLevel, Decision]:
    score = score_from_probability(probability)
    level = level_from_score(score)
    decision = decision_from_level(level)
    return score, level, decision
