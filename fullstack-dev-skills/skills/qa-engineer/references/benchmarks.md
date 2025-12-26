# Design Benchmarks

Domain-specific design benchmarking against industry leaders. Extensible structure for any application domain.

## Table of Contents
1. Benchmark Framework
2. Domain Configurations
3. Extraction Patterns
4. Comparison Criteria
5. Using Benchmarks

---

## 1. Benchmark Framework

### Structure

Each domain has a configuration defining:
- **Reference sites**: Industry leaders to benchmark against
- **Pages to analyze**: Key page types (home, list, detail, form)
- **Extraction targets**: What to capture (colors, typography, spacing, components)
- **Comparison weights**: Importance of each criterion

### Adding a New Domain

```yaml
# benchmarks/[domain-name].yaml
domain: domain-name
description: Brief description of the domain
reference_sites:
  - name: Site Name
    url: https://example.com
    why: Why this site is a benchmark
pages:
  - type: page-type
    path: /path
    extract:
      - colors
      - typography
      - spacing
extraction_focus:
  - specific elements to focus on
comparison_criteria:
  - criterion: name
    weight: 1-10
```

---

## 2. Domain Configurations

### Recruitment / Job Search

```yaml
domain: recruitment
description: Job search and career preparation platforms
reference_sites:
  - name: LinkedIn Jobs
    url: https://linkedin.com/jobs
    why: Industry standard, clean professional design
  - name: Indeed
    url: https://indeed.com
    why: High usability, clear job cards
  - name: Glassdoor
    url: https://glassdoor.com
    why: Rich information density, reviews integration
  - name: Handshake
    url: https://joinhandshake.com
    why: Student/graduate focused, modern design
  - name: Wellfound (AngelList)
    url: https://wellfound.com
    why: Startup-focused, modern aesthetics

pages:
  - type: home
    path: /
    extract: [hero, value_proposition, cta_buttons]
  - type: search_results
    path: /jobs
    extract: [job_cards, filters, pagination]
  - type: job_detail
    path: /jobs/[id]
    extract: [job_header, apply_button, company_info]
  - type: profile
    path: /profile
    extract: [resume_display, edit_forms, progress_indicators]
  - type: application_form
    path: /apply
    extract: [form_layout, file_upload, progress_steps]

extraction_focus:
  - Job card layout (title, company, location, salary)
  - Application flow (steps, progress indication)
  - Profile completeness indicators
  - Search and filter patterns
  - Mobile responsiveness

comparison_criteria:
  - criterion: Information Hierarchy
    weight: 9
    description: Clear visual hierarchy for job details
  - criterion: Form Usability
    weight: 9
    description: Easy-to-complete application forms
  - criterion: Trust Signals
    weight: 8
    description: Company logos, verification badges
  - criterion: Progress Feedback
    weight: 8
    description: Clear indication of application status
  - criterion: Mobile Experience
    weight: 7
    description: Fully functional on mobile devices
  - criterion: Load Performance
    weight: 7
    description: Fast initial load and interactions
```

### E-Commerce

```yaml
domain: ecommerce
description: Online shopping and retail platforms
reference_sites:
  - name: Shopify Themes
    url: https://themes.shopify.com
    why: Best-in-class e-commerce patterns
  - name: Amazon
    url: https://amazon.com
    why: Conversion-optimized, extensive A/B testing
  - name: Stripe Checkout
    url: https://stripe.com/payments/checkout
    why: Seamless payment experience

pages:
  - type: product_listing
    path: /products
    extract: [product_cards, filters, sort_options]
  - type: product_detail
    path: /products/[id]
    extract: [gallery, price, add_to_cart, reviews]
  - type: cart
    path: /cart
    extract: [line_items, totals, checkout_cta]
  - type: checkout
    path: /checkout
    extract: [form_steps, payment_methods, trust_badges]

extraction_focus:
  - Product card design (image, price, rating)
  - Add to cart interactions
  - Checkout flow steps
  - Trust and security indicators

comparison_criteria:
  - criterion: Product Presentation
    weight: 9
  - criterion: Checkout Friction
    weight: 10
  - criterion: Trust Signals
    weight: 9
  - criterion: Mobile Shopping
    weight: 8
```

### SaaS Dashboard

