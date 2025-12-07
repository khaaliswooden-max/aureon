"""
Pricing Intelligence Service

Provides competitive pricing analysis and benchmarking for federal contracts:
- Historical award data analysis
- Labor rate comparisons
- Contract value benchmarking
- Should-cost modeling
- Pricing recommendations
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


@dataclass
class LaborRateBenchmark:
    """Labor rate benchmark data."""
    labor_category: str
    min_rate: Decimal
    max_rate: Decimal
    median_rate: Decimal
    average_rate: Decimal
    sample_size: int
    data_source: str = "GSA Schedule"


@dataclass
class ContractValueBenchmark:
    """Contract value benchmark for NAICS/PSC."""
    naics_code: str
    psc_code: Optional[str]
    min_value: Decimal
    max_value: Decimal
    median_value: Decimal
    average_value: Decimal
    sample_size: int
    period: str = "FY2024"


@dataclass
class PricingRecommendation:
    """Pricing recommendation result."""
    opportunity_id: str
    recommended_price_min: Decimal
    recommended_price_max: Decimal
    competitive_position: str  # aggressive, competitive, premium
    confidence: float
    factors: Dict[str, Any]
    labor_rates: List[LaborRateBenchmark]
    benchmarks: List[ContractValueBenchmark]
    notes: List[str]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PricingIntelligenceService:
    """
    Pricing Intelligence Service for Federal Contracts.
    
    Capabilities:
    - Labor rate benchmarking by category
    - Contract value analysis by NAICS/PSC
    - Historical award analysis
    - Competitive pricing recommendations
    - Should-cost modeling
    """
    
    # Common labor categories with typical GSA rates (simplified)
    # In production, this would pull from actual GSA data
    LABOR_RATE_BENCHMARKS = {
        # IT Labor Categories
        "program_manager": LaborRateBenchmark(
            labor_category="Program Manager",
            min_rate=Decimal("125.00"),
            max_rate=Decimal("225.00"),
            median_rate=Decimal("175.00"),
            average_rate=Decimal("172.50"),
            sample_size=500,
            data_source="GSA IT Schedule 70",
        ),
        "project_manager": LaborRateBenchmark(
            labor_category="Project Manager",
            min_rate=Decimal("95.00"),
            max_rate=Decimal("175.00"),
            median_rate=Decimal("135.00"),
            average_rate=Decimal("132.00"),
            sample_size=800,
            data_source="GSA IT Schedule 70",
        ),
        "senior_engineer": LaborRateBenchmark(
            labor_category="Senior Software Engineer",
            min_rate=Decimal("110.00"),
            max_rate=Decimal("195.00"),
            median_rate=Decimal("155.00"),
            average_rate=Decimal("152.00"),
            sample_size=1200,
            data_source="GSA IT Schedule 70",
        ),
        "engineer": LaborRateBenchmark(
            labor_category="Software Engineer",
            min_rate=Decimal("75.00"),
            max_rate=Decimal("145.00"),
            median_rate=Decimal("110.00"),
            average_rate=Decimal("108.00"),
            sample_size=1500,
            data_source="GSA IT Schedule 70",
        ),
        "junior_engineer": LaborRateBenchmark(
            labor_category="Junior Software Engineer",
            min_rate=Decimal("55.00"),
            max_rate=Decimal("95.00"),
            median_rate=Decimal("72.00"),
            average_rate=Decimal("73.50"),
            sample_size=900,
            data_source="GSA IT Schedule 70",
        ),
        "senior_analyst": LaborRateBenchmark(
            labor_category="Senior Systems Analyst",
            min_rate=Decimal("95.00"),
            max_rate=Decimal("165.00"),
            median_rate=Decimal("125.00"),
            average_rate=Decimal("127.00"),
            sample_size=700,
            data_source="GSA IT Schedule 70",
        ),
        "analyst": LaborRateBenchmark(
            labor_category="Systems Analyst",
            min_rate=Decimal("65.00"),
            max_rate=Decimal("125.00"),
            median_rate=Decimal("92.00"),
            average_rate=Decimal("94.00"),
            sample_size=1100,
            data_source="GSA IT Schedule 70",
        ),
        "security_engineer": LaborRateBenchmark(
            labor_category="Cybersecurity Engineer",
            min_rate=Decimal("115.00"),
            max_rate=Decimal("210.00"),
            median_rate=Decimal("160.00"),
            average_rate=Decimal("158.00"),
            sample_size=450,
            data_source="GSA IT Schedule 70",
        ),
        "data_scientist": LaborRateBenchmark(
            labor_category="Data Scientist",
            min_rate=Decimal("105.00"),
            max_rate=Decimal("195.00"),
            median_rate=Decimal("150.00"),
            average_rate=Decimal("148.00"),
            sample_size=350,
            data_source="GSA IT Schedule 70",
        ),
        "cloud_architect": LaborRateBenchmark(
            labor_category="Cloud Solutions Architect",
            min_rate=Decimal("130.00"),
            max_rate=Decimal("235.00"),
            median_rate=Decimal("180.00"),
            average_rate=Decimal("178.00"),
            sample_size=280,
            data_source="GSA IT Schedule 70",
        ),
        # Professional Services
        "consultant_senior": LaborRateBenchmark(
            labor_category="Senior Consultant",
            min_rate=Decimal("115.00"),
            max_rate=Decimal("225.00"),
            median_rate=Decimal("165.00"),
            average_rate=Decimal("162.00"),
            sample_size=600,
            data_source="GSA PSS Schedule",
        ),
        "consultant": LaborRateBenchmark(
            labor_category="Consultant",
            min_rate=Decimal("75.00"),
            max_rate=Decimal("155.00"),
            median_rate=Decimal("110.00"),
            average_rate=Decimal("112.00"),
            sample_size=850,
            data_source="GSA PSS Schedule",
        ),
        "subject_matter_expert": LaborRateBenchmark(
            labor_category="Subject Matter Expert",
            min_rate=Decimal("140.00"),
            max_rate=Decimal("285.00"),
            median_rate=Decimal("200.00"),
            average_rate=Decimal("195.00"),
            sample_size=400,
            data_source="GSA PSS Schedule",
        ),
        # Administrative
        "admin_assistant": LaborRateBenchmark(
            labor_category="Administrative Assistant",
            min_rate=Decimal("35.00"),
            max_rate=Decimal("65.00"),
            median_rate=Decimal("48.00"),
            average_rate=Decimal("49.00"),
            sample_size=1000,
            data_source="GSA Schedule",
        ),
        "executive_assistant": LaborRateBenchmark(
            labor_category="Executive Assistant",
            min_rate=Decimal("50.00"),
            max_rate=Decimal("95.00"),
            median_rate=Decimal("70.00"),
            average_rate=Decimal("71.00"),
            sample_size=500,
            data_source="GSA Schedule",
        ),
    }
    
    # NAICS contract value benchmarks (simplified)
    NAICS_BENCHMARKS = {
        "541511": ContractValueBenchmark(
            naics_code="541511",
            psc_code="D302",
            min_value=Decimal("100000"),
            max_value=Decimal("50000000"),
            median_value=Decimal("2500000"),
            average_value=Decimal("5200000"),
            sample_size=2500,
        ),
        "541512": ContractValueBenchmark(
            naics_code="541512",
            psc_code="D306",
            min_value=Decimal("150000"),
            max_value=Decimal("75000000"),
            median_value=Decimal("3500000"),
            average_value=Decimal("7800000"),
            sample_size=1800,
        ),
        "541519": ContractValueBenchmark(
            naics_code="541519",
            psc_code="D399",
            min_value=Decimal("75000"),
            max_value=Decimal("25000000"),
            median_value=Decimal("1800000"),
            average_rate=Decimal("3200000"),
            sample_size=1200,
        ),
        "541330": ContractValueBenchmark(
            naics_code="541330",
            psc_code="C211",
            min_value=Decimal("200000"),
            max_value=Decimal("100000000"),
            median_value=Decimal("5000000"),
            average_value=Decimal("12500000"),
            sample_size=900,
        ),
        "561210": ContractValueBenchmark(
            naics_code="561210",
            psc_code="R699",
            min_value=Decimal("50000"),
            max_value=Decimal("15000000"),
            median_value=Decimal("850000"),
            average_value=Decimal("1800000"),
            sample_size=1500,
        ),
    }
    
    def __init__(self):
        """Initialize pricing intelligence service."""
        pass
    
    async def get_pricing_recommendation(
        self,
        opportunity: Dict[str, Any],
        organization: Optional[Dict[str, Any]] = None,
        labor_mix: Optional[Dict[str, int]] = None,
    ) -> PricingRecommendation:
        """
        Generate pricing recommendation for an opportunity.
        
        Args:
            opportunity: Opportunity data
            organization: Organization data (optional)
            labor_mix: Labor category mix with FTE counts (optional)
            
        Returns:
            PricingRecommendation with suggested pricing and analysis
        """
        naics_code = opportunity.get("naics_code", "")
        estimated_min = opportunity.get("estimated_value_min")
        estimated_max = opportunity.get("estimated_value_max")
        
        # Get relevant benchmarks
        naics_benchmark = self._get_naics_benchmark(naics_code)
        relevant_labor_rates = self._get_relevant_labor_rates(opportunity)
        
        # Calculate recommended pricing
        recommended_min, recommended_max = self._calculate_recommended_price(
            naics_benchmark,
            estimated_min,
            estimated_max,
            labor_mix,
            relevant_labor_rates,
        )
        
        # Determine competitive position
        competitive_position = self._determine_competitive_position(
            recommended_min, recommended_max, estimated_max, naics_benchmark
        )
        
        # Generate notes and factors
        factors = {
            "naics_code": naics_code,
            "has_government_estimate": estimated_max is not None,
            "benchmark_available": naics_benchmark is not None,
            "labor_mix_provided": labor_mix is not None,
        }
        
        notes = self._generate_pricing_notes(
            naics_benchmark, estimated_max, competitive_position, opportunity
        )
        
        return PricingRecommendation(
            opportunity_id=str(opportunity.get("id", "")),
            recommended_price_min=recommended_min,
            recommended_price_max=recommended_max,
            competitive_position=competitive_position,
            confidence=self._calculate_confidence(naics_benchmark, labor_mix),
            factors=factors,
            labor_rates=relevant_labor_rates,
            benchmarks=[naics_benchmark] if naics_benchmark else [],
            notes=notes,
        )
    
    async def get_labor_rate_benchmarks(
        self,
        categories: Optional[List[str]] = None,
    ) -> List[LaborRateBenchmark]:
        """
        Get labor rate benchmarks for specified categories.
        
        Args:
            categories: List of labor category keys (None = all)
            
        Returns:
            List of LaborRateBenchmark objects
        """
        if categories is None:
            return list(self.LABOR_RATE_BENCHMARKS.values())
        
        return [
            self.LABOR_RATE_BENCHMARKS[cat]
            for cat in categories
            if cat in self.LABOR_RATE_BENCHMARKS
        ]
    
    async def get_contract_benchmarks(
        self,
        naics_codes: Optional[List[str]] = None,
    ) -> List[ContractValueBenchmark]:
        """
        Get contract value benchmarks for specified NAICS codes.
        
        Args:
            naics_codes: List of NAICS codes (None = all)
            
        Returns:
            List of ContractValueBenchmark objects
        """
        if naics_codes is None:
            return list(self.NAICS_BENCHMARKS.values())
        
        results = []
        for code in naics_codes:
            # Check exact match first
            if code in self.NAICS_BENCHMARKS:
                results.append(self.NAICS_BENCHMARKS[code])
            else:
                # Check prefix matches
                for bench_code, benchmark in self.NAICS_BENCHMARKS.items():
                    if bench_code.startswith(code[:4]):
                        results.append(benchmark)
                        break
        
        return results
    
    async def calculate_should_cost(
        self,
        labor_mix: Dict[str, int],
        duration_months: int = 12,
        overhead_rate: float = 1.5,
        profit_margin: float = 0.10,
    ) -> Dict[str, Any]:
        """
        Calculate should-cost estimate based on labor mix.
        
        Args:
            labor_mix: Dictionary of labor category -> FTE count
            duration_months: Contract duration in months
            overhead_rate: Overhead/G&A multiplier
            profit_margin: Target profit margin
            
        Returns:
            Should-cost breakdown
        """
        hours_per_month = 173  # Standard
        total_hours = hours_per_month * duration_months
        
        labor_costs = {}
        total_direct_labor = Decimal("0")
        
        for category, fte_count in labor_mix.items():
            benchmark = self.LABOR_RATE_BENCHMARKS.get(category)
            if benchmark:
                # Use median rate
                category_cost = benchmark.median_rate * total_hours * fte_count
                labor_costs[category] = {
                    "fte_count": fte_count,
                    "hourly_rate": float(benchmark.median_rate),
                    "total_cost": float(category_cost),
                }
                total_direct_labor += category_cost
        
        # Calculate fully loaded cost
        overhead_cost = total_direct_labor * Decimal(str(overhead_rate - 1))
        subtotal = total_direct_labor + overhead_cost
        profit = subtotal * Decimal(str(profit_margin))
        total_price = subtotal + profit
        
        return {
            "labor_breakdown": labor_costs,
            "direct_labor": float(total_direct_labor),
            "overhead_cost": float(overhead_cost),
            "overhead_rate": overhead_rate,
            "subtotal": float(subtotal),
            "profit_margin": profit_margin,
            "profit": float(profit),
            "total_price": float(total_price),
            "duration_months": duration_months,
            "price_per_month": float(total_price / duration_months),
        }
    
    def _get_naics_benchmark(self, naics_code: str) -> Optional[ContractValueBenchmark]:
        """Get benchmark for NAICS code."""
        if naics_code in self.NAICS_BENCHMARKS:
            return self.NAICS_BENCHMARKS[naics_code]
        
        # Check 4-digit prefix
        for code, benchmark in self.NAICS_BENCHMARKS.items():
            if code.startswith(naics_code[:4]):
                return benchmark
        
        return None
    
    def _get_relevant_labor_rates(
        self,
        opportunity: Dict[str, Any],
    ) -> List[LaborRateBenchmark]:
        """Determine relevant labor categories based on opportunity."""
        naics_code = opportunity.get("naics_code", "")
        description = (opportunity.get("description") or "").lower()
        
        relevant = []
        
        # IT-related NAICS
        if naics_code.startswith("5415"):
            relevant.extend([
                self.LABOR_RATE_BENCHMARKS["program_manager"],
                self.LABOR_RATE_BENCHMARKS["project_manager"],
                self.LABOR_RATE_BENCHMARKS["senior_engineer"],
                self.LABOR_RATE_BENCHMARKS["engineer"],
                self.LABOR_RATE_BENCHMARKS["analyst"],
            ])
            
            if "security" in description or "cyber" in description:
                relevant.append(self.LABOR_RATE_BENCHMARKS["security_engineer"])
            if "data" in description or "analytics" in description:
                relevant.append(self.LABOR_RATE_BENCHMARKS["data_scientist"])
            if "cloud" in description or "aws" in description or "azure" in description:
                relevant.append(self.LABOR_RATE_BENCHMARKS["cloud_architect"])
        
        # Professional services
        elif naics_code.startswith("5416") or naics_code.startswith("5412"):
            relevant.extend([
                self.LABOR_RATE_BENCHMARKS["consultant_senior"],
                self.LABOR_RATE_BENCHMARKS["consultant"],
                self.LABOR_RATE_BENCHMARKS["subject_matter_expert"],
                self.LABOR_RATE_BENCHMARKS["project_manager"],
            ])
        
        # Default set
        if not relevant:
            relevant.extend([
                self.LABOR_RATE_BENCHMARKS["project_manager"],
                self.LABOR_RATE_BENCHMARKS["consultant"],
                self.LABOR_RATE_BENCHMARKS["analyst"],
            ])
        
        return relevant
    
    def _calculate_recommended_price(
        self,
        benchmark: Optional[ContractValueBenchmark],
        estimated_min: Optional[Decimal],
        estimated_max: Optional[Decimal],
        labor_mix: Optional[Dict[str, int]],
        labor_rates: List[LaborRateBenchmark],
    ) -> tuple[Decimal, Decimal]:
        """Calculate recommended price range."""
        
        # If government estimate provided, use it as anchor
        if estimated_max:
            # Recommend 85-100% of government estimate
            return (
                estimated_max * Decimal("0.85"),
                estimated_max * Decimal("1.00"),
            )
        
        # Use benchmark median as anchor
        if benchmark:
            return (
                benchmark.median_value * Decimal("0.8"),
                benchmark.median_value * Decimal("1.2"),
            )
        
        # Default fallback
        return (Decimal("250000"), Decimal("2500000"))
    
    def _determine_competitive_position(
        self,
        rec_min: Decimal,
        rec_max: Decimal,
        gov_estimate: Optional[Decimal],
        benchmark: Optional[ContractValueBenchmark],
    ) -> str:
        """Determine competitive positioning."""
        if gov_estimate:
            mid_price = (rec_min + rec_max) / 2
            ratio = mid_price / gov_estimate
            
            if ratio < Decimal("0.85"):
                return "aggressive"
            elif ratio < Decimal("0.95"):
                return "competitive"
            else:
                return "premium"
        
        return "competitive"
    
    def _calculate_confidence(
        self,
        benchmark: Optional[ContractValueBenchmark],
        labor_mix: Optional[Dict[str, int]],
    ) -> float:
        """Calculate confidence in pricing recommendation."""
        confidence = 0.5
        
        if benchmark:
            confidence += 0.2
            if benchmark.sample_size > 1000:
                confidence += 0.1
        
        if labor_mix:
            confidence += 0.15
        
        return min(0.95, confidence)
    
    def _generate_pricing_notes(
        self,
        benchmark: Optional[ContractValueBenchmark],
        gov_estimate: Optional[Decimal],
        position: str,
        opportunity: Dict[str, Any],
    ) -> List[str]:
        """Generate pricing guidance notes."""
        notes = []
        
        if gov_estimate:
            notes.append(f"Government estimate: ${gov_estimate:,.2f}")
        else:
            notes.append("No government estimate available - use benchmark data")
        
        if benchmark:
            notes.append(
                f"NAICS {benchmark.naics_code} median award: ${benchmark.median_value:,.2f} "
                f"(n={benchmark.sample_size})"
            )
        
        if opportunity.get("set_aside_type"):
            notes.append(f"Set-aside: {opportunity['set_aside_type']} - price competitiveness may vary")
        
        contract_type = opportunity.get("contract_type", "").lower()
        if "ffp" in contract_type or "firm fixed" in contract_type:
            notes.append("Firm Fixed Price - ensure all costs are captured in pricing")
        elif "t&m" in contract_type or "time and material" in contract_type:
            notes.append("T&M contract - focus on competitive labor rates")
        
        notes.append(f"Competitive position: {position.upper()}")
        
        return notes

