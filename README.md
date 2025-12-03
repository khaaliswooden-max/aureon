# Aureon: Planetary Procurement Substrate

**Version:** 0.1.0  
**Status:** MVP Development  
**Organization:** Visionblox LLC / Zuup Innovation Lab

---

## 🌍 Vision

Aureon is a **planetary-scale procurement substrate**—a foundational layer that represents, reasons about, and optimizes procurement across jurisdictions, enabling intelligent applications to operate on a unified, jurisdiction-agnostic platform.

Think of Aureon as the "Linux for procurement": a substrate that abstracts away fragmented portals, incompatible standards, and siloed data, providing common primitives that any procurement application can build upon.

---

## 🎯 The Problem

Global procurement is fundamentally broken:

- **Fragmentation:** Thousands of disconnected portals (SAM.gov, state systems, international platforms)
- **Asymmetric Intelligence:** Large contractors have massive intelligence advantages over small businesses
- **Compliance Complexity:** 2,000+ pages of FAR/DFARS, constantly changing, manually interpreted
- **Data Silos:** Opportunity aggregators, CRMs, and ERPs don't share data models or APIs
- **No Scale Path:** Current tools are applications built for single-jurisdiction workflows

**Result:** Organizations spend 60-70% of capture budgets on unqualified opportunities. Small businesses are systematically disadvantaged. Governments struggle to achieve competitive outcomes.

These aren't implementation bugs—they're **architectural failures**.

---

## 💡 The Aureon Solution

### Substrate-Level Architecture

Aureon provides five foundational layers:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 5: Application Layer (UI, Workflows, Integrations)│
├─────────────────────────────────────────────────────────┤
│  Layer 4: Orchestration & AI (Scoring, Optimization)     │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Rules & Compliance (FAR, DFARS, EU Directives) │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Knowledge Graph (Entities, Relations, Temporal)│
├─────────────────────────────────────────────────────────┤
│  Layer 1: Ingestion & Normalization (Multi-Source ETL)   │
└─────────────────────────────────────────────────────────┘
```

### Core Capabilities

**Universal Data Model**
- Jurisdiction-agnostic ontology for organizations, opportunities, contracts
- Extensible to any procurement regime (US federal, state, EU, commercial)
- Temporal reasoning (historical context, state changes, lifecycle tracking)

**Intelligence Layer**
- Relevance scoring (semantic similarity + taxonomy matching + past performance)
- Risk assessment (eligibility, technical, pricing, resource, compliance)
- Optimization (team formation, pipeline balancing, resource allocation)
- Explainability (every recommendation traceable to reasoning chain)

**Compliance Engine**
- Formalized regulatory rules (FAR clauses, set-asides, eligibility)
- Automated compliance checking
- Amendment tracking and impact analysis
- Audit trails and governance

**Multi-Jurisdiction Support**
- Same substrate operates across 50+ procurement regimes
- Sovereign instances (data residency, government control)
- Federated architecture (cross-border interoperability)

---

## 📊 Measurable Outcomes

Unlike vendor marketing claims, Aureon's performance is objectively measured through **APP-Bench** (Aureon Planetary Procurement Benchmark Suite):

| Metric | Current State | Aureon Target | Status |
|--------|---------------|---------------|--------|
| Opportunity Recall | 40-60% | 85-95% | 🎯 In Development |
| Relevance Precision@20 | <30% | 75-85% | 🎯 In Development |
| Bid/No-Bid Cycle Time | Baseline | 30-50% reduction | 🎯 In Development |
| Compliance Automation | Manual | 80%+ automated | 🎯 In Development |
| Detection Latency | Days | <15 minutes | 🎯 In Development |

**APP-Bench v0.1** provides 20 benchmark tasks across 7 dimensions with reproducible evaluation.

---

## 🏗️ Repository Structure

```
aureon/
├── docs/                                    # Documentation
│   ├── Aureon_Whitepaper_First_Principles_v0.1.md
│   ├── Aureon_Benchmark_Suite_v0.1.md
│   ├── Aureon_Build_Runbook_Cursor_Antigravity_v0.1.md
│   └── api/                                 # API documentation
│
├── apps/                                    # Deployable applications
│   ├── frontend/                            # Next.js web application
│   │   ├── app/                             # Next.js app directory
│   │   ├── components/                      # React components
│   │   └── package.json
│   │
│   └── backend/                             # FastAPI backend
│       ├── src/
│       │   ├── api/                         # API routes
│       │   ├── database/                    # Database models
│       │   ├── ingestion/                   # Data ingestion modules
│       │   ├── services/                    # Business logic
│       │   └── main.py                      # Application entry point
│       └── requirements.txt
│
├── packages/                                # Shared libraries
│   ├── core-domain/                         # Domain models (TypeScript & Python)
│   │   ├── src/entities/                    # Entity definitions
│   │   └── aureon_domain/                   # Python domain package
│   │
│   ├── benchmarks/                          # APP-Bench implementation
│   │   ├── src/
│   │   │   ├── scenarios/                   # Benchmark test data
│   │   │   ├── evaluators/                  # Task evaluators
│   │   │   ├── metrics/                     # Metric calculations
│   │   │   └── cli.py                       # Benchmark CLI
│   │   └── results/                         # Benchmark outputs
│   │
│   └── orchestration/                       # Workflow engines
│
├── infra/                                   # Infrastructure as code
│   ├── docker/
│   │   └── docker-compose.yml               # Local development
│   └── terraform/                           # Production infrastructure
│
├── tests/                                   # Test suites
│   ├── unit/                                # Unit tests
│   ├── integration/                         # Integration tests
│   └── e2e/                                 # End-to-end tests
│
├── scripts/                                 # Utility scripts
│
├── package.json                             # Root workspace config
├── turbo.json                               # Monorepo build configuration
└── README.md                                # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20.x+
- **Python** 3.11+
- **Docker Desktop** 24.x+
- **PostgreSQL** 15+ (via Docker)
- **Git** 2.40+

