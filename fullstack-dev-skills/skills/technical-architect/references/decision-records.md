# Decision Records

Architecture Decision Records (ADRs) document significant technical decisions.

## Table of Contents
1. ADR Format
2. When to Write an ADR
3. Common Decision Templates
4. Example ADRs

---

## 1. ADR Format

### Template

```markdown
# ADR-{NUMBER}: {TITLE}

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Tradeoff 1
- Tradeoff 2

### Neutral
- Side effect that is neither positive nor negative
```

### File Naming

```
docs/decisions/
├── 0001-use-supabase-for-database.md
├── 0002-monorepo-with-turborepo.md
├── 0003-rest-api-over-graphql.md
└── 0004-react-with-vite.md
```

---

## 2. When to Write an ADR

Write an ADR when deciding:

- **Technology choices**: Database, framework, language
- **Architecture patterns**: Monolith vs microservices, API style
- **Infrastructure**: Cloud provider, deployment strategy
- **Conventions**: Coding standards, branching strategy
- **Security**: Authentication method, data encryption

Skip ADRs for:
- Obvious choices with no alternatives considered
- Minor implementation details
- Temporary decisions (spikes, experiments)

---

## 3. Common Decision Templates

### Database Selection

```markdown
# ADR-001: Use Supabase for Database and Authentication

**Date:** 2024-01-15
**Status:** Accepted

## Context

We need a database solution that supports:
- PostgreSQL for relational data
- Real-time subscriptions
- Built-in authentication
- Row-level security
- Rapid development

Alternatives considered:
1. Self-hosted PostgreSQL + custom auth
2. Firebase (Firestore)
3. PlanetScale (MySQL)
4. Supabase

## Decision

Use Supabase as our database and authentication provider.

## Consequences

### Positive
- Built-in auth reduces development time by ~2 weeks
- Row-level security simplifies authorization logic
- Real-time subscriptions available out of the box
- PostgreSQL gives us full SQL capabilities
- Generous free tier for development

### Negative
- Vendor lock-in to Supabase-specific features
- Must learn Supabase RLS syntax
- Limited control over database server configuration

### Neutral
- Team needs to learn Supabase dashboard and CLI
```

### API Style Selection

```markdown
# ADR-002: REST API with OpenAPI over GraphQL

**Date:** 2024-01-16
**Status:** Accepted

## Context

We need to choose an API style for frontend-backend communication.

Options:
1. REST with OpenAPI specification
2. GraphQL
3. tRPC (type-safe RPC)

Considerations:
- Team familiarity
- Tooling ecosystem
- Type safety requirements
- Caching needs

## Decision

Use REST API with OpenAPI specification for type generation.

## Consequences

### Positive
- Team has REST experience, minimal learning curve
- HTTP caching works naturally
- OpenAPI generates TypeScript types for frontend
- Simpler debugging with standard HTTP tools
- Better fit for CRUD-heavy application

### Negative
- Multiple endpoints for related data (vs single GraphQL query)
- Manual optimization for overfetching
- More boilerplate than tRPC

### Neutral
- Need to maintain OpenAPI spec (but provides documentation)
```

### Monorepo Structure

```markdown
# ADR-003: Monorepo with Turborepo

**Date:** 2024-01-17
**Status:** Accepted

## Context

We're building a full-stack application with:
- React frontend
- Node.js backend
- Shared TypeScript types

Options:
1. Separate repositories (polyrepo)
2. Monorepo with Turborepo
3. Monorepo with Nx
4. Monorepo with Lerna

## Decision

Use Turborepo for monorepo management.

## Consequences

### Positive
- Shared types between frontend and backend
- Atomic commits across entire stack
- Simplified CI/CD with single pipeline
- Turborepo is lightweight and fast
- Built-in caching reduces build times

### Negative
- Larger repository size
- More complex initial setup
- All developers need full repo access

### Neutral
- pnpm workspaces for package management
```

### Authentication Strategy

```markdown
# ADR-004: Supabase Auth with JWT

**Date:** 2024-01-18
**Status:** Accepted

## Context

Need authentication supporting:
- Email/password login
- OAuth providers (Google, GitHub)
- Session management
- API authentication

## Decision

Use Supabase Auth with JWT tokens.

- Frontend stores JWT in memory (not localStorage)
- Backend validates JWT on each request
- Refresh tokens handled by Supabase client
- RLS policies use auth.uid() for authorization

## Consequences

### Positive
- Zero auth code to write
- OAuth providers pre-configured
- Integrates seamlessly with RLS
- Secure defaults (httpOnly cookies option)

### Negative
- Tied to Supabase ecosystem
- Limited customization of auth flows
- Must handle token refresh on frontend

### Neutral
- JWT expiry set to 1 hour (configurable)
```

### State Management

```markdown
# ADR-005: React Query for Server State

**Date:** 2024-01-19
**Status:** Accepted

## Context

Need to manage server state (API data) in React app.

Options:
1. useState + useEffect (manual)
2. Redux + RTK Query
3. React Query (TanStack Query)
4. SWR

## Decision

Use React Query for server state management.

## Consequences

### Positive
- Automatic caching and invalidation
- Built-in loading/error states
- Optimistic updates support
- DevTools for debugging
- Smaller bundle than Redux

### Negative
- Another library to learn
- Not suitable for complex client-only state

### Neutral
- Will use Zustand for client-only state if needed
```

---

## 4. Example ADRs

### Quick Reference Table

| ADR | Decision | Key Reason |
|-----|----------|------------|
| 001 | Supabase | Built-in auth + RLS |
| 002 | REST + OpenAPI | Team familiarity + caching |
| 003 | Turborepo | Shared types + fast builds |
| 004 | Supabase Auth | Zero auth code needed |
| 005 | React Query | Automatic cache management |

### ADR Review Checklist

Before finalizing an ADR:

- [ ] Context explains the problem clearly
- [ ] Alternatives were genuinely considered
- [ ] Decision is specific and actionable
- [ ] Consequences include both positives and negatives
- [ ] Status is set correctly
- [ ] Date is recorded
- [ ] Stakeholders have reviewed (if applicable)

---

## ADR Lifecycle

```
Proposed → Accepted → [Active]
                ↓
           Deprecated (better option found)
                ↓
           Superseded by ADR-XXX
```

When superseding:
1. Create new ADR with updated decision
2. Update old ADR status to "Superseded by ADR-XXX"
3. Link old ADR in new ADR's context section
