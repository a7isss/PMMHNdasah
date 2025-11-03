# 🗄️ Database Schema Design
## WhatsApp-Integrated Civil Engineering PM System v3.0 (Gamma)

**Version:** 1.0 - AI-Optimized Schema
**Last Updated:** November 2025
**Purpose:** Complete PostgreSQL schema with AI integration

---

## 🎯 Schema Design Principles

### AI-First Database Design
Every table designed to generate clean data for AI processing:

```sql
-- AI metadata stored with every record
ai_metadata JSONB DEFAULT '{
  "processed": false,
  "confidence_score": 0.0,
  "last_analyzed": null,
  "insights": [],
  "risk_score": 0.0
}'::jsonb,

-- Vector embeddings for semantic search
embedding VECTOR(1536), -- OpenAI text-embedding-ada-002

-- Full-text search optimized for AI queries
search_vector TSVECTOR GENERATED ALWAYS AS (
  setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(description, '')), 'B')
) STORED,
```

### Multi-Tenant Architecture
Complete data isolation with Row-Level Security:

```sql
-- Tenant isolation at database level
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_data_access" ON projects
  FOR ALL USING (auth.jwt() ->> 'tenant_id' = tenant_id::text);
```

---

## 📊 Core Tables Schema

### 1. Tenants (Multi-Tenant Support)

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subscription_plan VARCHAR(50) DEFAULT 'starter',
    is_active BOOLEAN DEFAULT true,

    -- Contact Information
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address JSONB,

    -- Settings
    settings JSONB DEFAULT '{
      "timezone": "UTC",
      "currency": "USD",
      "language": "en",
      "features": {
        "whatsapp": true,
        "ai_insights": true,
        "advanced_reporting": false
      }
    }'::jsonb,

    -- AI Configuration
    ai_config JSONB DEFAULT '{
      "openai_api_key": null,
      "model_preferences": {
        "intent_classification": "gpt-4-turbo",
        "response_generation": "gpt-4-turbo",
        "forecasting": "gpt-4-turbo"
      },
      "confidence_thresholds": {
        "intent": 0.8,
        "sentiment": 0.7,
        "urgency": 0.75
      }
    }'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (char_length(name) >= 2),
    CHECK (subscription_plan IN ('free', 'starter', 'professional', 'enterprise'))
);

-- Indexes
CREATE UNIQUE INDEX idx_tenants_domain ON tenants(domain) WHERE domain IS NOT NULL;
CREATE INDEX idx_tenants_active ON tenants(is_active) WHERE is_active = true;
```

### 2. Users (Authentication & Profiles)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Authentication
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    is_email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,

    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(50),
    job_title VARCHAR(100),

    -- Role & Permissions
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB DEFAULT '[]'::jsonb,

    -- Preferences
    preferences JSONB DEFAULT '{
      "theme": "light",
      "notifications": {
        "email": true,
        "whatsapp": true,
        "push": true
      },
      "language": "en",
      "timezone": "UTC"
    }'::jsonb,

    -- WhatsApp Integration
    whatsapp_number VARCHAR(20),
    whatsapp_verified BOOLEAN DEFAULT false,

    -- AI Personalization
    ai_profile JSONB DEFAULT '{
      "communication_style": "professional",
      "response_preferences": {
        "detail_level": "balanced",
        "urgency_sensitivity": "medium"
      },
      "learning_data": []
    }'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,
    deactivated_at TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    -- Constraints
    CHECK (role IN ('super_admin', 'admin', 'manager', 'member', 'viewer')),
    CHECK (char_length(email) >= 5),
    UNIQUE (tenant_id, email)
);

-- Indexes
CREATE UNIQUE INDEX idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX idx_users_role ON users(tenant_id, role);
CREATE INDEX idx_users_active ON users(tenant_id, is_active) WHERE is_active = true;
CREATE INDEX idx_users_whatsapp ON users(whatsapp_number) WHERE whatsapp_number IS NOT NULL;
```

