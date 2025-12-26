# Testing Patterns

Comprehensive testing strategies for backend applications.

## Table of Contents
1. Testing Pyramid
2. Unit Testing Patterns
3. Integration Testing
4. API Testing
5. Mocking Supabase
6. Test Data Management

## Testing Pyramid

```
        /\
       /E2E\        <- Few, slow, expensive
      /------\
     /Integration\  <- Some, moderate speed
    /--------------\
   /   Unit Tests   \ <- Many, fast, cheap
  /------------------\
```

Aim for: 70% unit, 20% integration, 10% E2E

## Unit Testing Patterns

### Service Layer Testing

```typescript
// src/services/posts.ts
export class PostService {
  constructor(private db: SupabaseClient) {}

  async create(data: CreatePostInput) {
    const { data: post, error } = await this.db
      .from('posts')
      .insert(data)
      .select()
      .single();
    if (error) throw new AppError(400, error.message);
    return post;
  }
}

// tests/unit/services/posts.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PostService } from '../../../src/services/posts';

describe('PostService', () => {
  let service: PostService;
  let mockDb: any;

  beforeEach(() => {
    mockDb = {
      from: vi.fn().mockReturnThis(),
      insert: vi.fn().mockReturnThis(),
      select: vi.fn().mockReturnThis(),
      single: vi.fn(),
    };
    service = new PostService(mockDb);
  });

  describe('create', () => {
    it('returns created post on success', async () => {
      const mockPost = { id: '123', title: 'Test' };
      mockDb.single.mockResolvedValue({ data: mockPost, error: null });

      const result = await service.create({ title: 'Test', content: 'Content' });

      expect(result).toEqual(mockPost);
      expect(mockDb.from).toHaveBeenCalledWith('posts');
    });

    it('throws AppError on database error', async () => {
      mockDb.single.mockResolvedValue({ 
        data: null, 
        error: { message: 'Duplicate key' } 
      });

      await expect(service.create({ title: 'Test' }))
        .rejects.toThrow('Duplicate key');
    });
  });
});
```

### Validation Testing

```typescript
// tests/unit/validation/posts.test.ts
import { describe, it, expect } from 'vitest';
import { createPostSchema } from '../../../src/validation/posts';

describe('createPostSchema', () => {
  it('accepts valid input', () => {
    const input = { title: 'Valid Title', content: 'Valid content' };
    const result = createPostSchema.safeParse(input);
    expect(result.success).toBe(true);
  });

  it('rejects empty title', () => {
    const input = { title: '', content: 'Content' };
    const result = createPostSchema.safeParse(input);
    expect(result.success).toBe(false);
    expect(result.error?.issues[0].path).toContain('title');
  });

  it('rejects title over 200 chars', () => {
    const input = { title: 'a'.repeat(201), content: 'Content' };
    const result = createPostSchema.safeParse(input);
    expect(result.success).toBe(false);
  });
});
```

### Utility Function Testing

```typescript
// tests/unit/utils/pagination.test.ts
import { describe, it, expect } from 'vitest';
import { calculatePagination } from '../../../src/utils/pagination';

describe('calculatePagination', () => {
  it('calculates correct offset for page 1', () => {
    const result = calculatePagination(1, 10);
    expect(result.offset).toBe(0);
    expect(result.limit).toBe(10);
  });

  it('calculates correct offset for page 3', () => {
    const result = calculatePagination(3, 10);
    expect(result.offset).toBe(20);
  });

  it('uses default limit when not provided', () => {
    const result = calculatePagination(1);
    expect(result.limit).toBe(20); // default
  });
});
```

## Integration Testing

### API Route Testing

