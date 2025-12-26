# Integration Validation

Detect frontend-backend mismatches before they become runtime errors.

## Table of Contents
1. Overview
2. Validation Checks
3. Contract File Requirements
4. Common Mismatches
5. Automated Validation
6. Manual Review Checklist

---

## 1. Overview

Integration issues occur when frontend and backend are developed separately without a shared contract. This validation catches:

- Field name mismatches (camelCase vs snake_case)
- Missing or extra API endpoints
- Type mismatches (string vs number)
- Validation rule drift
- Missing database security policies

### When to Run

- **Before PR merge**: Catch issues before they hit main branch
- **After architecture changes**: When contracts are updated
- **Before deployment**: Final sync check
- **When debugging 400/500 errors**: Often caused by contract drift

---

## 2. Validation Checks

### Check 1: Contract Files Exist

```
contracts/
├── database.sql      ✓ Required
├── types.ts          ✓ Required
├── endpoints.ts      ✓ Required
├── validation.ts     ✓ Required
└── errors.ts         ✓ Required
```

**Failure**: Any missing file blocks deployment.

### Check 2: Database-TypeScript Sync

Every column in `database.sql` must have a matching field in `types.ts`.

**database.sql:**
```sql
CREATE TABLE cvs (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  file_url TEXT NOT NULL,
  original_filename TEXT NOT NULL
);
```

**types.ts (CORRECT):**
```typescript
interface CV {
  id: string;
  user_id: string;      // ✓ Matches column name
  file_url: string;     // ✓ Matches column name
  original_filename: string;
}
```

**types.ts (WRONG):**
```typescript
interface CV {
  id: string;
  userId: string;       // ✗ Should be user_id
  fileUrl: string;      // ✗ Should be file_url
  originalFilename: string; // ✗ Should be original_filename
}
```

### Check 3: Frontend API Calls Match Backend Routes

Extract all `fetch()` and axios calls from frontend, compare to backend routes.

**Frontend code:**
```typescript
// Check these calls exist in backend
fetch('/api/v1/cv/upload', { method: 'POST' })
fetch('/api/v1/cv/${id}/analyze', { method: 'POST' })
fetch('/api/v1/cv', { method: 'GET' })
```

**Backend routes (express):**
```typescript
router.post('/api/v1/cv/upload', ...)     // ✓ Matches
router.post('/api/v1/cv/:id/analyze', ...) // ✓ Matches
router.get('/api/v1/cv', ...)              // ✓ Matches
```

**Common issues:**
- Frontend calls `/api/cv/upload`, backend has `/api/v1/cv/upload`
- Frontend uses `POST`, backend expects `PUT`
- Frontend sends to `/cv/:id`, backend has `/cvs/:id` (plural)

### Check 4: Request/Response Type Alignment

**Frontend expects:**
```typescript
interface CVUploadResponse {
  cv: {
    id: string;
    file_url: string;
  };
  message: string;
}
```

**Backend sends:**
```typescript
// WRONG - missing 'message' field
res.json({ cv: { id, file_url } });

// CORRECT
res.json({ cv: { id, file_url }, message: 'Upload successful' });
```

### Check 5: Validation Schema Sync

Client and server must use identical validation rules.

**Shared schema (contracts/validation.ts):**
```typescript
export const CVUploadSchema = z.object({
  file: z.custom<File>().refine(f => f.size <= 10 * 1024 * 1024),
  target_role: z.string().max(200).optional(),
});
```

**Frontend (CORRECT):**
```typescript
import { CVUploadSchema } from '@app/contracts';
const result = CVUploadSchema.safeParse(formData);
```

**Backend (CORRECT):**
```typescript
import { CVUploadSchema } from '@app/contracts';
app.post('/upload', validate(CVUploadSchema), handler);
```

**WRONG - different limits:**
```typescript
// Frontend allows 20MB
const MAX_SIZE = 20 * 1024 * 1024;

// Backend rejects > 10MB
const MAX_SIZE = 10 * 1024 * 1024;
```

### Check 6: RLS Policies Exist

Every table with user data must have Row Level Security.

```sql
-- Check all tables have RLS enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- Verify policies exist
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';
```

**Required policies per table:**
- SELECT policy (who can read)
- INSERT policy (who can create)
- UPDATE policy (who can modify)
- DELETE policy (who can remove)

---

## 3. Contract File Requirements

### database.sql

Must contain:
- [ ] All CREATE TABLE statements
- [ ] Column names in snake_case
- [ ] Foreign key constraints
- [ ] Indexes for foreign keys
- [ ] RLS ENABLE statements
- [ ] RLS policies for all operations
- [ ] Triggers for updated_at

### types.ts

Must contain:
- [ ] Interface for every database table
- [ ] Field names matching column names exactly
- [ ] Request types for all endpoints
- [ ] Response types for all endpoints
- [ ] Error type matching errors.ts