### 3. Projects (Core Entity)

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_number VARCHAR(50) UNIQUE,
    contract_type VARCHAR(50) DEFAULT 'lump_sum',

    -- Location with PostGIS
    location GEOGRAPHY(POINT, 4326),
    address JSONB,
    site_boundaries GEOGRAPHY(POLYGON, 4326),

    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,
    status project_status DEFAULT 'planning',

    -- Financial
    budget_total DECIMAL(15,2) NOT NULL DEFAULT 0,
    actual_cost DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Progress & Risk
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    risk_level VARCHAR(20) DEFAULT 'low',
    health_score DECIMAL(5,2) GENERATED ALWAYS AS (
        calculate_project_health(id)
    ) STORED,

    -- Team
    project_manager_id UUID REFERENCES users(id),
    client_contact JSONB,

    -- AI Integration
    ai_insights JSONB DEFAULT '{}',
    risk_predictions JSONB DEFAULT '[]',
    embedding VECTOR(1536),
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B')
    ) STORED,

    -- Metadata
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    ai_metadata JSONB DEFAULT '{}',

    -- WhatsApp Settings
    whatsapp_settings JSONB DEFAULT '{
      "auto_responses": true,
      "ai_processing": true,
      "notification_contacts": []
    }'::jsonb,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (end_date >= start_date),
    CHECK (actual_end_date >= actual_start_date OR actual_end_date IS NULL),
    CHECK (status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled')),
    CHECK (contract_type IN ('lump_sum', 'cost_plus', 'time_materials', 'unit_price')),
    CHECK (risk_level IN ('low', 'medium', 'high', 'critical'))
);

-- Indexes
CREATE INDEX idx_projects_tenant ON projects(tenant_id);
CREATE INDEX idx_projects_status ON projects(tenant_id, status);
CREATE INDEX idx_projects_health ON projects(tenant_id, health_score DESC);
CREATE INDEX idx_projects_risk ON projects(tenant_id, risk_level, updated_at DESC);
CREATE INDEX idx_projects_embedding ON projects USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_projects_location ON projects USING gist(location);
CREATE INDEX idx_projects_search ON projects USING gin(search_vector);
CREATE INDEX idx_projects_dates ON projects(tenant_id, start_date, end_date);
```

### 4. Project Members (Team Management)

```sql
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Role in Project
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB DEFAULT '["read"]'::jsonb,

    -- Assignment Details
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    deactivated_at TIMESTAMPTZ,

    -- Workload & Capacity
    capacity_percentage INTEGER DEFAULT 100 CHECK (capacity_percentage >= 0 AND capacity_percentage <= 100),
    workload_hours DECIMAL(5,2) DEFAULT 0,

    -- Communication Preferences
    notification_settings JSONB DEFAULT '{
      "email": true,
      "whatsapp": true,
      "task_assignments": true,
      "project_updates": true,
      "deadline_reminders": true
    }'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (role IN ('owner', 'manager', 'lead', 'member', 'viewer')),
    UNIQUE (project_id, user_id)
);

-- Indexes
CREATE UNIQUE INDEX idx_project_members_unique ON project_members(project_id, user_id);
CREATE INDEX idx_project_members_user ON project_members(user_id, is_active);
CREATE INDEX idx_project_members_role ON project_members(project_id, role);
```

### 5. Tasks (Project Breakdown)

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Task Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    task_code VARCHAR(50),

    -- Hierarchy
    parent_task_id UUID REFERENCES tasks(id),
    level INTEGER DEFAULT 1 CHECK (level >= 1),
    wbs_code VARCHAR(100), -- Work Breakdown Structure code

    -- Schedule
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Duration & Progress
    planned_duration_days INTEGER,
    actual_duration_days INTEGER,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    status task_status DEFAULT 'not_started',

    -- Resources
    assigned_to UUID REFERENCES users(id),
    estimated_hours DECIMAL(8,2),
    actual_hours DECIMAL(8,2),

    -- Dependencies
    predecessor_tasks UUID[],
    successor_tasks UUID[],
    lag_days INTEGER DEFAULT 0,

    -- Cost
    budgeted_cost DECIMAL(12,2) DEFAULT 0,
    actual_cost DECIMAL(12,2) DEFAULT 0,

    -- Critical Path
    is_critical_path BOOLEAN DEFAULT false,
    slack_days INTEGER DEFAULT 0,

    -- AI Integration
    ai_priority_score DECIMAL(3,2),
    ai_risk_score DECIMAL(3,2),
    ai_insights JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B')
    ) STORED,

    -- Metadata
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    ai_metadata JSONB DEFAULT '{}',

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (planned_end_date >= planned_start_date OR planned_end_date IS NULL),
    CHECK (actual_end_date >= actual_start_date OR actual_end_date IS NULL),
    CHECK (status IN ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled')),
    CHECK (ai_priority_score >= 0 AND ai_priority_score <= 1 OR ai_priority_score IS NULL),
    CHECK (ai_risk_score >= 0 AND ai_risk_score <= 1 OR ai_risk_score IS NULL)
);

-- Indexes
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to, status);
CREATE INDEX idx_tasks_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_dates ON tasks(project_id, planned_start_date, planned_end_date);
CREATE INDEX idx_tasks_critical ON tasks(project_id, is_critical_path) WHERE is_critical_path = true;
CREATE INDEX idx_tasks_embedding ON tasks USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_tasks_search ON tasks USING gin(search_vector);
CREATE INDEX idx_tasks_ai_priority ON tasks(project_id, ai_priority_score DESC NULLS LAST);
```

