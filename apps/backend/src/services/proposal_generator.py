"""
AI-Powered Proposal Generation Service

Uses GPT-4/Claude for contextual proposal section drafting:
- Executive summary generation
- Technical approach drafting
- Past performance narratives
- Management approach
- Compliance matrix population
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class ProposalSection:
    """Generated proposal section."""
    section_id: str
    title: str
    content: str
    word_count: int
    compliance_refs: List[str] = field(default_factory=list)
    confidence: float = 0.8


@dataclass
class GeneratedProposal:
    """Complete generated proposal."""
    opportunity_id: str
    organization_id: str
    sections: List[ProposalSection]
    compliance_matrix: Dict[str, Any]
    executive_summary: str
    total_word_count: int
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceMatrixItem:
    """Item in compliance matrix."""
    requirement_id: str
    requirement_text: str
    proposal_section: str
    compliance_status: str  # compliant, partial, non-compliant, na


class ProposalGenerator:
    """
    GPT-4/Claude Powered Proposal Generation Engine.
    
    Capabilities:
    - Executive summary generation
    - Technical approach drafting
    - Past performance narratives
    - Management approach
    - Compliance matrix population
    """
    
    SECTION_TEMPLATES = {
        "executive_summary": {
            "title": "Executive Summary",
            "max_words": 750,
            "system_prompt": "You are an expert federal proposal writer with 20 years of experience winning government contracts. Write compelling, compliant executive summaries.",
        },
        "technical_approach": {
            "title": "Technical Approach",
            "max_words": 2000,
            "system_prompt": "You are a technical proposal specialist. Write detailed, solution-oriented technical approaches that demonstrate deep understanding of requirements.",
        },
        "management_approach": {
            "title": "Management Approach",
            "max_words": 1500,
            "system_prompt": "You are a management proposal expert. Write clear management approaches covering organization, staffing, quality control, and risk management.",
        },
        "past_performance": {
            "title": "Past Performance",
            "max_words": 1000,
            "system_prompt": "You are a past performance narrative specialist. Write compelling past performance descriptions that demonstrate relevant experience and success.",
        },
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize proposal generator.
        
        Args:
            api_key: OpenAI API key (falls back to settings)
            model: Model to use for generation
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self._client = None
    
    async def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            if not self.api_key:
                logger.warning("No OpenAI API key configured")
                return None
            
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed")
                return None
        
        return self._client
    
    async def generate_proposal(
        self,
        opportunity: Dict[str, Any],
        organization: Dict[str, Any],
        sections: Optional[List[str]] = None,
    ) -> GeneratedProposal:
        """
        Generate complete proposal or specific sections.
        
        Args:
            opportunity: Opportunity data dictionary
            organization: Organization data dictionary
            sections: List of section types to generate (None = all)
            
        Returns:
            GeneratedProposal with all requested sections
        """
        if sections is None:
            sections = list(self.SECTION_TEMPLATES.keys())
        
        generated_sections = []
        
        # Generate sections in parallel
        tasks = [
            self._generate_section(section_type, opportunity, organization)
            for section_type in sections
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Section generation failed", error=str(result))
                continue
            generated_sections.append(result)
        
        # Generate compliance matrix
        compliance_matrix = await self._generate_compliance_matrix(opportunity)
        
        # Get executive summary (already generated or extract)
        exec_summary = next(
            (s.content for s in generated_sections if s.section_id == "executive_summary"),
            "Executive summary not generated"
        )
        
        return GeneratedProposal(
            opportunity_id=str(opportunity.get("id", "")),
            organization_id=str(organization.get("id", "")),
            sections=generated_sections,
            compliance_matrix=compliance_matrix,
            executive_summary=exec_summary,
            total_word_count=sum(s.word_count for s in generated_sections),
        )
    
    async def generate_section(
        self,
        section_type: str,
        opportunity: Dict[str, Any],
        organization: Dict[str, Any],
    ) -> ProposalSection:
        """
        Generate a single proposal section.
        
        Args:
            section_type: Type of section (executive_summary, technical_approach, etc.)
            opportunity: Opportunity data
            organization: Organization data
            
        Returns:
            ProposalSection with generated content
        """
        return await self._generate_section(section_type, opportunity, organization)
    
    async def _generate_section(
        self,
        section_type: str,
        opportunity: Dict[str, Any],
        organization: Dict[str, Any],
    ) -> ProposalSection:
        """Internal section generation logic."""
        template = self.SECTION_TEMPLATES.get(section_type)
        if not template:
            raise ValueError(f"Unknown section type: {section_type}")
        
        client = await self._get_client()
        
        if client is None:
            # Return template-based fallback content
            return self._generate_fallback_section(section_type, opportunity, organization)
        
        prompt = self._build_prompt(section_type, opportunity, organization)
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": template["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=template["max_words"] * 2,  # Tokens != words
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            return ProposalSection(
                section_id=section_type,
                title=template["title"],
                content=content,
                word_count=len(content.split()),
                compliance_refs=self._extract_compliance_refs(content),
                confidence=0.85,
            )
            
        except Exception as e:
            logger.error(f"Error generating {section_type}", error=str(e))
            return self._generate_fallback_section(section_type, opportunity, organization)
    
    def _build_prompt(
        self,
        section_type: str,
        opportunity: Dict[str, Any],
        organization: Dict[str, Any],
    ) -> str:
        """Build prompt for section generation."""
        
        if section_type == "executive_summary":
            return f"""
