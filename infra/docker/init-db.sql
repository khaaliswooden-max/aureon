-- Aureon Database Initialization
-- This script runs when PostgreSQL container first starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS aureon;
CREATE SCHEMA IF NOT EXISTS ingestion;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL ON SCHEMA aureon TO aureon;
GRANT ALL ON SCHEMA ingestion TO aureon;
GRANT ALL ON SCHEMA analytics TO aureon;

-- Create initial tables

-- Organizations table
CREATE TABLE IF NOT EXISTS aureon.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    legal_name VARCHAR(500),
    duns_number VARCHAR(13) UNIQUE,
    uei VARCHAR(12) UNIQUE,
    cage_code VARCHAR(10),
    ein VARCHAR(20),
    naics_codes TEXT[],
    psc_codes TEXT[],
    set_aside_types TEXT[],
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    website VARCHAR(500),
    employee_count INTEGER,
    annual_revenue DECIMAL(18, 2),
    founded_year INTEGER,
    capabilities_narrative TEXT,
    past_performance_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Opportunities table
CREATE TABLE IF NOT EXISTS aureon.opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id VARCHAR(100) NOT NULL,
    source_system VARCHAR(50) NOT NULL DEFAULT 'sam.gov',
    title TEXT NOT NULL,
    description TEXT,
    notice_type VARCHAR(100),
    solicitation_number VARCHAR(100),
    naics_code VARCHAR(10),
    naics_description TEXT,
    psc_code VARCHAR(20),
    psc_description TEXT,
    set_aside_type VARCHAR(100),
    response_deadline TIMESTAMP WITH TIME ZONE,
    posted_date TIMESTAMP WITH TIME ZONE,
    archive_date TIMESTAMP WITH TIME ZONE,
    contract_type VARCHAR(50),
    estimated_value_min DECIMAL(18, 2),
    estimated_value_max DECIMAL(18, 2),
    place_of_performance_city VARCHAR(100),
    place_of_performance_state VARCHAR(50),
    place_of_performance_zip VARCHAR(20),
    place_of_performance_country VARCHAR(100),
    contracting_office_name VARCHAR(500),
    contracting_office_address TEXT,
    contracting_officer_name VARCHAR(200),
    contracting_officer_email VARCHAR(255),
    contracting_officer_phone VARCHAR(50),
    point_of_contact_name VARCHAR(200),
    point_of_contact_email VARCHAR(255),
    point_of_contact_phone VARCHAR(50),
    award_date TIMESTAMP WITH TIME ZONE,
    award_amount DECIMAL(18, 2),
    awardee_name VARCHAR(500),
    awardee_uei VARCHAR(12),
    status VARCHAR(50) DEFAULT 'active',
    classification_code VARCHAR(50),
    security_clearance_required VARCHAR(100),
    attachments JSONB DEFAULT '[]',
    amendments JSONB DEFAULT '[]',
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_id, source_system)
);

-- Relevance scores table
CREATE TABLE IF NOT EXISTS aureon.relevance_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES aureon.organizations(id) ON DELETE CASCADE,
    opportunity_id UUID NOT NULL REFERENCES aureon.opportunities(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 4) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 1),
    naics_score DECIMAL(5, 4) CHECK (naics_score >= 0 AND naics_score <= 1),
    semantic_score DECIMAL(5, 4) CHECK (semantic_score >= 0 AND semantic_score <= 1),
    geographic_score DECIMAL(5, 4) CHECK (geographic_score >= 0 AND geographic_score <= 1),
    size_score DECIMAL(5, 4) CHECK (size_score >= 0 AND size_score <= 1),
    past_performance_score DECIMAL(5, 4) CHECK (past_performance_score >= 0 AND past_performance_score <= 1),
    competition_score DECIMAL(5, 4) CHECK (competition_score >= 0 AND competition_score <= 1),
    component_weights JSONB DEFAULT '{}',
    explanation TEXT,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) DEFAULT 'v1.0.0',
    UNIQUE (organization_id, opportunity_id)
);

