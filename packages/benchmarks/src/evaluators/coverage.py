"""
Coverage & Recall evaluators.
"""
from typing import Dict, Any, Tuple
import time
import httpx

from src.evaluators.base import BaseEvaluator
from src.config import BenchmarkConfig
from src.registry import BenchmarkTask


class NAICSCoverageEvaluator(BaseEvaluator):
    """APP-01: Basic NAICS Coverage"""
    
    # Test NAICS codes
    TEST_NAICS = ["541512", "541519", "541511"]
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate NAICS code coverage and retrieval."""
        
        results = []
        total_latency = 0
        
        for naics_code in self.TEST_NAICS:
            start = time.perf_counter()
            
            try:
                response = self._api_get(
                    client,
                    f"/opportunities/naics/{naics_code}",
                    params={"page_size": 100}
                )
                latency = (time.perf_counter() - start) * 1000
                total_latency += latency
                
                results.append({
                    "naics": naics_code,
                    "count": response.get("total", 0),
                    "latency_ms": latency,
                    "success": True,
                })
            except Exception as e:
                results.append({
                    "naics": naics_code,
                    "count": 0,
                    "latency_ms": 0,
                    "success": False,
                    "error": str(e),
                })
        
        # Calculate metrics
        successful = [r for r in results if r["success"]]
        recall = len(successful) / len(self.TEST_NAICS) if self.TEST_NAICS else 0
        
        latencies = [r["latency_ms"] for r in successful]
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        
        metrics = {
            "recall": recall,
            "latency_p95_ms": p95_latency,
        }
        
        details = {
            "naics_results": results,
            "total_opportunities": sum(r["count"] for r in successful),
        }
        
        return metrics, details


class SetAsideFilteringEvaluator(BaseEvaluator):
    """APP-02: Set-Aside Filtering"""
    
    TEST_SET_ASIDES = ["Small Business", "8(a)", "SDVOSB", "WOSB"]
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate set-aside filtering accuracy."""
        
        results = []
        
        for set_aside in self.TEST_SET_ASIDES:
            try:
                response = self._api_get(
                    client,
                    "/opportunities",
                    params={"set_aside_type": set_aside, "page_size": 50}
                )
                
                items = response.get("items", [])
                total = response.get("total", 0)
                
                # Check precision - all returned items should match filter
                matching = sum(1 for item in items if item.get("setAsideType") == set_aside)
                precision = matching / len(items) if items else 1.0
                
                results.append({
                    "set_aside": set_aside,
                    "total": total,
                    "returned": len(items),
                    "matching": matching,
                    "precision": precision,
                })
            except Exception as e:
                results.append({
                    "set_aside": set_aside,
                    "error": str(e),
                    "precision": 0,
                })
        
        # Calculate overall metrics
        avg_precision = sum(r.get("precision", 0) for r in results) / len(results)
        recall = len([r for r in results if "total" in r]) / len(self.TEST_SET_ASIDES)
        
        metrics = {
            "recall": recall,
            "precision": avg_precision,
        }
        
        details = {
            "set_aside_results": results,
        }
        
        return metrics, details