```yaml
domain: saas-dashboard
description: Software-as-a-service application dashboards
reference_sites:
  - name: Linear
    url: https://linear.app
    why: Clean, fast, keyboard-first design
  - name: Notion
    url: https://notion.so
    why: Flexible, intuitive interface
  - name: Figma
    url: https://figma.com
    why: Professional creative tool UX
  - name: Vercel Dashboard
    url: https://vercel.com/dashboard
    why: Developer-focused, clear status indicators

pages:
  - type: dashboard
    path: /dashboard
    extract: [metrics_cards, navigation, quick_actions]
  - type: list_view
    path: /[resource]
    extract: [table_or_cards, filters, bulk_actions]
  - type: detail_view
    path: /[resource]/[id]
    extract: [header, tabs, action_buttons]
  - type: settings
    path: /settings
    extract: [sections, form_groups, save_patterns]

extraction_focus:
  - Navigation patterns (sidebar, breadcrumbs)
  - Data density and readability
  - Action discoverability
  - Keyboard shortcuts
  - Loading and empty states

comparison_criteria:
  - criterion: Information Density
    weight: 8
  - criterion: Navigation Clarity
    weight: 9
  - criterion: Action Accessibility
    weight: 8
  - criterion: Performance Feel
    weight: 9
```

### Content / Blog

```yaml
domain: content
description: Content publishing and blog platforms
reference_sites:
  - name: Medium
    url: https://medium.com
    why: Reading experience optimized
  - name: Substack
    url: https://substack.com
    why: Clean, focused on content
  - name: The Verge
    url: https://theverge.com
    why: Modern editorial design

pages:
  - type: home
    path: /
    extract: [featured_content, content_grid, navigation]
  - type: article
    path: /[slug]
    extract: [typography, reading_progress, sharing]
  - type: author
    path: /author/[id]
    extract: [bio, article_list, follow_cta]

extraction_focus:
  - Typography and readability
  - Content width and line length
  - Image handling
  - Reading progress indicators

comparison_criteria:
  - criterion: Readability
    weight: 10
  - criterion: Typography
    weight: 9
  - criterion: Content Focus
    weight: 8
  - criterion: Performance
    weight: 7
```

---

## 3. Extraction Patterns

### Color Extraction

```typescript
// Extract dominant colors from a page
async function extractColors(page: Page): Promise<ColorPalette> {
  return await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const colors = new Map<string, number>();

    elements.forEach(el => {
      const style = getComputedStyle(el);
      const bg = style.backgroundColor;
      const text = style.color;
      
      if (bg && bg !== 'rgba(0, 0, 0, 0)') {
        colors.set(bg, (colors.get(bg) || 0) + 1);
      }
      if (text) {
        colors.set(text, (colors.get(text) || 0) + 1);
      }
    });

    // Sort by frequency and return top colors
    return Array.from(colors.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([color]) => color);
  });
}
```

### Typography Extraction

```typescript
// Extract typography patterns
async function extractTypography(page: Page): Promise<TypographySystem> {
  return await page.evaluate(() => {
    const headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
    const typography: Record<string, any> = {};

    headings.forEach(tag => {
      const el = document.querySelector(tag);
      if (el) {
        const style = getComputedStyle(el);
        typography[tag] = {
          fontFamily: style.fontFamily,
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
          lineHeight: style.lineHeight,
          letterSpacing: style.letterSpacing,
        };
      }
    });

    // Body text
    const body = document.querySelector('p');
    if (body) {
      const style = getComputedStyle(body);
      typography.body = {
        fontFamily: style.fontFamily,
        fontSize: style.fontSize,
        lineHeight: style.lineHeight,
      };
    }

    return typography;
  });
}
```

### Spacing Extraction

```typescript
// Extract spacing patterns
async function extractSpacing(page: Page): Promise<SpacingSystem> {
  return await page.evaluate(() => {
    const spacings = new Set<number>();
    const elements = document.querySelectorAll('*');

    elements.forEach(el => {
      const style = getComputedStyle(el);
      ['margin', 'padding'].forEach(prop => {
        ['Top', 'Right', 'Bottom', 'Left'].forEach(dir => {
          const value = parseInt(style[`${prop}${dir}` as any]);
          if (value > 0) spacings.add(value);
        });
      });
    });

    return Array.from(spacings).sort((a, b) => a - b);
  });
}
```

### Component Pattern Extraction