Generate an executive summary for a federal contract proposal.

OPPORTUNITY:
- Title: {opportunity.get('title', 'N/A')}
- Agency: {opportunity.get('contracting_office_name', 'N/A')}
- NAICS: {opportunity.get('naics_code', 'N/A')} - {opportunity.get('naics_description', '')}
- Contract Type: {opportunity.get('contract_type', 'N/A')}
- Set-Aside: {opportunity.get('set_aside_type', 'Full and Open')}
- Description: {opportunity.get('description', 'N/A')[:1000]}

ORGANIZATION:
- Name: {organization.get('name', 'Our Company')}
- Capabilities: {organization.get('capabilities_narrative', 'Professional services provider')[:500]}
- Relevant NAICS: {', '.join(organization.get('naics_codes', [])[:5])}
- Certifications: {', '.join(organization.get('set_aside_types', []))}

Write a compelling 500-700 word executive summary that:
1. Demonstrates clear understanding of the requirement
2. Highlights relevant experience and qualifications
3. Presents a clear value proposition
4. Uses confident, active voice
5. Avoids generic boilerplate

Do NOT include placeholder text like [Company Name] - use the actual organization name provided.
"""

        elif section_type == "technical_approach":
            return f"""
Generate a technical approach section for a federal contract proposal.

OPPORTUNITY:
- Title: {opportunity.get('title', 'N/A')}
- Description: {opportunity.get('description', 'N/A')[:1500]}
- NAICS: {opportunity.get('naics_code', 'N/A')} - {opportunity.get('naics_description', '')}

ORGANIZATION CAPABILITIES:
{organization.get('capabilities_narrative', 'Technical services provider')[:800]}

Write a detailed technical approach (1500-2000 words) that:
1. Addresses the stated requirements explicitly
2. Describes specific methodologies and tools
3. Includes clear deliverables and milestones
4. Demonstrates technical depth and innovation
5. Shows understanding of potential challenges and solutions

Structure with clear headings: Understanding, Approach, Methodology, Tools/Technologies, Quality Assurance.
"""

        elif section_type == "management_approach":
            return f"""
Generate a management approach section for a federal contract proposal.

OPPORTUNITY:
- Title: {opportunity.get('title', 'N/A')}
- Agency: {opportunity.get('contracting_office_name', 'N/A')}
- Period of Performance: TBD
- Location: {opportunity.get('place_of_performance_city', '')}, {opportunity.get('place_of_performance_state', '')}

ORGANIZATION:
- Name: {organization.get('name', 'Our Company')}
- Employee Count: {organization.get('employee_count', 'N/A')}

Write a management approach (1000-1500 words) covering:
1. Organizational structure and key personnel
2. Communication and reporting protocols
3. Quality control and assurance processes
4. Risk management approach
5. Staffing and transition planning

Include a description of roles and responsibilities.
"""

        elif section_type == "past_performance":
            return f"""
Generate a past performance narrative for a federal contract proposal.

OPPORTUNITY:
- Title: {opportunity.get('title', 'N/A')}
- NAICS: {opportunity.get('naics_code', 'N/A')} - {opportunity.get('naics_description', '')}
- Agency: {opportunity.get('contracting_office_name', 'N/A')}

ORGANIZATION PAST PERFORMANCE:
{organization.get('past_performance_summary', 'Experienced federal contractor with relevant contract history')[:1000]}

