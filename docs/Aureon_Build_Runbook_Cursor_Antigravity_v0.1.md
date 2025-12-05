# Aureon Build Runbook v0.1

**Technical Implementation Guide**

---

## Prerequisites

- **Node.js** 20.x+
- **Python** 3.11+
- **Docker Desktop** 24.x+
- **Git** 2.40+

---

## Quick Start

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/khaaliswooden-max/aureon.git
cd aureon

# Install Node.js dependencies
npm install
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL, Redis, Backend, Frontend
cd infra/docker
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f
```

### 3. Verify Setup

```bash
# Check API health
curl http://localhost:8000/health

# Open frontend
open http://localhost:3000

# API documentation
open http://localhost:8000/docs
```

---

## Project Structure

```
aureon/
├── apps/
│   ├── backend/          # FastAPI Python backend
│   │   ├── src/
│   │   │   ├── api/      # REST endpoints
│   │   │   ├── database/ # SQLAlchemy models
│   │   │   ├── services/ # Business logic
│   │   │   └── ingestion/# Data pipelines
│   │   └── requirements.txt
│   │
│   └── frontend/         # Next.js React frontend
│       ├── app/          # Next.js app router
│       ├── components/   # React components
│       └── lib/          # Utilities
│
├── packages/
│   ├── core-domain/      # Shared domain models
│   │   ├── src/          # TypeScript entities
│   │   └── aureon_domain/# Python entities
│   │
│   └── benchmarks/       # APP-Bench framework
│       └── src/          # CLI and evaluators
│
├── infra/
│   └── docker/           # Docker Compose setup
│
└── docs/                 # Documentation
```

---

## Backend Development

### Setup Python Environment

```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn src.main:app --reload --port 8000
```

### Key APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/opportunities` | GET | List opportunities |
| `/opportunities/{id}` | GET | Get single opportunity |
| `/organizations` | GET/POST | Manage organizations |
| `/scoring/calculate` | POST | Calculate relevance |
| `/risk/assess` | POST | Assess risk |
| `/ingestion/trigger` | POST | Trigger data ingestion |

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Frontend Development

### Setup

```bash
cd apps/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Key Technologies

- **Framework:** Next.js 14 with App Router
- **Styling:** TailwindCSS with custom design system
- **State:** TanStack Query + Zustand
- **Animation:** Framer Motion

---

## Data Ingestion

### SAM.gov Integration

```bash
# Set API key
export SAM_GOV_API_KEY="your_key_here"

# Run ingestion
cd apps/backend
python -m src.ingestion.sam_gov
```

### API Configuration

Get a free SAM.gov API key at: https://sam.gov/content/entity-registration

---

## Running Benchmarks

```bash
cd packages/benchmarks

# Install
pip install -e .

# List benchmarks
aureon-bench list

# Run specific benchmark
aureon-bench run APP-04 --org-id <org-id>

# Run all basic benchmarks
aureon-bench batch --difficulty basic
```

---

## Testing

### Backend Tests

```bash
cd apps/backend
pytest tests/ -v --cov=src
```

### Frontend Tests

```bash
cd apps/frontend
npm test
```

### End-to-End Tests

```bash
cd tests/e2e
pytest -v
```

---

## Deployment

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `REDIS_URL` | Redis connection | Yes |
| `SAM_GOV_API_KEY` | SAM.gov API key | No |
| `OPENAI_API_KEY` | OpenAI API key | No |
| `SECRET_KEY` | JWT signing key | Yes (prod) |

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Connect directly
psql -h localhost -U aureon -d aureon
```

### API Errors

```bash
# Check backend logs
docker-compose logs backend

# Test health endpoint
curl -v http://localhost:8000/health
```

### Frontend Build Issues

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run dev
```

---

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with tests
3. Run linting: `npm run lint`
4. Commit: `git commit -m "feat: description"`
5. Push and create PR

---

*For architecture details, see [Whitepaper](./Aureon_Whitepaper_First_Principles_v0.1.md).*

