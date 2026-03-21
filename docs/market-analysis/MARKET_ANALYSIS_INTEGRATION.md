# Market Analysis Integration Guide

This guide explains how to integrate the market investigation and evaluation prompts into IdeaBot's decision workflow.

## Overview

IdeaBot now supports two levels of idea evaluation:

1. **Basic Evaluation** (Current): Fast strategic alignment check using OCTO definition and strategic focus
2. **Market Analysis Evaluation** (New): Comprehensive market opportunity and commercial viability assessment

## When to Use Market Analysis

Use the comprehensive market analysis for ideas that:
- Pass the basic strategic alignment evaluation
- Request significant investment (> 6 months, > 5 engineers)
- Target new market categories for Red Hat
- Have unclear commercial potential
- Require executive-level approval

## Architecture

```
Idea Submission
    ↓
Basic Strategic Evaluation
    ↓
[PASS] → Market Analysis Gate
    ↓
Market Investigation Phase (9 prompts)
    ├── TAM Investigation
    ├── SAM Investigation
    ├── Competitive Landscape
    ├── Red Hat Positioning
    ├── Customer Buying Behavior
    ├── Technology & Standards
    ├── Investment & Resources
    ├── Market Entry Strategy
    └── Risk & Dependencies
    ↓
Market Evaluation Phase (5 assessments + final recommendation)
    ├── Market Opportunity Assessment
    ├── Competitive Winability Assessment
    ├── Investment Feasibility Assessment
    ├── Execution Risk Assessment
    ├── Strategic Value Assessment
    └── Final Recommendation
    ↓
Approval Decision
    ├── TIER 1: Approve for OCTO prototyping
    ├── TIER 2: Approve with conditions
    ├── TIER 3: Request more investigation
    └── TIER 4: Reject
```

## Implementation Options

### Option 1: Sequential Mode (Recommended for thoroughness)

Execute all investigation prompts sequentially, then all evaluation prompts.

**Pros:**
- Most comprehensive analysis
- Best data quality for evaluations
- Clear audit trail

**Cons:**
- Slower (requires multiple API calls)
- Higher cost (more tokens)

**Implementation:**
```python
async def comprehensive_market_analysis(submission: IdeaSubmission):
    # Phase 1: Investigations
    investigations = await run_all_investigations(submission)

    # Phase 2: Evaluations
    evaluations = await run_all_evaluations(submission, investigations)

    # Phase 3: Final Recommendation
    recommendation = await generate_final_recommendation(
        submission, investigations, evaluations
    )

    return recommendation
```

### Option 2: Consolidated Mode (Faster)

Combine multiple prompts into a single comprehensive prompt.

**Pros:**
- Faster execution
- Lower API call count
- More cost-effective

**Cons:**
- May miss nuances
- Harder to debug individual assessments
- Requires larger context window

**Implementation:**
```python
async def consolidated_market_analysis(submission: IdeaSubmission):
    # Single comprehensive prompt with all investigation and evaluation aspects
    prompt = build_comprehensive_market_prompt(submission)

    response = await client.messages.create(
        model=model_name,
        max_tokens=8192,  # Larger for comprehensive response
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_comprehensive_response(response)
```

### Option 3: Hybrid Mode (Balanced)

Core investigations in one pass, detailed evaluations in second pass.

**Pros:**
- Balanced speed and thoroughness
- Good for most use cases

**Cons:**
- Moderate complexity

**Implementation:**
```python
async def hybrid_market_analysis(submission: IdeaSubmission):
    # Phase 1: Combined market intelligence gathering
    market_intel = await gather_market_intelligence(submission)

    # Phase 2: Structured evaluation and recommendation
    recommendation = await evaluate_and_recommend(submission, market_intel)

    return recommendation
```

## Integration with Existing evaluate_idea Function

### Current Flow
```python
async def evaluate_idea(submission: IdeaSubmission) -> Dict:
    """Evaluate using OCTO definition and strategic focus only."""
    # ... existing code ...
```

### Enhanced Flow
```python
async def evaluate_idea(
    submission: IdeaSubmission,
    include_market_analysis: bool = False
) -> Dict:
    """
    Evaluate the submitted idea.

    Args:
        submission: The idea submission data
        include_market_analysis: If True, perform comprehensive market analysis

    Returns:
        Evaluation results with approval decision
    """
    # Basic strategic evaluation (fast)
    basic_eval = await basic_strategic_evaluation(submission)

    if not basic_eval["approved"]:
        # Reject early if doesn't meet basic criteria
        return basic_eval

    # If market analysis requested and basic eval passes
    if include_market_analysis:
        market_analysis = await comprehensive_market_analysis(submission)

        # Combine basic and market analysis results
        return {
            "approved": market_analysis["recommendation_tier"] in ["TIER 1", "TIER 2"],
            "basic_evaluation": basic_eval,
            "market_analysis": market_analysis,
            "reasoning": market_analysis["executive_summary"],
            "confidence": market_analysis["confidence_level"]
        }

    # Return basic evaluation only
    return basic_eval
```

## Database Schema Extensions

Add market analysis results to the database:

