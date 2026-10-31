# IdeaOS - Database Schema & Migrations

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Draft

---

## 1. Overview

- **Database**: PostgreSQL 15+ (Supabase)
- **Extensions**: `uuid-ossp`, `pgvector`, `pg_trgm`, `btree_gin`
- **Naming**: snake_case tables/columns, UUID primary keys, plural table names
- **Timestamps**: `created_at`, `updated_at` on all tables (trigger-maintained)
- **Soft Deletes**: `deleted_at` on core entities (captures, ideas, content)
- **Row Level Security**: Enforced on ALL tables via `workspace_id`
- **Indexes**: Strategic B-tree, GIN, HNSW (vector), partial indexes

---

## 2. Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   users     │       │  workspaces │       │  captures   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ id (PK)     │◄──────│ id (PK)     │
│ email       │       │ name        │       │ workspace_id│
│ name        │       │ owner_id    │       │ user_id     │
│ avatar_url  │       │ settings    │       │ type        │
│ created_at  │       │ created_at  │       │ status      │
└─────────────┘       └─────────────┘       │ source_text │
       │                   │                │ metadata    │
       │                   │                │ asset_id    │
       │                   │                │ idea_id     │
       │                   │                │ created_at  │
       │                   │                └──────┬──────┘
       │                   │                       │
       │                   │                ┌──────▼──────┐
       │                   │                │   assets    │
       │                   │                ├─────────────┤
       │                   │                │ id (PK)     │
       │                   │                │ workspace_id│
       │                   │                │ capture_id  │
       │                   │                │ storage_key │
       │                   │                │ mime_type   │
       │                   │                │ size_bytes  │
       │                   │                │ checksum    │
       │                   │                │ status      │
       │                   │                │ created_at  │
       │                   │                └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────────────┐
│           ideas                         │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ workspace_id (FK)                       │
│ capture_id (FK, nullable)               │
│ title                                   │
│ summary                                 │
│ original_thought                        │
│ main_topic                              │
│ supporting_context                      │
│ target_audience                         │
│ underlying_problem                      │
│ key_opinion_insight                     │
│ content_pillar                          │
│ suggested_formats (JSONB)               │
│ suggested_platforms (JSONB)             │
│ keywords_entities (JSONB)               │
│ embedding (vector(1536))                │
│ status (candidate|approved|archived)    │
│ version                                 │
│ parent_idea_id (FK, self-ref)           │
│ created_at, updated_at, deleted_at      │
└─────────────────────────────────────────┘
       │
       ├──┬──────────────────┐
       ▼  ▼                  ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│idea_sources │    │  idea_relations │    │fusion_proposals │
├─────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)     │    │ id (PK)         │    │ id (PK)         │
│ idea_id (FK)│    │ workspace_id    │    │ workspace_id    │
│ capture_id  │    │ source_idea_id  │    │ new_idea_id     │
│ asset_id    │    │ target_idea_id  │    │ source_idea_ids │
│ source_type │    │ relation_type   │    │ relationship[]  │
│ content     │    │ confidence      │    │ fusion_concept  │
│ metadata    │    │ explanation     │    │ confidence      │
│ created_at  │    │ created_at      │    │ status          │
└─────────────┘    └─────────────────┘    │ created_at      │
                                           └────────┬────────┘
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                              ┌──────────┐    ┌──────────┐    ┌──────────┐
                              │  brand_  │    │  brand_  │    │ content_ │
                              │ profiles │    │  rules   │    │ outputs  │
                              ├──────────┤    ├──────────┤    ├──────────┤
                              │ id (PK)  │    │ id (PK)  │    │ id (PK)  │
                              │workspace │    │workspace │    │workspace │
                              │ voice    │    │ rule_type│    │ idea_id  │
                              │ tone     │    │ pattern  │    │ platform │
                              │ style    │    │ severity │    │ format   │
                              │ audience │    │ message  │    │ content  │
                              │position  │    │ examples │    │ status   │
                              │ opinions │    │ created_at│   │quality   │
                              │ visual   │    └──────────┘    │ score    │
                              │prohibited│                     │ feedback │
                              │ version  │                     │ created_ │
                              └──────────┘                     └────┬─────┘
                                                                    │
                              ┌─────────────────┐                  │
                              │ calendar_items  │◄─────────────────┘
                              ├─────────────────┤
                              │ id (PK)         │
                              │ workspace_id    │
                              │ content_output_id
                              │ status          │
                              │ scheduled_at    │
                              │ published_at    │
                              │ platform        │
                              │ metadata        │
                              │ created_at      │
                              └─────────────────┘
                              ┌─────────────────┐
                              │ feedback_events │
                              ├─────────────────┤
                              │ id (PK)         │
                              │ workspace_id    │
                              │ entity_type     │
                              │ entity_id       │
                              │ action          │
                              │ reason          │
                              │ before/after    │
                              │ user_id         │
                              │ created_at      │
                              └─────────────────┘
                              ┌─────────────────┐
                              │processing_jobs  │
                              ├─────────────────┤
                              │ id (PK)         │
                              │ workspace_id    │
                              │ capture_id      │
                              │ job_type        │
                              │ status          │
                              │ payload         │
                              │ result          │
                              │ error           │
                              │ attempts        │
                              │ started_at      │
                              │ completed_at    │
                              └─────────────────┘
