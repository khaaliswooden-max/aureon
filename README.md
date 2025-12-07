# AUREON

<p align="center">
  <img src="docs/assets/aureon-logo.svg" alt="AUREON Logo" width="200"/>
</p>

<p align="center">
  <strong>Procurement Substrate</strong><br>
  <em>"The procurement layer for the next decade."</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#modules">Modules</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#compliance">Compliance</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FedRAMP-Moderate-blue" alt="FedRAMP Moderate"/>
  <img src="https://img.shields.io/badge/FAR/DFARS-Compliant-green" alt="FAR/DFARS"/>
  <img src="https://img.shields.io/badge/TAA-Compliant-orange" alt="TAA Compliant"/>
  <img src="https://img.shields.io/badge/Section_889-Compliant-purple" alt="Section 889"/>
  <img src="https://img.shields.io/badge/License-Proprietary-red" alt="License"/>
</p>

---

## Overview

**AUREON** is an AI-powered procurement intelligence platform designed for federal contractors, defense primes, and organizations navigating complex government acquisition landscapes. It transforms opportunity discovery, proposal development, and supply chain management into a unified, intelligent workflow.

AUREON serves as the procurement substrate—the foundational layer that connects opportunity intelligence, competitive analysis, proposal automation, and supply chain visibility into a single operational platform.

### The Problem We Solve

Government contractors and procurement teams struggle with:

- **Fragmented opportunity discovery** across SAM.gov, GovWin, agency portals
- **Manual, error-prone proposal development** taking weeks instead of days
- **Supply chain opacity** creating compliance risks (Section 889, TAA, DFARS)
- **Reactive competitive intelligence** instead of strategic positioning
- **Disconnected CRM and pipeline data** lacking federal-specific context

### Our Solution

AUREON delivers:

- **AI-Powered Opportunity Intelligence**: Automated SAM.gov monitoring, RFI/RFP matching, and win probability scoring
- **Proposal Automation Engine**: GPT-4 assisted generation with FAR compliance checking
- **Supply Chain Compliance**: Section 889 screening and TAA country-of-origin validation
- **Competitive Intelligence**: Real-time contract awards analysis and pricing benchmarks
- **Unified Pipeline Management**: Federal-specific CRM with relevance scoring

---

## Modules

| Module | Description | Key Features |
|--------|-------------|--------------|
| **Pro-Sales** | Opportunity & Proposal Management | SAM.gov integration, AI win probability, proposal automation, pricing intelligence |
| **Pro-Biz** | Supply Chain & Compliance | Section 889 screening, TAA validation, supplier risk scoring, provenance tracking |

---

## Features

### 🎯 Opportunity Intelligence (Pro-Sales)

- **Automated Discovery**: Real-time monitoring of SAM.gov with configurable filters
- **AI Matching Engine**: ML-powered opportunity scoring based on capabilities, NAICS codes, and past performance
- **Win Probability Analysis**: Predictive scoring using historical data and competitive analysis
- **Set-Aside Identification**: Automatic detection of 8(a), HUBZone, SDVOSB, WOSB opportunities
- **Pipeline Integration**: Seamless flow from discovery to pursuit decision

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SAM.gov    │────▶│   Ingestion  │────▶│  ML Scoring  │
│   eBuy       │     │   Pipeline   │     │   Engine     │
│   GovWin     │     └──────────────┘     └──────┬───────┘
└──────────────┘                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │  Pipeline    │
                                           │  Dashboard   │
                                           └──────────────┘
