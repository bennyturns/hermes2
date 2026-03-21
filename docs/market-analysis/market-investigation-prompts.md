# Market Investigation Prompts

These prompts are designed to gather comprehensive market intelligence about a proposed idea. They should be executed sequentially to build a complete market picture before evaluation.

## 1. TAM (Total Addressable Market) Investigation

You are a market research analyst investigating the Total Addressable Market for a technology idea.

**Investigation Focus:**
- What is the total global market size for this technology category in USD?
- What are the primary market segments within this space?
- What is the projected growth rate (CAGR) over the next 3-5 years?
- What are the key market drivers and trends accelerating or decelerating growth?
- Which geographic regions represent the largest market opportunity?
- What analyst reports or market research firms track this space? (Gartner, Forrester, IDC, etc.)

**Output Format:**
Provide a structured analysis including:
- Estimated TAM in USD (current and projected 3-year)
- Market growth rate and trajectory
- Key market segments and their relative sizes
- Geographic distribution
- Major trends affecting market size
- Sources and confidence level of estimates

---

## 2. SAM (Serviceable Addressable Market) Investigation

You are analyzing which portion of the TAM Red Hat can realistically serve given its business model and capabilities.

**Investigation Focus:**
- Of the total market, what portion aligns with Red Hat's:
  - Open source business model?
  - Enterprise/commercial customer base?
  - Linux and hybrid cloud positioning?
  - Current go-to-market capabilities?
- What market segments are unreachable due to:
  - Proprietary/closed-source requirements?
  - Consumer vs. enterprise focus?
  - Geographic or regulatory constraints?
  - Technology stack incompatibilities?
- What is the realistic SAM in USD?
- What would be required to expand the SAM (new capabilities, partnerships, etc.)?

**Output Format:**
Provide:
- SAM estimate in USD with confidence level
- Breakdown of addressable vs. non-addressable segments
- Key constraints limiting SAM
- Potential SAM expansion opportunities
- SAM as percentage of TAM with justification

---

## 3. Competitive Landscape Investigation

You are a competitive intelligence analyst mapping the competitive landscape.

**Investigation Focus:**
- Who are the top 5-10 players in this market?
- What is their market share distribution?
- What are the key competitive segments:
  - Open source vs. proprietary solutions?
  - Incumbent enterprise vendors vs. startups?
  - Cloud-native vs. traditional vendors?
- What are the competitive moats (technology, network effects, switching costs)?
- What is the typical sales cycle and deal size in this market?
- Are there dominant platforms or ecosystems that control market access?
- What is the competitive intensity (Red Ocean vs. Blue Ocean)?

**Output Format:**
Provide:
- Top competitors with market share estimates
- Competitive positioning map
- Analysis of open source vs. proprietary dynamics
- Barriers to entry and competitive moats
- Market concentration (fragmented vs. consolidated)
- Threat assessment for new entrants

---

## 4. Red Hat Positioning & Capability Investigation

You are assessing Red Hat's current positioning and capabilities relevant to this market.

**Investigation Focus:**
- Does Red Hat currently have products/solutions in or adjacent to this space?
- What are Red Hat's relevant strengths:
  - Technology assets and IP?
  - Customer relationships in target segments?
  - Partner ecosystem (ISVs, cloud providers, hardware vendors)?
  - Open source community leadership?
  - Brand perception in this domain?
- What are Red Hat's gaps or weaknesses:
  - Missing technical capabilities?
  - Limited market presence?
  - Skills or expertise gaps?
  - Go-to-market limitations?
- How does IBM's ownership affect positioning (positively or negatively)?

**Output Format:**
Provide:
- Current Red Hat positioning in this market (if any)
- Relevant strengths and assets (rated 1-5)
- Critical gaps and weaknesses (rated 1-5)
- IBM synergies or conflicts
- Existing customer base overlap percentage
- Partner ecosystem readiness

---

## 5. Customer Buying Behavior Investigation

You are analyzing how target customers make purchasing decisions in this market.

**Investigation Focus:**
- Who are the typical buyers (roles, titles, departments)?
- What is the buying process and typical sales cycle length?
- What are the key evaluation criteria customers use?
- How important is open source vs. proprietary in buying decisions?
- What is the typical contract size (ACV/TCV)?
- Is this a:
  - Top-down strategic purchase?
  - Bottom-up developer/practitioner adoption?
  - IT department driven?
  - LOB (Line of Business) driven?
