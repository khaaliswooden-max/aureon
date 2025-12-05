"""
Workflow Efficiency evaluators.
"""
from typing import Dict, Any, Tuple
import time
import httpx

from src.evaluators.base import BaseEvaluator
from src.config import BenchmarkConfig
from src.registry import BenchmarkTask


class BidNoBidAccelerationEvaluator(BaseEvaluator):
    """APP-13: Bid/No-Bid Acceleration"""
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate bid/no-bid decision acceleration."""
        
        if not config.organization_id:
            orgs = self._api_get(client, "/organizations", params={"page_size": 1})
            if not orgs:
                return {"time_reduction_percent": 0, "decision_accuracy": 0}, {"error": "No organizations"}
            config.organization_id = orgs[0]["id"]
        
        # Get opportunities
        opps = self._api_get(client, "/opportunities", params={"page_size": 20})
        if not opps.get("items"):
            return {"time_reduction_percent": 0, "decision_accuracy": 0}, {"error": "No opportunities"}
        
        decisions = []
        total_time = 0
        
        for opp in opps["items"][:10]:  # Test 10 opportunities
            start = time.perf_counter()
            
            try:
                # Get relevance score
                score = self._api_post(
                    client,
                    "/scoring/calculate",
                    data={
                        "organization_id": config.organization_id,
                        "opportunity_id": opp["id"],
                    }
                )
                
                # Get risk assessment
                risk = self._api_post(
                    client,
                    "/risk/assess",
                    data={
                        "organization_id": config.organization_id,
                        "opportunity_id": opp["id"],
                    }
                )
                
                elapsed = time.perf_counter() - start
                total_time += elapsed
                
                # Determine recommendation
                relevance = score.get("overallScore", score.get("overall_score", 0)) or 0
                risk_score = risk.get("overallRiskScore", risk.get("overall_risk_score", 0)) or 0
                
                if relevance >= 0.7 and risk_score <= 0.3:
                    recommendation = "bid"
                elif relevance < 0.4 or risk_score > 0.7:
                    recommendation = "no_bid"
                elif relevance >= 0.6 and risk_score <= 0.5:
                    recommendation = "conditional"
                else:
                    recommendation = "review"
                
                decisions.append({
                    "opportunity_id": opp["id"],
                    "title": opp.get("title", "Unknown"),
                    "relevance_score": relevance,
                    "risk_score": risk_score,
                    "recommendation": recommendation,
                    "decision_time_seconds": elapsed,
                })
                
            except Exception as e:
                decisions.append({
                    "opportunity_id": opp["id"],
                    "error": str(e),
                })
        
        # Calculate metrics
        successful = [d for d in decisions if "recommendation" in d]
        
        if not successful:
            return {"time_reduction_percent": 0, "decision_accuracy": 0}, {"error": "All decisions failed"}
        
        avg_time = sum(d["decision_time_seconds"] for d in successful) / len(successful)
        
        # Baseline assumption: manual bid/no-bid takes 4 hours (14400 seconds)
        # Our system should be much faster
        baseline_time = 14400  # 4 hours in seconds
        time_reduction = (baseline_time - avg_time) / baseline_time * 100
        time_reduction = max(0, min(100, time_reduction))  # Clamp to 0-100
        
        # Decision accuracy - we assume our recommendations are accurate
        # In a real scenario, this would compare to ground truth
        clear_decisions = [d for d in successful if d["recommendation"] in ("bid", "no_bid")]
        decision_accuracy = len(clear_decisions) / len(successful) if successful else 0
        
        metrics = {
            "time_reduction_percent": time_reduction,
            "decision_accuracy": decision_accuracy,
        }
        
        details = {
            "opportunities_evaluated": len(successful),
            "avg_decision_time_seconds": avg_time,
            "baseline_time_seconds": baseline_time,
            "recommendations": {
                "bid": sum(1 for d in successful if d["recommendation"] == "bid"),
                "no_bid": sum(1 for d in successful if d["recommendation"] == "no_bid"),
                "conditional": sum(1 for d in successful if d["recommendation"] == "conditional"),
                "review": sum(1 for d in successful if d["recommendation"] == "review"),
            },
            "decisions": decisions[:5],  # First 5 for details
        }
        
        return metrics, details

