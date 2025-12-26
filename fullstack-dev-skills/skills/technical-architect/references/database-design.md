# Database Design

Schema design patterns for Supabase/PostgreSQL applications.

## Table of Contents
1. Schema Design Process
2. Common Patterns
3. Relationships and Foreign Keys
4. Indexes Strategy
5. Row Level Security (RLS)
6. Migration Strategy

---

## 1. Schema Design Process

### Step 1: Identify Entities

List all domain objects:
```
User, Post, Comment, Tag, Category, Like, Follow, Notification
```

### Step 2: Define Attributes

For each entity, list required fields:
```
Post:
  - id (uuid, primary key)
  - title (text, required, max 200)
  - content (text, required)
  - slug (text, unique)
  - published (boolean, default false)
  - author_id (uuid, foreign key → users)
  - created_at (timestamptz)
  - updated_at (timestamptz)
```

### Step 3: Map Relationships

```
User ──1:N──► Post (user has many posts)
Post ──1:N──► Comment (post has many comments)
Post ◄──N:M──► Tag (many-to-many via post_tags)
User ──1:N──► Like (user likes many posts)
User ◄──N:M──► User (followers via follows table)
```

### Step 4: Create Schema SQL

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  bio TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Posts table
CREATE TABLE public.posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL CHECK (char_length(title) <= 200),
  slug TEXT UNIQUE NOT NULL,
  content TEXT NOT NULL,
  excerpt TEXT,
  published BOOLEAN DEFAULT false,
  published_at TIMESTAMPTZ,
  author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Comments table
