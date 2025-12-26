---
name: qa-engineer
description: Quality assurance and testing skill for full-stack applications. Use when writing unit tests, integration tests, E2E tests, validating browser console for errors, checking performance metrics, running accessibility audits, or comparing UI against domain benchmarks. Integrates with Chrome DevTools MCP and Playwright MCP for real browser testing. Triggers on requests like "write tests", "check for errors", "validate the UI", "run E2E tests", "compare design", "audit accessibility", or after implementation to verify quality.
---

# QA Engineer

Validate, test, and benchmark full-stack applications. This skill integrates with Chrome DevTools MCP and Playwright MCP for browser-based testing and provides domain-agnostic design benchmarking.

## Workflow Decision Tree

```
User Request
├─► "Write tests for this code"
│   └─► Test Generation Workflow → Unit/Integration/E2E
├─► "Check browser for errors"
│   └─► Browser Validation Workflow → Chrome DevTools MCP
├─► "Run E2E tests"
│   └─► E2E Execution Workflow → Playwright MCP
├─► "Check performance/accessibility"
│   └─► Audit Workflow → Lighthouse metrics via MCP
├─► "Compare UI to competitors"
│   └─► Design Benchmark Workflow → See references/benchmarks.md
├─► "Check frontend-backend integration"
│   └─► Integration Validation Workflow → See references/integration-validation.md
└─► "Validate after implementation"
    └─► Full QA Workflow → All checks in sequence
```

## MCP Integrations

### Chrome DevTools MCP

Real browser inspection and debugging.

**Configuration:**
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

**Key Tools:**
| Tool | Use Case |
|------|----------|
| `browser_navigate` | Open page for testing |
| `browser_console_messages` | Check for errors/warnings |
| `browser_network_requests` | Validate API calls |
| `browser_take_screenshot` | Visual evidence |
| `performance_start_trace` | Performance profiling |

### Playwright MCP

Automated browser testing and E2E execution.

**Configuration:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Key Tools:**
| Tool | Use Case |
|------|----------|
| `browser_navigate` | Load test pages |
| `browser_click`, `browser_type` | Simulate user actions |
| `browser_wait_for` | Wait for elements/text |
| `browser_evaluate` | Run assertions |
| `browser_take_screenshot` | Capture test evidence |

## Test Generation Workflow

### 1. Analyze Code Under Test

Identify:
- Functions/methods to test
- Dependencies to mock
- Edge cases and error paths
- Integration points

### 2. Select Test Type

| Change Type | Test Type | Coverage Target |
|-------------|-----------|-----------------|
| Utility function | Unit test | 90%+ |
| API endpoint | Integration test | 80%+ |
| Service with DB | Integration test | 80%+ |
| User flow | E2E test | Critical paths |
| UI component | Component test + E2E | Interactions |

### 3. Generate Tests

Follow patterns from `references/test-patterns.md`:
- Unit tests: Mock dependencies, test in isolation
- Integration tests: Real DB (test instance), real HTTP
- E2E tests: Full browser, user perspective

## Browser Validation Workflow

After frontend changes, validate in real browser:

### Step 1: Navigate and Capture
```
Use Chrome DevTools MCP:
1. browser_navigate → target URL
2. browser_take_screenshot → baseline
```

### Step 2: Check Console
```
Use browser_console_messages:
- Filter for "error" level
- Flag any errors as failures
- Warnings are advisory
```

### Step 3: Validate Network
```
Use browser_network_requests:
- All API calls return 2xx/3xx
- No failed resource loads
- No CORS errors
```

### Step 4: Performance Check
```
Use performance_start_trace / performance_stop_trace:
- LCP < 2.5s (good), < 4s (needs improvement)
- CLS < 0.1 (good), < 0.25 (needs improvement)
- FID < 100ms (good), < 300ms (needs improvement)
```

## E2E Test Workflow

### Step 1: Define User Flow

Example for CV Optimizer:
```
1. User lands on home page
2. Clicks "Upload CV"
3. Selects PDF file
4. Sees analysis results
5. Answers clarifying questions
6. Downloads optimized CV
```

### Step 2: Generate Playwright Test

```typescript
test('CV optimization flow', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Upload CV');
  await page.setInputFiles('input[type="file"]', 'fixtures/sample-cv.pdf');
  await expect(page.locator('.analysis-score')).toBeVisible();
  await page.fill('#target-role', 'Software Engineer');
  await page.click('text=Optimize');
  const download = await page.waitForEvent('download');
  expect(download.suggestedFilename()).toContain('optimized');
});
```