```

---

## 3. Table Definitions

### 3.1 Core Tables

#### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    avatar_url TEXT,
    password_hash VARCHAR(255),  -- For email/password auth
    auth_provider VARCHAR(50) DEFAULT 'email', -- email, google, github, apple
    auth_provider_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider, auth_provider_id);
```

#### `workspaces`
```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    owner_id UUID NOT NULL REFERENCES users(id),
    settings JSONB DEFAULT '{}', -- {theme, default_platforms, notifications, etc.}
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, team, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_slug ON workspaces(slug);
```

#### `workspace_members`
```sql
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- owner, admin, member, viewer
    invited_by UUID REFERENCES users(id),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, user_id)
);

CREATE INDEX idx_ws_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_ws_members_user ON workspace_members(user_id);
```

---

### 3.2 Capture & Asset Tables

#### `captures`
```sql
CREATE TABLE captures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- voice, image, file, link, text
    status VARCHAR(50) NOT NULL DEFAULT 'uploading', -- uploading, processing, completed, failed
    source_text TEXT, -- Original transcribed/extracted text
    metadata JSONB DEFAULT '{}', -- {duration, dimensions, filename, url, etc.}
    asset_id UUID, -- FK to assets (set after upload)
    idea_id UUID, -- FK to ideas (set after processing)
    error_message TEXT,
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_captures_workspace ON captures(workspace_id);
CREATE INDEX idx_captures_user ON captures(user_id);
CREATE INDEX idx_captures_status ON captures(status) WHERE status IN ('uploading', 'processing');
CREATE INDEX idx_captures_created ON captures(created_at DESC);
CREATE INDEX idx_captures_type ON captures(type);
```

#### `assets`
```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    capture_id UUID REFERENCES captures(id) ON DELETE SET NULL,
    storage_key VARCHAR(512) NOT NULL, -- R2/S3 object key
    bucket VARCHAR(100) NOT NULL DEFAULT 'ideaos-assets',
    mime_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    checksum VARCHAR(64) NOT NULL, -- SHA-256
    original_filename VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, ready, scanned, failed, quarantined
    scan_result JSONB, -- Malware scan results
    metadata JSONB DEFAULT '{}', -- {width, height, duration, pages, etc.}
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_workspace ON assets(workspace_id);
CREATE INDEX idx_assets_capture ON assets(capture_id);
CREATE INDEX idx_assets_checksum ON assets(checksum);
CREATE INDEX idx_assets_status ON assets(status);
```

---

### 3.3 Idea & Intelligence Tables

#### `ideas`
```sql
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    capture_id UUID REFERENCES captures(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT NOT NULL,
    original_thought TEXT NOT NULL,
    main_topic VARCHAR(255),
    supporting_context TEXT,
    target_audience TEXT,
    underlying_problem TEXT,
    key_opinion_insight TEXT,
    content_pillar VARCHAR(255),
    suggested_formats JSONB DEFAULT '[]', -- ["reel", "carousel", "thread", ...]
    suggested_platforms JSONB DEFAULT '[]', -- ["instagram", "linkedin", "x", ...]
    keywords_entities JSONB DEFAULT '[]', -- [{"entity": "...", "type": "topic|person|org"}]
    embedding VECTOR(1536), -- pgvector, dimension matches embedding model
    status VARCHAR(50) NOT NULL DEFAULT 'candidate', -- candidate, approved, archived, fused
    version INTEGER NOT NULL DEFAULT 1,
    parent_idea_id UUID REFERENCES ideas(id) ON DELETE SET NULL, -- For fusion lineage
    fusion_source_ids UUID[] DEFAULT '{}', -- IDs of ideas fused to create this
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Vector index for semantic search (HNSW)
CREATE INDEX idx_ideas_embedding ON ideas USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Standard indexes
CREATE INDEX idx_ideas_workspace ON ideas(workspace_id);
CREATE INDEX idx_ideas_status ON ideas(status) WHERE status IN ('candidate', 'approved');
CREATE INDEX idx_ideas_pillar ON ideas(content_pillar);
CREATE INDEX idx_ideas_created ON ideas(created_at DESC);
CREATE INDEX idx_ideas_parent ON ideas(parent_idea_id);
CREATE INDEX idx_ideas_main_topic ON ideas(main_topic);
CREATE INDEX idx_ideas_keywords_gin ON ideas USING gin (keywords_entities);
```