- What is the replacement cycle or customer lifetime?
- Are there platform lock-in effects?

**Output Format:**
Provide:
- Buyer personas and decision-making units
- Typical sales cycle timeline
- Deal size ranges and distribution
- Top 5 evaluation criteria in priority order
- Purchase motion (top-down, bottom-up, hybrid)
- Renewal/retention dynamics

---

## 6. Technology & Standards Investigation

You are analyzing the technology landscape and standards that affect market access.

**Investigation Focus:**
- What are the dominant technology standards or specifications?
- Are there critical open source projects or foundations involved?
- What are the key technology dependencies or integrations required?
- Is this a platform market with network effects?
- What is the rate of technology change/disruption?
- Are there emerging standards that could shift the market?
- What role does interoperability play?
- Are there regulatory or compliance requirements affecting technology choices?

**Output Format:**
Provide:
- Critical standards and their governance
- Key open source projects and Red Hat's involvement
- Technology dependency map
- Platform dynamics and network effects
- Technology maturity assessment
- Regulatory/compliance landscape
- Interoperability requirements

---

## 7. Investment & Resource Investigation

You are analyzing the investment required and Red Hat's capacity to invest.

**Investigation Focus:**
- What level of engineering investment is typically required to be competitive?
- What is the time-to-market for a minimally viable product?
- What ongoing R&D investment is needed to maintain competitiveness?
- What is Red Hat's available investment capacity:
  - OCTO's allocation (1% of Global Engineering)?
  - Product engineering capacity for commercialization?
  - Sales and marketing resources?
- What are the opportunity costs (what would be displaced)?
- Are there partnership opportunities to reduce investment requirements?
- What is the expected investment payback period in this market?

**Output Format:**
Provide:
- Estimated development investment required (engineering-months or USD)
- Time to minimum viable product
- Ongoing investment requirements
- Red Hat's available capacity assessment
- Investment efficiency factors (leverage open source, partnerships, etc.)
- Opportunity cost analysis
- ROI timeline expectations

---

## 8. Market Entry & Commercialization Investigation

You are analyzing potential paths to market and commercialization strategies.

**Investigation Focus:**
- What are the viable go-to-market strategies:
  - Direct sales to enterprise?
  - Cloud marketplace distribution?
  - OEM/ISV partnerships?
  - Community-led adoption with enterprise upsell?
- What is the typical product/pricing model in this market?
- What is the cost of customer acquisition (CAC)?
- What is the importance of professional services vs. product revenue?
- Are there strategic partnership opportunities (cloud providers, hardware vendors, ISVs)?
- What is the ecosystem development requirement (integrations, certifications, etc.)?
- How does this idea fit Red Hat's existing GTM motion and channels?

**Output Format:**
Provide:
- Recommended go-to-market strategy
- Pricing model analysis (subscription, consumption, perpetual, etc.)
- CAC estimates and customer acquisition channels
- Partnership opportunities and requirements
- Ecosystem development needs
- Fit with Red Hat's existing sales and channel infrastructure
- Revenue model projections (product vs. services mix)

---

## 9. Risk & Dependency Investigation

You are identifying critical risks and dependencies that could affect success.

**Investigation Focus:**
- What are the critical success factors (must-haves to win)?
- What are the major risks:
  - Technology risks (complexity, maturity, dependencies)?
  - Market risks (demand uncertainty, timing, competition)?
  - Execution risks (skills, resources, time)?
  - Partnership risks (dependency on third parties)?
- What external dependencies exist:
  - Upstream open source projects?
  - Hardware vendor roadmaps?
  - Cloud provider capabilities?
  - Standards body decisions?
- What could cause this market to fail to materialize or shrink?
- Are there regulatory or legal risks?
- What is the impact of competitive response (if Red Hat enters, will incumbents react aggressively)?

**Output Format:**
Provide:
- Critical success factors (top 5)
- Major risk categories with probability and impact ratings
- Dependency map with mitigation strategies
- Market failure scenarios and their likelihood
- Competitive response analysis
- Risk mitigation recommendations
- Overall risk profile (low/medium/high)

---

## Usage Instructions

These investigation prompts should be executed by the AI evaluation system to gather comprehensive market intelligence. The results from all 9 investigations will feed into the subsequent market evaluation prompts to make a final determination on market opportunity and Red Hat's probability of success.

Each investigation should produce structured data that can be aggregated into a comprehensive market intelligence report before proceeding to evaluation.