-- Risk assessments table
CREATE TABLE IF NOT EXISTS aureon.risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES aureon.organizations(id) ON DELETE CASCADE,
    opportunity_id UUID NOT NULL REFERENCES aureon.opportunities(id) ON DELETE CASCADE,
    overall_risk_level VARCHAR(20) NOT NULL CHECK (overall_risk_level IN ('low', 'medium', 'high', 'critical')),
    overall_risk_score DECIMAL(5, 4) NOT NULL CHECK (overall_risk_score >= 0 AND overall_risk_score <= 1),
    eligibility_risk JSONB DEFAULT '{}',
    technical_risk JSONB DEFAULT '{}',
    pricing_risk JSONB DEFAULT '{}',
    resource_risk JSONB DEFAULT '{}',
    compliance_risk JSONB DEFAULT '{}',
    timeline_risk JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '[]',
    mitigation_suggestions JSONB DEFAULT '[]',
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) DEFAULT 'v1.0.0',
    UNIQUE (organization_id, opportunity_id)
);

-- Ingestion logs table
CREATE TABLE IF NOT EXISTS ingestion.ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_system VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running',
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Benchmark results table
CREATE TABLE IF NOT EXISTS analytics.benchmark_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    benchmark_id VARCHAR(20) NOT NULL,
    run_id VARCHAR(100) NOT NULL,
    organization_id UUID REFERENCES aureon.organizations(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running',
    metrics JSONB DEFAULT '{}',
    configuration JSONB DEFAULT '{}',
    error_message TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON aureon.opportunities(source_system, source_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_naics ON aureon.opportunities(naics_code);
CREATE INDEX IF NOT EXISTS idx_opportunities_posted ON aureon.opportunities(posted_date DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON aureon.opportunities(response_deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON aureon.opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_title_trgm ON aureon.opportunities USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_opportunities_description_trgm ON aureon.opportunities USING gin(description gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_organizations_naics ON aureon.organizations USING gin(naics_codes);
CREATE INDEX IF NOT EXISTS idx_organizations_name_trgm ON aureon.organizations USING gin(name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_relevance_org ON aureon.relevance_scores(organization_id);
CREATE INDEX IF NOT EXISTS idx_relevance_opp ON aureon.relevance_scores(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_relevance_score ON aureon.relevance_scores(overall_score DESC);

CREATE INDEX IF NOT EXISTS idx_risk_org ON aureon.risk_assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_risk_opp ON aureon.risk_assessments(opportunity_id);

-- Full-text search configuration
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS aureon.procurement_config (COPY = english);

-- Create function for updated_at trigger
CREATE OR REPLACE FUNCTION aureon.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON aureon.organizations
    FOR EACH ROW
    EXECUTE FUNCTION aureon.update_updated_at_column();

CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON aureon.opportunities
    FOR EACH ROW
    EXECUTE FUNCTION aureon.update_updated_at_column();

-- Insert sample data for testing
INSERT INTO aureon.organizations (name, legal_name, uei, naics_codes, psc_codes, set_aside_types, city, state, employee_count, capabilities_narrative)
VALUES 
    ('Acme Tech Solutions', 'Acme Technology Solutions LLC', 'ABCD12345678', ARRAY['541512', '541519', '541511'], ARRAY['D302', 'D306', 'D307'], ARRAY['SB', 'SDVOSB'], 'Arlington', 'VA', 45, 'Full-stack software development, cloud migration, and cybersecurity services for federal agencies.'),
    ('Delta Defense Systems', 'Delta Defense Systems Inc', 'EFGH87654321', ARRAY['336411', '541330', '541715'], ARRAY['1560', '1680', 'K039'], ARRAY['SB', '8A'], 'San Diego', 'CA', 120, 'Defense systems integration, aerospace engineering, and R&D services.'),
    ('Epsilon Environmental', 'Epsilon Environmental Services LLC', 'IJKL11223344', ARRAY['562910', '541620', '541380'], ARRAY['F108', 'F999', 'B506'], ARRAY['WOSB', 'SB'], 'Denver', 'CO', 28, 'Environmental consulting, remediation services, and compliance support.')
ON CONFLICT DO NOTHING;

COMMIT;