CREATE TABLE public.comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  content TEXT NOT NULL CHECK (char_length(content) <= 2000),
  post_id UUID NOT NULL REFERENCES public.posts(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tags table
CREATE TABLE public.tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Post-Tags junction table (many-to-many)
CREATE TABLE public.post_tags (
  post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES public.tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

-- Likes table
CREATE TABLE public.likes (
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, post_id)
);

-- Follows table (self-referential many-to-many)
CREATE TABLE public.follows (
  follower_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  following_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (follower_id, following_id),
  CHECK (follower_id != following_id)
);
```

---

## 2. Common Patterns

### Soft Deletes

```sql
ALTER TABLE posts ADD COLUMN deleted_at TIMESTAMPTZ;

-- Query only active records
SELECT * FROM posts WHERE deleted_at IS NULL;

-- Create view for convenience
CREATE VIEW active_posts AS
SELECT * FROM posts WHERE deleted_at IS NULL;
```

### Audit Trail

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  old_data JSONB,
  new_data JSONB,
  user_id UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, user_id)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    TG_OP,
    CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) END,
    auth.uid()
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply to tables
CREATE TRIGGER posts_audit
AFTER INSERT OR UPDATE OR DELETE ON posts
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

### Updated Timestamp

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_updated_at
BEFORE UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Slug Generation

```sql
CREATE OR REPLACE FUNCTION generate_slug(title TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN lower(regexp_replace(title, '[^a-zA-Z0-9]+', '-', 'g'));
END;
$$ LANGUAGE plpgsql;

-- Auto-generate slug on insert
CREATE OR REPLACE FUNCTION auto_slug()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.slug IS NULL THEN
    NEW.slug = generate_slug(NEW.title) || '-' || substr(NEW.id::text, 1, 8);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_auto_slug
BEFORE INSERT ON posts
FOR EACH ROW EXECUTE FUNCTION auto_slug();
```

---

## 3. Relationships and Foreign Keys

### One-to-Many

```sql
-- Posts belong to users
author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE

-- ON DELETE options:
-- CASCADE: Delete posts when user deleted
-- SET NULL: Set author_id to NULL (requires nullable column)
-- RESTRICT: Prevent user deletion if posts exist
```

### Many-to-Many

```sql
-- Junction table with composite primary key
CREATE TABLE post_tags (
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

-- Query posts with tags
SELECT p.*, array_agg(t.name) as tags
FROM posts p
LEFT JOIN post_tags pt ON p.id = pt.post_id
LEFT JOIN tags t ON pt.tag_id = t.id
GROUP BY p.id;
```

### Self-Referential

```sql
-- Threaded comments
parent_id UUID REFERENCES comments(id) ON DELETE CASCADE

-- Recursive query for comment tree
WITH RECURSIVE comment_tree AS (
  SELECT id, content, parent_id, 0 as depth
  FROM comments WHERE post_id = $1 AND parent_id IS NULL
  UNION ALL
  SELECT c.id, c.content, c.parent_id, ct.depth + 1
  FROM comments c
  JOIN comment_tree ct ON c.parent_id = ct.id
)
SELECT * FROM comment_tree ORDER BY depth;
```

---

## 4. Indexes Strategy

### Primary Queries → Index

```sql
-- Posts by author (common query)
CREATE INDEX idx_posts_author ON posts(author_id);

-- Posts by published status and date
CREATE INDEX idx_posts_published ON posts(published, published_at DESC)
WHERE published = true;

-- Comments by post
CREATE INDEX idx_comments_post ON comments(post_id);

-- Full-text search
CREATE INDEX idx_posts_search ON posts
USING GIN (to_tsvector('english', title || ' ' || content));
```

### Index Guidelines

| Query Pattern | Index Type |
|--------------|------------|
| Equality (`=`) | B-tree (default) |
| Range (`<`, `>`, `BETWEEN`) | B-tree |
| Pattern matching (`LIKE 'foo%'`) | B-tree |
| Full-text search | GIN with tsvector |
| JSON containment | GIN |
| Array contains | GIN |
| Geospatial | GiST |

### Partial Indexes

```sql
-- Only index published posts (smaller index)
CREATE INDEX idx_published_posts ON posts(published_at DESC)
WHERE published = true AND deleted_at IS NULL;
```

### Composite Indexes

```sql
-- Order matters: leftmost columns used for equality
CREATE INDEX idx_posts_author_date ON posts(author_id, created_at DESC);

-- Supports: WHERE author_id = $1 ORDER BY created_at DESC
-- Supports: WHERE author_id = $1
-- Does NOT support: WHERE created_at > $1 (without author_id filter)
```

---

## 5. Row Level Security (RLS)

### Enable RLS

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
```

### Common Policies

```sql
-- Public read for published posts
CREATE POLICY "Public can view published posts"
ON posts FOR SELECT
USING (published = true);

-- Authors can view their own posts
CREATE POLICY "Authors can view own posts"
ON posts FOR SELECT
USING (author_id = auth.uid());

-- Authors can create posts
CREATE POLICY "Authenticated users can create posts"
ON posts FOR INSERT
WITH CHECK (auth.uid() = author_id);

-- Authors can update own posts
CREATE POLICY "Authors can update own posts"
ON posts FOR UPDATE
USING (author_id = auth.uid())
WITH CHECK (author_id = auth.uid());

-- Authors can delete own posts
CREATE POLICY "Authors can delete own posts"
ON posts FOR DELETE
USING (author_id = auth.uid());
```

### Profile Policies

```sql
-- Public profiles
CREATE POLICY "Profiles are public"
ON profiles FOR SELECT
USING (true);

-- Users can update own profile
CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());
```

### Admin Override

```sql
-- Create admin role check
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Admin can do anything
CREATE POLICY "Admins have full access"
ON posts FOR ALL
USING (is_admin())
WITH CHECK (is_admin());
```

---

## 6. Migration Strategy

### Naming Convention

```
YYYYMMDDHHMMSS_description.sql
20240115120000_create_posts_table.sql
20240116140000_add_posts_slug_column.sql
20240117090000_create_comments_table.sql
```

### Migration Structure

```sql
-- 20240115120000_create_posts_table.sql

-- Up migration
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  author_id UUID NOT NULL REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_posts_author ON posts(author_id);

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Down migration (comment out, keep for reference)
-- DROP TABLE posts;
```

### Safe Migration Practices

```sql
-- Adding column (safe)
ALTER TABLE posts ADD COLUMN excerpt TEXT;

-- Adding NOT NULL column (requires default)
ALTER TABLE posts ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0;

-- Renaming column (breaking change - coordinate with code)
ALTER TABLE posts RENAME COLUMN excerpt TO summary;

-- Changing column type (may require data migration)
ALTER TABLE posts ALTER COLUMN view_count TYPE BIGINT;

-- Adding unique constraint (may fail if duplicates exist)
-- First: check for duplicates
SELECT slug, COUNT(*) FROM posts GROUP BY slug HAVING COUNT(*) > 1;
-- Then: add constraint
ALTER TABLE posts ADD CONSTRAINT posts_slug_unique UNIQUE (slug);
```

### Zero-Downtime Migrations

1. **Add nullable column** → Deploy code that writes to both → Backfill → Make NOT NULL
2. **Rename column** → Add new column → Deploy code using new → Backfill → Drop old
3. **Add index** → Use `CONCURRENTLY` to avoid locking

```sql
CREATE INDEX CONCURRENTLY idx_posts_slug ON posts(slug);
```

---

## Schema Review Checklist

Before finalizing schema:

- [ ] All tables have `id` (UUID) primary key
- [ ] All tables have `created_at` timestamp
- [ ] Mutable tables have `updated_at` with trigger
- [ ] Foreign keys have appropriate `ON DELETE` action
- [ ] Indexes exist for all foreign keys
- [ ] Indexes exist for common query patterns
- [ ] RLS enabled on all user-data tables
- [ ] RLS policies cover SELECT, INSERT, UPDATE, DELETE
- [ ] Check constraints for validation (lengths, formats)
- [ ] Soft delete considered if data recovery needed
