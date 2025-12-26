# Binding Contracts

Single source of truth for frontend-backend integration. These contracts prevent integration issues by ensuring both sides implement against the same specification.

## Table of Contents
1. Contract Directory Structure
2. Database Contract
3. Types Contract
4. Endpoints Contract
5. Validation Contract
6. Error Contract
7. Contract Sync Rules
8. Common Integration Issues

---

## 1. Contract Directory Structure

Every project MUST have a `contracts/` directory at the root (or in `packages/shared/`):

```
contracts/
├── database.sql          # Complete database schema
├── types.ts              # All shared TypeScript types
├── endpoints.ts          # API endpoint constants
├── validation.ts         # Zod schemas for all requests/responses
├── errors.ts             # Error codes and response shapes
└── api.yaml              # OpenAPI specification (optional but recommended)
```

### Placement in Monorepo

```
my-project/
├── apps/
│   ├── web/              # Frontend imports from contracts
│   └── server/           # Backend imports from contracts
├── packages/
│   └── shared/
│       └── src/
│           └── contracts/  # ← Lives here
└── contracts/            # Or at root, symlinked
```

---

## 2. Database Contract

### Template: `contracts/database.sql`

```sql
-- ============================================
-- DATABASE CONTRACT
-- Generated: [DATE]
-- Version: 1.0.0
-- ============================================
-- IMPORTANT: Execute this EXACTLY as written.
-- Column names MUST match types.ts field names.
-- ============================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS (extends Supabase auth.users)
-- ============================================
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ============================================
-- CVS
-- ============================================
CREATE TABLE public.cvs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  file_url TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_size_bytes INTEGER NOT NULL,
  mime_type TEXT NOT NULL DEFAULT 'application/pdf',
  target_role TEXT,
  status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'analyzing', 'analyzed', 'error')),
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ============================================
-- CV_ANALYSES
-- ============================================
CREATE TABLE public.cv_analyses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  cv_id UUID NOT NULL REFERENCES public.cvs(id) ON DELETE CASCADE,
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
  suggestions JSONB NOT NULL DEFAULT '[]',
  sections JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_cvs_user_id ON public.cvs(user_id);
CREATE INDEX idx_cvs_status ON public.cvs(status);
CREATE INDEX idx_cv_analyses_cv_id ON public.cv_analyses(cv_id);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cv_analyses ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read all, update own
CREATE POLICY "Profiles are viewable by everyone" ON public.profiles
  FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- CVs: users can CRUD own CVs only
CREATE POLICY "Users can view own CVs" ON public.cvs
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own CVs" ON public.cvs
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own CVs" ON public.cvs
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own CVs" ON public.cvs
  FOR DELETE USING (auth.uid() = user_id);

-- CV Analyses: users can view analyses for own CVs
CREATE POLICY "Users can view own CV analyses" ON public.cv_analyses
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.cvs WHERE cvs.id = cv_analyses.cv_id AND cvs.user_id = auth.uid()
    )
  );

-- ============================================
-- TRIGGERS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER cvs_updated_at BEFORE UPDATE ON public.cvs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Naming Rules

| Database | TypeScript | Rule |
|----------|------------|------|
| `user_id` | `user_id` | MUST match exactly (snake_case) |
| `file_size_bytes` | `file_size_bytes` | MUST match exactly |
| `created_at` | `created_at` | Timestamps as strings in TS |

**DO NOT** use camelCase in database if TypeScript uses snake_case or vice versa.

---

## 3. Types Contract

### Template: `contracts/types.ts`

```typescript
// ============================================
// TYPES CONTRACT
// Generated: [DATE]
// Version: 1.0.0
// ============================================
// IMPORTANT: Field names MUST match database.sql column names exactly.
// Both frontend and backend MUST import from this file.
// ============================================

// ============================================
// DATABASE ENTITIES
// ============================================

export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CV {
  id: string;
  user_id: string;
  file_url: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  target_role: string | null;
  status: CVStatus;
  created_at: string;
  updated_at: string;
}

export type CVStatus = 'uploaded' | 'analyzing' | 'analyzed' | 'error';

export interface CVAnalysis {
  id: string;
  cv_id: string;
  score: number;
  suggestions: string[];
  sections: Record<string, SectionAnalysis>;
  created_at: string;
}

export interface SectionAnalysis {
  score: number;
  feedback: string;
  improvements: string[];
}

// ============================================
// API REQUEST TYPES
// ============================================

export interface CVUploadRequest {
  file: File;
  target_role?: string;
}

export interface CVAnalyzeRequest {
  cv_id: string;
}

export interface CVOptimizeRequest {
  cv_id: string;
  answers: Record<string, string>;
}

// ============================================
// API RESPONSE TYPES
// ============================================

