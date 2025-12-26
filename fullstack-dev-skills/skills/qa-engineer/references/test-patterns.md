# Test Patterns

Comprehensive testing patterns for full-stack applications.

## Table of Contents
1. Unit Test Patterns
2. Integration Test Patterns
3. E2E Test Patterns
4. Component Test Patterns
5. Mocking Strategies
6. Test Data Management

---

## 1. Unit Test Patterns

### Pure Function Testing

```typescript
// src/utils/cv-parser.ts
export function extractSkills(text: string): string[] {
  const skillPatterns = /skills?:?\s*([^.]+)/gi;
  const matches = text.match(skillPatterns) || [];
  return matches
    .flatMap(m => m.replace(/skills?:?\s*/i, '').split(/[,;]/))
    .map(s => s.trim())
    .filter(Boolean);
}

// tests/unit/utils/cv-parser.test.ts
import { describe, it, expect } from 'vitest';
import { extractSkills } from '../../../src/utils/cv-parser';

describe('extractSkills', () => {
  it('extracts comma-separated skills', () => {
    const text = 'Skills: JavaScript, TypeScript, React';
    expect(extractSkills(text)).toEqual(['JavaScript', 'TypeScript', 'React']);
  });

  it('handles semicolon separators', () => {
    const text = 'Skills: Python; Django; PostgreSQL';
    expect(extractSkills(text)).toEqual(['Python', 'Django', 'PostgreSQL']);
  });

  it('returns empty array when no skills found', () => {
    const text = 'No relevant information here';
    expect(extractSkills(text)).toEqual([]);
  });

  it('handles multiple skill sections', () => {
    const text = 'Technical Skills: React, Node. Soft Skills: Leadership';
    const result = extractSkills(text);
    expect(result).toContain('React');
    expect(result).toContain('Leadership');
  });
});
```

### Service Layer Testing (with Mocks)

```typescript
// src/services/cv-analyzer.ts
export class CVAnalyzerService {
  constructor(
    private claude: ClaudeClient,
    private db: SupabaseClient
  ) {}

  async analyze(cvText: string, targetRole: string) {
    const analysis = await this.claude.complete({
      prompt: `Analyze this CV for ${targetRole} role...`,
      text: cvText,
    });
    
    await this.db.from('analyses').insert({
      cv_text: cvText,
      target_role: targetRole,
      result: analysis,
    });
    
    return analysis;
  }
}

// tests/unit/services/cv-analyzer.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CVAnalyzerService } from '../../../src/services/cv-analyzer';

describe('CVAnalyzerService', () => {
  let service: CVAnalyzerService;
  let mockClaude: any;
  let mockDb: any;

  beforeEach(() => {
    mockClaude = {
      complete: vi.fn(),
    };
    mockDb = {
      from: vi.fn().mockReturnThis(),
      insert: vi.fn().mockResolvedValue({ error: null }),
    };
    service = new CVAnalyzerService(mockClaude, mockDb);
  });

  it('calls Claude with CV text and target role', async () => {
    mockClaude.complete.mockResolvedValue({ score: 85, suggestions: [] });

    await service.analyze('My CV content', 'Software Engineer');

    expect(mockClaude.complete).toHaveBeenCalledWith(
      expect.objectContaining({
        text: 'My CV content',
      })
    );
  });

  it('stores analysis result in database', async () => {
    mockClaude.complete.mockResolvedValue({ score: 85 });

    await service.analyze('CV text', 'Designer');

    expect(mockDb.from).toHaveBeenCalledWith('analyses');
    expect(mockDb.insert).toHaveBeenCalledWith(
      expect.objectContaining({
        cv_text: 'CV text',
        target_role: 'Designer',
      })
    );
  });

  it('returns Claude analysis result', async () => {
    const expectedResult = { score: 90, suggestions: ['Add metrics'] };
    mockClaude.complete.mockResolvedValue(expectedResult);

    const result = await service.analyze('CV', 'PM');

    expect(result).toEqual(expectedResult);
  });
});
```

