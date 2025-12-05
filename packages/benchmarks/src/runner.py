"""
Benchmark runner and result handling.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import time
import httpx

from src.config import BenchmarkConfig
from src.registry import BenchmarkTask
from src.evaluators import get_evaluator


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    task_id: str
    task_name: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    metrics: Dict[str, float]
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "passed": self.passed,
            "details": self.details,
            "errors": self.errors,
        }


class BenchmarkRunner:
    """Executes benchmark tasks and collects results."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.client = httpx.Client(
            base_url=config.api_url,
            timeout=config.api_timeout,
        )
    
    def run(self, task: BenchmarkTask) -> BenchmarkResult:
        """Run a single benchmark task."""
        started_at = datetime.utcnow()
        start_time = time.perf_counter()
        
        errors = []
        metrics = {}
        details = {}
        
        try:
            # Get the evaluator for this task
            evaluator = get_evaluator(task.id)
            
            if evaluator is None:
                raise ValueError(f"No evaluator found for task {task.id}")
            
            # Run evaluation
            metrics, details = evaluator.evaluate(
                client=self.client,
                config=self.config,
                task=task,
            )
            
        except Exception as e:
            errors.append(str(e))
            if self.config.verbose:
                import traceback
                errors.append(traceback.format_exc())
        
        end_time = time.perf_counter()
        completed_at = datetime.utcnow()
        duration = end_time - start_time
        
        # Determine if passed
        passed = len(errors) == 0 and all(
            metrics.get(m, 0) >= t 
            for m, t in task.targets.items()
            if isinstance(t, (int, float))
        )
        
        return BenchmarkResult(
            task_id=task.id,
            task_name=task.name,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            metrics=metrics,
            passed=passed,
            details=details,
            errors=errors,
        )
    
    def close(self):
        """Close HTTP client."""
        self.client.close()