```typescript
// tests/integration/routes/posts.test.ts
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import request from 'supertest';
import { app } from '../../../src/app';
import { testDb, createTestUser, cleanupTestData } from '../../helpers';

describe('Posts API', () => {
  let authToken: string;
  let userId: string;

  beforeAll(async () => {
    const user = await createTestUser();
    userId = user.id;
    authToken = user.token;
  });

  afterAll(async () => {
    await cleanupTestData();
  });

  beforeEach(async () => {
    await testDb.from('posts').delete().neq('id', '');
  });

  describe('GET /api/posts', () => {
    it('returns empty array when no posts', async () => {
      const res = await request(app)
        .get('/api/posts')
        .set('Authorization', `Bearer ${authToken}`);

      expect(res.status).toBe(200);
      expect(res.body.data).toEqual([]);
    });

    it('returns paginated posts', async () => {
      // Create 15 posts
      for (let i = 0; i < 15; i++) {
        await testDb.from('posts').insert({
          title: `Post ${i}`,
          content: 'Content',
          author_id: userId,
        });
      }

      const res = await request(app)
        .get('/api/posts?page=1&limit=10')
        .set('Authorization', `Bearer ${authToken}`);

      expect(res.status).toBe(200);
      expect(res.body.data).toHaveLength(10);
      expect(res.body.pagination.total).toBe(15);
      expect(res.body.pagination.pages).toBe(2);
    });
  });

  describe('POST /api/posts', () => {
    it('creates post with valid data', async () => {
      const res = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'New Post', content: 'Content' });

      expect(res.status).toBe(201);
      expect(res.body.data.title).toBe('New Post');
      expect(res.body.data.author_id).toBe(userId);
    });

    it('returns 400 for invalid data', async () => {
      const res = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: '' });

      expect(res.status).toBe(400);
      expect(res.body.errors).toBeDefined();
    });

    it('returns 401 without auth', async () => {
      const res = await request(app)
        .post('/api/posts')
        .send({ title: 'Test', content: 'Content' });

      expect(res.status).toBe(401);
    });
  });
});
```

### Database Integration Testing

```typescript
// tests/integration/db/posts.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { testDb, createTestUser, cleanupTestData } from '../../helpers';

describe('Posts Database Operations', () => {
  let userId: string;

  beforeAll(async () => {
    const user = await createTestUser();
    userId = user.id;
  });

  afterAll(cleanupTestData);

  it('enforces RLS - users can only see own posts', async () => {
    // Create post as user
    await testDb.from('posts').insert({
      title: 'My Post',
      content: 'Content',
      author_id: userId,
    });

    // Create another user
    const otherUser = await createTestUser('other@test.com');

    // Query as other user (simulate with different auth context)
    const { data } = await testDb
      .from('posts')
      .select()
      .eq('author_id', otherUser.id);

    expect(data).toHaveLength(0);
  });

  it('cascades delete when user is deleted', async () => {
    const { data: post } = await testDb
      .from('posts')
      .insert({ title: 'Test', content: 'Content', author_id: userId })
      .select()
      .single();

    // Delete user
    await testDb.auth.admin.deleteUser(userId);

    // Check post is deleted
    const { data } = await testDb
      .from('posts')
      .select()
      .eq('id', post.id);

    expect(data).toHaveLength(0);
  });
});
```

## API Testing

### Using Test Helpers

```typescript
// tests/helpers/index.ts
import { createClient } from '@supabase/supabase-js';

export const testDb = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

export async function createTestUser(email = 'test@example.com') {
  const { data: user } = await testDb.auth.admin.createUser({
    email,
    password: 'testpassword123',
    email_confirm: true,
  });

  const { data: session } = await testDb.auth.signInWithPassword({
    email,
    password: 'testpassword123',
  });

  return {
    id: user.user!.id,
    email,
    token: session.session!.access_token,
  };
}

export async function cleanupTestData() {
  // Delete in order respecting foreign keys
  await testDb.from('comments').delete().neq('id', '');
  await testDb.from('posts').delete().neq('id', '');
  
  // Delete test users
  const { data: users } = await testDb.auth.admin.listUsers();
  for (const user of users.users) {
    if (user.email?.includes('test')) {
      await testDb.auth.admin.deleteUser(user.id);
    }
  }
}
```

### Request Builder Pattern

