"""
Benchmark configuration.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs."""
    
    # API connection
    api_url: str = "http://localhost:8000"
    api_timeout: int = 30
    
    # Context
    organization_id: Optional[str] = None
    
    # Execution
    max_concurrent: int = 5
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # Output
    output_dir: str = "results"
    verbose: bool = False
    
    # Limits
    max_opportunities: int = 1000
    max_organizations: int = 100

