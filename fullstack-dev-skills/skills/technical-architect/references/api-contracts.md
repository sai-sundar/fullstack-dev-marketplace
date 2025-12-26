# API Contracts

Define API interfaces before implementation to ensure frontend and backend alignment.

## Table of Contents
1. OpenAPI Specification
2. tRPC for Type-Safe APIs
3. Shared Types Strategy
4. Error Contract Standards
5. Versioning Approaches

---

## 1. OpenAPI Specification

### Basic Structure

```yaml
openapi: 3.0.3
info:
  title: MyApp API
  version: 1.0.0
  description: API contract for MyApp

servers:
  - url: http://localhost:3000/api
    description: Development
  - url: https://api.myapp.com
    description: Production

paths:
  /posts:
    get:
      summary: List all posts
      operationId: listPosts
      tags: [Posts]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Paginated list of posts
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedPosts'
    post:
      summary: Create a post
      operationId: createPost
      tags: [Posts]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreatePostInput'
      responses:
        '201':
          description: Post created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Post'
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /posts/{id}:
    get:
      summary: Get a post by ID
      operationId: getPost
      tags: [Posts]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Post details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Post'
        '404':
          $ref: '#/components/responses/NotFound'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Post:
      type: object
      required: [id, title, content, authorId, createdAt]
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
          maxLength: 200
        content:
          type: string
        published:
          type: boolean
          default: false
        authorId:
          type: string
          format: uuid
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    CreatePostInput:
      type: object
      required: [title, content]
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 200
        content:
          type: string
          minLength: 1
        published:
          type: boolean
          default: false

    PaginatedPosts:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Post'
        pagination:
          $ref: '#/components/schemas/Pagination'

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        pages:
          type: integer

    Error:
      type: object
      properties:
        error:
          type: string
        code:
          type: string
        details:
          type: object

  responses:
    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: Validation failed
            code: VALIDATION_ERROR
            details:
              title: ["Title is required"]

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: Authentication required
            code: UNAUTHORIZED

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: Post not found
            code: NOT_FOUND
```

### Generate TypeScript Types from OpenAPI

```bash
# Install openapi-typescript
npm install -D openapi-typescript

# Generate types
npx openapi-typescript ./openapi.yaml -o ./src/types/api.ts
```

Generated types can be shared between frontend and backend.

---

## 2. tRPC for Type-Safe APIs

For monorepo setups where frontend and backend share code, tRPC provides end-to-end type safety.

### Router Definition (Backend)

```typescript
// packages/api/src/routers/posts.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../trpc';

export const postsRouter = router({
  list: publicProcedure
    .input(z.object({
      page: z.number().default(1),
      limit: z.number().default(20),
    }))
    .query(async ({ input, ctx }) => {
      const { page, limit } = input;
      const offset = (page - 1) * limit;
      
      const { data, count } = await ctx.db
        .from('posts')
        .select('*', { count: 'exact' })
        .range(offset, offset + limit - 1);
      
      return {
        data,
        pagination: { page, limit, total: count, pages: Math.ceil(count / limit) }
      };
    }),

  create: protectedProcedure
    .input(z.object({
      title: z.string().min(1).max(200),
      content: z.string().min(1),
      published: z.boolean().default(false),
    }))
    .mutation(async ({ input, ctx }) => {
      const { data, error } = await ctx.db
        .from('posts')
        .insert({ ...input, author_id: ctx.user.id })
        .select()
        .single();
      
      if (error) throw new TRPCError({ code: 'BAD_REQUEST', message: error.message });
      return data;
    }),

  byId: publicProcedure
    .input(z.string().uuid())
    .query(async ({ input, ctx }) => {
      const { data, error } = await ctx.db
        .from('posts')
        .select('*')
        .eq('id', input)
        .single();
      
      if (error || !data) throw new TRPCError({ code: 'NOT_FOUND' });
      return data;
    }),
});
```

### Client Usage (Frontend)

