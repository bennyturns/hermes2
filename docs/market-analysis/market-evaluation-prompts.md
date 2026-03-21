# Market Evaluation Prompts

These prompts evaluate the market opportunity and Red Hat's probability of success based on the investigation data gathered from the market-investigation-prompts. Execute these after completing all investigations.

---

## 1. Market Opportunity Assessment

You are evaluating whether this represents a material market opportunity for Red Hat.

**Context Required:**
- TAM and SAM investigation results
- Strategic focus areas alignment
- Red Hat's revenue scale and growth targets

**Evaluation Criteria:**

### Market Size Threshold
- Is the SAM at least $500M+ within 3-5 years?
- Does this represent at least 5% potential growth to Red Hat's addressable market?
- Is the TAM growing at 15%+ CAGR or higher?

### Strategic Alignment
- Does this market directly align with Red Hat's strategic focus areas (AI, hybrid cloud, open source)?
- Does this support or extend Red Hat's platform strategy?
- Does this protect or expand an existing strategic position?

### Market Timing
- Is the market mature enough to generate revenue within OCTO's 12-36 month horizon?
- Is Red Hat entering early enough to influence standards and ecosystem?
- Are we too early (market not ready) or too late (market consolidated)?

**Scoring:**
Rate each criterion as:
- **Strong Opportunity** (3 points): Clear positive indicators
- **Moderate Opportunity** (2 points): Mixed signals or acceptable threshold
- **Weak Opportunity** (1 point): Below threshold or negative indicators
- **No Opportunity** (0 points): Clear disqualifier

**Minimum Threshold:** 6 out of 9 points to proceed

**Output Format:**
```json
{
  "market_size_score": 0-3,
  "strategic_alignment_score": 0-3,
  "market_timing_score": 0-3,
  "total_score": 0-9,
  "passes_threshold": true/false,
  "market_opportunity_assessment": "detailed rationale",
  "confidence": "high/medium/low"
}
```

---

## 2. Competitive Winability Assessment

You are evaluating Red Hat's ability to win meaningful market share against competition.

**Context Required:**
- Competitive landscape investigation
- Red Hat positioning and capability investigation
- Customer buying behavior investigation

**Evaluation Criteria:**

### Differentiation Potential
- Can Red Hat create meaningful differentiation through open source?
- Are there unique Red Hat assets (community, IP, partnerships) that competitors lack?
- Can Red Hat leverage the IBM relationship for competitive advantage?
- Score: 3 = Strong differentiation possible, 2 = Moderate, 1 = Weak, 0 = None

### Competitive Intensity
- Is this a fragmented market (5+ meaningful players) vs. consolidated (1-2 dominant)?
- Are there open source alternatives that can level the playing field?
- What is the cost for customers to switch or multi-source?
- Score: 3 = Favorable intensity, 2 = Moderate, 1 = Difficult, 0 = Impossible

### Go-to-Market Advantage
- Does this leverage Red Hat's existing enterprise relationships?
- Can Red Hat bundle this with existing products to create value?
- Is the buying persona someone Red Hat already sells to?
- Score: 3 = Strong GTM fit, 2 = Moderate fit, 1 = New motion required, 0 = Complete mismatch

### Open Source Dynamics
- Is open source a credible alternative to proprietary solutions in this market?
- Will customers value open source for this use case (avoiding lock-in, transparency, etc.)?
- Can Red Hat lead or significantly contribute to the key open source projects?
- Score: 3 = Open source is a winner, 2 = Competitive, 1 = Minor factor, 0 = Irrelevant/liability

**Target Market Share:**
- **Realistic:** Can Red Hat achieve 10%+ market share within 3-5 years?
- **Aspirational:** Is 20%+ market share achievable with strong execution?

**Minimum Threshold:** 8 out of 12 points AND realistic market share ≥10%

**Output Format:**
```json
{
  "differentiation_score": 0-3,
  "competitive_intensity_score": 0-3,
  "gtm_advantage_score": 0-3,
  "open_source_dynamics_score": 0-3,
  "total_score": 0-12,
  "realistic_market_share_pct": 0-100,
  "aspirational_market_share_pct": 0-100,
  "passes_threshold": true/false,
  "competitive_winability_assessment": "detailed rationale",
  "key_competitive_risks": ["risk1", "risk2", "risk3"],
  "confidence": "high/medium/low"
}
```