### endpoints.ts

Must contain:
- [ ] All API endpoints as constants
- [ ] Parameterized endpoints as functions
- [ ] Consistent versioning (e.g., /api/v1/)
- [ ] No hardcoded strings elsewhere in code

### validation.ts

Must contain:
- [ ] Zod schema for every request type
- [ ] Matching constraints (lengths, formats)
- [ ] File size limits matching server config
- [ ] Exported type aliases from schemas

### errors.ts

Must contain:
- [ ] All error codes used in backend
- [ ] HTTP status mapping
- [ ] User-friendly messages

---

## 4. Common Mismatches

### Mismatch 1: Case Convention

| Layer | Convention | Example |
|-------|------------|---------|
| Database | snake_case | `user_id` |
| TypeScript | snake_case (to match DB) | `user_id` |
| JSON API | snake_case | `{ "user_id": "..." }` |

**DO NOT MIX**: If frontend expects `userId` but backend sends `user_id`, JSON parsing works but TypeScript types lie.

### Mismatch 2: Null vs Undefined

```typescript
// Database: NULL
// TypeScript: null (not undefined)

interface CV {
  target_role: string | null;  // ✓ Correct
  target_role?: string;        // ✗ Wrong - undefined ≠ null
}
```

### Mismatch 3: Date Handling

```typescript
// Database: TIMESTAMPTZ
// JSON: ISO string
// TypeScript: string (not Date)

interface CV {
  created_at: string;  // ✓ Correct - JSON has string
  created_at: Date;    // ✗ Wrong - JSON.parse won't create Date
}
```

### Mismatch 4: File Upload

```typescript
// Frontend sends: FormData with File
// Backend receives: multipart/form-data

// Frontend
const formData = new FormData();
formData.append('file', file);
fetch('/upload', { method: 'POST', body: formData });

// Backend (Express + multer)
upload.single('file')  // Field name must match 'file'
```

### Mismatch 5: Array vs Object

```typescript
// Frontend expects array
interface Response {
  data: CV[];
}

// Backend sends object with array inside
// WRONG
res.json({ cvs: [...] });

// CORRECT
res.json({ data: [...] });
```

---

## 5. Automated Validation

### Run Validation Script

```bash
python scripts/validate_integration.py --project-dir /path/to/project
```

### What It Checks

1. **Contract directory exists** with all required files
2. **Parses database.sql** to extract tables and columns
3. **Parses types.ts** to extract interfaces and fields
4. **Compares** database columns to TypeScript fields
5. **Scans frontend** for API calls
6. **Scans backend** for route definitions
7. **Reports** all mismatches

### Sample Output

```
🔍 Integration Validation Report

✓ Contract files: All present
✓ Database tables: 5 found
✓ TypeScript interfaces: 5 found

⚠ Mismatches Found:

1. Field name mismatch in 'cvs' table:
   - Database: user_id
   - TypeScript CV interface: userId
   
2. Missing endpoint in backend:
   - Frontend calls: POST /api/v1/cv/optimize
   - Backend routes: Not found

3. Type mismatch:
   - Database cvs.file_size_bytes: INTEGER
   - TypeScript CV.file_size_bytes: string (should be number)

❌ 3 issues found. Fix before deployment.
```

---

## 6. Manual Review Checklist

Before each release, verify:

### Database ↔ Types
- [ ] Every table has corresponding interface
- [ ] Column names match field names exactly
- [ ] Types are compatible (UUID→string, INTEGER→number)
- [ ] Nullable columns have `| null` in TypeScript

### Frontend ↔ Backend
- [ ] All fetch/axios URLs exist in backend routes
- [ ] HTTP methods match (GET/POST/PUT/DELETE)
- [ ] Request body shape matches backend expectation
- [ ] Response shape matches frontend type

### Validation
- [ ] File size limits match
- [ ] String length limits match
- [ ] Required fields match
- [ ] Enum values match

### Security
- [ ] RLS enabled on all user-data tables
- [ ] Policies exist for SELECT, INSERT, UPDATE, DELETE
- [ ] Service role only used server-side
- [ ] Anon key never exposes sensitive data

---

## Quick Fix Patterns

### Fix Case Mismatch

Option 1: Use snake_case everywhere (recommended)
```typescript
interface CV {
  user_id: string;  // Match database
}
```

Option 2: Transform at API boundary
```typescript
// Backend transforms before sending
const response = {
  userId: row.user_id,  // Transform here only
};
```

### Fix Missing Endpoint

1. Check if endpoint exists with different path
2. Add route to backend if genuinely missing
3. Update `contracts/endpoints.ts`
4. Regenerate types if needed

### Fix Validation Drift

1. Update `contracts/validation.ts` with correct rules
2. Ensure both frontend and backend import from contracts
3. Remove any local validation overrides
