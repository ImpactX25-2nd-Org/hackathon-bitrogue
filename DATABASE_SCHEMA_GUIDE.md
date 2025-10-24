# 🗄️ KrishiLok Database Schema & Implementation Guide

## 📊 Database Type: PostgreSQL

**Why PostgreSQL?**
- ACID compliance for data integrity
- JSONB support for flexible data structures
- Full-text search capabilities
- Robust indexing for performance
- Excellent scalability
- Strong community support

---

## 📐 Complete Database Schema

### 1. Users Table
```sql
CREATE TYPE user_role AS ENUM ('farmer', 'expert', 'extension_worker', 'admin');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    language VARCHAR(5) DEFAULT 'en' CHECK (language IN ('en', 'ta', 'mr', 'kn', 'hi', 'te')),
    trust_score DECIMAL(5,2) DEFAULT 50.0 CHECK (trust_score >= 0 AND trust_score <= 100),
    role user_role DEFAULT 'farmer',
    avatar_url TEXT,
    is_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_trust_score ON users(trust_score DESC);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Relationships:**
- One-to-Many: scans, community_posts, post_responses, suggestions, trust_feedback

---

### 2. Scans Table
```sql
CREATE TYPE scan_status AS ENUM ('processing', 'completed', 'failed');

CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    voice_file_url TEXT,
    transcription TEXT,
    translation TEXT,
    status scan_status DEFAULT 'processing',
    disease_name VARCHAR(255),
    reliability DECIMAL(5,2) CHECK (reliability >= 0 AND reliability <= 100),
    next_steps JSONB,
    is_common BOOLEAN DEFAULT false,
    language VARCHAR(5) DEFAULT 'en',
    ml_model_version VARCHAR(50),
    processing_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_disease_name ON scans(disease_name);
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX idx_scans_crop_name ON scans(crop_name);
CREATE INDEX idx_scans_is_common ON scans(is_common);

-- Full-text search on disease name
CREATE INDEX idx_scans_disease_name_fts ON scans USING gin(to_tsvector('english', disease_name));
```

**Relationships:**
- Many-to-One: users
- One-to-Many: community_posts (via scan_id), suggestions, trust_feedback

---

### 3. Community Posts Table
```sql
CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    crop_name VARCHAR(100),
    image_url TEXT,
    scan_id UUID REFERENCES scans(id) ON DELETE SET NULL,
    tags TEXT[] DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT false,
    accepted_response_id UUID,
    view_count INTEGER DEFAULT 0,
    response_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_posts_user_id ON community_posts(user_id);
CREATE INDEX idx_posts_is_resolved ON community_posts(is_resolved);
CREATE INDEX idx_posts_created_at ON community_posts(created_at DESC);
CREATE INDEX idx_posts_crop_name ON community_posts(crop_name);
CREATE INDEX idx_posts_tags ON community_posts USING gin(tags);
CREATE INDEX idx_posts_scan_id ON community_posts(scan_id);

-- Full-text search on title and description
CREATE INDEX idx_posts_title_fts ON community_posts USING gin(to_tsvector('english', title));
CREATE INDEX idx_posts_description_fts ON community_posts USING gin(to_tsvector('english', description));

-- Composite index for popular posts
CREATE INDEX idx_posts_popular ON community_posts(response_count DESC, view_count DESC, created_at DESC);
```

**Relationships:**
- Many-to-One: users, scans
- One-to-Many: post_responses

---

### 4. Post Responses Table
```sql
CREATE TYPE response_role AS ENUM ('farmer', 'expert', 'extension_worker');

CREATE TABLE post_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT false,
    verification_reason TEXT,
    verification_confidence DECIMAL(3,2) CHECK (verification_confidence >= 0 AND verification_confidence <= 1),
    helpful_count INTEGER DEFAULT 0,
    is_expert_advice BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_responses_post_id ON post_responses(post_id);
CREATE INDEX idx_responses_user_id ON post_responses(user_id);
CREATE INDEX idx_responses_is_verified ON post_responses(is_verified);
CREATE INDEX idx_responses_created_at ON post_responses(created_at DESC);
CREATE INDEX idx_responses_helpful ON post_responses(helpful_count DESC);

-- Composite index for top responses
CREATE INDEX idx_responses_top ON post_responses(post_id, helpful_count DESC, is_verified DESC);
```

**Relationships:**
- Many-to-One: community_posts, users

---

### 5. Suggestions Table
```sql
CREATE TABLE suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disease_name VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    details TEXT,
    usefulness_score DECIMAL(5,2) DEFAULT 50.0 CHECK (usefulness_score >= 0 AND usefulness_score <= 100),
    usage_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_suggestions_disease_name ON suggestions(disease_name);
