# Developer Onboarding Guide

> **Generated for**: [Project Name]
> **Date**: [Date]
> **Estimated onboarding time**: [X] hours

---

## Welcome! 👋

Welcome to the team! This guide will help you get up to speed with our codebase. By the end of your first week, you'll be able to understand our architecture, run the project locally, and make your first contribution.

---

## Quick Start (Day 1)

### 1. Clone and Setup

```bash
# Clone the repository
git clone [repo-url]
cd [project-name]

# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with values from team password manager

# Start development servers
pnpm dev
```

### 2. Verify Everything Works

- [ ] Frontend runs at http://localhost:5173
- [ ] Backend runs at http://localhost:3000
- [ ] Can sign up / log in
- [ ] Can perform main feature (e.g., upload a CV)

### 3. Get Access To

- [ ] GitHub repository (push access)
- [ ] Supabase dashboard
- [ ] Team Slack channel
- [ ] Project management tool (Linear/Jira/etc.)

---

## Project Overview

### What Does This App Do?

[Brief description of the application and its main purpose]

### Who Are Our Users?

[Description of target users and their goals]

### Main Features

1. **[Feature 1]**: [Brief description]
2. **[Feature 2]**: [Brief description]
3. **[Feature 3]**: [Brief description]

---

## Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                   React + TypeScript                        │
│                   (apps/web)                                │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│                  Express + TypeScript                       │
│                   (apps/server)                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                              │
│               Supabase (PostgreSQL)                         │
│                    + Auth + Storage                         │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
[project-name]/
├── apps/
│   ├── web/                 # Frontend React application
│   │   ├── src/
│   │   │   ├── components/  # UI components
│   │   │   ├── hooks/       # Custom React hooks
│   │   │   ├── pages/       # Page components
│   │   │   └── api/         # API client functions
│   │   └── ...
│   │
│   └── server/              # Backend Express application
│       ├── src/
│       │   ├── routes/      # HTTP route handlers
│       │   ├── services/    # Business logic
│       │   ├── middleware/  # Express middleware
│       │   └── utils/       # Utility functions
│       └── ...
│
├── packages/
│   └── shared/              # Shared code between apps
│       └── src/
│           └── contracts/   # Shared types and schemas
│
├── contracts/               # API contracts (source of truth)
│   ├── database.sql         # Database schema
│   ├── types.ts             # TypeScript types
│   ├── endpoints.ts         # API endpoint constants
│   └── validation.ts        # Zod validation schemas
│
└── docs/                    # Documentation
    └── decisions/           # Architecture Decision Records
```

### Key Architectural Patterns

#### 1. Contracts Pattern
We use a `contracts/` directory as the single source of truth for:
- Database schema
- TypeScript types
- API endpoints
- Validation rules

**Why?** Prevents frontend-backend drift. If you change a type, both sides update.

#### 2. Service Layer
Business logic lives in `services/`, not in route handlers.

```
Route Handler → Service → Database
     ↓
  (HTTP stuff)   (Business logic)   (Data access)