### Step 3: Execute and Report

```
Use Playwright MCP to:
1. Run the test scenario
2. Capture screenshots at key steps
3. Report pass/fail with evidence
```

## Accessibility Audit Workflow

### Automated Checks

```typescript
// Using @axe-core/playwright
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('accessibility audit', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

### Manual Verification via MCP

```
1. browser_navigate → page
2. browser_evaluate → run axe-core
3. Check for:
   - Missing alt text
   - Low contrast
   - Missing form labels
   - Keyboard navigation
```

## Design Benchmark Workflow

Compare UI against domain leaders. See `references/benchmarks.md` for:
- Domain-specific benchmark sites
- Extraction patterns
- Comparison criteria

### Process

1. **Load benchmark config** for your domain
2. **Capture competitor patterns** via Playwright MCP
3. **Extract design tokens**: colors, typography, spacing
4. **Compare** your UI against extracted patterns
5. **Report** gaps and recommendations

## Full QA Workflow

After implementation, run complete validation:

```
┌─────────────────────────────────────────┐
│ 0. Contract Validation (NEW)            │
│    Verify frontend-backend sync         │
│    See references/integration-validation│
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 1. Run Unit Tests                       │
│    npm test -- --coverage               │
│    Threshold: 80% coverage              │
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 2. Run Integration Tests                │
│    npm run test:integration             │
│    All API contracts validated          │
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 3. Browser Validation (Chrome MCP)      │
│    - Console errors: 0                  │
│    - Network failures: 0                │
│    - Performance: LCP < 2.5s            │
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 4. E2E Tests (Playwright MCP)           │
│    - Critical user flows pass           │
│    - Screenshots captured               │
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 5. Accessibility Audit                  │
│    - Zero critical violations           │
│    - Keyboard navigable                 │
└────────────────┬────────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────────┐
│ 6. Design Benchmark (optional)          │
│    - Compare to domain leaders          │
│    - Flag UX gaps                       │
└─────────────────────────────────────────┘
```

## Integration Validation Workflow (CRITICAL)

**Run this BEFORE other tests to catch frontend-backend mismatches early.**

### What It Checks

| Check | Description | Blocking? |
|-------|-------------|-----------|
| Contract files exist | `contracts/` has all required files | Yes |
| Types match database | TypeScript fields = SQL columns | Yes |
| Endpoints match routes | Frontend calls match backend routes | Yes |
| Validation in sync | Client and server use same schemas | Yes |
| RLS policies exist | All tables have security policies | Yes |

### Quick Check Command

```bash
python scripts/validate_integration.py --project-dir .
```

### Common Issues Detected

1. **Field name mismatch**: Frontend uses `userId`, backend expects `user_id`
2. **Missing endpoint**: Frontend calls `/api/cv/upload`, backend only has `/api/cv`
3. **Type mismatch**: Frontend sends `File`, backend expects `base64` string
4. **Missing RLS**: Table exists but no security policies defined
5. **Validation drift**: Client allows 20MB files, server rejects > 10MB

See `references/integration-validation.md` for full validation rules.

## Quality Gates

### Before Merge

| Check | Threshold | Blocking? |
|-------|-----------|-----------|
| Unit test pass | 100% | Yes |
| Coverage | 80%+ | Yes |
| Integration tests | 100% | Yes |
| Console errors | 0 | Yes |
| E2E critical paths | 100% | Yes |
| Accessibility critical | 0 violations | Yes |
| Performance LCP | < 4s | No (warning) |

### Severity Levels

- **Critical**: Blocks release (test failures, console errors, accessibility critical)
- **Warning**: Should fix soon (performance, accessibility minor)
- **Info**: Nice to have (design benchmark gaps)

## References

- **Integration Validation**: See `references/integration-validation.md` for contract sync checks
- **Test Patterns**: See `references/test-patterns.md` for unit/integration/E2E examples
- **Benchmarks**: See `references/benchmarks.md` for domain-specific design comparisons
- **CI Integration**: See `references/ci-integration.md` for GitHub Actions setup

## Scripts

- `scripts/run_full_qa.py`: Execute complete QA workflow
- `scripts/validate_integration.py`: Check frontend-backend contract sync
- `scripts/benchmark_capture.py`: Capture design patterns from competitor sites
