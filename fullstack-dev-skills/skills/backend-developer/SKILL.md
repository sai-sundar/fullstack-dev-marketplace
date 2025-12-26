---
name: backend-developer
description: Full-stack backend engineering skill for building, maintaining, and debugging server-side applications. Use when creating REST/GraphQL APIs, designing database schemas, implementing authentication with Supabase, writing automated tests, or handling server-side logic. Integrates with Supabase MCP for database operations, authentication, and real-time subscriptions. Covers Node.js/Express, Python/FastAPI, database design, migrations, testing strategies, and deployment patterns.
---

# Backend Developer

Build production-grade, secure, and scalable backend applications. This skill combines modern frameworks (Node.js/Express, Python/FastAPI), Supabase for database and auth, testing strategies, and best practices for API design.

## Workflow Decision Tree

```
User Request
├─► "Build new API/backend/server"
│   └─► New Project Workflow → Tech Stack Selection → Implementation
├─► "Add database/tables/schema"
│   └─► Database Workflow → Schema Design → Migrations → Supabase MCP
├─► "Implement authentication"
│   └─► Auth Workflow → Supabase Auth → RLS Policies
├─► "Write tests for my API"
│   └─► Testing Workflow → Unit/Integration/E2E Tests
├─► "Debug/fix backend issue"
│   └─► Debug Workflow → Logs → Database Queries → Fix
└─► "Add new endpoint/feature"
    └─► Feature Workflow → Design → Implement → Test
```

## Tech Stack Selection

| Stack | Best For | Database |
|-------|----------|----------|
| Node.js + Express + TypeScript | REST APIs, real-time apps | Supabase (PostgreSQL) |
| Python + FastAPI | ML backends, async APIs | Supabase (PostgreSQL) |
| Node.js + tRPC | Type-safe APIs with React | Supabase (PostgreSQL) |

Default recommendation: **Node.js + Express + TypeScript + Supabase**

## Supabase MCP Integration

Supabase MCP provides direct database and auth operations from Claude.

### Configuration

Add to `.claude/mcp.json` or `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "<SUPABASE_ACCESS_TOKEN>"]
    }
  }
}
```

Claude Code setup:
```bash
claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest --access-token $SUPABASE_ACCESS_TOKEN
```

### Available Tools

| Tool | Description |
|------|-------------|
| `list_projects` | List all Supabase projects |
| `get_project` | Get project details |
| `list_tables` | List tables in a schema |
| `get_table` | Get table schema and columns |
| `create_table` | Create new table with columns |
| `update_table` | Modify table structure |
| `list_extensions` | List PostgreSQL extensions |
| `apply_migration` | Apply SQL migration |
| `execute_sql` | Run arbitrary SQL |
| `get_logs` | Fetch project logs |

### Database Operations via MCP

```
# List all tables
Use: list_tables with schema: "public"

# Create a table
Use: create_table with:
  - name: "posts"
  - columns: [
      { name: "id", type: "uuid", primary: true, default: "gen_random_uuid()" },
      { name: "title", type: "text", nullable: false },
      { name: "created_at", type: "timestamptz", default: "now()" }
    ]

# Apply migration
Use: apply_migration with sql: "ALTER TABLE posts ADD COLUMN author_id uuid REFERENCES auth.users(id);"
```

## New Project Workflow

### 1. Initialize Project

**Node.js + Express + TypeScript:**
```bash
mkdir my-api && cd my-api
npm init -y
npm install express cors helmet dotenv
npm install -D typescript @types/node @types/express ts-node nodemon
npx tsc --init
```

**Python + FastAPI:**
```bash
mkdir my-api && cd my-api
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv
pip install supabase  # Supabase client
```

### 2. Project Structure

```
src/
├── config/
│   └── env.ts           # Environment configuration
├── middleware/
│   ├── auth.ts          # Authentication middleware
│   ├── validation.ts    # Request validation
│   └── error.ts         # Error handling
├── routes/
│   ├── index.ts         # Route aggregator
│   └── users.ts         # User routes
├── services/
│   └── supabase.ts      # Supabase client
├── types/
│   └── index.ts         # TypeScript types
├── utils/
│   └── response.ts      # Response helpers
├── tests/
│   ├── unit/
│   └── integration/
└── app.ts               # Express app setup
```

### 3. Essential Files