#### `idea_sources`
```sql
CREATE TABLE idea_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    capture_id UUID REFERENCES captures(id) ON DELETE SET NULL,
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    source_type VARCHAR(50) NOT NULL, -- capture, asset, external_url, manual
    content TEXT, -- Relevant excerpt
    metadata JSONB DEFAULT '{}', -- {page_range, timestamp_range, url, etc.}
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_idea_sources_idea ON idea_sources(idea_id);
CREATE INDEX idx_idea_sources_capture ON idea_sources(capture_id);
```

#### `idea_relations`
```sql
CREATE TABLE idea_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    target_idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL, -- similar, complementary, continuation, contradictory, common_theme, new_angle
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    explanation TEXT NOT NULL,
    fusion_concept TEXT, -- Combined narrative if fused
    content_opportunities JSONB DEFAULT '[]',
    discovered_by VARCHAR(50) DEFAULT 'fusion_engine', -- fusion_engine, manual, import
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_idea_id, target_idea_id, relation_type)
);

CREATE INDEX idx_idea_relations_workspace ON idea_relations(workspace_id);
CREATE INDEX idx_idea_relations_source ON idea_relations(source_idea_id);
CREATE INDEX idx_idea_relations_target ON idea_relations(target_idea_id);
CREATE INDEX idx_idea_relations_type ON idea_relations(relation_type);
CREATE INDEX idx_idea_relations_confidence ON idea_relations(confidence DESC);
```

#### `fusion_proposals`
```sql
CREATE TABLE fusion_proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    new_idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    source_idea_ids UUID[] NOT NULL, -- Array of idea IDs
    relationships JSONB NOT NULL, -- [{"source_id": "...", "type": "...", "confidence": 0.9, "explanation": "..."}]
    fusion_concept TEXT NOT NULL,
    content_opportunities JSONB DEFAULT '[]',
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, edited
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejected_reason TEXT,
    edited_fusion_concept TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fusion_workspace ON fusion_proposals(workspace_id);
CREATE INDEX idx_fusion_new_idea ON fusion_proposals(new_idea_id);
CREATE INDEX idx_fusion_status ON fusion_proposals(status);
CREATE INDEX idx_fusion_created ON fusion_proposals(created_at DESC);
```

---

### 3.4 Brand Memory Tables

#### `brand_profiles`
```sql
CREATE TABLE brand_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,
    -- Voice & Tone
    voice_description TEXT, -- "Conversational, witty, slightly irreverent"
    tone_attributes JSONB DEFAULT '[]', -- ["confident", "approachable", "authoritative"]
    style_guidelines TEXT, -- "Short sentences. Active voice. No jargon."
    vocabulary_preferences JSONB DEFAULT '{}', -- {"preferred": [...], "avoid": [...]}
    -- Audience & Positioning
    target_audience TEXT,
    audience_personas JSONB DEFAULT '[]',
    positioning_statement TEXT,
    value_propositions JSONB DEFAULT '[]',
    -- Opinions & Beliefs
    core_opinions JSONB DEFAULT '[]', -- [{"topic": "...", "stance": "...", "conviction": 0.9}]
    prohibited_topics JSONB DEFAULT '[]',
    prohibited_phrases JSONB DEFAULT '[]',
    -- Visual Preferences
    visual_style JSONB DEFAULT '{}', -- {colors, fonts, composition, filters}
    brand_colors JSONB DEFAULT '[]',
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    previous_version_id UUID REFERENCES brand_profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brand_profiles_workspace ON brand_profiles(workspace_id);
```

