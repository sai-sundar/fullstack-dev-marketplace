---
name: technical-architect
description: System design and architecture planning for full-stack applications. Use when starting new projects, designing API contracts between frontend and backend, planning database schemas, making technology decisions, creating system diagrams, setting up monorepos, or coordinating work between frontend and backend development. Triggers on requests like "design the architecture", "plan the system", "create API contracts", "set up project structure", "what's the best approach for...", or any pre-implementation planning phase.
---

# Technical Architect

Plan and design full-stack applications before implementation. This skill bridges frontend and backend development with API contracts, system design, and architectural decisions.

## Workflow Decision Tree

```
User Request
├─► "Start new project / design system"
│   └─► Full Architecture Workflow → Requirements → Design → Contracts → Structure
├─► "Design API / create contracts"
│   └─► API Contract Workflow → See references/api-contracts.md
├─► "Plan database schema"
│   └─► Schema Design Workflow → See references/database-design.md
├─► "Set up monorepo / project structure"
│   └─► Project Structure Workflow → See references/project-structure.md
├─► "Make technology decision"
│   └─► Decision Record Workflow → See references/decision-records.md
└─► "Create architecture diagram"
    └─► Diagram Workflow → Mermaid diagrams in references/diagrams.md
```

## Full Architecture Workflow

For new projects or major features, follow this sequence:

1. **Gather Requirements** → Understand scope, users, constraints
2. **Create System Design** → High-level architecture, component boundaries
3. **Define API Contracts** → OpenAPI specs or tRPC schemas
4. **Design Database Schema** → Tables, relationships, indexes
5. **Generate Binding Contracts** → Create `contracts/` directory with artifacts
6. **Plan Project Structure** → Monorepo setup, shared packages
7. **Document Decisions** → ADRs for key technology choices
8. **Hand off to Implementation** → Frontend and backend skills take over

## CRITICAL: Binding Contracts

**Every architecture MUST produce a `contracts/` directory** that serves as the single source of truth for both frontend and backend. Without this, integration issues will occur.

### Required Contract Artifacts

```
contracts/
├── api.yaml                 # OpenAPI 3.0 specification
├── database.sql             # Complete schema with exact column names
├── types.ts                 # Shared TypeScript types
├── endpoints.ts             # API endpoint constants
├── errors.ts                # Error codes and response shapes
└── validation.ts            # Zod schemas for request/response
```

### Contract Rules

1. **Column names in `database.sql` MUST match field names in `types.ts`**
2. **Every endpoint in `api.yaml` MUST have corresponding type in `types.ts`**
3. **Frontend and backend MUST import from contracts, never define their own**
4. **Any schema change MUST update all contract files together**

### Example: CV Upload Contract

```sql
-- contracts/database.sql
CREATE TABLE cvs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  file_url TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_size_bytes INTEGER NOT NULL,
  target_role TEXT,
  uploaded_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

```typescript
// contracts/types.ts
export interface CV {
  id: string;
  user_id: string;           // MUST match database column exactly
  file_url: string;
  original_filename: string;
  file_size_bytes: number;
  target_role: string | null;
  uploaded_at: string;
  updated_at: string;
}

export interface CVUploadRequest {
  file: File;
  target_role?: string;
}

export interface CVUploadResponse {
  cv: CV;
  upload_url: string;
}
```

```typescript
// contracts/endpoints.ts
export const API = {
  CV: {
    UPLOAD: '/api/v1/cv/upload',
    ANALYZE: '/api/v1/cv/:id/analyze',
    GET: '/api/v1/cv/:id',
    LIST: '/api/v1/cv',
  },
  // ... other endpoints
} as const;
```

```typescript
// contracts/validation.ts
import { z } from 'zod';

export const CVUploadSchema = z.object({
  file: z.instanceof(File).refine(
    f => f.size <= 10 * 1024 * 1024,
    'File must be under 10MB'
  ),
  target_role: z.string().optional(),
});