### Setup (5 minutes)

```bash
# Clone repository
git clone https://github.com/khaaliswooden-max/aureon.git
cd aureon

# Install dependencies
npm install

# Start development environment (PostgreSQL, Redis, Backend, Frontend)
cd infra/docker
docker-compose up -d

# Backend will be at http://localhost:8000
# Frontend will be at http://localhost:3000
# API docs at http://localhost:8000/docs
```

### Run Your First Benchmark

```bash
# Navigate to benchmarks package
cd packages/benchmarks

# Install dependencies
pip install -e .

# Run APP-04 (Relevance Ranking benchmark)
python -m src.cli run APP-04 --org-id <test-org-id>

# View results
cat results/APP-04/metrics.json
```

### Ingest Sample Data

```bash
# Set SAM.gov API key (get free key at sam.gov)
export SAM_GOV_API_KEY="your_key_here"

# Run ingestion
cd apps/backend
python -m src.ingestion.sam_gov

# Verify
psql -h localhost -U aureon -d aureon -c "SELECT COUNT(*) FROM opportunities;"
```

---

## 📚 Documentation

### Core Documents

1. **[First-Principles White Paper](./docs/Aureon_Whitepaper_First_Principles_v0.1.md)**  
   8-page equivalent deconstructing procurement from foundational principles, system architecture, and roadmap.

2. **[APP-Bench v0.1 Specification](./docs/Aureon_Benchmark_Suite_v0.1.md)**  
   Complete benchmark suite with 20 tasks, scoring metrics, and evaluation methodology.

3. **[Build Runbook](./docs/Aureon_Build_Runbook_Cursor_Antigravity_v0.1.md)**  
   Step-by-step technical implementation guide from zero to running MVP.

### API Documentation

- **Interactive API Docs:** http://localhost:8000/docs (when backend running)
- **OpenAPI Spec:** http://localhost:8000/openapi.json

### Additional Resources

- **Architecture Decision Records (ADRs):** `docs/adr/`
- **Deployment Guides:** `docs/deployment/`
- **Contributing Guidelines:** `CONTRIBUTING.md` (coming soon)

---

## 🎯 Current Status

### ✅ Completed (v0.1 MVP)

- [x] Core domain models (TypeScript + Python)
- [x] Repository structure and monorepo setup
- [x] Database schema and ORM models
- [x] SAM.gov ingestion pipeline
- [x] Relevance scoring service (NAICS + semantic + geographic + size)
- [x] Risk assessment service
- [x] RESTful API with FastAPI
- [x] Basic frontend (Next.js + React)
- [x] APP-Bench framework (20 tasks defined, 2 fully implemented)
- [x] Docker-based development environment
- [x] Comprehensive documentation

### 🚧 In Progress