### 6. Cost Items (Financial Tracking)

```sql
CREATE TABLE cost_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Cost Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),

    -- Financial
    budgeted_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    actual_amount DECIMAL(12,2) DEFAULT 0,
    committed_amount DECIMAL(12,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Schedule
    planned_date DATE,
    actual_date DATE,

    -- Vendor/Supplier
    vendor_id UUID,
    vendor_name VARCHAR(255),
    contract_reference VARCHAR(100),

    -- Approval Workflow
    status cost_status DEFAULT 'planned',
    approval_required BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,

    -- Task Association
    task_id UUID REFERENCES tasks(id),

    -- AI Integration
    ai_category_prediction VARCHAR(100),
    ai_amount_forecast DECIMAL(12,2),
    ai_risk_score DECIMAL(3,2),
    ai_insights JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B')
    ) STORED,

    -- Metadata
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    ai_metadata JSONB DEFAULT '{}',

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (status IN ('planned', 'committed', 'approved', 'incurred', 'paid')),
    CHECK (actual_amount >= 0),
    CHECK (budgeted_amount >= 0),
    CHECK (ai_risk_score >= 0 AND ai_risk_score <= 1 OR ai_risk_score IS NULL)
);

-- Indexes
CREATE INDEX idx_cost_items_project ON cost_items(project_id);
CREATE INDEX idx_cost_items_category ON cost_items(project_id, category);
CREATE INDEX idx_cost_items_status ON cost_items(project_id, status);
CREATE INDEX idx_cost_items_vendor ON cost_items(vendor_id);
CREATE INDEX idx_cost_items_dates ON cost_items(project_id, planned_date, actual_date);
CREATE INDEX idx_cost_items_embedding ON cost_items USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_cost_items_search ON cost_items USING gin(search_vector);
```

### 7. WhatsApp Contacts

```sql
CREATE TABLE whatsapp_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Contact Information
    whatsapp_number VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    company VARCHAR(255),

    -- Profile
    avatar_url VARCHAR(500),
    location VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',

    -- Relationship
    contact_type VARCHAR(50) DEFAULT 'client',
    projects UUID[], -- Associated project IDs

    -- Communication Preferences
    notification_settings JSONB DEFAULT '{
      "updates": true,
      "alerts": true,
      "reports": false
    }'::jsonb,

    -- AI Integration
    ai_personality_profile JSONB DEFAULT '{}',
    ai_communication_history JSONB DEFAULT '[]',
    embedding VECTOR(1536),

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_contacted_at TIMESTAMPTZ,
    message_count INTEGER DEFAULT 0,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (contact_type IN ('client', 'contractor', 'supplier', 'team_member', 'other')),
    UNIQUE (tenant_id, whatsapp_number)
);

-- Indexes
CREATE UNIQUE INDEX idx_whatsapp_contacts_tenant_number ON whatsapp_contacts(tenant_id, whatsapp_number);
CREATE INDEX idx_whatsapp_contacts_active ON whatsapp_contacts(tenant_id, is_active) WHERE is_active = true;
CREATE INDEX idx_whatsapp_contacts_embedding ON whatsapp_contacts USING ivfflat(embedding vector_cosine_ops);
```

### 8. WhatsApp Messages (AI Processing Core)

