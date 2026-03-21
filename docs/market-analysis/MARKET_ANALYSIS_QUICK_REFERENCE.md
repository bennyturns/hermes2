# Market Analysis Quick Reference

## Investigation Prompts (9 total)

| # | Investigation Area | Key Outputs | Time Est. |
|---|-------------------|-------------|-----------|
| 1 | TAM (Total Addressable Market) | Market size ($USD), growth rate (CAGR), segments | 2 min |
| 2 | SAM (Serviceable Addressable Market) | Red Hat addressable portion, constraints | 2 min |
| 3 | Competitive Landscape | Top competitors, market share, competitive intensity | 3 min |
| 4 | Red Hat Positioning | Current position, strengths, gaps, IBM synergies | 3 min |
| 5 | Customer Buying Behavior | Buyer personas, sales cycle, deal sizes, criteria | 2 min |
| 6 | Technology & Standards | Key standards, open source projects, dependencies | 2 min |
| 7 | Investment & Resources | Required investment, Red Hat capacity, ROI timeline | 3 min |
| 8 | Market Entry & GTM | Go-to-market strategy, pricing, partnerships | 3 min |
| 9 | Risk & Dependencies | Critical success factors, risks, dependencies | 3 min |

**Total Investigation Time:** ~25 minutes

## Evaluation Prompts (6 total)

| # | Evaluation Area | Scoring | Pass Threshold | Key Question |
|---|----------------|---------|----------------|--------------|
| 1 | Market Opportunity | 0-9 pts | ≥6 pts | Is this a material opportunity ($500M+ SAM)? |
| 2 | Competitive Winability | 0-12 pts | ≥8 pts | Can we win 10%+ market share? |
| 3 | Investment Feasibility | 0-12 pts | ≥8 pts | Can we afford it and get $50M+ ARR? |
| 4 | Execution Risk | 0-15 pts | ≤7 pts | Are risks manageable? (lower is better) |
| 5 | Strategic Value | 0-15 pts | ≥8 pts | Does this have strategic value beyond revenue? |
| 6 | Final Recommendation | - | 3/5 pass | Synthesize into TIER 1-4 recommendation |

**Total Evaluation Time:** ~15 minutes

## Decision Tiers

| Tier | Recommendation | Criteria | Action |
|------|---------------|----------|--------|
| **TIER 1** | **STRONGLY RECOMMEND** | 5/5 thresholds passed, no critical risks | Approve for OCTO prototyping |
| **TIER 2** | **RECOMMEND WITH CONDITIONS** | 4/5 thresholds passed, risks manageable | Approve with mitigations |
| **TIER 3** | **INVESTIGATE FURTHER** | 3/5 thresholds passed, significant unknowns | Pilot/spike before commitment |
| **TIER 4** | **DO NOT RECOMMEND** | <3 thresholds passed, critical issues | Reject |

## Key Thresholds

### Market Size
- **Minimum SAM:** $500M+ (3-5 year horizon)
- **Minimum TAM Growth:** 15%+ CAGR
- **Red Hat Market Impact:** 5%+ growth to addressable market

### Market Share
- **Success:** 10-15% share
- **Strong Success:** 20-25% share
- **Category Leadership:** 30%+ share

### Financial Returns
- **Minimum 5-Year ARR:** $50M+
- **Payback Period:** <5 years
- **Investment Efficiency:** High leverage through open source/partnerships preferred

### Investment Capacity
- **OCTO Prototype:** <50 engineer-months
- **Time to MVP:** 12-24 months
- **R&D % of Revenue:** Must be reasonable for market opportunity

## Scoring Summary

| Assessment | Max Score | Pass Threshold | Weight |
|-----------|-----------|----------------|--------|
| Market Opportunity | 9 | ≥6 | Critical |
| Competitive Winability | 12 | ≥8 | Critical |
| Investment Feasibility | 12 | ≥8 | Critical |
| Execution Risk | 15 | ≤7 | Critical |
| Strategic Value | 15 | ≥8 | Important |