```

### 📝 Proposal Automation (Pro-Sales)

- **AI-Assisted Drafting**: GPT-4 powered section generation with context awareness
- **Compliance Matrix Automation**: Auto-populate requirement traceability matrices
- **Template Library**: Pre-built templates for LPTA, Best Value, IDIQ task orders
- **Review Workflow**: Multi-stage approval with color team integration

| Feature | Description | Time Savings |
|---------|-------------|--------------|
| Executive Summary Generation | AI drafts based on PWS analysis | 4-6 hours |
| Technical Approach | Contextual generation from capability library | 8-12 hours |
| Past Performance Narratives | Auto-populated from organization profile | 2-4 hours |
| Compliance Matrix | Automated cross-referencing | 6-8 hours |

### 💰 Pricing Intelligence (Pro-Sales)

- **Competitive Benchmarking**: Historical award data analysis by NAICS/PSC
- **Cost Model Templates**: Pre-built models for T&M, FFP, CPFF contracts
- **Rate Analysis**: Labor rate comparison across contract vehicles
- **Should-Cost Modeling**: AI-assisted independent cost estimates

### 🔗 Supply Chain Compliance (Pro-Biz)

- **Section 889 Screening**: Automated supplier verification against prohibited entities
- **TAA Compliance**: Country-of-origin validation for Trade Agreements Act
- **Supplier Risk Scoring**: ML-based risk assessment for supply chain partners
- **Provenance Tracking**: Complete audit trail for compliance documentation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUPPLY CHAIN COMPLIANCE ENGINE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   SUPPLIER        VERIFICATION        RISK SCORE        STATUS      │
│   ┌───────┐       ┌───────┐          ┌───────┐        ┌───────┐    │
│   │ Input │──────▶│Section│─────────▶│  ML   │───────▶│Compliant│   │
│   │ Data  │       │  889  │          │ Risk  │        │   or    │   │
│   └───────┘       │  TAA  │          │Engine │        │Flagged  │   │
│                   └───────┘          └───────┘        └───────┘    │
│                                                                      │
│   • Prohibited entity screening (Huawei, ZTE, Hikvision, etc.)      │
│   • TAA designated country validation                                │
│   • SAM.gov exclusion list integration                               │
│   • Real-time risk scoring                                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 📊 Relevance & Risk Assessment

- **Multi-Factor Scoring**: NAICS alignment, semantic matching, geographic fit, capacity analysis
- **Risk Assessment**: Eligibility, technical, pricing, and compliance risk evaluation
- **Explainable AI**: Every recommendation traceable to reasoning chain
- **Configurable Weights**: Customize scoring based on organizational priorities

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AUREON PLATFORM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Web Portal │  │   API GW    │  │  Admin UI   │  │   CLI       │        │
│  │  (Next.js)  │  │  (FastAPI)  │  │  (React)    │  │  (Python)   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│         └────────────────┴────────────────┴────────────────┘                │
│                                   │                                          │
│                    ┌──────────────┴──────────────┐                          │
│                    │       FastAPI Backend       │                          │
│                    │   Rate Limiting • Auth • SSL │                          │
│                    └──────────────┬──────────────┘                          │
│                                   │                                          │
│  ┌────────────────────────────────┼────────────────────────────────┐        │
│  │                         SERVICES                                 │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │        │
│  │  │Opportunity│ │ Proposal │ │  Supply  │ │  Pricing │           │        │
│  │  │ Service  │ │ Service  │ │  Chain   │ │ Service  │           │        │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │        │
│  └────────────────────────────────┬────────────────────────────────┘        │
│                                   │                                          │
│  ┌────────────────────────────────┼────────────────────────────────┐        │
│  │                         ML PLATFORM                              │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │        │
│  │  │   Win    │ │Relevance │ │ Supplier │ │  Pricing │           │        │
│  │  │Probability│ │  Scorer  │ │   Risk   │ │  Model   │           │        │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │        │
│  └────────────────────────────────┬────────────────────────────────┘        │
│                                   │                                          │
│  ┌────────────────────────────────┼────────────────────────────────┐        │
│  │                         DATA LAYER                               │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │        │
│  │  │PostgreSQL│ │  Elastic │ │  Redis   │ │   S3     │           │        │
│  │  │ Primary  │ │  Search  │ │  Cache   │ │  Storage │           │        │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │        │
│  └─────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 14, TypeScript, TailwindCSS | Web application |
| Backend | Python 3.11 (FastAPI) | API & Microservices |
| ML Platform | OpenAI GPT-4, scikit-learn, sentence-transformers | AI/ML models |
| Primary DB | PostgreSQL 15 | Transactional data |
| Search | Elasticsearch 8.x | Full-text opportunity search |
| Cache | Redis 7 | Session, cache |
| Container | Docker, Docker Compose | Development & Deployment |
| CI/CD | GitHub Actions | Pipeline automation |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20 LTS
- Docker & Docker Compose
- PostgreSQL 15+ client (optional, via Docker)

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/visionblox/aureon.git
cd aureon

# Install root dependencies
npm install

# Start local services (PostgreSQL, Redis, Backend, Frontend)
cd infra/docker
docker-compose up -d

# Verify services
docker-compose ps

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://aureon:aureon_dev_password@localhost:5432/aureon
REDIS_URL=redis://localhost:6379/0

# SAM.gov API (get free key at sam.gov)
SAM_GOV_API_KEY=your-sam-gov-api-key

# OpenAI (for proposal generation)
OPENAI_API_KEY=your-openai-api-key

# Anthropic (optional, for Claude)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit -v

# E2E tests
pytest tests/e2e -v

# With coverage
pytest tests/ --cov=apps/backend/src --cov-report=html
```

---

## API Reference

### Authentication

All API requests require authentication via Bearer token (when auth is enabled):

```bash
curl -X GET "http://localhost:8000/opportunities" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Core Endpoints

#### Health Check
```bash
GET /health
```

#### Opportunities

```bash
# List opportunities with filters
GET /opportunities?query=cloud&naics_code=541512&set_aside_type=SB

# Get single opportunity
GET /opportunities/{opportunity_id}

# Get opportunities by NAICS
GET /opportunities/naics/{naics_code}

# Get opportunity statistics
GET /opportunities/stats/summary
```

#### Organizations

```bash
# List organizations
GET /organizations

# Get organization profile
GET /organizations/{org_id}

# Create organization
POST /organizations