export interface CVUploadResponse {
  cv: CV;
}

export interface CVAnalyzeResponse {
  analysis: CVAnalysis;
}

export interface CVOptimizeResponse {
  optimized_cv: CV;
  changes: CVChange[];
}

export interface CVChange {
  section: string;
  original: string;
  optimized: string;
  reason: string;
}

// ============================================
// PAGINATION
// ============================================

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// ============================================
// API RESPONSE WRAPPER
// ============================================

export interface ApiResponse<T> {
  success: true;
  data: T;
}

export interface ApiError {
  success: false;
  error: {
    code: ErrorCode;
    message: string;
    details?: Record<string, string[]>;
  };
}

export type ApiResult<T> = ApiResponse<T> | ApiError;
```

---

## 4. Endpoints Contract

### Template: `contracts/endpoints.ts`

```typescript
// ============================================
// ENDPOINTS CONTRACT
// Generated: [DATE]
// Version: 1.0.0
// ============================================
// IMPORTANT: Frontend and backend MUST use these constants.
// Never hardcode endpoint strings.
// ============================================

export const API_VERSION = 'v1';
export const API_BASE = `/api/${API_VERSION}`;

export const ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: `${API_BASE}/auth/login`,
    LOGOUT: `${API_BASE}/auth/logout`,
    REFRESH: `${API_BASE}/auth/refresh`,
    ME: `${API_BASE}/auth/me`,
  },

  // CVs
  CV: {
    LIST: `${API_BASE}/cv`,
    GET: (id: string) => `${API_BASE}/cv/${id}`,
    UPLOAD: `${API_BASE}/cv/upload`,
    DELETE: (id: string) => `${API_BASE}/cv/${id}`,
    ANALYZE: (id: string) => `${API_BASE}/cv/${id}/analyze`,
    OPTIMIZE: (id: string) => `${API_BASE}/cv/${id}/optimize`,
    DOWNLOAD: (id: string) => `${API_BASE}/cv/${id}/download`,
  },

  // Motivation Letters
  LETTER: {
    LIST: `${API_BASE}/letters`,
    GET: (id: string) => `${API_BASE}/letters/${id}`,
    GENERATE: `${API_BASE}/letters/generate`,
    UPDATE: (id: string) => `${API_BASE}/letters/${id}`,
  },

  // Interviews
  INTERVIEW: {
    START: `${API_BASE}/interview/start`,
    GET: (id: string) => `${API_BASE}/interview/${id}`,
    ANSWER: (id: string) => `${API_BASE}/interview/${id}/answer`,
    COMPLETE: (id: string) => `${API_BASE}/interview/${id}/complete`,
  },
} as const;

// Type helper for endpoint parameters
export type EndpointWithParam = (id: string) => string;
```

---

## 5. Validation Contract

### Template: `contracts/validation.ts`

```typescript
// ============================================
// VALIDATION CONTRACT
// Generated: [DATE]
// Version: 1.0.0
// ============================================
// IMPORTANT: Use these schemas for BOTH client and server validation.
// ============================================

import { z } from 'zod';

// ============================================
// CV VALIDATION
// ============================================

export const CVUploadSchema = z.object({
  file: z.custom<File>(
    (val) => val instanceof File,
    'Must be a file'
  ).refine(
    (file) => file.size <= 10 * 1024 * 1024,
    'File must be under 10MB'
  ).refine(
    (file) => ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type),
    'File must be PDF or Word document'
  ),
  target_role: z.string().max(200).optional(),
});

export const CVAnalyzeSchema = z.object({
  cv_id: z.string().uuid(),
});

export const CVOptimizeSchema = z.object({
  cv_id: z.string().uuid(),
  answers: z.record(z.string(), z.string()),
});

