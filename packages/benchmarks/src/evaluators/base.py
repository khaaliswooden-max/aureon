"""
Base evaluator class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import httpx

from src.config import BenchmarkConfig
from src.registry import BenchmarkTask


class BaseEvaluator(ABC):
    """Base class for benchmark evaluators."""
    
    @abstractmethod
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Run the evaluation and return metrics and details.
        
        Returns:
            Tuple of (metrics_dict, details_dict)
        """
        pass
    
    def _api_get(self, client: httpx.Client, endpoint: str, params: dict = None) -> dict:
        """Helper to make API GET request."""
        response = client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def _api_post(self, client: httpx.Client, endpoint: str, data: dict = None) -> dict:
        """Helper to make API POST request."""
        response = client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