**Environment Configuration (`src/config/env.ts`):**
```typescript
import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: process.env.PORT || 3000,
  supabaseUrl: process.env.SUPABASE_URL!,
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY!,
  supabaseServiceKey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
  jwtSecret: process.env.JWT_SECRET!,
  nodeEnv: process.env.NODE_ENV || 'development',
};
```

**Supabase Client (`src/services/supabase.ts`):**
```typescript
import { createClient } from '@supabase/supabase-js';
import { config } from '../config/env';

// Public client (respects RLS)
export const supabase = createClient(config.supabaseUrl, config.supabaseAnonKey);

// Admin client (bypasses RLS - use carefully)
export const supabaseAdmin = createClient(config.supabaseUrl, config.supabaseServiceKey);
```

## Authentication with Supabase

### Setup Auth Middleware

```typescript
import { Request, Response, NextFunction } from 'express';
import { supabase } from '../services/supabase';

export interface AuthRequest extends Request {
  user?: { id: string; email: string; role: string };
}

export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const { data: { user }, error } = await supabase.auth.getUser(token);
  
  if (error || !user) {
    return res.status(401).json({ error: 'Invalid token' });
  }

  req.user = { id: user.id, email: user.email!, role: user.role || 'user' };
  next();
};
```

### Auth Routes

```typescript
import { Router } from 'express';
import { supabase } from '../services/supabase';

const router = Router();

// Sign up
router.post('/signup', async (req, res) => {
  const { email, password } = req.body;
  const { data, error } = await supabase.auth.signUp({ email, password });
  if (error) return res.status(400).json({ error: error.message });
  res.json({ user: data.user, session: data.session });
});

// Sign in
router.post('/signin', async (req, res) => {
  const { email, password } = req.body;
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) return res.status(401).json({ error: error.message });
  res.json({ user: data.user, session: data.session });
});

// Sign out
router.post('/signout', async (req, res) => {
  const { error } = await supabase.auth.signOut();
  if (error) return res.status(400).json({ error: error.message });
  res.json({ message: 'Signed out successfully' });
});

export default router;
```

### Row Level Security (RLS)

Always enable RLS for user data. Apply via Supabase MCP or SQL:

```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can read their own posts
CREATE POLICY "Users can view own posts" ON posts
  FOR SELECT USING (auth.uid() = author_id);

-- Users can insert their own posts
CREATE POLICY "Users can create posts" ON posts
  FOR INSERT WITH CHECK (auth.uid() = author_id);

-- Users can update their own posts
CREATE POLICY "Users can update own posts" ON posts
  FOR UPDATE USING (auth.uid() = author_id);

-- Users can delete their own posts
CREATE POLICY "Users can delete own posts" ON posts
  FOR DELETE USING (auth.uid() = author_id);
```

## API Design Patterns

### RESTful Endpoints

```typescript
// CRUD pattern for resources
router.get('/posts', listPosts);           // GET /api/posts
router.get('/posts/:id', getPost);         // GET /api/posts/:id
router.post('/posts', createPost);         // POST /api/posts
router.put('/posts/:id', updatePost);      // PUT /api/posts/:id
router.delete('/posts/:id', deletePost);   // DELETE /api/posts/:id

// Nested resources
router.get('/posts/:postId/comments', listComments);
router.post('/posts/:postId/comments', createComment);
```

### Request Validation

Use Zod for runtime validation:

```typescript
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

export const validateCreatePost = (req: Request, res: Response, next: NextFunction) => {
  const result = createPostSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }
  req.body = result.data;
  next();
};
```

### Error Handling

```typescript
// Custom error class
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public code?: string
  ) {
    super(message);
  }
}

// Global error handler
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.message,
      code: err.code,
    });
  }
  
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
};
```

### Response Helpers

```typescript
export const success = <T>(res: Response, data: T, status = 200) => {
  res.status(status).json({ success: true, data });
};

export const paginated = <T>(
  res: Response,
  data: T[],
  page: number,
  limit: number,
  total: number
) => {
  res.json({
    success: true,
    data,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  });
};
```

## Database Operations

### Queries with Supabase