### Error Handling Tests

```typescript
describe('CVAnalyzerService - Error Handling', () => {
  it('throws when Claude API fails', async () => {
    mockClaude.complete.mockRejectedValue(new Error('API rate limited'));

    await expect(service.analyze('CV', 'Role'))
      .rejects.toThrow('API rate limited');
  });

  it('throws when database insert fails', async () => {
    mockClaude.complete.mockResolvedValue({ score: 80 });
    mockDb.insert.mockResolvedValue({ error: { message: 'DB error' } });

    await expect(service.analyze('CV', 'Role'))
      .rejects.toThrow('DB error');
  });
});
```

---

## 2. Integration Test Patterns

### API Endpoint Testing

```typescript
// tests/integration/api/cv.test.ts
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import request from 'supertest';
import { app } from '../../../src/app';
import { testDb, createTestUser, cleanupTestData } from '../../helpers';

describe('CV API', () => {
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

  describe('POST /api/cv/analyze', () => {
    it('analyzes CV and returns score', async () => {
      const response = await request(app)
        .post('/api/cv/analyze')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          cvText: 'Experienced software engineer with 5 years...',
          targetRole: 'Senior Developer',
        });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('score');
      expect(response.body).toHaveProperty('suggestions');
      expect(typeof response.body.score).toBe('number');
    });

    it('returns 400 for missing cvText', async () => {
      const response = await request(app)
        .post('/api/cv/analyze')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ targetRole: 'Developer' });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('cvText');
    });

    it('returns 401 without authentication', async () => {
      const response = await request(app)
        .post('/api/cv/analyze')
        .send({ cvText: 'CV', targetRole: 'Role' });

      expect(response.status).toBe(401);
    });
  });

  describe('POST /api/cv/optimize', () => {
    it('returns optimized CV with changes tracked', async () => {
      // First create an analysis
      const analysisRes = await request(app)
        .post('/api/cv/analyze')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ cvText: 'Original CV', targetRole: 'Developer' });

      const response = await request(app)
        .post('/api/cv/optimize')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          analysisId: analysisRes.body.id,
          answers: { experience: 'Added 2 more projects' },
        });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('optimizedCv');
      expect(response.body).toHaveProperty('changes');
    });
  });
});
```

### Database Integration Testing

```typescript
// tests/integration/db/cv-repository.test.ts
import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { CVRepository } from '../../../src/repositories/cv';
import { testDb } from '../../helpers';

describe('CVRepository', () => {
  let repo: CVRepository;
  let testUserId: string;

  beforeAll(async () => {
    repo = new CVRepository(testDb);
    // Create test user
    const { data } = await testDb.auth.admin.createUser({
      email: 'cvtest@example.com',
      password: 'password123',
      email_confirm: true,
    });
    testUserId = data.user!.id;
  });

  afterEach(async () => {
    // Clean up CVs after each test
    await testDb.from('cvs').delete().eq('user_id', testUserId);
  });

  it('saves CV and retrieves by ID', async () => {
    const cv = await repo.save({
      userId: testUserId,
      originalText: 'My CV content',
      targetRole: 'Engineer',
    });

    const retrieved = await repo.findById(cv.id);

    expect(retrieved).not.toBeNull();
    expect(retrieved!.originalText).toBe('My CV content');
  });

  it('lists all CVs for a user', async () => {
    await repo.save({ userId: testUserId, originalText: 'CV 1', targetRole: 'Role 1' });
    await repo.save({ userId: testUserId, originalText: 'CV 2', targetRole: 'Role 2' });

    const cvs = await repo.findByUserId(testUserId);

    expect(cvs).toHaveLength(2);
  });

  it('enforces RLS - users cannot see others CVs', async () => {
    // Create CV as test user
    const cv = await repo.save({
      userId: testUserId,
      originalText: 'Private CV',
      targetRole: 'Secret Role',
    });

    // Try to access with different user context
    const otherUserClient = createClientWithUser('other@example.com');
    const otherRepo = new CVRepository(otherUserClient);

    const result = await otherRepo.findById(cv.id);

    expect(result).toBeNull();
  });
});
```

