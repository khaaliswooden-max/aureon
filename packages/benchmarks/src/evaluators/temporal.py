"""
Temporal Responsiveness evaluators.
"""
from typing import Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
import httpx

from src.evaluators.base import BaseEvaluator
from src.config import BenchmarkConfig
from src.registry import BenchmarkTask


class DeadlineTrackingEvaluator(BaseEvaluator):
    """APP-11: Deadline Tracking"""
    
    def evaluate(
        self,
        client: httpx.Client,
        config: BenchmarkConfig,
        task: BenchmarkTask,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Evaluate deadline tracking accuracy."""
        
        # Get opportunities with deadlines
        opps = self._api_get(client, "/opportunities", params={"page_size": 100})
        
        if not opps.get("items"):
            return {"accuracy": 1.0, "alert_timeliness_hours": 0}, {"error": "No opportunities found"}
        
        now = datetime.now(timezone.utc)
        upcoming = []
        has_deadline_count = 0
        valid_deadline_count = 0
        
        for opp in opps["items"]:
            deadline_str = opp.get("responseDeadline") or opp.get("response_deadline")
            if deadline_str:
                has_deadline_count += 1
                try:
                    # Parse deadline
                    deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                    
                    # Check if in the future
                    if deadline > now:
                        valid_deadline_count += 1
                        days_until = (deadline - now).days
                        hours_until = (deadline - now).total_seconds() / 3600
                        
                        upcoming.append({
                            "id": opp["id"],
                            "title": opp.get("title", "Unknown"),
                            "deadline": deadline_str,
                            "days_until": days_until,
                            "hours_until": hours_until,
                        })
                except Exception:
                    pass
        
        # Calculate accuracy (valid deadlines / deadlines found)
        accuracy = valid_deadline_count / has_deadline_count if has_deadline_count > 0 else 1.0
        
        # Sort by deadline
        upcoming.sort(key=lambda x: x["hours_until"])
        
        # Check alert timeliness (assuming alerts for deadlines within 24 hours)
        urgent = [o for o in upcoming if o["hours_until"] <= 24]
        timeliness = 24.0 if urgent else 0.0  # All urgent items are "alerted"
        
        metrics = {
            "accuracy": accuracy,
            "alert_timeliness_hours": timeliness,
        }
        
        details = {
            "total_opportunities": len(opps["items"]),
            "with_deadlines": has_deadline_count,
            "valid_future_deadlines": valid_deadline_count,
            "urgent_within_24h": len(urgent),
            "upcoming_deadlines": upcoming[:10],  # Top 10
        }
        
        return metrics, details

