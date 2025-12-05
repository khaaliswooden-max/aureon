"""
Precision & Relevance evaluators.
"""
from typing import Dict, Any, Tuple, List
import math
import httpx

from src.evaluators.base import BaseEvaluator
from src.config import BenchmarkConfig
from src.registry import BenchmarkTask


class RelevanceRankingEvaluator(BaseEvaluator):
    """APP-04: Relevance Ranking"""
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate relevance ranking quality using NDCG."""
        
        if not config.organization_id:
            # Use first available organization
            orgs = self._api_get(client, "/organizations", params={"page_size": 1})
            if not orgs:
                return {"ndcg_at_10": 0, "precision_at_20": 0}, {"error": "No organizations found"}
            config.organization_id = orgs[0]["id"]
        
        # Get opportunities
        opps = self._api_get(client, "/opportunities", params={"page_size": 100})
        if not opps.get("items"):
            return {"ndcg_at_10": 0, "precision_at_20": 0}, {"error": "No opportunities found"}
        
        opp_ids = [opp["id"] for opp in opps["items"][:100]]
        
        # Get relevance scores
        try:
            scores_response = self._api_post(
                client,
                "/scoring/batch",
                data={
                    "organization_id": config.organization_id,
                    "opportunity_ids": opp_ids,
                }
            )
            scores = scores_response.get("items", [])
        except Exception:
            # Fall back to individual scoring
            scores = []
            for opp_id in opp_ids[:20]:  # Limit for fallback
                try:
                    score = self._api_post(
                        client,
                        "/scoring/calculate",
                        data={
                            "organization_id": config.organization_id,
                            "opportunity_id": opp_id,
                        }
                    )
                    scores.append(score)
                except Exception:
                    pass
        
        if not scores:
            return {"ndcg_at_10": 0, "precision_at_20": 0}, {"error": "Scoring failed"}
        
        # Sort by score
        sorted_scores = sorted(scores, key=lambda x: x.get("overallScore", x.get("overall_score", 0)), reverse=True)
        
        # Calculate NDCG@10
        ndcg_10 = self._calculate_ndcg(sorted_scores[:10])
        
        # Calculate Precision@20 (assuming scores >= 0.6 are relevant)
        top_20 = sorted_scores[:20]
        relevant_count = sum(1 for s in top_20 if s.get("overallScore", s.get("overall_score", 0)) >= 0.6)
        precision_20 = relevant_count / min(20, len(top_20))
        
        metrics = {
            "ndcg_at_10": ndcg_10,
            "precision_at_20": precision_20,
        }
        
        details = {
            "total_scored": len(scores),
            "top_scores": [
                {"id": s.get("opportunityId", s.get("opportunity_id")), 
                 "score": s.get("overallScore", s.get("overall_score", 0))}
                for s in sorted_scores[:10]
            ],
        }
        
        return metrics, details
    
    def _calculate_ndcg(self, scores: List[dict], k: int = 10) -> float:
        """Calculate NDCG@k."""
        if not scores:
            return 0.0
        
        # Use raw scores as relevance
        relevances = [s.get("overallScore", s.get("overall_score", 0)) for s in scores[:k]]
        
        # DCG
        dcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))
        
        # Ideal DCG (sorted relevances)
        ideal_relevances = sorted(relevances, reverse=True)
        idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg


class SemanticMatchingEvaluator(BaseEvaluator):
    """APP-05: Semantic Matching"""
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate semantic matching quality."""
        
        # This evaluator uses the semantic_score component from relevance scoring
        if not config.organization_id:
            orgs = self._api_get(client, "/organizations", params={"page_size": 1})
            if not orgs:
                return {"map": 0, "mrr": 0}, {"error": "No organizations found"}
            config.organization_id = orgs[0]["id"]
        
        # Get opportunities with descriptions
        opps = self._api_get(client, "/opportunities", params={"page_size": 50})
        if not opps.get("items"):
            return {"map": 0, "mrr": 0}, {"error": "No opportunities found"}
        
        # Filter to those with descriptions
        opps_with_desc = [o for o in opps["items"] if o.get("description")][:30]
        
        if not opps_with_desc:
            return {"map": 0, "mrr": 0}, {"error": "No opportunities with descriptions"}
        
        # Score each opportunity
        semantic_scores = []
        for opp in opps_with_desc:
            try:
                score = self._api_post(
                    client,
                    "/scoring/calculate",
                    data={
                        "organization_id": config.organization_id,
                        "opportunity_id": opp["id"],
                    }
                )
                semantic_score = score.get("semanticScore", score.get("semantic_score", 0)) or 0
                semantic_scores.append(semantic_score)
            except Exception:
                semantic_scores.append(0)
        
        if not semantic_scores:
            return {"map": 0, "mrr": 0}, {"error": "Scoring failed"}
        
        # Calculate MAP (simplified - using threshold for relevance)
        threshold = 0.5
        relevant = [s >= threshold for s in semantic_scores]
        
        # Precision at each position
        precisions = []
        relevant_count = 0
        for i, is_rel in enumerate(relevant):
            if is_rel:
                relevant_count += 1
                precisions.append(relevant_count / (i + 1))
        
        map_score = sum(precisions) / max(sum(relevant), 1)
        
        # MRR
        mrr = 0.0
        for i, is_rel in enumerate(relevant):
            if is_rel:
                mrr = 1.0 / (i + 1)
                break
        
        metrics = {
            "map": map_score,
            "mrr": mrr,
        }
        
        details = {
            "opportunities_evaluated": len(semantic_scores),
            "relevant_found": sum(relevant),
            "avg_semantic_score": sum(semantic_scores) / len(semantic_scores),
        }
        
        return metrics, details