---

## 3. E2E Test Patterns

### User Flow Testing

```typescript
// tests/e2e/cv-optimizer.spec.ts
import { test, expect } from '@playwright/test';

test.describe('CV Optimizer Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('complete CV optimization flow', async ({ page }) => {
    // Step 1: Navigate to CV optimizer
    await page.click('text=Optimize CV');
    await expect(page).toHaveURL('/cv/optimize');

    // Step 2: Upload CV
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/sample-cv.pdf');

    // Step 3: Wait for analysis
    await expect(page.locator('.analysis-loading')).toBeVisible();
    await expect(page.locator('.analysis-score')).toBeVisible({ timeout: 30000 });

    // Step 4: Check score is displayed
    const score = await page.locator('.analysis-score').textContent();
    expect(parseInt(score!)).toBeGreaterThan(0);

    // Step 5: Answer clarifying questions
    await page.fill('[name="experience-detail"]', 'Led team of 5 engineers');
    await page.fill('[name="achievements"]', 'Reduced load time by 50%');
    await page.click('text=Generate Optimized CV');

    // Step 6: Wait for optimization
    await expect(page.locator('.optimized-preview')).toBeVisible({ timeout: 30000 });

    // Step 7: Download
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('text=Download CV'),
    ]);
    expect(download.suggestedFilename()).toMatch(/optimized.*\.pdf/);
  });

  test('shows validation errors for empty upload', async ({ page }) => {
    await page.click('text=Optimize CV');
    await page.click('text=Analyze');

    await expect(page.locator('.error-message')).toContainText('Please upload a CV');
  });
});
```

### Multi-Page Flow Testing

```typescript
// tests/e2e/interview-prep.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Mock Interview Flow', () => {
  test('complete interview session', async ({ page }) => {
    await page.goto('/interview/start');

    // Select interview type
    await page.click('text=Technical Interview');
    await page.selectOption('[name="role"]', 'frontend-engineer');
    await page.click('text=Start Interview');

    // Answer 3 questions
    for (let i = 0; i < 3; i++) {
      await expect(page.locator('.question-text')).toBeVisible();
      
      const questionText = await page.locator('.question-text').textContent();
      expect(questionText).toBeTruthy();

      await page.fill('[name="answer"]', `My answer to question ${i + 1}...`);
      await page.click('text=Submit Answer');

      // Wait for feedback
      await expect(page.locator('.feedback-card')).toBeVisible({ timeout: 20000 });
      
      if (i < 2) {
        await page.click('text=Next Question');
      }
    }

    // Complete interview
    await page.click('text=Finish Interview');
    await expect(page.locator('.interview-summary')).toBeVisible();
    await expect(page.locator('.overall-score')).toBeVisible();
  });
});
```

---

## 4. Component Test Patterns

### React Component Testing

```typescript
// tests/components/ScoreCard.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScoreCard } from '../../src/components/ScoreCard';

describe('ScoreCard', () => {
  it('displays score with correct color for high scores', () => {
    render(<ScoreCard score={90} maxScore={100} />);

    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByTestId('score-indicator')).toHaveClass('text-green-500');
  });

  it('displays warning color for medium scores', () => {
    render(<ScoreCard score={65} maxScore={100} />);

    expect(screen.getByTestId('score-indicator')).toHaveClass('text-yellow-500');
  });

  it('displays error color for low scores', () => {
    render(<ScoreCard score={40} maxScore={100} />);

    expect(screen.getByTestId('score-indicator')).toHaveClass('text-red-500');
  });

  it('shows suggestions when provided', () => {
    const suggestions = ['Add more metrics', 'Include keywords'];
    render(<ScoreCard score={70} suggestions={suggestions} />);

    expect(screen.getByText('Add more metrics')).toBeInTheDocument();
    expect(screen.getByText('Include keywords')).toBeInTheDocument();
  });
});
```

