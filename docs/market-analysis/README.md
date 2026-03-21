# Market Analysis Framework

This directory contains the comprehensive market analysis framework for IdeaBot, originally developed by [Ron Haberman](https://github.com/habermanron) in [redhat-et/hermes PR #8](https://github.com/redhat-et/hermes/pull/8).

## Overview

The market analysis system provides rigorous, data-driven evaluation of technology ideas using a two-phase approach:

**Phase 1: Market Intelligence Gathering** - 9 investigation areas
**Phase 2: Multi-Dimensional Evaluation** - 5 assessment dimensions

## Files

### Investigation Prompts
- **[market-investigation-prompts.md](market-investigation-prompts.md)** - Detailed prompts for gathering market intelligence across 9 areas:
  1. TAM (Total Addressable Market)
  2. SAM (Serviceable Addressable Market)
  3. Competitive Landscape
  4. Red Hat Positioning
  5. Customer Buying Behavior
  6. Technology & Standards
  7. Investment & Resources
  8. Market Entry & GTM Strategy
  9. Risk & Dependencies

### Evaluation Prompts
- **[market-evaluation-prompts.md](market-evaluation-prompts.md)** - Scoring framework with 5 dimensions:
  1. **Market Opportunity** (0-9 points, pass ≥6)
     - Market size, strategic alignment, timing
  2. **Competitive Winability** (0-12 points, pass ≥8)
     - Differentiation, competitive position, GTM advantage, open source dynamics
  3. **Investment Feasibility** (0-12 points, pass ≥8)
     - Resource fit, ROI potential, cost to execute
  4. **Execution Risk** (0-15 points, pass ≤7) *Lower is better*
     - Technical, market, partnership, competitive response risks
  5. **Strategic Value** (0-15 points, pass ≥8)
     - Portfolio fit, ecosystem value, learning/capability building

### Documentation
- **[MARKET_ANALYSIS_INTEGRATION.md](MARKET_ANALYSIS_INTEGRATION.md)** - Integration guide and architecture
- **[MARKET_ANALYSIS_QUICK_REFERENCE.md](MARKET_ANALYSIS_QUICK_REFERENCE.md)** - Quick reference for scoring and thresholds

## TIER Recommendation System

Based on how many dimensions pass their thresholds:

| TIER | Criteria | Recommendation |
|------|----------|----------------|
| **TIER 1** | All 5 dimensions pass | **RECOMMEND STRONGLY** - Approve for OCTO prototyping |
| **TIER 2** | 4 of 5 dimensions pass | **RECOMMEND WITH CONDITIONS** - Approve with risk mitigation |
| **TIER 3** | 2-3 dimensions pass | **CONSIDER WITH CAUTION** - Request more investigation |
| **TIER 4** | 0-1 dimensions pass | **DO NOT RECOMMEND** - Reject or fundamentally rethink |

## Key Thresholds

- **Minimum SAM**: $500M+ (3-5 year projection)
- **Market Share Target**: 10%+ realistic achievable share
- **5-Year ARR Goal**: $50M+ minimum
- **Investment Constraint**: Must fit OCTO capacity (<50 engineer-months for prototype)

## Implementation

The market analysis is integrated into Hermes IdeaBot via the `MarketAgent` class in `agents/market_agent.py`. It uses a hybrid approach that consolidates the 9 investigations into a single comprehensive prompt, then performs the 5-dimensional evaluation.

### Usage in IdeaBot

1. User submits an idea through IdeaBot
2. Basic strategic evaluation is performed
3. If approved, user can optionally run "Market Analysis"
4. Market intelligence is gathered and evaluated
5. TIER 1-4 recommendation is generated
6. Results are displayed with detailed scores and findings

## Credit

This framework was originally developed by Ron Haberman for the standalone IdeaBot application and has been integrated into the Hermes ProtoBot system.

Original PR: https://github.com/redhat-et/hermes/pull/8
