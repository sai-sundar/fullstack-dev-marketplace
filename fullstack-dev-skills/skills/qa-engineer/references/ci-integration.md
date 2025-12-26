# CI Integration

Automated testing pipelines for continuous integration.

## Table of Contents
1. GitHub Actions Setup
2. Test Stages
3. Quality Gates
4. Reporting
5. Parallelization

---

## 1. GitHub Actions Setup

### Complete Workflow

```yaml
# .github/workflows/qa.yml
name: QA Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}

jobs:
  # Stage 1: Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v3
        with:
          version: 8
          
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          
      - run: pnpm install
      
      - name: Run Unit Tests
        run: pnpm test:unit --coverage
        
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
          fail_ci_if_error: true
          
      - name: Check Coverage Threshold
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 80% threshold"
            exit 1
          fi

  # Stage 2: Integration Tests
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: supabase/postgres:15.1.0.117
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v3
        with:
          version: 8
          
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          
      - run: pnpm install
      
      - name: Run Migrations
        run: pnpm db:migrate
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
          
      - name: Run Integration Tests
        run: pnpm test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres

  # Stage 3: E2E Tests
  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v3
        with:
          version: 8
          
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          
      - run: pnpm install
      
      - name: Install Playwright Browsers
        run: pnpm exec playwright install --with-deps chromium
        
      - name: Build Application
        run: pnpm build
        
      - name: Start Application
        run: |
          pnpm preview &
          sleep 5
          
      - name: Run E2E Tests
        run: pnpm test:e2e
        
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7

  # Stage 4: Accessibility Audit
  accessibility:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v3
        with:
          version: 8
          
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          
      - run: pnpm install
      - run: pnpm build
      
      - name: Start Application
        run: |
          pnpm preview &
          sleep 5
          
      - name: Run Accessibility Tests
        run: pnpm test:a11y
        
      - name: Upload A11y Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: a11y-report/

  # Stage 5: Performance Audit
  performance:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v3
        with:
          version: 8
          
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          
      - run: pnpm install
      - run: pnpm build
      
      - name: Start Application
        run: |
          pnpm preview &
          sleep 5
          
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

  # Final Gate
  qa-gate:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests, accessibility, performance]
    steps:
      - name: QA Gate Passed
        run: echo "All quality gates passed!"
```

---

## 2. Test Stages

### Stage Order

```
┌─────────────────┐
│   Unit Tests    │  Fast, isolated, run first
│   (~30 seconds) │
└────────┬────────┘
         │
┌────────▼────────┐
│  Integration    │  Database, API contracts
│   (~2 minutes)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌───▼───┐
│  E2E  │ │ A11y  │  Can run in parallel
│(~5min)│ │(~2min)│
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│   Performance   │  Lighthouse audits
│   (~3 minutes)  │
└────────┬────────┘
         │
┌────────▼────────┐
│    QA Gate      │  Final approval
└─────────────────┘
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:e2e": "playwright test",
    "test:a11y": "playwright test tests/a11y",
    "test:coverage": "vitest run --coverage",
    "test:ci": "vitest run --reporter=junit --outputFile=test-results.xml"
  }
}
```

---

## 3. Quality Gates

### Thresholds Configuration

```javascript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
});
```

### Lighthouse Configuration

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:4173/', 'http://localhost:4173/cv/optimize'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.8 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### Gate Summary

| Gate | Threshold | Blocking |
|------|-----------|----------|
| Unit Test Pass Rate | 100% | Yes |
| Code Coverage | 80%+ | Yes |
| Integration Test Pass | 100% | Yes |
| E2E Critical Paths | 100% | Yes |
| Accessibility Score | 90+ | Yes |
| Performance Score | 80+ | No (warning) |
| LCP | < 2.5s | No (warning) |
| CLS | < 0.1 | No (warning) |

---

## 4. Reporting

### JUnit Reports (for CI)

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    reporters: ['default', 'junit'],
    outputFile: {
      junit: './test-results/junit.xml',
    },
  },
});
```

### Playwright Reports

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'test-results/e2e-junit.xml' }],
  ],
});
```

### PR Comments

```yaml
# Add to workflow
- name: Comment PR with Results
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const coverage = JSON.parse(fs.readFileSync('coverage/coverage-summary.json'));
      const lines = coverage.total.lines.pct;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `## QA Report
        
        | Metric | Value |
        |--------|-------|
        | Coverage | ${lines}% |
        | Unit Tests | ✅ Passed |
        | Integration | ✅ Passed |
        | E2E | ✅ Passed |
        `
      });
```

---

## 5. Parallelization

### Parallel Test Execution

```yaml
# Split E2E tests across multiple runners
e2e-tests:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - uses: actions/checkout@v4
    # ... setup steps ...
    
    - name: Run E2E Tests (Shard ${{ matrix.shard }})
      run: pnpm test:e2e --shard=${{ matrix.shard }}/${{ strategy.job-total }}
```

### Playwright Sharding

```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 2 : undefined,
  fullyParallel: true,
  // Shard configuration comes from CLI
});
```

### Caching

```yaml
# Cache node_modules and Playwright browsers
- uses: actions/cache@v4
  with:
    path: |
      ~/.pnpm-store
      ~/.cache/ms-playwright
    key: ${{ runner.os }}-deps-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

---

## Quick Start

### Minimal Setup

1. Copy the workflow file to `.github/workflows/qa.yml`
2. Add secrets in GitHub repository settings:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
3. Ensure package.json has required test scripts
4. Push to trigger pipeline

### Local Verification

```bash
# Run the same checks locally before pushing
pnpm test:unit --coverage
pnpm test:integration
pnpm build && pnpm preview &
pnpm test:e2e
```
