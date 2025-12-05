"""
Benchmark evaluators for each task.
"""
from typing import Optional
from src.evaluators.base import BaseEvaluator
from src.evaluators.coverage import NAICSCoverageEvaluator, SetAsideFilteringEvaluator
from src.evaluators.relevance import RelevanceRankingEvaluator, SemanticMatchingEvaluator
from src.evaluators.compliance import SetAsideEligibilityEvaluator
from src.evaluators.temporal import DeadlineTrackingEvaluator
from src.evaluators.workflow import BidNoBidAccelerationEvaluator


EVALUATOR_REGISTRY = {
    "APP-01": NAICSCoverageEvaluator(),
    "APP-02": SetAsideFilteringEvaluator(),
    "APP-04": RelevanceRankingEvaluator(),
    "APP-05": SemanticMatchingEvaluator(),
    "APP-07": SetAsideEligibilityEvaluator(),
    "APP-11": DeadlineTrackingEvaluator(),
    "APP-13": BidNoBidAccelerationEvaluator(),
}


def get_evaluator(task_id: str) -> Optional[BaseEvaluator]:
    """Get the evaluator for a task."""
    return EVALUATOR_REGISTRY.get(task_id.upper())


__all__ = [
    "BaseEvaluator",
    "get_evaluator",
    "EVALUATOR_REGISTRY",
]