Write past performance narratives (800-1000 words) that:
1. Highlight 2-3 relevant contract examples
2. Demonstrate similar scope, complexity, and requirements
3. Include specific outcomes and metrics where possible
4. Show lessons learned and continuous improvement
5. Emphasize customer satisfaction and on-time delivery

Format as distinct project summaries with: Contract/Client, Relevance, Scope, Outcomes.
"""
        
        return "Generate proposal content based on provided context."
    
    def _generate_fallback_section(
        self,
        section_type: str,
        opportunity: Dict[str, Any],
        organization: Dict[str, Any],
    ) -> ProposalSection:
        """Generate template-based fallback content when AI is unavailable."""
        template = self.SECTION_TEMPLATES.get(section_type, {})
        org_name = organization.get('name', 'Our Organization')
        opp_title = opportunity.get('title', 'this opportunity')
        
        fallback_content = {
            "executive_summary": f"""
{org_name} is pleased to submit this proposal in response to {opp_title}.

Our organization brings extensive experience in the areas required by this solicitation. We understand the importance of this requirement to the agency and are committed to delivering exceptional results.

Key differentiators that make {org_name} the ideal choice include:
• Proven track record of successful federal contract performance
• Deep expertise in the relevant technical domains
• Commitment to quality, compliance, and customer satisfaction
• Agile and responsive project management approach

We look forward to the opportunity to demonstrate our capabilities and contribute to the agency's mission success.

[Note: This is a template summary. Full AI-generated content requires API configuration.]
""",
            "technical_approach": f"""
# Technical Approach

## Understanding of Requirements
{org_name} thoroughly understands the requirements outlined in this solicitation. Our approach is designed to meet and exceed all stated objectives.

## Methodology
Our proven methodology encompasses:
1. Requirements Analysis and Planning
2. Solution Design and Development
3. Implementation and Integration
4. Testing and Quality Assurance
5. Deployment and Transition
6. Ongoing Support and Optimization

## Tools and Technologies
We leverage industry-leading tools and technologies appropriate to the requirement.

## Quality Assurance
Our quality management system ensures consistent, high-quality deliverables.

[Note: This is a template approach. Full AI-generated content requires API configuration.]
""",
            "management_approach": f"""
# Management Approach

## Organization Structure
{org_name} will establish a dedicated project team with clear roles and responsibilities.

## Key Personnel
- Program Manager: Overall accountability
- Technical Lead: Technical direction and oversight
- Quality Manager: QA/QC processes

## Communication
Regular status reporting, weekly meetings, and responsive communication channels.

## Risk Management
Proactive risk identification, assessment, and mitigation strategies.

[Note: This is a template approach. Full AI-generated content requires API configuration.]
""",
            "past_performance": f"""
# Past Performance

{org_name} has successfully delivered similar contracts demonstrating our capability.

## Relevant Experience
Our past performance demonstrates:
• Successful delivery of comparable scope and complexity
• Strong customer satisfaction ratings
• On-time and on-budget performance
• Effective problem resolution

{organization.get('past_performance_summary', 'Contact us for detailed past performance references.')}

[Note: This is a template narrative. Full AI-generated content requires API configuration.]
""",
        }
        
        content = fallback_content.get(section_type, "Section content not available.")
        
        return ProposalSection(
            section_id=section_type,
            title=template.get("title", section_type.replace("_", " ").title()),
            content=content.strip(),
            word_count=len(content.split()),
            compliance_refs=[],
            confidence=0.4,  # Lower confidence for template content
        )
    
    def _extract_compliance_refs(self, content: str) -> List[str]:
        """Extract compliance references from generated content."""
        import re
        
        # Look for FAR/DFARS references
        far_pattern = r'FAR\s+\d+\.\d+'
        dfars_pattern = r'DFARS\s+\d+\.\d+'
        
        refs = []
        refs.extend(re.findall(far_pattern, content))
        refs.extend(re.findall(dfars_pattern, content))
        
        return list(set(refs))
    
    async def _generate_compliance_matrix(
        self,
        opportunity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate compliance matrix structure."""
        # In a full implementation, this would parse PWS/SOW requirements
        # For now, return a structured placeholder
        
        return {
            "total_requirements": 0,
            "addressed": 0,
            "compliance_rate": 0.0,
            "requirements": [],
            "note": "Full compliance matrix requires PWS/SOW parsing"
        }