```sql
-- Add column to dashboard table
ALTER TABLE dashboard ADD COLUMN market_analysis TEXT;

-- Create market analysis results table
CREATE TABLE IF NOT EXISTS market_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dashboard_id INTEGER,
    submission_id INTEGER,

    -- Market sizing
    tam_current_millions REAL,
    sam_current_millions REAL,
    sam_3yr_millions REAL,

    -- Projections
    realistic_market_share_pct REAL,
    projected_3yr_arr_millions REAL,
    projected_5yr_arr_millions REAL,

    -- Assessment scores
    market_opportunity_score INTEGER,
    competitive_winability_score INTEGER,
    investment_feasibility_score INTEGER,
    execution_risk_score INTEGER,
    strategic_value_score INTEGER,

    -- Recommendation
    recommendation_tier TEXT,
    overall_recommendation TEXT,
    confidence_level TEXT,

    -- Full results JSON
    investigation_results TEXT,
    evaluation_results TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (dashboard_id) REFERENCES dashboard(id)
);
```

## API Endpoint Extensions

### New Endpoint: Trigger Market Analysis

```python
@app.post("/api/market-analysis/{dashboard_id}")
async def run_market_analysis(dashboard_id: int):
    """
    Run comprehensive market analysis on an approved idea.

    This is useful for ideas that passed basic evaluation but need
    deeper market validation before significant investment.
    """
    # Retrieve the approved idea
    idea = get_dashboard_entry(dashboard_id)

    # Reconstruct submission from stored data
    submission = reconstruct_submission(idea)

    # Run market analysis
    analysis = await comprehensive_market_analysis(submission)

    # Store results
    store_market_analysis(dashboard_id, analysis)

    return {
        "status": "completed",
        "analysis": analysis
    }
```

### Enhanced Submit Endpoint

```python
@app.post("/api/submit")
async def submit_idea(
    submission: IdeaSubmission,
    market_analysis: bool = False
):
    """
    Submit and evaluate a new idea.

    Args:
        submission: Idea submission data
        market_analysis: Whether to include comprehensive market analysis
    """
    evaluation = await evaluate_idea(submission, include_market_analysis=market_analysis)

    # ... rest of existing code ...
```

## UI Enhancements

### Submission Form

Add optional checkbox:
```html
<div class="form-group">
    <label>
        <input type="checkbox" name="market_analysis" />
        Request comprehensive market analysis (takes longer, provides detailed commercial assessment)
    </label>
</div>
```

### Dashboard View

Add market analysis button for approved ideas:
```html
<button onclick="requestMarketAnalysis(${entry.id})">
    Run Market Analysis
</button>
```

### Market Analysis Report View

Create dedicated view to display:
- Market sizing (TAM, SAM, projections)
- Competitive positioning
- Investment requirements
- Risk assessment
- Success scenarios
- Final recommendation with confidence

## Prompt Context Files

The market analysis prompts can reference these context files:

**Existing:**
- `octo-definition.md` - OCTO's mission and charter
- `strategic-focus.txt` - Current strategic focus areas

**New (Optional):**
- `redhat-financials.md` - Red Hat revenue, budget, investment capacity
- `redhat-portfolio.md` - Current product portfolio and positioning
- `partner-ecosystem.md` - Key partnerships and ecosystem relationships
- `competitive-intelligence.md` - Known competitors and market dynamics

## Cost Considerations

Market analysis is significantly more expensive than basic evaluation:

- **Basic Evaluation**: ~2,000 tokens, $0.01 per evaluation
- **Market Analysis**: ~50,000-100,000 tokens, $0.50-$1.00 per evaluation

**Recommendations:**
- Use basic evaluation for all submissions (filter out obvious misalignments)
- Use market analysis selectively for high-potential ideas
- Consider caching investigation results for similar idea categories
- Implement rate limiting to prevent abuse

## Testing

Create test cases for different scenarios:

```python
# Test cases
test_ideas = [
    {
        "name": "Strong opportunity - should be TIER 1",
        "characteristics": "Large TAM, weak competition, clear Red Hat advantage"
    },
    {
        "name": "Risky opportunity - should be TIER 2",
        "characteristics": "Good market, strong competition, requires partnership"
    },
    {
        "name": "Uncertain opportunity - should be TIER 3",
        "characteristics": "Unclear market size, novel technology, needs validation"
    },
    {
        "name": "Poor opportunity - should be TIER 4",
        "characteristics": "Small market, strong incumbents, poor strategic fit"
    }
]
```

## Next Steps

1. **Immediate**: Review and validate the investigation and evaluation prompts
2. **Short-term**: Implement basic integration (Option 3: Hybrid Mode recommended)
3. **Medium-term**: Add database schema and API endpoints
4. **Long-term**: Build comprehensive UI for market analysis reports

## References

- `market-investigation-prompts.md` - 9 investigation prompts for market intelligence gathering
- `market-evaluation-prompts.md` - 6 evaluation prompts including final recommendation
- `main.py` - Current IdeaBot implementation
- `strategic-focus.txt` - Strategic focus areas for alignment
- `octo-definition.md` - OCTO mission and operational model