```typescript
// apps/web/src/hooks/usePosts.ts
import { trpc } from '../utils/trpc';

export function usePosts(page = 1) {
  return trpc.posts.list.useQuery({ page, limit: 20 });
}

export function useCreatePost() {
  const utils = trpc.useUtils();
  
  return trpc.posts.create.useMutation({
    onSuccess: () => {
      utils.posts.list.invalidate();
    },
  });
}

// Full type safety - TypeScript knows the exact shape of data
const { data } = usePosts();
// data.data[0].title is typed as string
// data.pagination.total is typed as number
```

### tRPC Project Structure

```
packages/
├── api/                    # tRPC routers and procedures
│   ├── src/
│   │   ├── routers/
│   │   │   ├── posts.ts
│   │   │   ├── users.ts
│   │   │   └── index.ts    # Merge all routers
│   │   ├── trpc.ts         # tRPC initialization
│   │   └── context.ts      # Request context
│   └── package.json
├── shared/                 # Shared types and utilities
│   ├── src/
│   │   ├── types/
│   │   └── utils/
│   └── package.json
apps/
├── web/                    # React frontend
│   └── src/
│       └── utils/trpc.ts   # tRPC client setup
└── server/                 # Express/Fastify server
    └── src/
        └── index.ts        # Mount tRPC adapter
```

---

## 3. Shared Types Strategy

### Option A: Generated from OpenAPI

```
openapi.yaml → openapi-typescript → types/api.ts (copy to both)
```

### Option B: Shared Package (Monorepo)

```typescript
// packages/shared/src/types/post.ts
export interface Post {
  id: string;
  title: string;
  content: string;
  published: boolean;
  authorId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreatePostInput {
  title: string;
  content: string;
  published?: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// packages/shared/src/types/index.ts
export * from './post';
export * from './user';
export * from './error';
```

### Option C: Zod Schemas (Runtime + Types)

```typescript
// packages/shared/src/schemas/post.ts
import { z } from 'zod';

export const PostSchema = z.object({
  id: z.string().uuid(),
  title: z.string().max(200),
  content: z.string(),
  published: z.boolean(),
  authorId: z.string().uuid(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

export const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

// Infer TypeScript types from schemas
export type Post = z.infer<typeof PostSchema>;
export type CreatePostInput = z.infer<typeof CreatePostSchema>;

// Use for validation in both frontend and backend
const result = CreatePostSchema.safeParse(userInput);
if (!result.success) {
  // Handle validation errors
}
```

---

## 4. Error Contract Standards

### Standard Error Response

```typescript
// packages/shared/src/types/error.ts
export interface ApiError {
  error: string;           // Human-readable message
  code: ErrorCode;         // Machine-readable code
  details?: Record<string, string[]>;  // Field-level errors
  requestId?: string;      // For debugging
}

export type ErrorCode =
  | 'VALIDATION_ERROR'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'CONFLICT'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR';

export const HTTP_STATUS: Record<ErrorCode, number> = {
  VALIDATION_ERROR: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  RATE_LIMITED: 429,
  INTERNAL_ERROR: 500,
};
```

### Backend Error Handling

```typescript
// Backend throws structured errors
throw new AppError('VALIDATION_ERROR', 'Title is required', {
  title: ['Title is required', 'Title must be at least 1 character']
});
```

### Frontend Error Handling

```typescript
// Frontend handles errors consistently
try {
  await createPost(input);
} catch (error) {
  if (isApiError(error)) {
    if (error.code === 'VALIDATION_ERROR') {
      setFieldErrors(error.details);
    } else {
      toast.error(error.error);
    }
  }
}
```

---

## 5. Versioning Approaches

### URL Prefix (Recommended for REST)

```
/api/v1/posts
/api/v2/posts  # Breaking changes
```

### Header-Based

```
GET /api/posts
Accept: application/vnd.myapp.v1+json
```

### Query Parameter

```
GET /api/posts?version=1
```

### tRPC Versioning

For tRPC, version via router structure:

```typescript
export const appRouter = router({
  v1: v1Router,  // Legacy
  v2: v2Router,  // Current
});
```

---

## Contract Review Checklist

Before implementation, verify:

- [ ] All endpoints documented with request/response schemas
- [ ] Authentication requirements specified per endpoint
- [ ] Error responses defined for all failure cases
- [ ] Pagination format standardized
- [ ] Field validations documented (min/max lengths, formats)
- [ ] Types shared between frontend and backend
- [ ] Breaking change strategy defined
