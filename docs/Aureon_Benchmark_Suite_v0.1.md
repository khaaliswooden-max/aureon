# APP-Bench v0.1: Aureon Planetary Procurement Benchmark Suite

**Version 0.1 | December 2025**

---

## Overview

APP-Bench provides standardized evaluation of procurement intelligence systems across 7 dimensions with 20 discrete tasks. The suite enables reproducible, quantitative comparison of system capabilities.

---

## Dimensions

### 1. Coverage & Recall (CR)
*Can the system find all relevant opportunities?*

### 2. Precision & Relevance (PR)
*Does the system rank genuinely aligned opportunities highly?*

### 3. Compliance Fidelity (CF)
*Does the system correctly interpret regulations?*

### 4. Temporal Responsiveness (TR)
*How quickly does the system detect and respond to changes?*

### 5. Workflow Efficiency (WE)
*Does the system reduce time and effort for users?*

### 6. Robustness & Stress (RS)
*Does the system degrade gracefully under adverse conditions?*

### 7. Planetary Scale (PS)
*Can the system operate across multiple jurisdictions?*

---

## Task Specifications

### APP-01: Basic NAICS Coverage
**Dimension:** Coverage & Recall  
**Difficulty:** Basic  
**Description:** Given a set of NAICS codes, retrieve all matching opportunities from the last 30 days.  
**Metrics:**
- Recall ≥ 0.95
- P95 Latency ≤ 2000ms

### APP-02: Set-Aside Filtering
**Dimension:** Coverage & Recall  
**Difficulty:** Basic  
**Description:** Filter opportunities by set-aside type and verify completeness.  
**Metrics:**
- Recall ≥ 0.98
- Precision ≥ 0.95

### APP-03: Multi-Jurisdiction Discovery
**Dimension:** Coverage & Recall  
**Difficulty:** Advanced  
**Description:** Discover matching opportunities across federal and 5 state portals.  
**Metrics:**
- Recall ≥ 0.85
- Coverage ≥ 80%

### APP-04: Relevance Ranking
**Dimension:** Precision & Relevance  
**Difficulty:** Basic  
**Description:** Rank 100 opportunities by relevance for a given organization profile.  
**Metrics:**
- NDCG@10 ≥ 0.75
- Precision@20 ≥ 0.80

### APP-05: Semantic Matching
**Dimension:** Precision & Relevance  
**Difficulty:** Intermediate  
**Description:** Match capability statements to opportunity requirements using semantic similarity.  
**Metrics:**
- MAP ≥ 0.70
- MRR ≥ 0.75

### APP-06: False Positive Resistance
**Dimension:** Precision & Relevance  
**Difficulty:** Advanced  
**Description:** Correctly reject opportunities that appear relevant but have disqualifying factors.  
**Metrics:**
- Specificity ≥ 0.90
- F1 Score ≥ 0.85

### APP-07: Set-Aside Eligibility
**Dimension:** Compliance Fidelity  
**Difficulty:** Basic  
**Description:** Correctly determine eligibility for various set-aside types.  
**Metrics:**
- Accuracy ≥ 0.98
- False Positive Rate ≤ 0.02

### APP-08: FAR Clause Interpretation
**Dimension:** Compliance Fidelity  
**Difficulty:** Intermediate  
**Description:** Extract and interpret key FAR clause requirements.  
**Metrics:**
- Accuracy ≥ 0.85
- Extraction F1 ≥ 0.80

### APP-09: Amendment Impact Analysis
**Dimension:** Compliance Fidelity  
**Difficulty:** Advanced  
**Description:** Detect and assess impact of solicitation amendments.  
**Metrics:**
- Detection Rate ≥ 0.95
- Impact Accuracy ≥ 0.80

### APP-10: New Opportunity Detection
**Dimension:** Temporal Responsiveness  
**Difficulty:** Basic  
**Description:** Detect newly posted opportunities within 15 minutes.  
**Metrics:**
- Detection Latency ≤ 15 minutes
- Detection Rate ≥ 0.99

