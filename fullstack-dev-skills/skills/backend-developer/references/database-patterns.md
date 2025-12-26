# Database Patterns

Advanced PostgreSQL and Supabase patterns for production applications.

## Table of Contents
1. Schema Design Patterns
2. Index Strategies
3. Query Optimization
4. Common Data Patterns
5. Real-time Subscriptions

## Schema Design Patterns

### UUID vs Serial IDs

```sql
-- Prefer UUIDs for distributed systems
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Use serial only for internal sequences
CREATE SEQUENCE order_number_seq;
order_number INTEGER DEFAULT nextval('order_number_seq')
```

### Soft Deletes

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  deleted_at TIMESTAMPTZ,
  -- Add index for queries filtering out deleted
  CONSTRAINT posts_not_deleted CHECK (deleted_at IS NULL OR deleted_at > '1970-01-01')
);

CREATE INDEX idx_posts_active ON posts(id) WHERE deleted_at IS NULL;

-- RLS policy for soft deletes
CREATE POLICY "Hide deleted posts" ON posts
  FOR SELECT USING (deleted_at IS NULL);
```

### Audit Columns

```sql
-- Standard audit columns
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- ... other columns
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  created_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_by UUID REFERENCES auth.users(id)
);

-- Auto-update trigger
CREATE OR REPLACE FUNCTION set_audit_columns()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    NEW.created_at = now();
    NEW.created_by = auth.uid();
  END IF;
  NEW.updated_at = now();
  NEW.updated_by = auth.uid();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER audit_posts
  BEFORE INSERT OR UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION set_audit_columns();
```

### Enum Types

```sql
-- Create enum type
CREATE TYPE post_status AS ENUM ('draft', 'published', 'archived');

-- Use in table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status post_status DEFAULT 'draft' NOT NULL
);

-- Add new value to enum
ALTER TYPE post_status ADD VALUE 'scheduled' BEFORE 'published';
```

### JSON/JSONB Columns

```sql
-- Store flexible metadata
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  -- Index for JSON queries
  CONSTRAINT metadata_valid CHECK (jsonb_typeof(metadata) = 'object')
);

-- GIN index for JSONB containment queries
CREATE INDEX idx_posts_metadata ON posts USING GIN (metadata);

-- Query JSONB
SELECT * FROM posts 
WHERE metadata @> '{"featured": true}'::jsonb;

-- Extract values
SELECT metadata->>'author' as author FROM posts;
SELECT metadata->'tags'->>0 as first_tag FROM posts;
```

## Index Strategies

### Common Index Types

```sql
-- B-tree (default, for equality and range)
CREATE INDEX idx_posts_created ON posts(created_at DESC);

-- Partial index (smaller, faster for specific queries)
CREATE INDEX idx_posts_published ON posts(created_at DESC) 
  WHERE published = true;

-- Composite index (for multi-column queries)
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);

-- Covering index (includes columns to avoid table lookup)
CREATE INDEX idx_posts_list ON posts(author_id, created_at DESC) 
  INCLUDE (title, slug);

-- GIN for arrays and JSONB
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- Full-text search
CREATE INDEX idx_posts_search ON posts 
  USING GIN (to_tsvector('english', title || ' ' || content));
```

### When to Add Indexes

- Foreign key columns (always)
- Columns in WHERE clauses (if selective)
- Columns in ORDER BY (for sorting)
- Columns in JOIN conditions
- Avoid indexing: low-cardinality columns, frequently updated columns

### Query Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM posts WHERE author_id = 'uuid';

-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'posts';
```

## Common Data Patterns

### One-to-Many

```sql
-- Users have many posts
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL
);

CREATE INDEX idx_posts_author ON posts(author_id);
```

### Many-to-Many

```sql
-- Posts have many tags, tags have many posts
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE post_tags (
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

-- Query with junction table
SELECT p.*, array_agg(t.name) as tags
FROM posts p
LEFT JOIN post_tags pt ON p.id = pt.post_id
LEFT JOIN tags t ON pt.tag_id = t.id
GROUP BY p.id;
```

### Tree/Hierarchy (Adjacency List)

```sql
CREATE TABLE categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  parent_id UUID REFERENCES categories(id)
);

-- Recursive CTE for tree traversal
WITH RECURSIVE category_tree AS (
  SELECT id, name, parent_id, 1 as depth
  FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.name, c.parent_id, ct.depth + 1
  FROM categories c
  JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY depth, name;
```

### Tree/Hierarchy (Materialized Path)

```sql
CREATE TABLE categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  path TEXT NOT NULL,  -- e.g., '/root/parent/child/'
  CONSTRAINT valid_path CHECK (path ~ '^/([^/]+/)+$')
);

CREATE INDEX idx_categories_path ON categories USING GIST (path gist_trgm_ops);

-- Find all children
SELECT * FROM categories WHERE path LIKE '/electronics/phones/%';

-- Find ancestors
SELECT * FROM categories 
WHERE '/electronics/phones/iphone/' LIKE path || '%'
ORDER BY length(path);
```

## Real-time Subscriptions

### Enable Realtime

```sql
-- Enable realtime for a table
ALTER PUBLICATION supabase_realtime ADD TABLE posts;
```

### Subscribe in Client

```typescript
// Subscribe to changes
const subscription = supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'posts' },
    (payload) => {
      console.log('Change received:', payload);
    }
  )
  .subscribe();

// Filter by user
const userPosts = supabase
  .channel('my-posts')
  .on(
    'postgres_changes',
    { 
      event: '*', 
      schema: 'public', 
      table: 'posts',
      filter: `author_id=eq.${userId}`
    },
    handleChange
  )
  .subscribe();

// Cleanup
subscription.unsubscribe();
```

### Broadcast for Ephemeral Data

```typescript
// For presence, typing indicators, etc.
const room = supabase.channel('room-1');

room
  .on('broadcast', { event: 'typing' }, ({ payload }) => {
    console.log(payload.user, 'is typing');
  })
  .subscribe();

// Send broadcast
room.send({
  type: 'broadcast',
  event: 'typing',
  payload: { user: 'alice' }
});
```

## Performance Tips

1. **Use connection pooling** - Supabase handles this automatically
2. **Batch operations** - Use `insert([...])` for multiple rows
3. **Select only needed columns** - Avoid `select('*')` in production
4. **Use prepared statements** - Supabase client handles this
5. **Monitor slow queries** - Check Supabase dashboard for slow queries
6. **Vacuum regularly** - Supabase handles autovacuum