---

## 3. Investment Feasibility Assessment

You are evaluating whether Red Hat has the capacity and willingness to make the required investment.

**Context Required:**
- Investment & resource investigation
- OCTO's charter (1% of Global Engineering, 12-36 month prototypes)
- Technology transfer requirements

**Evaluation Criteria:**

### Initial Investment Scope
- Can a meaningful prototype be developed within OCTO's resources (< 50 engineer-months)?
- Can minimum viable product be delivered in 12-24 months?
- Is the technical complexity manageable for rapid prototyping?
- Score: 3 = Well within capacity, 2 = Challenging but feasible, 1 = Requires stretching, 0 = Beyond capacity

### Commercialization Investment
- Is there a clear product team to receive the technology transfer?
- Is the ongoing engineering investment reasonable for the market opportunity (R&D % of revenue)?
- Can this be staffed with available skills, or are scarce/expensive specialists required?
- Score: 3 = Clear path and capacity, 2 = Requires planning, 1 = Difficult, 0 = Not feasible

### Investment Efficiency
- Can Red Hat leverage existing open source projects vs. building from scratch?
- Are there partnership opportunities to share investment burden?
- Can this extend existing Red Hat products vs. requiring net-new development?
- Score: 3 = High leverage, 2 = Moderate leverage, 1 = Low leverage, 0 = No leverage

### Opportunity Cost
- What would be displaced to pursue this (other OCTO projects, product roadmap priorities)?
- Is this more valuable than alternative uses of the investment?
- Does this create strategic options that justify the investment even if direct ROI is unclear?
- Score: 3 = Clearly best use, 2 = Competitive with alternatives, 1 = Questionable, 0 = Better alternatives exist

**ROI Expectations:**
- Can this generate $50M+ ARR within 5 years to justify the investment?
- Is the investment payback period acceptable (< 5 years)?

**Minimum Threshold:** 8 out of 12 points AND ROI ≥ $50M ARR

**Output Format:**
```json
{
  "initial_investment_score": 0-3,
  "commercialization_investment_score": 0-3,
  "investment_efficiency_score": 0-3,
  "opportunity_cost_score": 0-3,
  "total_score": 0-12,
  "estimated_prototype_cost_months": 0-100,
  "estimated_5yr_arr_millions": 0-1000,
  "investment_payback_years": 0-10,
  "passes_threshold": true/false,
  "investment_feasibility_assessment": "detailed rationale",
  "critical_resource_gaps": ["gap1", "gap2"],
  "confidence": "high/medium/low"
}
```

---

## 4. Execution Risk Assessment

You are evaluating the risks that could prevent successful execution.

**Context Required:**
- Risk & dependency investigation
- Technology & standards investigation
- Market entry & commercialization investigation

**Evaluation Criteria:**

### Technical Execution Risk
- Is the technology mature enough to build on (not bleeding edge)?
- Are dependencies on upstream projects stable and reliable?
- Does Red Hat have or can acquire the necessary technical expertise?
- Risk Level: **Low** (0 points) / **Medium** (1 point) / **High** (2 points) / **Critical** (3 points)

### Market Execution Risk
- Is customer demand validated or speculative?
- Is the product/market fit clear or requires discovery?
- Are there proven reference customers or design partners available?
- Risk Level: **Low** (0 points) / **Medium** (1 point) / **High** (2 points) / **Critical** (3 points)

### Partnership Risk
- Are critical dependencies controlled by Red Hat or in trusted hands?
- Could third-party decisions kill the initiative (cloud providers, hardware vendors, etc.)?
- Are there single points of failure in the ecosystem?
- Risk Level: **Low** (0 points) / **Medium** (1 point) / **High** (2 points) / **Critical** (3 points)

### Competitive Response Risk
- Will incumbents respond aggressively if Red Hat succeeds (pricing, FUD, exclusivity)?
- Could competitors block Red Hat through standards bodies or ecosystem control?
- Are there patent or IP landmines?
- Risk Level: **Low** (0 points) / **Medium** (1 point) / **High** (2 points) / **Critical** (3 points)