### APP-11: Deadline Tracking
**Dimension:** Temporal Responsiveness  
**Difficulty:** Basic  
**Description:** Accurately track and alert on upcoming deadlines.  
**Metrics:**
- Accuracy ≥ 0.995
- Alert Timeliness ≤ 24 hours

### APP-12: Change Detection
**Dimension:** Temporal Responsiveness  
**Difficulty:** Intermediate  
**Description:** Detect modifications to tracked opportunities.  
**Metrics:**
- Detection Rate ≥ 0.95
- Latency ≤ 30 minutes

### APP-13: Bid/No-Bid Acceleration
**Dimension:** Workflow Efficiency  
**Difficulty:** Basic  
**Description:** Reduce time to initial bid/no-bid decision.  
**Metrics:**
- Time Reduction ≥ 30%
- Decision Accuracy ≥ 0.85

### APP-14: Pipeline Optimization
**Dimension:** Workflow Efficiency  
**Difficulty:** Intermediate  
**Description:** Optimize opportunity pipeline based on capacity constraints.  
**Metrics:**
- Utilization Improvement ≥ 20%
- Win Rate Improvement ≥ 10%

### APP-15: Team Formation
**Dimension:** Workflow Efficiency  
**Difficulty:** Advanced  
**Description:** Suggest optimal team compositions for opportunities.  
**Metrics:**
- Match Quality ≥ 0.80
- Recommendation Latency ≤ 5000ms

### APP-16: Data Quality Resilience
**Dimension:** Robustness & Stress  
**Difficulty:** Intermediate  
**Description:** Maintain performance with noisy or incomplete data.  
**Metrics:**
- Max Degradation ≤ 10%
- Error Rate ≤ 5%

### APP-17: Load Handling
**Dimension:** Robustness & Stress  
**Difficulty:** Advanced  
**Description:** Handle 1000 concurrent scoring requests.  
**Metrics:**
- Throughput ≥ 100 RPS
- P99 Latency ≤ 1000ms

### APP-18: Adversarial Inputs
**Dimension:** Robustness & Stress  
**Difficulty:** Expert  
**Description:** Resist manipulation through adversarial opportunity descriptions.  
**Metrics:**
- Manipulation Resistance ≥ 0.95
- FP Increase ≤ 5%

### APP-19: Cross-Jurisdiction Query
**Dimension:** Planetary Scale  
**Difficulty:** Advanced  
**Description:** Execute unified queries across 10+ procurement systems.  
**Metrics:**
- Systems Covered ≥ 10
- Query Latency ≤ 10000ms

### APP-20: Multi-Tenant Isolation
**Dimension:** Planetary Scale  
**Difficulty:** Expert  
**Description:** Ensure complete data isolation in multi-tenant deployment.  
**Metrics:**
- Isolation Score = 1.0
- Cross-Tenant Leakage = 0.0

---

## Running Benchmarks

```bash
# Install CLI
cd packages/benchmarks
pip install -e .

# List available tasks
aureon-bench list

# Run specific task
aureon-bench run APP-04 --org-id <organization-id>

# Run by difficulty
aureon-bench batch --difficulty basic

# Generate report
aureon-bench report --run-id <run-id>
```

---

## Scoring

Each task produces metrics compared against targets. A task **passes** if all metrics meet or exceed their targets.

Overall system score is calculated as:

```
Score = (Passed Tasks / Total Implemented Tasks) × 100
```

Difficulty-weighted scoring applies multipliers:
- Basic: 1.0x
- Intermediate: 1.5x
- Advanced: 2.0x
- Expert: 3.0x

---

## Evaluation Methodology

1. **Reproducibility:** All test data and scenarios are version-controlled
2. **Isolation:** Each run uses fresh state
3. **Multiple Runs:** Metrics are averaged over 3+ runs
4. **Statistical Significance:** Report confidence intervals

---

*For implementation details, see the source code in `packages/benchmarks/`.*

