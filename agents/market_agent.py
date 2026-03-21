"""
Market Analysis Agent - Comprehensive Market Intelligence and Evaluation

Provides market analysis for IdeaBot submissions with:
- Market intelligence gathering (TAM, SAM, competitive landscape, etc.)
- Multi-dimensional evaluation (market opportunity, winability, feasibility, risk, strategic value)
- TIER 1-4 recommendations based on comprehensive scoring
"""

import logging
import json
from typing import Dict, Any

from vertex_client import vertex_client
from config import settings

logger = logging.getLogger(__name__)


class MarketAgent:
    """
    Market Analysis Agent for IdeaBot execution.

    Responsibilities:
    - Gather comprehensive market intelligence (9 investigation areas)
    - Evaluate market opportunity with 5-dimensional scoring
    - Generate TIER 1-4 recommendations
    - Provide detailed analysis for decision-making
    """

    def __init__(self):
        pass

    async def gather_market_intelligence(self, submission_data: Dict[str, Any], octo_definition: str, strategic_focus: str) -> Dict:
        """
        Phase 1: Gather comprehensive market intelligence.

        Investigates 9 key market areas:
        1. TAM (Total Addressable Market)
        2. SAM (Serviceable Addressable Market)
        3. Competitive Landscape
        4. Red Hat Positioning
        5. Customer Buying Behavior
        6. Technology & Standards
        7. Investment & Resources
        8. Market Entry & GTM
        9. Risk & Dependencies

        Args:
            submission_data: Dict with project/idea details
            octo_definition: OCTO mission and definition
            strategic_focus: Strategic focus areas

        Returns:
            Dict with market intelligence data
        """

        prompt = f"""You are a comprehensive market research analyst investigating a technology idea for Red Hat's Office of the CTO (OCTO).

OCTO DEFINITION:
{octo_definition}

STRATEGIC FOCUS AREAS:
{strategic_focus}

IDEA SUBMISSION:
- Name: {submission_data.get('name', 'N/A')}
- Project Name: {submission_data.get('project_name', 'N/A')}
- Idea: {submission_data.get('idea', 'N/A')}
- Market Relevance: {submission_data.get('market_relevance', 'N/A')}
- Strategic Priority: {submission_data.get('strategic_priority', 'N/A')}
- Catcher Product: {submission_data.get('catcher_product', 'N/A')}

Conduct a comprehensive market intelligence investigation covering these 9 areas:

1. TAM (Total Addressable Market): Global market size, growth rate (CAGR), segments, trends
2. SAM (Serviceable Addressable Market): Red Hat's addressable portion given open source/enterprise focus
3. Competitive Landscape: Top players, market share, competitive intensity, open source vs proprietary
4. Red Hat Positioning: Current position, strengths, gaps, IBM synergies
5. Customer Buying Behavior: Buyer personas, sales cycle, deal sizes, evaluation criteria
6. Technology & Standards: Key standards, open source projects, dependencies, maturity
7. Investment & Resources: Required investment, Red Hat's capacity (OCTO: 1% of Global Engineering), ROI
8. Market Entry & GTM: Go-to-market strategy, pricing models, partnerships, channels
9. Risk & Dependencies: Critical success factors, risks (technical, market, partnership, competitive)

Provide your analysis in the following JSON format:
{{
  "tam": {{
    "current_usd_millions": <number>,
    "projected_3yr_usd_millions": <number>,
    "cagr_pct": <number>,
    "key_segments": ["segment1", "segment2"],
    "trends": ["trend1", "trend2"],
    "confidence": "high/medium/low"
  }},
  "sam": {{
    "current_usd_millions": <number>,
    "projected_3yr_usd_millions": <number>,
    "sam_as_pct_of_tam": <number>,
    "addressable_segments": ["segment1"],
    "non_addressable_segments": ["segment1"],
    "constraints": ["constraint1"],
    "confidence": "high/medium/low"
  }},
  "competitive_landscape": {{
    "top_competitors": [{{"name": "CompanyX", "market_share_pct": 25, "type": "proprietary/open source"}}],
    "competitive_intensity": "low/medium/high",
    "open_source_advantage": "strong/moderate/weak/none",
    "barriers_to_entry": ["barrier1"]
  }},
  "redhat_positioning": {{
    "current_position": "leader/player/new entrant/none",
    "strengths": [{{"area": "strength1", "rating": 1-5}}],
    "gaps": [{{"area": "gap1", "rating": 1-5}}],
    "ibm_synergies": "strong/moderate/weak/negative"
  }},
  "customer_buying": {{
    "buyer_personas": ["CTO", "VP Engineering"],
    "sales_cycle_months": <number>,
    "avg_deal_size_usd": <number>,
    "top_criteria": ["criterion1", "criterion2"],
    "purchase_motion": "top-down/bottom-up/hybrid"
  }},
  "technology": {{
    "key_standards": ["standard1"],
    "critical_open_source_projects": ["project1"],
    "dependencies": ["dependency1"],
    "maturity": "emerging/growing/mature/declining",
    "interoperability_importance": "critical/important/minor"
  }},
  "investment": {{
    "estimated_prototype_engineer_months": <number>,
    "time_to_mvp_months": <number>,
    "ongoing_annual_investment_usd_millions": <number>,
    "redhat_capacity_assessment": "well within/challenging/requires stretch/beyond capacity",
    "leverage_opportunities": ["open source", "partnerships"]
  }},
  "market_entry": {{
    "recommended_gtm": "direct enterprise/cloud marketplace/partnerships/community-led",
    "pricing_model": "subscription/consumption/perpetual/hybrid",
    "cac_estimate_usd": <number>,
    "partnership_opportunities": ["partner1"],
    "ecosystem_requirements": ["requirement1"]
  }},
  "risks": {{
    "critical_success_factors": ["factor1", "factor2", "factor3"],
    "technical_risks": [{{"risk": "risk1", "severity": "low/medium/high/critical"}}],
    "market_risks": [{{"risk": "risk1", "severity": "low/medium/high/critical"}}],
    "partnership_risks": [{{"risk": "risk1", "severity": "low/medium/high/critical"}}],
    "competitive_response_risks": [{{"risk": "risk1", "severity": "low/medium/high/critical"}}]
  }},
  "summary": "Executive summary of market intelligence findings"
}}

Be thorough and realistic. Base estimates on actual market data where possible, and clearly indicate confidence levels."""

        try:
            response = await vertex_client.create_message_with_retry(
                system="You are a market research analyst providing data-driven market intelligence for technology investments.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=8192
            )

            response_text = response.content[0].text

            # Parse JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            market_intel = json.loads(response_text)
            logger.info("Market intelligence gathered successfully")
            return market_intel

        except Exception as e:
            logger.error(f"Error gathering market intelligence: {e}")
            raise

    async def evaluate_market_opportunity(self, submission_data: Dict[str, Any], market_intel: Dict, octo_definition: str, strategic_focus: str) -> Dict:
        """
        Phase 2: Evaluate market opportunity and generate TIER 1-4 recommendation.

        5-Dimensional Evaluation:
        1. Market Opportunity (0-9): market size, strategic alignment, timing
        2. Competitive Winability (0-12): differentiation, competitive position, GTM advantage
        3. Investment Feasibility (0-12): resource requirements, ROI, capacity fit
        4. Execution Risk (0-15): technical, market, partnership, competitive risks (lower is better)
        5. Strategic Value (0-15): portfolio fit, ecosystem, learning value

        TIER Recommendations:
        - TIER 1: RECOMMEND STRONGLY - All dimensions pass, high confidence
        - TIER 2: RECOMMEND WITH CONDITIONS - Most pass, some concerns
        - TIER 3: CONSIDER WITH CAUTION - Mixed results, significant concerns
        - TIER 4: DO NOT RECOMMEND - Fails key dimensions

        Args:
            submission_data: Project/idea details
            market_intel: Market intelligence from Phase 1
            octo_definition: OCTO mission
            strategic_focus: Strategic focus areas

        Returns:
            Dict with scores, recommendation tier, and executive summary
        """

        market_intel_summary = json.dumps(market_intel, indent=2)

        prompt = f"""You are a strategic investment analyst evaluating a technology opportunity for Red Hat's Office of the CTO (OCTO).

OCTO DEFINITION:
{octo_definition}

STRATEGIC FOCUS AREAS:
{strategic_focus}

IDEA SUBMISSION:
- Name: {submission_data.get('name', 'N/A')}
- Project Name: {submission_data.get('project_name', 'N/A')}
- Idea: {submission_data.get('idea', 'N/A')}
- Strategic Priority: {submission_data.get('strategic_priority', 'N/A')}

MARKET INTELLIGENCE:
{market_intel_summary}

Evaluate this opportunity using 5 dimensions and provide a TIER 1-4 recommendation:

**1. Market Opportunity (0-9 points, pass ≥6)**
- Market Size (0-3): TAM/SAM size, growth rate
- Strategic Alignment (0-3): Fit with OCTO mission and strategic focus
- Market Timing (0-3): Entry timing, market maturity

**2. Competitive Winability (0-12 points, pass ≥8)**
- Differentiation (0-3): Unique value proposition vs competitors
- Competitive Intensity (0-3): Ability to win against competitors
- GTM Advantage (0-3): Go-to-market strength
- Open Source Dynamics (0-3): Open source positioning advantage

**3. Investment Feasibility (0-12 points, pass ≥8)**
- Resource Fit (0-4): Within OCTO capacity
- ROI Potential (0-4): Return on investment timeline
- Cost to Execute (0-4): Reasonable cost structure

**4. Execution Risk (0-15 points, pass ≤7) - Lower is better**
- Technical Risk (0-4): Technology maturity, dependencies
- Market Risk (0-4): Market changes, adoption challenges
- Partnership Risk (0-3): Dependency on partners
- Competitive Response Risk (0-4): Competitor reactions

**5. Strategic Value (0-15 points, pass ≥8)**
- Portfolio Fit (0-5): Complements existing offerings
- Ecosystem Value (0-5): Strengthens Red Hat ecosystem
- Learning/Capability (0-5): Builds strategic capabilities

**TIER RECOMMENDATIONS:**
- TIER 1: RECOMMEND STRONGLY - All 5 dimensions pass thresholds
- TIER 2: RECOMMEND WITH CONDITIONS - 4 of 5 pass, one manageable concern
- TIER 3: CONSIDER WITH CAUTION - 2-3 pass, significant concerns
- TIER 4: DO NOT RECOMMEND - Fails most dimensions

**KEY THRESHOLDS:**
- Minimum SAM: $500M+ (3-5 years)
- Realistic Market Share: 10%+ achievable
- 5-Year ARR Target: $50M+ minimum
- Investment: Must fit OCTO capacity (<50 engineer-months for prototype)

Provide your evaluation in this JSON format:
{{
  "recommendation_tier": "TIER 1/TIER 2/TIER 3/TIER 4",
  "overall_recommendation": "RECOMMEND STRONGLY/RECOMMEND WITH CONDITIONS/CONSIDER WITH CAUTION/DO NOT RECOMMEND",
  "assessment_scores": {{
    "market_opportunity": {{
      "market_size_score": <0-3>,
      "strategic_alignment_score": <0-3>,
      "market_timing_score": <0-3>,
      "total_score": <0-9>,
      "passed": true/false
    }},
    "competitive_winability": {{
      "differentiation_score": <0-3>,
      "competitive_intensity_score": <0-3>,
      "gtm_advantage_score": <0-3>,
      "open_source_dynamics_score": <0-3>,
      "total_score": <0-12>,
      "realistic_market_share_pct": <number>,
      "passed": true/false
    }},
    "investment_feasibility": {{
      "resource_fit_score": <0-4>,
      "roi_potential_score": <0-4>,
      "cost_to_execute_score": <0-4>,
      "total_score": <0-12>,
      "projected_3yr_arr_millions": <number>,
      "projected_5yr_arr_millions": <number>,
      "passed": true/false
    }},
    "execution_risk": {{
      "technical_risk_score": <0-4>,
      "market_risk_score": <0-4>,
      "partnership_risk_score": <0-3>,
      "competitive_response_risk_score": <0-4>,
      "total_score": <0-15>,
      "passed": true/false
    }},
    "strategic_value": {{
      "portfolio_fit_score": <0-5>,
      "ecosystem_value_score": <0-5>,
      "learning_capability_score": <0-5>,
      "total_score": <0-15>,
      "passed": true/false
    }}
  }},
  "pass_fail_summary": {{
    "dimensions_passed": <number>,
    "dimensions_failed": <number>,
    "threshold_analysis": "Brief analysis of pass/fail vs thresholds"
  }},
  "key_findings": {{
    "strengths": ["strength1", "strength2", "strength3"],
    "concerns": ["concern1", "concern2"],
    "conditions": ["condition1", "condition2"]
  }},
  "recommendation_rationale": "1-2 paragraph rationale for the TIER recommendation",
  "executive_summary": "Concise executive summary suitable for decision-makers",
  "confidence_level": "high/medium/low"
}}

Be rigorous and data-driven. Base scores on the market intelligence provided."""

        try:
            response = await vertex_client.create_message_with_retry(
                system="You are a strategic investment analyst providing rigorous market opportunity evaluation.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=8192
            )

            response_text = response.content[0].text

            # Parse JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            evaluation = json.loads(response_text)
            logger.info(f"Market evaluation complete: {evaluation.get('recommendation_tier')}")
            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating market opportunity: {e}")
            raise

    async def comprehensive_market_analysis(self, submission_data: Dict[str, Any], octo_definition: str, strategic_focus: str) -> Dict:
        """
        Run comprehensive two-phase market analysis.

        Phase 1: Gather Market Intelligence
        Phase 2: Evaluate and Recommend

        Args:
            submission_data: Project/idea details
            octo_definition: OCTO mission
            strategic_focus: Strategic focus areas

        Returns:
            Dict with market intelligence, evaluation, and recommendation
        """
        # Phase 1: Market Intelligence
        market_intel = await self.gather_market_intelligence(submission_data, octo_definition, strategic_focus)

        # Phase 2: Evaluation and Recommendation
        evaluation = await self.evaluate_market_opportunity(submission_data, market_intel, octo_definition, strategic_focus)

        # Combine results
        return {
            "market_intelligence": market_intel,
            "evaluation": evaluation,
            "approved": evaluation["recommendation_tier"] in ["TIER 1", "TIER 2"],
            "reasoning": evaluation.get("executive_summary", ""),
            "confidence": evaluation.get("confidence_level", "medium")
        }


# ============================================================================
# Global Agent Instance
# ============================================================================

# Singleton instance
market_agent = MarketAgent()