// Server-side file validation (for multipart)
export const CVFileServerSchema = z.object({
  fieldname: z.literal('file'),
  originalname: z.string(),
  mimetype: z.enum(['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
  size: z.number().max(10 * 1024 * 1024),
  buffer: z.instanceof(Buffer),
});

// ============================================
// LETTER VALIDATION
// ============================================

export const LetterGenerateSchema = z.object({
  company_url: z.string().url(),
  job_title: z.string().min(1).max(200),
  cv_id: z.string().uuid().optional(),
  additional_context: z.string().max(2000).optional(),
});

// ============================================
// INTERVIEW VALIDATION
// ============================================

export const InterviewStartSchema = z.object({
  type: z.enum(['technical', 'behavioral', 'mixed']),
  role: z.string().min(1).max(200),
  difficulty: z.enum(['junior', 'mid', 'senior']).default('mid'),
});

export const InterviewAnswerSchema = z.object({
  question_id: z.string().uuid(),
  answer: z.string().min(1).max(5000),
});

// ============================================
// PAGINATION
// ============================================

export const PaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

// ============================================
// TYPE EXPORTS (inferred from schemas)
// ============================================

export type CVUploadInput = z.infer<typeof CVUploadSchema>;
export type CVAnalyzeInput = z.infer<typeof CVAnalyzeSchema>;
export type CVOptimizeInput = z.infer<typeof CVOptimizeSchema>;
export type LetterGenerateInput = z.infer<typeof LetterGenerateSchema>;
export type InterviewStartInput = z.infer<typeof InterviewStartSchema>;
export type InterviewAnswerInput = z.infer<typeof InterviewAnswerSchema>;
export type PaginationInput = z.infer<typeof PaginationSchema>;
```

---

## 6. Error Contract

### Template: `contracts/errors.ts`

```typescript
// ============================================
// ERROR CONTRACT
// Generated: [DATE]
// Version: 1.0.0
// ============================================

export const ERROR_CODES = {
  // Authentication
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',

  // Validation
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',

  // Resources
  NOT_FOUND: 'NOT_FOUND',
  CV_NOT_FOUND: 'CV_NOT_FOUND',
  ANALYSIS_NOT_FOUND: 'ANALYSIS_NOT_FOUND',

  // Operations
  ANALYSIS_IN_PROGRESS: 'ANALYSIS_IN_PROGRESS',
  ANALYSIS_FAILED: 'ANALYSIS_FAILED',
  OPTIMIZATION_FAILED: 'OPTIMIZATION_FAILED',

  // Rate limiting
  RATE_LIMITED: 'RATE_LIMITED',

  // Server
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

export const HTTP_STATUS: Record<ErrorCode, number> = {
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  TOKEN_EXPIRED: 401,
  VALIDATION_ERROR: 400,
  INVALID_FILE_TYPE: 400,
  FILE_TOO_LARGE: 400,
  NOT_FOUND: 404,
  CV_NOT_FOUND: 404,
  ANALYSIS_NOT_FOUND: 404,
  ANALYSIS_IN_PROGRESS: 409,
  ANALYSIS_FAILED: 500,
  OPTIMIZATION_FAILED: 500,
  RATE_LIMITED: 429,
  INTERNAL_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};

export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  UNAUTHORIZED: 'Authentication required',
  FORBIDDEN: 'You do not have permission to access this resource',
  TOKEN_EXPIRED: 'Your session has expired, please log in again',
  VALIDATION_ERROR: 'Invalid input data',
  INVALID_FILE_TYPE: 'File type not supported',
  FILE_TOO_LARGE: 'File exceeds maximum size limit',
  NOT_FOUND: 'Resource not found',
  CV_NOT_FOUND: 'CV not found',
  ANALYSIS_NOT_FOUND: 'Analysis not found',
  ANALYSIS_IN_PROGRESS: 'Analysis is already in progress',
  ANALYSIS_FAILED: 'Failed to analyze CV',
  OPTIMIZATION_FAILED: 'Failed to optimize CV',
  RATE_LIMITED: 'Too many requests, please try again later',
  INTERNAL_ERROR: 'An unexpected error occurred',
  SERVICE_UNAVAILABLE: 'Service temporarily unavailable',
};
```

---

## 7. Contract Sync Rules

### MUST Rules

1. **Database column names = TypeScript field names** (both snake_case)
2. **Every API endpoint has a corresponding type**
3. **Validation schemas match request types**
4. **Error codes are exhaustive**

### Sync Checklist

Before implementation, verify:

- [ ] All tables in `database.sql` have interfaces in `types.ts`
- [ ] All columns match field names exactly
- [ ] All endpoints in `endpoints.ts` have request/response types
- [ ] All request types have Zod schemas in `validation.ts`
- [ ] Error codes cover all failure scenarios

---

## 8. Common Integration Issues

### Issue: Frontend sends camelCase, backend expects snake_case

**Wrong:**
```typescript
// Frontend sends
{ userId: '123', targetRole: 'Developer' }

// Backend expects (from database)
{ user_id: '123', target_role: 'Developer' }
```

**Fix:** Use snake_case everywhere, or add transformation layer.

### Issue: Frontend uses hardcoded URLs

**Wrong:**
```typescript
fetch('/api/cv/upload')
```

**Right:**
```typescript
import { ENDPOINTS } from '@app/contracts';
fetch(ENDPOINTS.CV.UPLOAD)
```

### Issue: Different validation on client and server

**Wrong:**
```typescript
// Client: allows 20MB
// Server: rejects > 10MB
```

**Right:** Both import from `contracts/validation.ts`

### Issue: Database schema drift

**Wrong:** Developer adds column directly to Supabase without updating contracts

**Right:** Update `contracts/database.sql` first, then apply migration
