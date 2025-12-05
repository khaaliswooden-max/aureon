"""
Benchmark task registry.

Defines all APP-Bench tasks across 7 dimensions with 20 total tasks.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any


@dataclass
class BenchmarkTask:
    """Definition of a benchmark task."""
    id: str
    name: str
    dimension: str
    difficulty: str  # basic, intermediate, advanced, expert
    description: str
    targets: Dict[str, float]  # metric_name -> target value
    implemented: bool = False
    evaluator: Optional[Callable] = None
    setup_fn: Optional[Callable] = None


# ============================================================
# DIMENSION 1: Coverage & Recall (CR)
# ============================================================

APP_01 = BenchmarkTask(
    id="APP-01",
    name="Basic NAICS Coverage",
    dimension="Coverage & Recall",
    difficulty="Basic",
    description="Given a set of NAICS codes, retrieve all matching opportunities from the last 30 days.",
    targets={"recall": 0.95, "latency_p95_ms": 2000},
    implemented=True,
)

APP_02 = BenchmarkTask(
    id="APP-02",
    name="Set-Aside Filtering",
    dimension="Coverage & Recall",
    difficulty="Basic",
    description="Filter opportunities by set-aside type and verify completeness.",
    targets={"recall": 0.98, "precision": 0.95},
    implemented=True,
)

APP_03 = BenchmarkTask(
    id="APP-03",
    name="Multi-Jurisdiction Discovery",
    dimension="Coverage & Recall",
    difficulty="Advanced",
    description="Discover matching opportunities across federal and 5 state portals.",
    targets={"recall": 0.85, "coverage_percentage": 0.80},
    implemented=False,
)

# ============================================================
# DIMENSION 2: Precision & Relevance (PR)
# ============================================================

APP_04 = BenchmarkTask(
    id="APP-04",
    name="Relevance Ranking",
    dimension="Precision & Relevance",
    difficulty="Basic",
    description="Rank 100 opportunities by relevance for a given organization profile.",
    targets={"ndcg_at_10": 0.75, "precision_at_20": 0.80},
    implemented=True,
)

APP_05 = BenchmarkTask(
    id="APP-05",
    name="Semantic Matching",
    dimension="Precision & Relevance",
    difficulty="Intermediate",
    description="Match capability statements to opportunity requirements using semantic similarity.",
    targets={"map": 0.70, "mrr": 0.75},
    implemented=True,
)

APP_06 = BenchmarkTask(
    id="APP-06",
    name="False Positive Resistance",
    dimension="Precision & Relevance",
    difficulty="Advanced",
    description="Correctly reject opportunities that appear relevant but have disqualifying factors.",
    targets={"specificity": 0.90, "f1_score": 0.85},
    implemented=False,
)

# ============================================================
# DIMENSION 3: Compliance Fidelity (CF)
# ============================================================

APP_07 = BenchmarkTask(
    id="APP-07",
    name="Set-Aside Eligibility",
    dimension="Compliance Fidelity",
    difficulty="Basic",
    description="Correctly determine eligibility for various set-aside types.",
    targets={"accuracy": 0.98, "false_positive_rate": 0.02},
    implemented=True,
)

APP_08 = BenchmarkTask(
    id="APP-08",
    name="FAR Clause Interpretation",
    dimension="Compliance Fidelity",
    difficulty="Intermediate",
    description="Extract and interpret key FAR clause requirements.",
    targets={"accuracy": 0.85, "extraction_f1": 0.80},
    implemented=False,
)

APP_09 = BenchmarkTask(
    id="APP-09",
    name="Amendment Impact Analysis",
    dimension="Compliance Fidelity",
    difficulty="Advanced",
    description="Detect and assess impact of solicitation amendments.",
    targets={"detection_rate": 0.95, "impact_accuracy": 0.80},
    implemented=False,
)

# ============================================================
# DIMENSION 4: Temporal Responsiveness (TR)
# ============================================================

APP_10 = BenchmarkTask(
    id="APP-10",
    name="New Opportunity Detection",
    dimension="Temporal Responsiveness",
    difficulty="Basic",
    description="Detect newly posted opportunities within 15 minutes.",
    targets={"detection_latency_minutes": 15, "detection_rate": 0.99},
    implemented=False,
)

APP_11 = BenchmarkTask(
    id="APP-11",
    name="Deadline Tracking",
    dimension="Temporal Responsiveness",
    difficulty="Basic",
    description="Accurately track and alert on upcoming deadlines.",
    targets={"accuracy": 0.995, "alert_timeliness_hours": 24},
    implemented=True,
)

APP_12 = BenchmarkTask(
    id="APP-12",
    name="Change Detection",
    dimension="Temporal Responsiveness",
    difficulty="Intermediate",
    description="Detect modifications to tracked opportunities.",
    targets={"detection_rate": 0.95, "latency_minutes": 30},
    implemented=False,
)

# ============================================================
# DIMENSION 5: Workflow Efficiency (WE)
# ============================================================

APP_13 = BenchmarkTask(
    id="APP-13",
    name="Bid/No-Bid Acceleration",
    dimension="Workflow Efficiency",
    difficulty="Basic",
    description="Reduce time to initial bid/no-bid decision.",
    targets={"time_reduction_percent": 30, "decision_accuracy": 0.85},
    implemented=True,
)

APP_14 = BenchmarkTask(
    id="APP-14",
    name="Pipeline Optimization",
    dimension="Workflow Efficiency",
    difficulty="Intermediate",
    description="Optimize opportunity pipeline based on capacity constraints.",
    targets={"utilization_improvement": 0.20, "win_rate_improvement": 0.10},
    implemented=False,
)

APP_15 = BenchmarkTask(
    id="APP-15",
    name="Team Formation",
    dimension="Workflow Efficiency",
    difficulty="Advanced",
    description="Suggest optimal team compositions for opportunities.",
    targets={"match_quality": 0.80, "recommendation_latency_ms": 5000},
    implemented=False,
)

# ============================================================
# DIMENSION 6: Robustness & Stress (RS)
# ============================================================

APP_16 = BenchmarkTask(
    id="APP-16",
    name="Data Quality Resilience",
    dimension="Robustness & Stress",
    difficulty="Intermediate",
    description="Maintain performance with noisy or incomplete data.",
    targets={"degradation_max_percent": 10, "error_rate": 0.05},
    implemented=False,
)

APP_17 = BenchmarkTask(
    id="APP-17",
    name="Load Handling",
    dimension="Robustness & Stress",
    difficulty="Advanced",
    description="Handle 1000 concurrent scoring requests.",
    targets={"throughput_rps": 100, "p99_latency_ms": 1000},
    implemented=False,
)

APP_18 = BenchmarkTask(
    id="APP-18",
    name="Adversarial Inputs",
    dimension="Robustness & Stress",
    difficulty="Expert",
    description="Resist manipulation through adversarial opportunity descriptions.",
    targets={"manipulation_resistance": 0.95, "false_positive_increase": 0.05},
    implemented=False,
)

# ============================================================
# DIMENSION 7: Planetary Scale (PS)
# ============================================================

APP_19 = BenchmarkTask(
    id="APP-19",
    name="Cross-Jurisdiction Query",
    dimension="Planetary Scale",
    difficulty="Advanced",
    description="Execute unified queries across 10+ procurement systems.",
    targets={"systems_covered": 10, "query_latency_ms": 10000},
    implemented=False,
)

APP_20 = BenchmarkTask(
    id="APP-20",
    name="Multi-Tenant Isolation",
    dimension="Planetary Scale",
    difficulty="Expert",
    description="Ensure complete data isolation in multi-tenant deployment.",
    targets={"isolation_score": 1.0, "cross_tenant_leakage": 0.0},
    implemented=False,
)


# Registry of all benchmarks
BENCHMARK_REGISTRY: Dict[str, BenchmarkTask] = {
    "APP-01": APP_01,
    "APP-02": APP_02,
    "APP-03": APP_03,
    "APP-04": APP_04,
    "APP-05": APP_05,
    "APP-06": APP_06,
    "APP-07": APP_07,
    "APP-08": APP_08,
    "APP-09": APP_09,
    "APP-10": APP_10,
    "APP-11": APP_11,
    "APP-12": APP_12,
    "APP-13": APP_13,
    "APP-14": APP_14,
    "APP-15": APP_15,
    "APP-16": APP_16,
    "APP-17": APP_17,
    "APP-18": APP_18,
    "APP-19": APP_19,
    "APP-20": APP_20,
}


def get_benchmark(task_id: str) -> Optional[BenchmarkTask]:
    """Get a benchmark task by ID."""
    return BENCHMARK_REGISTRY.get(task_id.upper())


def list_by_dimension(dimension: str) -> list[BenchmarkTask]:
    """List all benchmarks in a dimension."""
    return [t for t in BENCHMARK_REGISTRY.values() if dimension.lower() in t.dimension.lower()]


def list_by_difficulty(difficulty: str) -> list[BenchmarkTask]:
    """List all benchmarks at a difficulty level."""
    return [t for t in BENCHMARK_REGISTRY.values() if t.difficulty.lower() == difficulty.lower()]


def list_implemented() -> list[BenchmarkTask]:
    """List all implemented benchmarks."""
    return [t for t in BENCHMARK_REGISTRY.values() if t.implemented]