- [ ] Complete APP-Bench implementation (18 remaining tasks)
- [ ] LLM integration for requirement extraction
- [ ] Authentication and user management
- [ ] State procurement portal connectors (5 pilot states)
- [ ] Mobile-responsive UI enhancements

### 🔮 Roadmap (Next 6 Months)

**Month 1-2: MVP Hardening**
- Production database deployment
- Security audit and penetration testing
- Performance optimization (caching, indexing)
- Monitoring and observability setup

**Month 3-4: Pilot Deployments**
- Onboard 10-20 pilot organizations
- 5 state procurement portal integrations
- User feedback collection and iteration
- Pass all "Basic" APP-Bench tasks

**Month 5-6: Intelligence Enhancements**
- Past performance analysis integration
- Competition intensity modeling
- Team formation recommendations
- Advanced compliance checking (CMMC, FedRAMP)

**Long-Term Vision:** See [White Paper](./docs/Aureon_Whitepaper_First_Principles_v0.1.md) for 3-5 year roadmap to planetary scale.

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Backend unit tests
cd apps/backend
pytest tests/ -v

# Frontend tests
cd apps/frontend
npm test

# End-to-end tests
cd tests/e2e
pytest test_opportunity_workflow.py -v

# Run benchmarks
cd packages/benchmarks
python -m src.cli run --all
```

---

## 🤝 Contributing

Aureon is being developed openly with the goal of becoming a public substrate.

### How to Contribute

1. **Report Issues:** Found a bug? Open an issue with reproduction steps
2. **Suggest Enhancements:** Have ideas? Start a discussion in Issues
3. **Submit Benchmark Tasks:** Propose new APP-Bench scenarios
4. **Contribute Code:** Fork, create a feature branch, submit PR

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit with clear messages
git commit -m "feat: add semantic caching to relevance scorer"

# Run tests and linting
npm test
npm run lint

# Push and create PR
git push origin feature/your-feature-name
```

### Code Standards

- **TypeScript:** Strict mode, ESLint + Prettier
- **Python:** Type hints, Black formatter, MyPy static checking
- **Tests:** >80% coverage for new code
- **Documentation:** Update docs for API or architecture changes

---

## 🏛️ Governance & Sovereignty

### Deployment Models

**Sovereign Instance**
- Deployed in jurisdiction (on-premises or jurisdiction cloud)
- Government controls all data, rules, and access
- Suitable for: Federal agencies, defense, critical infrastructure

**Federated Substrate**
- Multiple sovereign instances interoperate via standardized APIs
- Data sharing by consent
- Suitable for: Cross-border procurement, allied nations

**Multi-Tenant SaaS**
- Visionblox-operated cloud service
- Strong tenant isolation, optional data residency
- Suitable for: Commercial organizations, small governments

### Data Sovereignty

- All data physically resides in jurisdiction of sovereignty
- Encryption at rest and in transit
- Immutable audit trails for regulatory compliance
- No vendor lock-in (open substrate, standard APIs)

---

## 📊 Benchmarking & Accountability

### APP-Bench: Objective Evaluation

Aureon's performance is measured through the **Aureon Planetary Procurement Benchmark Suite (APP-Bench)**, providing:

- **20 discrete tasks** across 7 dimensions
- **Quantitative metrics** (NDCG, precision, recall, latency, F1)
- **Reproducible scenarios** with ground truth labels
- **Progressive difficulty** (Basic → Intermediate → Advanced → Expert)

### Running Benchmarks

```bash
# List available benchmarks
aureon-bench list

# Run specific task
aureon-bench run APP-04

# Run all basic tasks
aureon-bench run --difficulty basic

# Run full suite
aureon-bench run --all

# Generate report
aureon-bench report --run-id run-2025-12-03-001
```

### Benchmark Dimensions

1. **Coverage & Recall (CR):** Find all relevant opportunities
2. **Precision & Relevance (PR):** Rank genuinely aligned results high
3. **Compliance Fidelity (CF):** Correctly interpret regulations
4. **Temporal Responsiveness (TR):** Real-time detection and updates
5. **Workflow Efficiency (WE):** Reduce time and steps
6. **Robustness & Stress (RS):** Graceful degradation under adversarial conditions
7. **Planetary Scale (PS):** Multi-jurisdiction capability

---

## 🛡️ Security & Compliance

### Security Measures