```sql
CREATE TABLE whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES whatsapp_contacts(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    -- Message Content
    direction message_direction NOT NULL,
    message_type message_type DEFAULT 'text',
    content TEXT,
    media_urls TEXT[],
    media_metadata JSONB DEFAULT '{}',

    -- WhatsApp Specific
    whatsapp_message_id VARCHAR(255),
    whatsapp_timestamp TIMESTAMPTZ,

    -- AI Analysis Results
    ai_processed BOOLEAN DEFAULT false,
    intent_classification VARCHAR(100),
    sentiment_score DECIMAL(3,2),
    urgency_level VARCHAR(20),
    extracted_entities JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),

    -- Context Linking
    related_task_id UUID REFERENCES tasks(id),
    related_cost_item_id UUID REFERENCES cost_items(id),
    conversation_context JSONB DEFAULT '{}',

    -- Response
    auto_response_sent BOOLEAN DEFAULT false,
    response_content TEXT,
    response_timestamp TIMESTAMPTZ,

    -- Delivery & Status
    delivery_status VARCHAR(20) DEFAULT 'sent',
    read_at TIMESTAMPTZ,
    error_message TEXT,

    -- Search & AI
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(content, '')), 'A')
    ) STORED,
    embedding VECTOR(1536),

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_messages_contact ON whatsapp_messages(contact_id);
CREATE INDEX idx_messages_project ON whatsapp_messages(project_id);
CREATE INDEX idx_messages_timestamp ON whatsapp_messages(whatsapp_timestamp DESC);
CREATE INDEX idx_messages_ai_processed ON whatsapp_messages(project_id, ai_processed) WHERE ai_processed = false;
CREATE INDEX idx_messages_intent ON whatsapp_messages(project_id, intent_classification, created_at DESC);
CREATE INDEX idx_messages_sentiment ON whatsapp_messages(project_id, sentiment_score);
CREATE INDEX idx_messages_embedding ON whatsapp_messages USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_messages_search ON whatsapp_messages USING gin(search_vector);
```

---

## 🔒 Row-Level Security Policies

### Core Security Policies

```sql
-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;

-- Tenants: Users can only see their own tenant
CREATE POLICY "tenants_access" ON tenants
    FOR ALL USING (auth.jwt() ->> 'tenant_id' = id::text);

-- Users: Users can see users in their tenant
CREATE POLICY "users_access" ON users
    FOR ALL USING (auth.jwt() ->> 'tenant_id' = tenant_id::text);

-- Projects: Users can access projects where they are members or tenant admins
CREATE POLICY "projects_access" ON projects
    FOR ALL USING (
      -- User is project member
      EXISTS (
        SELECT 1 FROM project_members pm
        WHERE pm.project_id = projects.id
        AND pm.user_id = auth.uid()
        AND pm.is_active = true
      )
      -- OR user has tenant admin role
      OR EXISTS (
        SELECT 1 FROM users u
        WHERE u.id = auth.uid()
        AND u.tenant_id = projects.tenant_id
        AND u.role IN ('admin', 'super_admin')
      )
    );

-- Tasks: Same as projects
CREATE POLICY "tasks_access" ON tasks
    FOR ALL USING (
      EXISTS (
        SELECT 1 FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE tasks.project_id = p.id
        AND pm.user_id = auth.uid()
        AND pm.is_active = true
      )
    );

-- Cost Items: Same as projects
CREATE POLICY "cost_items_access" ON cost_items
    FOR ALL USING (
      EXISTS (
        SELECT 1 FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE cost_items.project_id = p.id
        AND pm.user_id = auth.uid()
        AND pm.is_active = true
      )
    );

-- WhatsApp Contacts: Tenant-level access
CREATE POLICY "whatsapp_contacts_access" ON whatsapp_contacts
    FOR ALL USING (auth.jwt() ->> 'tenant_id' = tenant_id::text);

-- WhatsApp Messages: Project member access
CREATE POLICY "whatsapp_messages_access" ON whatsapp_messages
    FOR ALL USING (
      -- User can access project messages
      EXISTS (
        SELECT 1 FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE whatsapp_messages.project_id = p.id
        AND pm.user_id = auth.uid()
        AND pm.is_active = true
      )
      -- OR user can access contact messages (tenant level)
      OR EXISTS (
        SELECT 1 FROM whatsapp_contacts wc
        WHERE whatsapp_messages.contact_id = wc.id
        AND wc.tenant_id::text = auth.jwt() ->> 'tenant_id'
      )
    );
```