```typescript
// tests/helpers/request.ts
import request from 'supertest';
import { app } from '../../src/app';

export class ApiRequest {
  private req: request.Test;
  private token?: string;

  constructor(method: 'get' | 'post' | 'put' | 'delete', path: string) {
    this.req = request(app)[method](path);
  }

  auth(token: string) {
    this.token = token;
    return this;
  }

  send(body: object) {
    this.req.send(body);
    return this;
  }

  async execute() {
    if (this.token) {
      this.req.set('Authorization', `Bearer ${this.token}`);
    }
    return this.req;
  }
}

// Usage
const res = await new ApiRequest('post', '/api/posts')
  .auth(token)
  .send({ title: 'Test' })
  .execute();
```

## Mocking Supabase

### Full Client Mock

```typescript
// tests/mocks/supabase.ts
import { vi } from 'vitest';

export const createMockSupabase = () => ({
  from: vi.fn(() => ({
    select: vi.fn().mockReturnThis(),
    insert: vi.fn().mockReturnThis(),
    update: vi.fn().mockReturnThis(),
    delete: vi.fn().mockReturnThis(),
    eq: vi.fn().mockReturnThis(),
    neq: vi.fn().mockReturnThis(),
    order: vi.fn().mockReturnThis(),
    range: vi.fn().mockReturnThis(),
    single: vi.fn(),
    maybeSingle: vi.fn(),
  })),
  auth: {
    getUser: vi.fn(),
    signInWithPassword: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
  },
});

// Usage in test
const mockSupabase = createMockSupabase();
mockSupabase.from('posts').single.mockResolvedValue({
  data: { id: '123', title: 'Test' },
  error: null,
});
```

### Partial Mock with Real Client

```typescript
// tests/setup.ts
import { vi } from 'vitest';

// Mock only specific methods
vi.mock('../src/services/supabase', async () => {
  const actual = await vi.importActual('../src/services/supabase');
  return {
    ...actual,
    supabase: {
      ...actual.supabase,
      // Override specific methods
      auth: {
        getUser: vi.fn().mockResolvedValue({
          data: { user: { id: 'mock-user' } },
          error: null,
        }),
      },
    },
  };
});
```

## Test Data Management

### Factories

```typescript
// tests/factories/post.ts
import { faker } from '@faker-js/faker';

export const postFactory = {
  build: (overrides = {}) => ({
    title: faker.lorem.sentence(),
    content: faker.lorem.paragraphs(3),
    published: false,
    ...overrides,
  }),

  buildList: (count: number, overrides = {}) =>
    Array.from({ length: count }, () => postFactory.build(overrides)),
};

// Usage
const post = postFactory.build({ title: 'Custom Title' });
const posts = postFactory.buildList(5, { published: true });
```

### Fixtures

```typescript
// tests/fixtures/posts.json
{
  "validPost": {
    "title": "Test Post",
    "content": "Test content for the post"
  },
  "invalidPost": {
    "title": "",
    "content": ""
  }
}

// tests/fixtures/index.ts
import posts from './posts.json';

export const fixtures = {
  posts,
};

// Usage
import { fixtures } from '../fixtures';
const res = await request(app)
  .post('/api/posts')
  .send(fixtures.posts.validPost);
```

### Database Seeding

```typescript
// tests/seed.ts
import { testDb } from './helpers';
import { postFactory } from './factories/post';

export async function seedTestData() {
  // Create test users
  const users = await Promise.all([
    createTestUser('user1@test.com'),
    createTestUser('user2@test.com'),
  ]);

  // Create posts for each user
  for (const user of users) {
    const posts = postFactory.buildList(5, { author_id: user.id });
    await testDb.from('posts').insert(posts);
  }

  return { users };
}
```

## Test Configuration

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts'],
    exclude: ['tests/e2e/**'],
    testTimeout: 10000,
    hookTimeout: 10000,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: ['tests/**', '**/*.d.ts', '**/types/**'],
    },
    env: {
      NODE_ENV: 'test',
    },
  },
});
```

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:integration
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
      - uses: codecov/codecov-action@v3
```
