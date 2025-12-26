# Project Structure

Monorepo setup and package organization for full-stack applications.

## Table of Contents
1. Monorepo vs Polyrepo Decision
2. Turborepo Setup
3. Package Organization
4. Shared Code Strategy
5. Environment Configuration
6. Build and Deploy Coordination

---

## 1. Monorepo vs Polyrepo Decision

### Choose Monorepo When:
- Frontend and backend share types/schemas
- Single team owns both frontend and backend
- Coordinated deployments needed
- Shared utilities benefit both sides

### Choose Polyrepo When:
- Separate teams with different release cycles
- Different programming languages
- Independent scaling requirements
- Strict separation of concerns needed

**Default recommendation: Monorepo with Turborepo** for most full-stack apps.

---

## 2. Turborepo Setup

### Initialize

```bash
npx create-turbo@latest my-app
cd my-app
```

### Directory Structure

```
my-app/
├── apps/
│   ├── web/                 # React frontend
│   │   ├── src/
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── server/              # Express/Node backend
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── shared/              # Shared types and utilities
│   │   ├── src/
│   │   │   ├── types/
│   │   │   ├── utils/
│   │   │   └── index.ts
│   │   └── package.json
│   ├── ui/                  # Shared UI components (optional)
│   │   ├── src/
│   │   └── package.json
│   ├── config-eslint/       # Shared ESLint config
│   │   └── index.js
│   └── config-typescript/   # Shared TypeScript config
│       └── base.json
├── turbo.json
├── package.json
└── pnpm-workspace.yaml
```

### Root package.json

```json
{
  "name": "my-app",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  },
  "packageManager": "pnpm@8.15.0"
}
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "lint": {},
    "type-check": {
      "dependsOn": ["^build"]
    }
  }
}
```

### pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

---

## 3. Package Organization

### apps/web (Frontend)

```json
{
  "name": "@my-app/web",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@my-app/shared": "workspace:*",
    "@my-app/ui": "workspace:*",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  }
}
```

### apps/server (Backend)

```json
{
  "name": "@my-app/server",
  "private": true,
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@my-app/shared": "workspace:*",
    "@supabase/supabase-js": "^2.0.0",
    "express": "^4.18.0",
    "zod": "^3.23.0"
  }
}
```

### packages/shared

```json
{
  "name": "@my-app/shared",
  "version": "0.0.0",
  "main": "./dist/index.js",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch"
  },
  "devDependencies": {
    "tsup": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

### packages/shared/src Structure

```
packages/shared/src/
├── types/
│   ├── post.ts          # Post types
│   ├── user.ts          # User types
│   ├── api.ts           # API response types
│   └── index.ts         # Re-export all
├── schemas/
│   ├── post.ts          # Zod schemas for validation
│   ├── user.ts
│   └── index.ts
├── utils/
│   ├── date.ts          # Date formatting
│   ├── validation.ts    # Common validators
│   └── index.ts
├── constants/
│   └── index.ts         # Shared constants
└── index.ts             # Main entry point
```

### packages/shared/src/index.ts

```typescript
// Types
export * from './types';

// Schemas (Zod)
export * from './schemas';

// Utilities
export * from './utils';

// Constants
export * from './constants';
```

---

## 4. Shared Code Strategy

### What to Share

| Category | Location | Example |
|----------|----------|---------|
| Types/Interfaces | `packages/shared/types` | `Post`, `User`, `ApiResponse` |
| Validation Schemas | `packages/shared/schemas` | Zod schemas |
| Constants | `packages/shared/constants` | Error codes, limits |
| Pure Utilities | `packages/shared/utils` | Date formatting, slug generation |
| UI Components | `packages/ui` | Button, Card, Modal |

### What NOT to Share

- Database queries (backend only)
- React hooks (frontend only)
- Environment-specific config
- Server middleware
- Client-side state management

### Importing Shared Code

```typescript
// In apps/web
import { Post, CreatePostSchema } from '@my-app/shared';
import { Button } from '@my-app/ui';

// In apps/server
import { Post, CreatePostSchema } from '@my-app/shared';
```

---

## 5. Environment Configuration

### Environment Files

```
my-app/
├── .env                    # Shared defaults (committed)
├── .env.local              # Local overrides (gitignored)
├── apps/
│   ├── web/
│   │   ├── .env            # Web-specific defaults
│   │   └── .env.local      # Web local overrides
│   └── server/
│       ├── .env            # Server-specific defaults
│       └── .env.local      # Server local overrides
```

### .gitignore

```gitignore
# Environment
.env.local
.env.*.local

# But commit defaults
!.env
```

### Environment Variable Naming

```bash
# apps/web/.env
VITE_API_URL=http://localhost:3001/api
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx

# apps/server/.env
PORT=3001
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx  # Never expose to frontend
JWT_SECRET=xxx
```

### Type-Safe Environment

```typescript
// apps/server/src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  PORT: z.coerce.number().default(3001),
  DATABASE_URL: z.string(),
  SUPABASE_URL: z.string().url(),
  SUPABASE_SERVICE_KEY: z.string(),
  JWT_SECRET: z.string().min(32),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export const env = envSchema.parse(process.env);
```

---

## 6. Build and Deploy Coordination

### Development Workflow

```bash
# Start all apps in dev mode
pnpm dev

# Start specific app
pnpm --filter @my-app/web dev
pnpm --filter @my-app/server dev

# Run command in all packages
pnpm -r test
```

### Build Order

Turbo handles build order automatically based on dependencies:

```
packages/shared (build first)
    ↓
packages/ui (depends on shared)
    ↓
apps/web + apps/server (depend on shared, ui)
```

### CI Pipeline Example

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 8
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install
      - run: pnpm lint
      - run: pnpm type-check
      - run: pnpm test
      - run: pnpm build
```

### Deployment Strategies

**Option A: Deploy Together**
```yaml
# Single workflow deploys both
deploy:
  needs: build
  steps:
    - run: pnpm --filter @my-app/server deploy
    - run: pnpm --filter @my-app/web deploy
```

**Option B: Deploy Independently**
```yaml
# Separate workflows per app
# .github/workflows/deploy-web.yml
on:
  push:
    paths:
      - 'apps/web/**'
      - 'packages/shared/**'
      - 'packages/ui/**'
```

---

## Project Setup Checklist

When initializing a new monorepo:

- [ ] Initialize with Turborepo or Nx
- [ ] Create `packages/shared` for types and utilities
- [ ] Set up TypeScript path aliases
- [ ] Configure ESLint with shared config
- [ ] Set up environment variable strategy
- [ ] Create development scripts in root package.json
- [ ] Configure CI/CD pipeline
- [ ] Document local setup in README
- [ ] Set up pre-commit hooks (husky + lint-staged)