---

## 🤖 AI Integration Functions

### Project Health Calculation

```sql
CREATE OR REPLACE FUNCTION calculate_project_health(project_uuid UUID)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
AS $$
DECLARE
    health_score DECIMAL(5,2) := 0;
    progress_weight DECIMAL(3,2) := 0.3;
    budget_weight DECIMAL(3,2) := 0.25;
    schedule_weight DECIMAL(3,2) := 0.25;
    risk_weight DECIMAL(3,2) := 0.2;

    progress_score DECIMAL(5,2);
    budget_score DECIMAL(5,2);
    schedule_score DECIMAL(5,2);
    risk_score DECIMAL(5,2);

    project_record RECORD;
BEGIN
    -- Get project data
    SELECT * INTO project_record FROM projects WHERE id = project_uuid;

    IF NOT FOUND THEN
        RETURN 0;
    END IF;

    -- Progress Score (0-100)
    progress_score := project_record.progress_percentage;

    -- Budget Score (0-100): Lower variance = higher score
    IF project_record.budget_total > 0 THEN
        budget_score := GREATEST(0, 100 - ((project_record.actual_cost - project_record.budget_total) / project_record.budget_total * 100));
    ELSE
        budget_score := 100;
    END IF;

    -- Schedule Score (0-100): Based on planned vs actual dates
    IF project_record.end_date IS NOT NULL AND project_record.actual_end_date IS NOT NULL THEN
        -- Calculate schedule variance
        planned_days := project_record.end_date - project_record.start_date;
        actual_days := project_record.actual_end_date - project_record.start_date;
        schedule_variance := (actual_days - planned_days) / planned_days * 100;
        schedule_score := GREATEST(0, 100 - ABS(schedule_variance));
    ELSIF project_record.actual_end_date IS NULL THEN
        -- Project still active, score based on progress vs time elapsed
        total_days := project_record.end_date - project_record.start_date;
        elapsed_days := CURRENT_DATE - project_record.start_date;
        expected_progress := (elapsed_days::DECIMAL / total_days) * 100;
        schedule_score := GREATEST(0, 100 - ABS(project_record.progress_percentage - expected_progress));
    ELSE
        schedule_score := 100; -- Project completed on time
    END IF;

    -- Risk Score (0-100): Based on risk level and AI predictions
    CASE project_record.risk_level
        WHEN 'low' THEN risk_score := 90
        WHEN 'medium' THEN risk_score := 70
        WHEN 'high' THEN risk_score := 40
        WHEN 'critical' THEN risk_score := 10
        ELSE risk_score := 50
    END CASE;

    -- Calculate weighted health score
    health_score := (
        progress_score * progress_weight +
        budget_score * budget_weight +
        schedule_score * schedule_weight +
        risk_score * risk_weight
    );

    RETURN ROUND(health_score, 2);
END;
$$;

-- Semantic Search Function for AI Queries
CREATE OR REPLACE FUNCTION semantic_project_search(
  query_embedding VECTOR(1536),
  tenant_uuid UUID,
  match_threshold FLOAT DEFAULT 0.8,
  max_results INTEGER DEFAULT 20
)
RETURNS TABLE (
  id UUID,
  name VARCHAR(255),
  similarity FLOAT,
  score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.name,
    1 - (p.embedding <=> query_embedding) as similarity,
    -- Combined score: semantic + text + recency
    (1 - (p.embedding <=> query_embedding)) * 0.7 +
    ts_rank(p.search_vector, plainto_tsquery('english', 'construction project')) * 0.2 +
    (EXTRACT(EPOCH FROM (NOW() - p.updated_at)) / 86400 / 365) * 0.1 as score
  FROM projects p
  WHERE p.tenant_id = tenant_uuid
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
  ORDER BY score DESC
  LIMIT max_results;
END;
$$;

-- AI Insight Generation Trigger
CREATE OR REPLACE FUNCTION generate_ai_insights()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  -- Trigger AI analysis for significant changes
  IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
    -- Queue AI analysis job
    PERFORM pg_notify('ai_analysis_queue',
      json_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'record_id', NEW.id,
        'tenant_id', NEW.tenant_id
      )::text
    );
  END IF;

  RETURN NEW;
END;
$$;

-- Apply triggers to key tables
CREATE TRIGGER projects_ai_insights_trigger
  AFTER INSERT OR UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION generate_ai_insights();

CREATE TRIGGER tasks_ai_insights_trigger
  AFTER INSERT OR UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION generate_ai_insights();

CREATE TRIGGER whatsapp_messages_ai_trigger
  AFTER INSERT ON whatsapp_messages
  FOR EACH ROW EXECUTE FUNCTION generate_ai_insights();

---

## 🔧 Custom Types & Enums

### Project Status Types
```sql
CREATE TYPE project_status AS ENUM (
    'planning',
    'active',
    'on_hold',
    'completed',
    'cancelled'
);
```

### Task Status Types
```sql
CREATE TYPE task_status AS ENUM (
    'not_started',
    'in_progress',
    'completed',
    'on_hold',
    'cancelled'
);
```

### Cost Status Types
```sql
CREATE TYPE cost_status AS ENUM (
    'planned',
    'committed',
    'approved',
    'incurred',
    'paid'
);
```

### WhatsApp Message Direction
```sql
CREATE TYPE message_direction AS ENUM (
    'inbound',
    'outbound'
);
```

### WhatsApp Message Types
```sql
CREATE TYPE message_type AS ENUM (
    'text',
    'image',
    'video',
    'audio',
    'document',
    'location',
    'contact'
);
```

---

## 🚀 Database Setup Script

### Complete Schema Creation Order
```sql
-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- 2. Create custom types
CREATE TYPE project_status AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');
CREATE TYPE task_status AS ENUM ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled');
CREATE TYPE cost_status AS ENUM ('planned', 'committed', 'approved', 'incurred', 'paid');
CREATE TYPE message_direction AS ENUM ('inbound', 'outbound');
CREATE TYPE message_type AS ENUM ('text', 'image', 'video', 'audio', 'document', 'location', 'contact');