### Organizational Risk
- Is there organizational commitment to see this through commercialization?
- Are there internal political or cultural barriers?
- Does this require significant organizational change?
- Risk Level: **Low** (0 points) / **Medium** (1 point) / **High** (2 points) / **Critical** (3 points)

**Risk Scoring:**
- Lower is better (0 = lowest risk, 15 = highest risk)
- **Any Critical (3) risk is a potential showstopper**

**Maximum Acceptable Risk:** 7 out of 15 points AND no Critical (3) risks

**Output Format:**
```json
{
  "technical_risk_score": 0-3,
  "market_risk_score": 0-3,
  "partnership_risk_score": 0-3,
  "competitive_response_risk_score": 0-3,
  "organizational_risk_score": 0-3,
  "total_risk_score": 0-15,
  "has_critical_risks": true/false,
  "passes_threshold": true/false,
  "execution_risk_assessment": "detailed rationale",
  "critical_risks": ["risk1", "risk2"],
  "mitigation_strategies": ["strategy1", "strategy2"],
  "risk_level": "low/medium/high/critical",
  "confidence": "high/medium/low"
}
```

---

## 5. Strategic Value Assessment

You are evaluating the strategic value beyond direct revenue potential.

**Context Required:**
- OCTO's mission and strategic focus
- Red Hat's platform and ecosystem strategy
- Competitive positioning objectives

**Evaluation Criteria:**

### Platform Value
- Does this strengthen Red Hat's platform position (OpenShift, RHEL, AAP)?
- Does this create new platform extension opportunities?
- Does this increase customer lock-in or switching costs (in a positive way)?
- Score: 3 = Core platform enhancement, 2 = Moderate platform value, 1 = Minor, 0 = No platform value

### Ecosystem Value
- Does this attract new ISVs, partners, or developers to Red Hat ecosystem?
- Does this enable new partner solutions or integrations?
- Does this strengthen Red Hat's role in key open source communities?
- Score: 3 = Major ecosystem catalyst, 2 = Meaningful expansion, 1 = Minor benefit, 0 = No ecosystem impact

### Defensive Value
- Does this protect existing revenue streams from competitive threats?
- Does this prevent customer churn or commoditization of existing products?
- Does this block a competitive wedge into Red Hat's installed base?
- Score: 3 = Critical defensive move, 2 = Important protection, 1 = Minor defensive value, 0 = Not defensive

### Strategic Optionality
- Does this create future strategic options (M&A targets, new markets, new business models)?
- Does this position Red Hat for emerging industry shifts?
- Does this build critical capabilities for multiple future scenarios?
- Score: 3 = High optionality, 2 = Moderate options, 1 = Limited options, 0 = No optionality

### Brand & Market Perception
- Does this enhance Red Hat's brand as an innovation leader?
- Does this improve analyst and influencer perception?
- Does this strengthen Red Hat's recruiting and talent value proposition?
- Score: 3 = Major brand enhancement, 2 = Positive impact, 1 = Minor benefit, 0 = No impact

**Minimum Threshold:** 8 out of 15 points (recognizing some ideas have high strategic value even with uncertain revenue)

**Output Format:**
```json
{
  "platform_value_score": 0-3,
  "ecosystem_value_score": 0-3,
  "defensive_value_score": 0-3,
  "strategic_optionality_score": 0-3,
  "brand_perception_score": 0-3,
  "total_score": 0-15,
  "passes_threshold": true/false,
  "strategic_value_assessment": "detailed rationale",
  "key_strategic_benefits": ["benefit1", "benefit2", "benefit3"],
  "strategic_risks": ["risk1", "risk2"],
  "confidence": "high/medium/low"
}
```

---

## 6. FINAL RECOMMENDATION

You are synthesizing all evaluation results to make a final recommendation.

**Context Required:**
- All investigation results
- All evaluation assessment results
- Strategic focus areas and OCTO mission

**Decision Framework:**