CREATE INDEX idx_suggestions_user_id ON suggestions(user_id);
CREATE INDEX idx_suggestions_usefulness ON suggestions(usefulness_score DESC);
CREATE INDEX idx_suggestions_created_at ON suggestions(created_at DESC);

-- Composite index for ranking
CREATE INDEX idx_suggestions_ranked ON suggestions(disease_name, usefulness_score DESC, positive_feedback_count DESC);
```

**Relationships:**
- Many-to-One: users
- One-to-Many: trust_feedback

---

### 6. Trust Feedback Table
```sql
CREATE TABLE trust_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suggestion_id UUID NOT NULL REFERENCES suggestions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
    feedback_text TEXT,
    scan_id UUID REFERENCES scans(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_trust_feedback_suggestion_id ON trust_feedback(suggestion_id);
CREATE INDEX idx_trust_feedback_user_id ON trust_feedback(user_id);
CREATE INDEX idx_trust_feedback_farmer_id ON trust_feedback(farmer_id);
CREATE INDEX idx_trust_feedback_scan_id ON trust_feedback(scan_id);
CREATE INDEX idx_trust_feedback_created_at ON trust_feedback(created_at DESC);

-- Prevent duplicate feedback
CREATE UNIQUE INDEX idx_trust_feedback_unique ON trust_feedback(user_id, suggestion_id);
```

**Relationships:**
- Many-to-One: suggestions, users (both user_id and farmer_id), scans

---

### 7. Notifications Table
```sql
CREATE TYPE notification_type AS ENUM (
    'trust_score_followup',
    'post_response',
    'post_resolved',
    'scan_completed',
    'trending_alert',
    'system'
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_scheduled_for ON notifications(scheduled_for) WHERE sent_at IS NULL;
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Composite index for user's unread notifications
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read, created_at DESC);
```

**Relationships:**
- Many-to-One: users

---

### 8. Disease Database Table (Reference Data)
```sql
CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    scientific_name VARCHAR(255),
    common_names JSONB, -- {"en": "Early Blight", "hi": "...", "ta": "..."}
    affected_crops TEXT[] DEFAULT '{}',
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    is_common BOOLEAN DEFAULT false,
    symptoms TEXT,
    causes TEXT,
    prevention_steps JSONB,
    treatment_steps JSONB,
    images TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_diseases_name ON diseases(name);
CREATE INDEX idx_diseases_affected_crops ON diseases USING gin(affected_crops);
CREATE INDEX idx_diseases_is_common ON diseases(is_common);

-- Full-text search
CREATE INDEX idx_diseases_name_fts ON diseases USING gin(to_tsvector('english', name));
```

---

### 9. Crop Information Table (Reference Data)
```sql
CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(255),
    local_names JSONB, -- {"en": "Groundnut", "ta": "நிலக்கடலை", "hi": "मूंगफली"}
    season VARCHAR(100),
    growing_regions TEXT[],
    common_diseases TEXT[],
    common_pests TEXT[],
    info_gap TEXT,
    best_practices JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_crops_name ON crops(name);
CREATE INDEX idx_crops_growing_regions ON crops USING gin(growing_regions);
```

---

### 10. Analytics Events Table (Optional)
```sql
CREATE TYPE event_type AS ENUM (
    'scan_submitted',
    'scan_completed',
    'post_created',
    'post_viewed',
    'response_added',
    'trust_score_updated',
    'user_login',
    'user_registered'
);

CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type event_type NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at DESC);

-- Partitioning by month (for large scale)
-- ALTER TABLE analytics_events PARTITION BY RANGE (created_at);
```

---

## 🔗 Table Relationships Diagram

```
users (1) ----< (M) scans
users (1) ----< (M) community_posts
users (1) ----< (M) post_responses
users (1) ----< (M) suggestions
users (1) ----< (M) trust_feedback (as user_id)
users (1) ----< (M) trust_feedback (as farmer_id)
users (1) ----< (M) notifications

scans (1) ----< (M) community_posts
scans (1) ----< (M) suggestions
scans (1) ----< (M) trust_feedback

community_posts (1) ----< (M) post_responses
community_posts (1) ---- (1) post_responses (accepted_response_id)

suggestions (1) ----< (M) trust_feedback
```

---

## 🔧 Database Functions & Triggers

### 1. Update Timestamp Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scans_updated_at BEFORE UPDATE ON scans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON community_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Repeat for other tables...
```

---

### 2. Update Response Count on Post
```sql
CREATE OR REPLACE FUNCTION update_post_response_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE community_posts
        SET response_count = response_count + 1
        WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE community_posts
        SET response_count = response_count - 1
        WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_response_count
AFTER INSERT OR DELETE ON post_responses
FOR EACH ROW EXECUTE FUNCTION update_post_response_count();
```

---