```typescript
// Basic CRUD
const { data, error } = await supabase
  .from('posts')
  .select('*')
  .eq('author_id', userId)
  .order('created_at', { ascending: false })
  .range(0, 9);  // Pagination

// With relationships
const { data } = await supabase
  .from('posts')
  .select(`
    *,
    author:profiles(id, name, avatar_url),
    comments(id, content, created_at)
  `)
  .eq('id', postId)
  .single();

// Insert
const { data, error } = await supabase
  .from('posts')
  .insert({ title, content, author_id: userId })
  .select()
  .single();

// Update
const { data, error } = await supabase
  .from('posts')
  .update({ title, content })
  .eq('id', postId)
  .eq('author_id', userId)  // Ensure ownership
  .select()
  .single();

// Delete
const { error } = await supabase
  .from('posts')
  .delete()
  .eq('id', postId)
  .eq('author_id', userId);
```

### Migrations

Store migrations in `supabase/migrations/`. Naming: `YYYYMMDDHHMMSS_description.sql`

```sql
-- 20240101120000_create_posts.sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  published BOOLEAN DEFAULT false,
  author_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);

-- Add trigger for updated_at
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

Apply via Supabase MCP: `apply_migration` with the SQL content.

## Testing Strategy

### Unit Tests (Vitest/Jest)

```typescript
// tests/unit/services/posts.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createPost } from '../../../src/services/posts';

describe('PostService', () => {
  it('creates a post with valid data', async () => {
    const mockSupabase = {
      from: vi.fn().mockReturnThis(),
      insert: vi.fn().mockReturnThis(),
      select: vi.fn().mockReturnThis(),
      single: vi.fn().mockResolvedValue({
        data: { id: '123', title: 'Test' },
        error: null,
      }),
    };

    const result = await createPost(mockSupabase, {
      title: 'Test',
      content: 'Content',
      author_id: 'user-123',
    });

    expect(result.data).toHaveProperty('id');
    expect(mockSupabase.from).toHaveBeenCalledWith('posts');
  });
});
```

### Integration Tests

```typescript
// tests/integration/api/posts.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../../../src/app';
import { supabaseAdmin } from '../../../src/services/supabase';

describe('POST /api/posts', () => {
  let authToken: string;

  beforeAll(async () => {
    // Create test user and get token
    const { data } = await supabaseAdmin.auth.admin.createUser({
      email: 'test@example.com',
      password: 'testpassword',
      email_confirm: true,
    });
    const { data: session } = await supabaseAdmin.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'testpassword',
    });
    authToken = session.session!.access_token;
  });

  afterAll(async () => {
    // Cleanup test data
    await supabaseAdmin.from('posts').delete().neq('id', '');
    await supabaseAdmin.auth.admin.deleteUser(testUserId);
  });

  it('creates a post when authenticated', async () => {
    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ title: 'Test Post', content: 'Test content' });

    expect(response.status).toBe(201);
    expect(response.body.data).toHaveProperty('id');
  });

  it('returns 401 without auth token', async () => {
    const response = await request(app)
      .post('/api/posts')
      .send({ title: 'Test', content: 'Content' });

    expect(response.status).toBe(401);
  });
});
```

### Test Configuration

**vitest.config.ts:**
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
    },
  },
});
```

**Package.json scripts:**
```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:coverage": "vitest run --coverage"
  }
}
```

## Debug Workflow

1. **Check Logs**
   - Use Supabase MCP `get_logs` to fetch project logs
   - Check application logs with proper log levels

2. **Database Issues**
   - Use `execute_sql` to run diagnostic queries
   - Check RLS policies with `SELECT * FROM pg_policies;`

3. **Auth Issues**
   - Verify JWT token format and expiry
   - Check Supabase auth logs
   - Ensure RLS policies match auth context

4. **Common Issues**
   - Missing environment variables → Check `.env` file
   - CORS errors → Verify allowed origins
   - 401 errors → Check token and middleware order
   - Database errors → Verify schema and migrations

## Security Checklist

- [ ] Enable RLS on all tables with user data
- [ ] Use parameterized queries (Supabase client handles this)
- [ ] Validate all input with Zod or similar
- [ ] Use HTTPS in production
- [ ] Set secure headers with Helmet
- [ ] Implement rate limiting
- [ ] Store secrets in environment variables
- [ ] Use service role key only server-side
- [ ] Audit database access patterns
- [ ] Enable Supabase database backups

## Additional References

See the `references/` directory for:
- `database-patterns.md` - Advanced database patterns, indexes, and query optimization
- `testing-patterns.md` - Comprehensive testing strategies and mocking patterns
- `deployment.md` - Deployment guides for various platforms