```

**Why?** Easier to test, reuse, and maintain.

#### 3. Shared Types
Both frontend and backend import types from `@app/shared/contracts`.

**Why?** Type safety across the entire stack.

---

## Tech Stack

| Layer | Technology | Docs |
|-------|------------|------|
| Frontend | React 18 | [react.dev](https://react.dev) |
| Routing | React Router | [reactrouter.com](https://reactrouter.com) |
| Styling | Tailwind CSS | [tailwindcss.com](https://tailwindcss.com) |
| State | TanStack Query | [tanstack.com/query](https://tanstack.com/query) |
| Backend | Express | [expressjs.com](https://expressjs.com) |
| Database | Supabase | [supabase.com/docs](https://supabase.com/docs) |
| Validation | Zod | [zod.dev](https://zod.dev) |
| Language | TypeScript | [typescriptlang.org](https://typescriptlang.org) |
| Monorepo | Turborepo | [turbo.build](https://turbo.build) |

---

## Day-by-Day Onboarding

### Day 1: Setup & Orientation

- [ ] Complete Quick Start (above)
- [ ] Read this entire document
- [ ] Meet with buddy/mentor for intro
- [ ] Explore the codebase (just browse, don't dive deep yet)

### Day 2: Codebase Tour

Use the dev-teacher skill:
```
"Give me a tour of this codebase"
```

Focus on:
- [ ] Understand the folder structure
- [ ] Trace one feature end-to-end (e.g., CV upload)
- [ ] Find where key files are located

### Day 3: First Contribution

- [ ] Find a "good-first-issue" ticket
- [ ] Set up your branch: `git checkout -b feature/your-name-issue-number`
- [ ] Make the change
- [ ] Write/update tests
- [ ] Submit PR for review

### Day 4: Deep Dive

Use the dev-teacher skill:
```
"Quiz me on [topic you want to learn]"
```

Topics to cover:
- [ ] React patterns used in this project
- [ ] How authentication works
- [ ] Database queries with Supabase
- [ ] Our testing approach

### Day 5: Independent Work

- [ ] Pick up a medium-complexity ticket
- [ ] Work on it independently
- [ ] Ask questions when stuck (it's encouraged!)
- [ ] End-of-week check-in with mentor

---

## Learning Checkpoints

By end of Week 1, you should:
- [ ] Be able to run the project locally
- [ ] Understand the high-level architecture
- [ ] Have made at least one PR
- [ ] Know where to find things in the codebase

By end of Week 2, you should:
- [ ] Understand the contracts pattern
- [ ] Be able to add a new API endpoint
- [ ] Be able to add a new React component
- [ ] Understand our testing approach

By end of Month 1, you should:
- [ ] Have completed 5+ tickets independently
- [ ] Understand most of the codebase
- [ ] Be able to review others' PRs
- [ ] Have ideas for improvements

---

## Common Tasks

### Adding a New API Endpoint

1. Define in `contracts/endpoints.ts`
2. Add types in `contracts/types.ts`
3. Add validation in `contracts/validation.ts`
4. Create route in `apps/server/src/routes/`
5. Create service in `apps/server/src/services/`
6. Write tests

### Adding a New Database Table

1. Add schema in `contracts/database.sql`
2. Create migration file
3. Add TypeScript interface in `contracts/types.ts`
4. Add RLS policies
5. Run migration

### Adding a New React Component

1. Create component in `apps/web/src/components/`
2. Import shared types from `@app/shared/contracts`
3. Use existing patterns (check similar components)
4. Add to Storybook if applicable

---

## Code Conventions

### Naming

- Files: `kebab-case.ts` for utilities, `PascalCase.tsx` for components
- Variables: `camelCase`
- Types: `PascalCase`
- Database columns: `snake_case`

### Git

- Branch names: `feature/description` or `fix/description`
- Commit messages: Present tense, descriptive ("Add CV upload validation")
- PRs: Fill out template, link to issue

### Code Style

- ESLint and Prettier are configured - just save and format
- Prefer explicit types over inference for function signatures
- Write tests for new features

---

## Getting Help

### Resources

- **This guide**: Bookmark it!
- **dev-teacher skill**: Ask "teach me about X" or "quiz me on Y"
- **ADRs**: Check `docs/decisions/` for why things are built this way
- **Slack**: `#team-channel` for questions

### People

- **Your Buddy**: [Name] - for day-to-day questions
- **Tech Lead**: [Name] - for architecture questions
- **PM**: [Name] - for product questions

### Stuck?

1. Try for 15-20 minutes on your own
2. Search existing code for similar patterns
3. Ask the dev-teacher skill
4. Ask in Slack (no question is too basic!)

---

## FAQ

**Q: How do I run just the frontend/backend?**
```bash
pnpm dev --filter web    # Just frontend
pnpm dev --filter server # Just backend
```

**Q: How do I reset the database?**
```bash
pnpm db:reset
```

**Q: Where are environment variables documented?**
Check `.env.example` - it has comments explaining each variable.

**Q: How do I see the database?**
Go to Supabase dashboard → Table Editor

**Q: What if my PR fails CI?**
Check the Actions tab for error details. Usually it's:
- Lint errors: Run `pnpm lint:fix`
- Type errors: Run `pnpm typecheck`
- Test failures: Run `pnpm test` locally

---

## Next Steps

1. Complete Day 1 tasks
2. Schedule your mentor intro meeting
3. Start exploring!

Welcome to the team! 🎉