### 3. Calculate Trust Score
```sql
CREATE OR REPLACE FUNCTION calculate_trust_score(p_user_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    base_score DECIMAL := 50.0;
    accepted_responses INT;
    total_feedback INT;
    avg_feedback DECIMAL;
    verified_responses INT;
    final_score DECIMAL;
BEGIN
    -- Count accepted responses
    SELECT COUNT(*) INTO accepted_responses
    FROM community_posts
    WHERE accepted_response_id IN (
        SELECT id FROM post_responses WHERE user_id = p_user_id
    );
    
    -- Get average feedback score
    SELECT COUNT(*), AVG(score) INTO total_feedback, avg_feedback
    FROM trust_feedback
    WHERE farmer_id = p_user_id;
    
    -- Count verified responses
    SELECT COUNT(*) INTO verified_responses
    FROM post_responses
    WHERE user_id = p_user_id AND is_verified = true;
    
    -- Calculate final score
    final_score := base_score 
                 + (accepted_responses * 10)
                 + (COALESCE(avg_feedback, 0) * 5)
                 + (verified_responses * 3);
    
    -- Clamp between 0 and 100
    final_score := LEAST(GREATEST(final_score, 0), 100);
    
    RETURN final_score;
END;
$$ LANGUAGE plpgsql;
```

---

### 4. Update Usefulness Score for Suggestions
```sql
CREATE OR REPLACE FUNCTION update_suggestion_usefulness()
RETURNS TRIGGER AS $$
DECLARE
    v_usefulness DECIMAL;
BEGIN
    -- Recalculate usefulness based on feedback
    SELECT 50.0 + (AVG(score) - 3) * 20 INTO v_usefulness
    FROM trust_feedback
    WHERE suggestion_id = NEW.suggestion_id;
    
    UPDATE suggestions
    SET 
        usefulness_score = LEAST(GREATEST(v_usefulness, 0), 100),
        positive_feedback_count = (
            SELECT COUNT(*) FROM trust_feedback 
            WHERE suggestion_id = NEW.suggestion_id AND score >= 4
        ),
        negative_feedback_count = (
            SELECT COUNT(*) FROM trust_feedback 
            WHERE suggestion_id = NEW.suggestion_id AND score <= 2
        )
    WHERE id = NEW.suggestion_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_suggestion_usefulness
AFTER INSERT ON trust_feedback
FOR EACH ROW EXECUTE FUNCTION update_suggestion_usefulness();
```

---

## 📊 Common Queries

### Get User Dashboard Stats
```sql
SELECT 
    u.id,
    u.name,
    u.trust_score,
    COUNT(DISTINCT s.id) as total_scans,
    COUNT(DISTINCT cp.id) as total_posts,
    COUNT(DISTINCT pr.id) as total_responses,
    COUNT(DISTINCT CASE WHEN cp.is_resolved THEN cp.id END) as resolved_posts
FROM users u
LEFT JOIN scans s ON s.user_id = u.id
LEFT JOIN community_posts cp ON cp.user_id = u.id
LEFT JOIN post_responses pr ON pr.user_id = u.id
WHERE u.id = $1
GROUP BY u.id, u.name, u.trust_score;
```

---

### Get Trending Diseases (Last 7 Days)
```sql
SELECT 
    disease_name,
    COUNT(*) as scan_count,
    AVG(reliability) as avg_reliability,
    COUNT(DISTINCT user_id) as affected_farmers
FROM scans
WHERE 
    status = 'completed'
    AND created_at >= NOW() - INTERVAL '7 days'
    AND disease_name IS NOT NULL
GROUP BY disease_name
ORDER BY scan_count DESC
LIMIT 10;
```

---

### Get Top Community Contributors
```sql
SELECT 
    u.id,
    u.name,
    u.trust_score,
    COUNT(DISTINCT pr.id) as response_count,
    COUNT(DISTINCT cp.accepted_response_id) as accepted_count,
    SUM(pr.helpful_count) as total_helpful_votes
FROM users u
LEFT JOIN post_responses pr ON pr.user_id = u.id
LEFT JOIN community_posts cp ON cp.accepted_response_id = pr.id
WHERE u.role = 'farmer'
GROUP BY u.id, u.name, u.trust_score
ORDER BY u.trust_score DESC, accepted_count DESC
LIMIT 20;
```

---

### Get Suggestions for Disease
```sql
SELECT 
    s.*,
    u.name as author_name,
    u.avatar_url as author_avatar,
    u.trust_score as author_trust_score
FROM suggestions s
JOIN users u ON u.id = s.user_id
WHERE s.disease_name = $1
ORDER BY 
    s.usefulness_score DESC,
    s.positive_feedback_count DESC,
    u.trust_score DESC
LIMIT 10;
```