-- 3. Create tables (in dependency order)
-- ... [All table creation statements from above]

-- 4. Create functions
-- ... [All function creation statements from above]

-- 5. Create triggers
-- ... [All trigger creation statements from above]

-- 6. Enable real-time subscriptions
ALTER PUBLICATION supabase_realtime ADD TABLE projects;
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE cost_items;

-- 7. Create indexes
-- ... [All index creation statements from above]

-- 8. Enable Row-Level Security
-- ... [All RLS statements from above]
```

---

## 📊 Database Performance Optimization

### Query Optimization Examples

```sql
-- Optimized project dashboard query
SELECT
    p.id,
    p.name,
    p.status,
    p.progress_percentage,
    p.health_score,
    p.budget_total,
    p.actual_cost,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
    SUM(c.actual_amount) as total_cost_incurred,
    MAX(wm.created_at) as last_message_at
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN cost_items c ON p.id = c.project_id
LEFT JOIN whatsapp_messages wm ON p.id = wm.project_id
WHERE p.tenant_id = $1
  AND p.status IN ('active', 'planning')
GROUP BY p.id, p.name, p.status, p.progress_percentage, p.health_score, p.budget_total, p.actual_cost
ORDER BY p.health_score DESC, p.updated_at DESC
LIMIT 50;
```

### AI Data Generation Queries

```sql
-- Generate training data for intent classification
SELECT
    content,
    intent_classification,
    sentiment_score,
    urgency_level,
    extracted_entities,
    confidence_score,
    ai_metadata
FROM whatsapp_messages
WHERE ai_processed = true
  AND confidence_score > 0.8
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

---

## 🔍 Monitoring & Maintenance

### Key Metrics to Monitor

```sql
-- Database performance metrics
SELECT
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Vector search performance
SELECT
    query,
    total_time,
    mean_time,
    calls,
    rows
FROM pg_stat_statements
WHERE query LIKE '%<=>%'
ORDER BY mean_time DESC;
```

---

## 🎯 Next Steps

Now that you have the complete database schema:

1. **Set up Supabase project** with the required extensions
2. **Execute the schema creation** in the correct order
3. **Configure Row-Level Security** policies
4. **Test the schema** with sample data
5. **Move to Phase 1, Week 2**: Authentication & Basic API

---

*This AI-optimized database schema is designed for the ultimate construction project management system.*