### Hook Testing

```typescript
// tests/hooks/useAnalysis.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useAnalysis } from '../../src/hooks/useAnalysis';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const wrapper = ({ children }) => (
  <QueryClientProvider client={new QueryClient()}>
    {children}
  </QueryClientProvider>
);

describe('useAnalysis', () => {
  it('fetches analysis on mount', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve({ score: 85, suggestions: [] }),
    });
    global.fetch = mockFetch;

    const { result } = renderHook(() => useAnalysis('cv-123'), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data.score).toBe(85);
  });
});
```

---

## 5. Mocking Strategies

### Claude API Mock

```typescript
// tests/mocks/claude.ts
import { vi } from 'vitest';

export const createMockClaude = () => ({
  complete: vi.fn().mockImplementation(async ({ prompt }) => {
    // Return deterministic responses based on prompt content
    if (prompt.includes('analyze')) {
      return {
        score: 75,
        suggestions: ['Add quantifiable achievements', 'Include relevant keywords'],
        sections: { experience: 'good', skills: 'needs improvement' },
      };
    }
    if (prompt.includes('optimize')) {
      return {
        optimizedText: 'Improved CV content...',
        changes: [{ type: 'addition', text: 'Added metrics' }],
      };
    }
    return { response: 'Default mock response' };
  }),
});
```

### Supabase Mock

```typescript
// tests/mocks/supabase.ts
import { vi } from 'vitest';

export const createMockSupabase = (initialData = {}) => {
  const store = { ...initialData };

  return {
    from: vi.fn((table) => ({
      select: vi.fn().mockReturnThis(),
      insert: vi.fn((data) => {
        store[table] = store[table] || [];
        const newRecord = { id: crypto.randomUUID(), ...data, created_at: new Date() };
        store[table].push(newRecord);
        return { data: newRecord, error: null };
      }),
      update: vi.fn().mockReturnThis(),
      delete: vi.fn().mockReturnThis(),
      eq: vi.fn().mockReturnThis(),
      single: vi.fn(() => ({
        data: store[table]?.[0] || null,
        error: null,
      })),
    })),
    auth: {
      getUser: vi.fn().mockResolvedValue({
        data: { user: { id: 'mock-user-id', email: 'test@example.com' } },
        error: null,
      }),
    },
  };
};
```

---

## 6. Test Data Management

### Fixtures

```typescript
// tests/fixtures/cvs.ts
export const sampleCVs = {
  juniorDeveloper: {
    text: `John Doe
    Junior Software Developer
    Skills: JavaScript, React, Node.js
    Experience: 1 year internship at TechCorp`,
    expectedScore: { min: 50, max: 70 },
  },
  seniorEngineer: {
    text: `Jane Smith
    Senior Software Engineer | 8 years experience
    Led team of 10 engineers, reduced system latency by 40%
    Skills: Python, Go, Kubernetes, AWS`,
    expectedScore: { min: 80, max: 95 },
  },
  careerChanger: {
    text: `Bob Johnson
    Former Teacher transitioning to Tech
    Completed bootcamp, built 3 projects`,
    expectedScore: { min: 40, max: 60 },
  },
};
```

### Factory Pattern

```typescript
// tests/factories/user.ts
import { faker } from '@faker-js/faker';

export const userFactory = {
  build: (overrides = {}) => ({
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    createdAt: faker.date.past(),
    ...overrides,
  }),

  buildList: (count: number, overrides = {}) =>
    Array.from({ length: count }, () => userFactory.build(overrides)),
};

// tests/factories/cv.ts
export const cvFactory = {
  build: (overrides = {}) => ({
    id: faker.string.uuid(),
    userId: faker.string.uuid(),
    originalText: faker.lorem.paragraphs(3),
    targetRole: faker.person.jobTitle(),
    score: faker.number.int({ min: 40, max: 95 }),
    createdAt: faker.date.past(),
    ...overrides,
  }),
};
```