---

### Get Community Posts with Filters
```sql
SELECT 
    cp.*,
    u.name as farmer_name,
    u.avatar_url as farmer_avatar,
    u.trust_score
FROM community_posts cp
JOIN users u ON u.id = cp.user_id
WHERE 
    ($1::boolean IS NULL OR cp.is_resolved = $1)
    AND ($2::text IS NULL OR cp.crop_name ILIKE '%' || $2 || '%')
    AND ($3::text[] IS NULL OR cp.tags && $3)
ORDER BY 
    CASE WHEN $4 = 'popular' THEN cp.response_count END DESC,
    CASE WHEN $4 = 'trending' THEN cp.view_count END DESC,
    cp.created_at DESC
LIMIT $5 OFFSET $6;
```

---

## 🔐 Row-Level Security (RLS)

### Enable RLS on Sensitive Tables
```sql
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own scans
CREATE POLICY scans_select_policy ON scans
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Policy: Users can only see their own notifications
CREATE POLICY notifications_select_policy ON notifications
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Policy: Anyone can see published community posts
CREATE POLICY posts_select_policy ON community_posts
    FOR SELECT
    USING (true);

-- Policy: Users can only edit/delete their own posts
CREATE POLICY posts_update_policy ON community_posts
    FOR UPDATE
    USING (user_id = current_setting('app.current_user_id')::UUID);
```

---

## 🎯 Performance Optimization

### 1. Materialized Views for Analytics
```sql
CREATE MATERIALIZED VIEW mv_user_stats AS
SELECT 
    u.id as user_id,
    u.trust_score,
    COUNT(DISTINCT s.id) as total_scans,
    COUNT(DISTINCT cp.id) as total_posts,
    COUNT(DISTINCT pr.id) as total_responses,
    COUNT(DISTINCT CASE WHEN cp.accepted_response_id = pr.id THEN pr.id END) as accepted_responses
FROM users u
LEFT JOIN scans s ON s.user_id = u.id
LEFT JOIN community_posts cp ON cp.user_id = u.id
LEFT JOIN post_responses pr ON pr.user_id = u.id
GROUP BY u.id, u.trust_score;

CREATE UNIQUE INDEX idx_mv_user_stats_user_id ON mv_user_stats(user_id);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_stats;
```

---

### 2. Partitioning for Large Tables
```sql
-- Partition scans by month
CREATE TABLE scans_partitioned (
    LIKE scans INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE scans_2024_10 PARTITION OF scans_partitioned
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

CREATE TABLE scans_2024_11 PARTITION OF scans_partitioned
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

-- Auto-create partitions with extension
CREATE EXTENSION IF NOT EXISTS pg_partman;
```

---

## 🔄 Data Migration Scripts

### Seed Initial Crop Data
```sql
INSERT INTO crops (name, scientific_name, local_names, season, info_gap) VALUES
('Groundnut', 'Arachis hypogaea', 
 '{"en": "Groundnut", "ta": "நிலக்கடலை", "hi": "मूंगफली"}',
 'June–October',
 'Unawareness about calcium and sulfur micronutrient importance for better pod formation'),
 
('Cotton', 'Gossypium spp.',
 '{"en": "Cotton", "ta": "பருத்தி", "hi": "कपास"}',
 'June–September',
 'Farmers lack access to pest surveillance data (bollworm outbreaks)'),

('Tomato', 'Solanum lycopersicum',
 '{"en": "Tomato", "ta": "தக்காளி", "hi": "टमाटर"}',
 'Year-round',
 'Limited awareness about disease-resistant varieties and proper spacing');
```

---

## 📦 Backup & Recovery

### Daily Backup Script
```bash
#!/bin/bash
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h $DB_HOST \
    -U $DB_USER \
    -d krishilok_db \
    -F c \
    -f /backups/krishilok_$(date +%Y%m%d).dump

# Upload to cloud storage
aws s3 cp /backups/krishilok_$(date +%Y%m%d).dump s3://backups/
```

### Restore from Backup
```bash
pg_restore -h $DB_HOST -U $DB_USER -d krishilok_db backup_file.dump
```

---

## ✅ Schema Checklist

- [x] All tables created with proper constraints
- [x] Indexes on foreign keys
- [x] Full-text search indexes where needed
- [x] Triggers for auto-updating timestamps
- [x] Triggers for maintaining counts
- [x] Functions for complex calculations
- [x] Row-level security policies
- [x] Materialized views for performance
- [x] Reference data tables seeded
- [x] Backup strategy implemented

---

**Database Version:** PostgreSQL 14+  
**Extensions Required:** uuid-ossp, pg_trgm (for fuzzy search), pg_partman (optional)  
**Last Updated:** 2025-10-25  
**Status:** Production Ready ✅