#### `brand_rules`
```sql
CREATE TABLE brand_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    rule_type VARCHAR(50) NOT NULL, -- must_include, must_avoid, tone_check, format_rule, legal
    pattern VARCHAR(500), -- Regex or keyword
    severity VARCHAR(20) NOT NULL DEFAULT 'warning', -- error, warning, info
    message TEXT NOT NULL, -- Human-readable explanation
    examples JSONB DEFAULT '[]', -- ["bad example", "good example"]
    applies_to JSONB DEFAULT '["all"]', -- ["all", "instagram", "linkedin", "x"]
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brand_rules_workspace ON brand_rules(workspace_id);
CREATE INDEX idx_brand_rules_type ON brand_rules(rule_type);
CREATE INDEX idx_brand_rules_active ON brand_rules(is_active) WHERE is_active = true;
```

---

### 3.5 Content & Calendar Tables

#### `content_outputs`
```sql
CREATE TABLE content_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- instagram_reel, instagram_carousel, linkedin_post, linkedin_article, youtube_shorts, youtube_outline, x_thread, newsletter
    format VARCHAR(50) NOT NULL, -- reel, carousel, post, article, shorts, outline, thread, newsletter
    title VARCHAR(500),
    hook TEXT,
    body TEXT NOT NULL,
    cta TEXT,
    hashtags JSONB DEFAULT '[]',
    visual_notes JSONB DEFAULT '[]', -- [{"slide": 1, "description": "..."}, ...]
    estimated_duration_seconds INTEGER, -- For video/audio
    character_count INTEGER,
    -- Quality
    quality_score NUMERIC(3,2), -- 0-1 from Brand Guardian
    quality_warnings JSONB DEFAULT '[]',
    quality_passed BOOLEAN,
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, reviewing, approved, scheduled, published, archived
    version INTEGER NOT NULL DEFAULT 1,
    parent_output_id UUID REFERENCES content_outputs(id), -- For regeneration lineage
    -- Publishing
    published_url TEXT,
    published_at TIMESTAMPTZ,
    external_id VARCHAR(255), -- Platform post ID
    -- Metadata
    generation_model VARCHAR(100), -- claude-opus-5-5, etc.
    generation_prompt_hash VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_content_workspace ON content_outputs(workspace_id);
CREATE INDEX idx_content_idea ON content_outputs(idea_id);
CREATE INDEX idx_content_platform ON content_outputs(platform);
CREATE INDEX idx_content_status ON content_outputs(status);
CREATE INDEX idx_content_created ON content_outputs(created_at DESC);
CREATE INDEX idx_content_quality ON content_outputs(quality_score) WHERE quality_score IS NOT NULL;
```

#### `calendar_items`
```sql
CREATE TABLE calendar_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content_output_id UUID NOT NULL REFERENCES content_outputs(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'captured', -- captured, developing, ready_for_production, scheduled, published, recycle_or_improve
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    platform VARCHAR(50) NOT NULL,
    sort_order INTEGER DEFAULT 0, -- For drag-drop ordering
    metadata JSONB DEFAULT '{}', -- {campaign, tags, assignee, notes}
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_calendar_workspace ON calendar_items(workspace_id);
CREATE INDEX idx_calendar_status ON calendar_items(status);
CREATE INDEX idx_calendar_scheduled ON calendar_items(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX idx_calendar_content ON calendar_items(content_output_id);
CREATE INDEX idx_calendar_platform_date ON calendar_items(platform, scheduled_at);
```

---

### 3.6 Feedback & Processing Tables

#### `feedback_events`
```sql
CREATE TABLE feedback_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- idea, fusion_proposal, content_output, calendar_item
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- approved, rejected, edited, regenerated, scheduled, published
    reason_category VARCHAR(100), -- off_brand, inaccurate, repetitive, not_useful, other
    reason_text TEXT,
    before_state JSONB, -- Snapshot before change
    after_state JSONB, -- Snapshot after change
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_workspace ON feedback_events(workspace_id);
CREATE INDEX idx_feedback_entity ON feedback_events(entity_type, entity_id);
CREATE INDEX idx_feedback_action ON feedback_events(action);
CREATE INDEX idx_feedback_user ON feedback_events(user_id);
CREATE INDEX idx_feedback_created ON feedback_events(created_at DESC);
```

#### `processing_jobs`
```sql
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    capture_id UUID REFERENCES captures(id) ON DELETE SET NULL,
    job_type VARCHAR(50) NOT NULL, -- transcribe, extract, embed, fusion, generate, quality_check
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, dead_letter
    payload JSONB NOT NULL, -- Input parameters
    result JSONB, -- Output/result
    error TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    next_retry_at TIMESTAMPTZ,
    celery_task_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_workspace ON processing_jobs(workspace_id);
CREATE INDEX idx_jobs_capture ON processing_jobs(capture_id);
CREATE INDEX idx_jobs_status ON processing_jobs(status) WHERE status IN ('pending', 'running');
CREATE INDEX idx_jobs_next_retry ON processing_jobs(next_retry_at) WHERE status = 'pending';
CREATE INDEX idx_jobs_type_status ON processing_jobs(job_type, status);
```