```typescript
// Extract component patterns (e.g., job cards)
async function extractComponentPattern(
  page: Page, 
  selector: string
): Promise<ComponentPattern> {
  return await page.evaluate((sel) => {
    const component = document.querySelector(sel);
    if (!component) return null;

    const rect = component.getBoundingClientRect();
    const style = getComputedStyle(component);

    return {
      dimensions: {
        width: rect.width,
        height: rect.height,
      },
      styling: {
        background: style.backgroundColor,
        border: style.border,
        borderRadius: style.borderRadius,
        boxShadow: style.boxShadow,
      },
      children: Array.from(component.children).map(child => ({
        tag: child.tagName.toLowerCase(),
        classes: Array.from(child.classList),
      })),
    };
  }, selector);
}
```

---

## 4. Comparison Criteria

### Scoring Rubric

| Score | Description |
|-------|-------------|
| 1-2 | Significantly below benchmark |
| 3-4 | Below benchmark, needs improvement |
| 5-6 | Meets basic expectations |
| 7-8 | Good, matches benchmarks |
| 9-10 | Excellent, exceeds benchmarks |

### Automated Checks

```typescript
interface ComparisonResult {
  criterion: string;
  score: number;
  benchmark: string;
  yourValue: string;
  recommendation: string;
}

function compareTypography(
  yours: TypographySystem,
  benchmark: TypographySystem
): ComparisonResult {
  // Check if body font size is readable
  const yourBodySize = parseInt(yours.body?.fontSize || '14');
  const benchmarkSize = parseInt(benchmark.body?.fontSize || '16');

  let score = 5;
  let recommendation = '';

  if (yourBodySize < 14) {
    score = 3;
    recommendation = 'Increase body font size to at least 16px for readability';
  } else if (yourBodySize >= 16 && yourBodySize <= 18) {
    score = 9;
  }

  return {
    criterion: 'Body Typography',
    score,
    benchmark: `${benchmarkSize}px`,
    yourValue: `${yourBodySize}px`,
    recommendation,
  };
}
```

---

## 5. Using Benchmarks

### Workflow

1. **Select domain** from configurations
2. **Run capture script** on benchmark sites
3. **Run capture** on your application
4. **Generate comparison report**
5. **Prioritize improvements** by weight × gap

### CLI Usage

```bash
# Capture benchmark data
python scripts/benchmark_capture.py --domain recruitment

# Compare your site
python scripts/benchmark_capture.py --url http://localhost:5173 --compare recruitment

# Generate report
python scripts/benchmark_report.py --domain recruitment --output report.html
```

### Playwright MCP Workflow

```
1. Load benchmark config for domain
2. For each reference site:
   a. browser_navigate → site URL
   b. browser_take_screenshot → visual reference
   c. browser_evaluate → run extraction scripts
   d. Store extracted patterns
3. Navigate to your app
4. Run same extractions
5. Compare and score
6. Generate recommendations
```

### Report Output

```markdown
# Design Benchmark Report: Recruitment Tool

## Overall Score: 72/100

### By Criterion

| Criterion | Weight | Score | Gap |
|-----------|--------|-------|-----|
| Information Hierarchy | 9 | 8 | -1 |
| Form Usability | 9 | 6 | -3 |
| Trust Signals | 8 | 5 | -3 |
| Progress Feedback | 8 | 7 | -1 |
| Mobile Experience | 7 | 6 | -1 |

### Top Recommendations

1. **Add progress indicators** to CV optimization flow (Form Usability)
2. **Include company logos** in job recommendations (Trust Signals)
3. **Improve mobile form layout** for CV upload (Mobile Experience)

### Visual Comparisons

[Screenshots comparing your UI to benchmarks]
```

---

## Extending to New Domains

### Template

```yaml
# benchmarks/[your-domain].yaml
domain: your-domain
description: Description of the domain

reference_sites:
  - name: Leader 1
    url: https://...
    why: Reason this is a benchmark
  # Add 3-5 reference sites

pages:
  - type: page_type
    path: /path
    extract: [elements_to_extract]
  # Define key page types

extraction_focus:
  - What makes this domain unique
  - Key UI patterns to compare

comparison_criteria:
  - criterion: Criterion Name
    weight: 1-10
    description: What this measures
  # Add 5-10 criteria
```

### Checklist for New Domain

- [ ] Identify 3-5 industry-leading sites
- [ ] Define 3-5 key page types
- [ ] List domain-specific extraction targets
- [ ] Define 5-10 weighted comparison criteria
- [ ] Create sample extraction scripts
- [ ] Test capture on reference sites