### Scoring Summary
Calculate aggregate scores from all assessments:
1. Market Opportunity Assessment (0-9 points, threshold: 6)
2. Competitive Winability Assessment (0-12 points, threshold: 8)
3. Investment Feasibility Assessment (0-12 points, threshold: 8)
4. Execution Risk Assessment (0-15 points, threshold: ≤7, lower is better)
5. Strategic Value Assessment (0-15 points, threshold: 8)

### Decision Tiers

**TIER 1 - STRONGLY RECOMMEND:**
- Passes all 5 assessment thresholds
- At least 3 assessments score in top 25% of their range
- No critical execution risks
- Clear strategic alignment with OCTO mission

**TIER 2 - RECOMMEND WITH CONDITIONS:**
- Passes 4 out of 5 assessment thresholds
- One failing assessment has clear mitigation path
- Execution risks are manageable with proper planning
- Strategic value justifies the investment even if direct ROI is uncertain

**TIER 3 - INVESTIGATE FURTHER:**
- Passes 3 out of 5 assessment thresholds
- Significant unknowns in market or technical feasibility
- Requires deeper investigation or design partner validation
- Recommend pilot/spike before full commitment

**TIER 4 - DO NOT RECOMMEND:**
- Passes fewer than 3 assessment thresholds
- Critical execution risks with no mitigation
- Poor strategic fit with OCTO mission
- Better alternative uses of resources exist

### Market Share Success Criteria

Based on the SAM, define success thresholds:
- **Success:** Red Hat achieves 10-15% market share = $X ARR
- **Strong Success:** Red Hat achieves 20-25% market share = $Y ARR
- **Category Leadership:** Red Hat achieves 30%+ market share = $Z ARR

### Recommendation Output

**Output Format:**
```json
{
  "recommendation_tier": "TIER 1-4",
  "overall_recommendation": "STRONGLY RECOMMEND / RECOMMEND WITH CONDITIONS / INVESTIGATE FURTHER / DO NOT RECOMMEND",

  "assessment_scores": {
    "market_opportunity": {"score": 0-9, "passed": true/false},
    "competitive_winability": {"score": 0-12, "passed": true/false},
    "investment_feasibility": {"score": 0-12, "passed": true/false},
    "execution_risk": {"score": 0-15, "passed": true/false},
    "strategic_value": {"score": 0-15, "passed": true/false}
  },

  "thresholds_passed": "X out of 5",

  "market_projections": {
    "tam_current_usd_millions": 0-100000,
    "sam_current_usd_millions": 0-50000,
    "sam_3yr_usd_millions": 0-50000,
    "realistic_market_share_pct": 0-100,
    "projected_3yr_arr_millions": 0-1000,
    "projected_5yr_arr_millions": 0-2000
  },

  "success_scenarios": {
    "success_threshold": "10-15% share = $X ARR",
    "strong_success_threshold": "20-25% share = $Y ARR",
    "category_leadership_threshold": "30%+ share = $Z ARR",
    "most_likely_scenario": "success/strong success/category leadership"
  },

  "key_strengths": [
    "strength 1",
    "strength 2",
    "strength 3"
  ],

  "key_concerns": [
    "concern 1",
    "concern 2",
    "concern 3"
  ],

  "critical_success_factors": [
    "factor 1",
    "factor 2",
    "factor 3"
  ],

  "conditions_or_mitigations": [
    "condition 1",
    "condition 2"
  ],

  "next_steps": [
    "step 1",
    "step 2",
    "step 3"
  ],

  "executive_summary": "2-3 paragraph summary of the recommendation with key rationale",

  "confidence_level": "high/medium/low",

  "decision_rationale": "detailed explanation of why this recommendation tier was selected"
}
```

---

## Usage Instructions

1. Execute all 9 market investigation prompts first to gather comprehensive data
2. Execute evaluation prompts 1-5 sequentially, using investigation data as input
3. Execute final recommendation prompt (6) synthesizing all prior results
4. The final recommendation should provide clear guidance on whether to approve the idea for prototyping

The evaluation prompts are designed to be objective, data-driven, and aligned with OCTO's mission of high-reward strategic prototyping with manageable risk and investment.