---

## 4. Row Level Security (RLS) Policies

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE captures ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
ALTER TABLE idea_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE idea_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE fusion_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;

-- Helper function to get current workspace from JWT
CREATE OR REPLACE FUNCTION current_workspace_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_workspace_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Policy template (applied to each table)
-- Example for ideas:
CREATE POLICY ideas_workspace_isolation ON ideas
    USING (workspace_id = current_workspace_id())
    WITH CHECK (workspace_id = current_workspace_id());

-- Workspace members can read workspace
CREATE POLICY workspaces_member_read ON workspaces
    USING (
        id = current_workspace_id() OR
        id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid())
    );

-- Users can read their own profile
CREATE POLICY users_self_read ON users
    USING (id = auth.uid());
```

---

## 5. Triggers & Functions

### 5.1 Updated At Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ... repeat for all tables
```

### 5.2 Soft Delete Filter
```sql
-- Automatically filter deleted_at IS NULL
CREATE OR REPLACE FUNCTION filter_deleted() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        NEW.deleted_at = NOW();
        RETURN NEW;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. Migration Scripts

### 6.1 Initial Migration (001_initial_schema.sql)
```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create all tables in dependency order
-- 1. users
-- 2. workspaces
-- 3. workspace_members
-- 4. captures
-- 5. assets
-- 6. ideas
-- 7. idea_sources
-- 8. idea_relations
-- 9. fusion_proposals
-- 10. brand_profiles
-- 11. brand_rules
-- 12. content_outputs
-- 13. calendar_items
-- 14. feedback_events
-- 15. processing_jobs

-- Apply RLS policies
-- Create indexes
-- Create triggers
```

### 6.2 Vector Index Migration (002_vector_indexes.sql)
```sql
-- HNSW indexes for vector similarity search
-- Run AFTER data exists for optimal build

-- Ideas embedding index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ideas_embedding_hnsw
ON ideas USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
WHERE embedding IS NOT NULL;

-- Brand profile embeddings (if stored separately)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_brand_embeddings_hnsw
-- ON brand_embeddings USING hnsw (embedding vector_cosine_ops);
```

### 6.3 Partitioning Migration (003_partitioning.sql) - Future
```sql
-- For high-volume tables, consider time-based partitioning
-- ALTER TABLE processing_jobs SET (partition_by = 'RANGE (created_at)');
-- CREATE TABLE processing_jobs_2026_q1 PARTITION OF processing_jobs
--     FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

---

## 7. Seed Data (Development)

```sql
-- Demo workspace
INSERT INTO workspaces (id, name, slug, owner_id, settings)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo Workspace',
    'demo',
    '00000000-0000-0000-0000-000000000000',
    '{"default_platforms": ["instagram", "linkedin", "x"], "theme": "dark"}'
);

-- Demo brand profile
INSERT INTO brand_profiles (workspace_id, voice_description, tone_attributes, style_guidelines)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Conversational, insightful, slightly contrarian',
    '["confident", "approachable", "thoughtful"]',
    'Short sentences. Lead with the insight. No fluff. Use concrete examples.'
);
```

---

## 8. Performance Considerations

| Table | Expected Volume | Key Indexes | Partitioning |
|-------|-----------------|-------------|--------------|
| users | 100K | email, auth_provider | No |
| workspaces | 50K | owner, slug | No |
| captures | 10M | workspace+status, created_at | By month (future) |
| assets | 10M | workspace, capture, checksum | By month (future) |
| ideas | 5M | workspace+status, embedding (HNSW), pillar | No |
| idea_relations | 20M | workspace, source/target, type | No |
| content_outputs | 2M | workspace+status, idea, platform | No |
| calendar_items | 1M | workspace+status, scheduled_at | No |
| feedback_events | 5M | workspace, entity, created_at | By month |
| processing_jobs | 10M | workspace+status, next_retry, type | By month |

---

## 9. Backup & Recovery

- **PITR**: Enabled (Supabase default, 7-day retention)
- **Daily snapshots**: 30-day retention
- **Cross-region replica**: For DR
- **Schema migrations**: Run via Alembic in CI/CD, backward compatible

---

*End of Database Schema Document*