export const CVSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  file_url: z.string().url(),
  original_filename: z.string(),
  file_size_bytes: z.number().int().positive(),
  target_role: z.string().nullable(),
  uploaded_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
```

## Quick Reference

### Technology Stack Recommendations

| Layer | Default Choice | Alternative | When to Switch |
|-------|---------------|-------------|----------------|
| Frontend | React + Vite + TypeScript | Next.js | Need SSR/SSG |
| Backend | Node.js + Express + TypeScript | FastAPI (Python) | ML-heavy backend |
| Database | Supabase (PostgreSQL) | - | Default for all |
| Auth | Supabase Auth | - | Default for all |
| API Style | REST + OpenAPI | tRPC | Type-safe monorepo |
| Monorepo | Turborepo | Nx | Enterprise scale |

### Component Boundaries

Define clear boundaries between frontend and backend:

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  React Components → Hooks → API Client → Types (shared) │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────┐
│                      BACKEND                            │
│  Routes → Controllers → Services → Database (Supabase)  │
│                    ↓                                    │
│              Types (shared)                             │
└─────────────────────────────────────────────────────────┘
```

### API Design Principles

1. **Contract-first**: Define OpenAPI/tRPC schema before implementation
2. **Consistent naming**: `GET /api/posts`, `POST /api/posts`, `GET /api/posts/:id`
3. **Typed responses**: Share types between frontend and backend
4. **Error contracts**: Standardize error response format
5. **Versioning strategy**: URL prefix (`/api/v1/`) or header-based

## Handoff Protocol

When architecture is complete, provide implementation teams:

**CRITICAL: Both skills MUST read `contracts/` before implementation**

**For Backend Developer skill:**
- `contracts/database.sql` — Execute exactly as written
- `contracts/api.yaml` — Implement these exact endpoints
- `contracts/validation.ts` — Use these schemas for request validation
- `contracts/types.ts` — Response shapes must match exactly
- Auth requirements and RLS policies
- Environment variables needed

**For Frontend Developer skill:**
- `contracts/types.ts` — Use these types for all API interactions
- `contracts/endpoints.ts` — Import endpoint URLs, never hardcode
- `contracts/validation.ts` — Use for client-side validation
- Component hierarchy diagram
- State management approach
- Design system requirements

**Handoff Checklist:**
- [ ] `contracts/` directory exists with all required files
- [ ] Database SQL has been reviewed and is executable
- [ ] All endpoints in api.yaml have types in types.ts
- [ ] Validation schemas cover all request bodies
- [ ] Error codes are defined in errors.ts

## References

Detailed guides for specific workflows:

- **API Contracts**: See `references/api-contracts.md` for OpenAPI specs, tRPC setup, type sharing
- **Database Design**: See `references/database-design.md` for schema patterns, normalization, indexes
- **Project Structure**: See `references/project-structure.md` for monorepo setup, package organization
- **Decision Records**: See `references/decision-records.md` for ADR templates, common decisions
- **Diagrams**: See `references/diagrams.md` for Mermaid syntax, architecture patterns

## Scripts

- `scripts/generate_openapi.py`: Generate OpenAPI spec from route definitions
- `scripts/init_monorepo.sh`: Initialize Turborepo with shared packages
- `scripts/generate_contracts.py`: Generate complete contracts/ directory from requirements

## References

- **Binding Contracts**: See `references/binding-contracts.md` for contract templates and validation
- **API Contracts**: See `references/api-contracts.md` for OpenAPI specs, tRPC setup, type sharing
- **Database Design**: See `references/database-design.md` for schema patterns, normalization, indexes
- **Project Structure**: See `references/project-structure.md` for monorepo setup, package organization
- **Decision Records**: See `references/decision-records.md` for ADR templates, common decisions
- **Diagrams**: See `references/diagrams.md` for Mermaid syntax, architecture patterns