- **Authentication:** OAuth 2.0 / OIDC
- **Authorization:** Role-Based Access Control (RBAC)
- **Encryption:** TLS 1.3 for all network traffic, AES-256 at rest
- **Secrets Management:** AWS Secrets Manager / HashiCorp Vault
- **Audit Logging:** Immutable logs for all actions
- **Regular Audits:** Quarterly security assessments

### Compliance Support

- **FedRAMP:** Architecture designed for Moderate/High authorization
- **CMMC:** Cybersecurity Maturity Model Certification alignment
- **GDPR:** Data privacy and right-to-be-forgotten support
- **SOC 2 Type II:** In progress (target Q2 2026)

---

## 📈 Technology Stack

### Frontend
- **Framework:** Next.js 14 (React 18, TypeScript)
- **Styling:** TailwindCSS
- **State Management:** React Query, Zustand
- **Visualization:** Recharts, D3.js

### Backend
- **API:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy with Alembic migrations
- **Async:** asyncio, httpx
- **Validation:** Pydantic v2

### Data Layer
- **Relational:** PostgreSQL 15
- **Graph:** Neo4j or AWS Neptune (planned)
- **Search:** OpenSearch / Elasticsearch
- **Cache:** Redis 7
- **Object Storage:** S3-compatible

### AI/ML
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **LLM Orchestration:** LangChain, OpenAI API, Anthropic Claude
- **Classical ML:** Scikit-learn, XGBoost
- **Optimization:** PuLP, OR-Tools

### Infrastructure
- **Containers:** Docker, Kubernetes
- **IaC:** Terraform
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana, Sentry
- **Logging:** Structured JSON, OpenTelemetry

---

## 🌟 Why Aureon?

### For Organizations

- **Level Playing Field:** Small businesses get same intelligence as large primes
- **Reduce Waste:** Stop chasing unqualified opportunities
- **Accelerate Capture:** 30-50% faster bid/no-bid decisions
- **Unified View:** Single platform across all jurisdictions
- **No Lock-In:** Open substrate, standard APIs

### For Governments

- **Increased Competition:** More diverse, qualified bidders
- **Better Outcomes:** Improved value, reduced cycle times
- **Reduced Protests:** Better compliance upfront
- **Sovereignty:** Control your data and rules
- **Interoperability:** Federated substrate enables collaboration

### For the Ecosystem

- **Open Innovation:** Build applications on substrate APIs
- **Fair Competition:** Vendor differentiation on UX, not lock-in
- **Reduced Integration Costs:** Standard ontology and interfaces
- **Research Platform:** Anonymized data for academic studies

---

## 📞 Contact & Support

### Project Leadership

**Khaalis Maat**  
Director, Enterprise Capture & Compliance  
Visionblox LLC / Zuup Innovation Lab

### Get Involved

- **Email:** contact@aureon.ai
- **Technical Discussion:** aureon-wg@googlegroups.com (coming soon)
- **Issues & PRs:** [GitHub Issues](https://github.com/khaaliswooden-max/aureon/issues)
- **Pilot Partnerships:** pilots@aureon.ai
- **Investment Inquiries:** investors@aureon.ai

### Community

- **Working Group:** Join the Aureon Working Group for technical collaboration
- **Monthly Office Hours:** Coming Q1 2026
- **Annual Conference:** AureonCon (planned 2026)

---

## 📜 License

**Copyright 2025 Visionblox LLC / Zuup Innovation Lab. All rights reserved.**

This project is currently proprietary during MVP development. We plan to open-source the core substrate under Apache 2.0 or similar permissive license upon reaching production maturity (target Q3 2026).

Interested in early access or licensing? Contact: contact@aureon.ai

---

## 🙏 Acknowledgments

Aureon synthesizes insights from:
- Federal procurement officers and contracting specialists
- Small business contractors across multiple sectors
- Large prime contractors (confidential discussions)
- State and local procurement officials
- International procurement experts (EU, Canada, Australia)
- Academic researchers in computer science and public policy

Special thanks to all pilot partners and early contributors.

---

## 🔗 Links

- **Website:** aureon.ai (coming soon)
- **GitHub:** https://github.com/khaaliswooden-max/aureon
- **Documentation:** https://docs.aureon.ai (coming soon)
- **Blog:** https://blog.aureon.ai (coming soon)
- **Twitter:** @AureonSubstrate (coming soon)

---

<div align="center">

**Built with ❤️ for procurement professionals everywhere**

*Aureon: Making procurement intelligent, accessible, and fair*

</div>