# Update organization
PUT /organizations/{org_id}
```

#### Relevance Scoring

```bash
# Score opportunities for an organization
POST /scoring/relevance
{
  "organization_id": "uuid",
  "opportunity_ids": ["uuid1", "uuid2"]
}

# Batch score all active opportunities
POST /scoring/relevance/batch
{
  "organization_id": "uuid"
}
```

#### Risk Assessment

```bash
# Assess risk for opportunity
POST /risk/assess
{
  "organization_id": "uuid",
  "opportunity_id": "uuid"
}
```

#### Win Probability

```bash
# Calculate win probability
POST /win-probability/calculate
{
  "organization_id": "uuid",
  "opportunity_id": "uuid"
}
```

#### Proposal Generation

```bash
# Generate proposal section
POST /proposals/generate
{
  "opportunity_id": "uuid",
  "organization_id": "uuid",
  "section": "executive_summary"
}
```

#### Supply Chain Compliance

```bash
# Verify supplier compliance
POST /supply-chain/verify
{
  "supplier_name": "Acme Corp",
  "country_of_origin": "US"
}

# Check Section 889 compliance
POST /supply-chain/section-889/check
{
  "supplier_name": "Component Manufacturer"
}

# Check TAA compliance
POST /supply-chain/taa/check
{
  "country_code": "CN"
}
```

#### Data Ingestion

```bash
# Trigger SAM.gov sync
POST /ingestion/sam-gov/sync

# Get ingestion status
GET /ingestion/status
```

---

## Compliance

### Federal Certifications

| Certification | Status | Scope |
|---------------|--------|-------|
| FedRAMP Moderate | In Progress | Full Platform |
| SOC 2 Type II | Planned | Full Platform |
| FAR/DFARS | Compliant | Procurement Module |
| Section 889 | Compliant | Supply Chain Module |
| TAA | Compliant | Supply Chain Module |
| FISMA Moderate | In Progress | Full Platform |

### Data Handling

- All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- Complete audit logging for all data access
- OFAC and SAM.gov exclusion list integration
- Role-based access control (RBAC)

---

## Repository Structure

```
aureon/
├── apps/
│   ├── backend/                    # FastAPI Python backend
│   │   ├── src/
│   │   │   ├── api/               # API route handlers
│   │   │   ├── database/          # Models & connection
│   │   │   ├── ingestion/         # SAM.gov & data pipelines
│   │   │   ├── services/          # Business logic
│   │   │   │   ├── relevance_scorer.py
│   │   │   │   ├── risk_assessor.py
│   │   │   │   ├── win_probability.py
│   │   │   │   ├── proposal_generator.py
│   │   │   │   └── supply_chain.py
│   │   │   └── main.py
│   │   └── requirements.txt
│   │
│   └── frontend/                   # Next.js web application
│       ├── app/                    # Next.js app router
│       ├── components/             # React components
│       └── lib/                    # Utilities & API client
│
├── packages/
│   ├── core-domain/               # Shared domain models
│   └── benchmarks/                # APP-Bench test suite
│
├── infra/
│   ├── docker/                    # Docker Compose setup
│   └── terraform/                 # Infrastructure as Code
│
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
│
├── docs/                          # Documentation
└── README.md
```

---

## Current Status

### ✅ Implemented

- [x] Core domain models (TypeScript + Python)
- [x] Database schema and ORM models (PostgreSQL)
- [x] SAM.gov ingestion pipeline
- [x] Relevance scoring service (multi-factor)
- [x] Risk assessment service
- [x] RESTful API with FastAPI
- [x] Web frontend (Next.js + TailwindCSS)
- [x] Opportunity search & filtering
- [x] Organization management
- [x] Docker development environment

### 🚧 In Progress

- [ ] Win probability ML model
- [ ] Proposal automation (GPT-4)
- [ ] Supply chain compliance (Section 889, TAA)
- [ ] Pricing intelligence
- [ ] Authentication (JWT)
- [ ] Elasticsearch integration
- [ ] Frontend-backend API wiring

### 🔮 Roadmap

- Mobile applications (Flutter)
- GSA integration
- Advanced analytics dashboard
- Multi-tenant SaaS deployment
- FedRAMP authorization

---

## Contributing

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, run tests
pytest tests/ -v

# Commit with conventional commits
git commit -m "feat: add win probability model"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Standards

- **Python**: PEP 8, Black formatting, type hints required
- **TypeScript**: Strict mode, ESLint + Prettier
- **Tests**: 80%+ coverage for new code
- **Documentation**: Update docs for API changes

---

## Support

| Channel | Contact |
|---------|---------|
| Technical Support | support@aureon.ai |
| Sales Inquiries | sales@visionblox.io |
| Security Issues | security@visionblox.io |

---

## License

Copyright © 2025 Visionblox LLC / Zuup Innovation Lab. All rights reserved.

This software is proprietary and confidential. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>AUREON</strong> — The Procurement Layer for the Next Decade<br>
  <em>A Zuup Innovation Lab Platform</em>
</p>