**Minimum to Approve:** Pass at least 3 out of 5 critical assessments

## Risk Flags

**AUTOMATIC REJECTION if ANY of:**
- Critical execution risk (score of 3 in any risk category)
- No clear path to $50M+ ARR within 5 years
- SAM < $500M
- Cannot achieve 10%+ market share
- Beyond OCTO's investment capacity with no clear commercialization path

**PROCEED WITH CAUTION if ANY of:**
- Passes only 3 out of 5 assessments
- Execution risk score 6-7 (near threshold)
- Market share projection 10-12% (barely viable)
- Requires scarce/expensive skills
- High dependency on third parties

**STRONG CANDIDATE if ALL of:**
- Passes 5 out of 5 assessments
- Multiple assessments score in top quartile
- Clear differentiation through open source
- Leverages existing Red Hat strengths
- 20%+ market share achievable

## Implementation Modes

### Quick Mode (~10 min)
- Consolidated prompt combining key investigations
- Single evaluation with recommendation
- Use for: Initial screening, low-investment ideas

### Balanced Mode (~40 min)
- Combined market intelligence phase
- Structured evaluation phase
- Use for: Most ideas requiring market analysis

### Comprehensive Mode (~60-90 min)
- All 9 investigations separately
- All 6 evaluations separately
- Use for: High-stakes decisions, board-level approval

## API Usage

### Basic Evaluation (existing)
```bash
POST /api/submit
{
  "name": "...",
  "idea": "...",
  # ... other fields
}
```

### With Market Analysis (new)
```bash
POST /api/submit?market_analysis=true
{
  "name": "...",
  "idea": "...",
  # ... other fields
}
```

### Retroactive Analysis (new)
```bash
POST /api/market-analysis/{dashboard_id}
```

## Cost Estimates

| Mode | Tokens | Cost | Time |
|------|--------|------|------|
| Basic Evaluation | ~2K | $0.01 | 30s |
| Quick Market Analysis | ~20K | $0.10 | 10m |
| Balanced Market Analysis | ~60K | $0.30 | 40m |
| Comprehensive Market Analysis | ~120K | $0.60 | 90m |

**Note:** Costs based on Claude Sonnet 4 pricing. Actual costs may vary.

## Example Output Structure

```json
{
  "recommendation_tier": "TIER 1",
  "overall_recommendation": "STRONGLY RECOMMEND",

  "thresholds_passed": "5 out of 5",

  "market_projections": {
    "tam_current_usd_millions": 15000,
    "sam_3yr_usd_millions": 3500,
    "realistic_market_share_pct": 18,
    "projected_5yr_arr_millions": 630
  },

  "assessment_scores": {
    "market_opportunity": {"score": 8, "passed": true},
    "competitive_winability": {"score": 10, "passed": true},
    "investment_feasibility": {"score": 9, "passed": true},
    "execution_risk": {"score": 4, "passed": true},
    "strategic_value": {"score": 12, "passed": true}
  },

  "key_strengths": [
    "Large and growing market ($3.5B SAM by year 3)",
    "Strong open source differentiation opportunity",
    "Leverages existing OpenShift customer base"
  ],

  "key_concerns": [
    "Requires new GPU acceleration expertise",
    "Competitive response from cloud providers likely"
  ],

  "next_steps": [
    "Secure design partner customers (3-5 enterprises)",
    "Build prototype on MOC research cloud",
    "Align with OpenShift AI product team on transfer"
  ],

  "confidence_level": "high"
}
```

## File References

- **Investigation Prompts:** `market-investigation-prompts.md`
- **Evaluation Prompts:** `market-evaluation-prompts.md`
- **Integration Guide:** `MARKET_ANALYSIS_INTEGRATION.md`
- **Context Files:** `octo-definition.md`, `strategic-focus.txt`
