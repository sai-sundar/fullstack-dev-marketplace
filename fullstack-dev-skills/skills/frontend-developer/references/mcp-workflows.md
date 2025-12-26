# MCP Workflows Reference

Detailed workflows for using Chrome DevTools, Playwright, and Figma MCP servers in frontend development.

## Table of Contents
1. [Chrome DevTools MCP Workflows](#chrome-devtools-mcp-workflows)
2. [Playwright MCP Workflows](#playwright-mcp-workflows)
3. [Figma MCP Workflows](#figma-mcp-workflows)
4. [Combined Workflows](#combined-workflows)

## Chrome DevTools MCP Workflows

### Configuration

**Claude Code (terminal)**:
```bash
claude mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

**MCP Config file** (`.claude/mcp.json` or `claude_desktop_config.json`):
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

### Available Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to a URL |
| `browser_click` | Click on elements |
| `browser_type` | Type text into inputs |
| `browser_take_screenshot` | Capture current page state |
| `browser_console_messages` | Read console logs/errors |
| `browser_network_requests` | Inspect network activity |
| `browser_accessibility_tree` | Get accessibility snapshot |
| `performance_start_trace` | Begin performance recording |
| `performance_stop_trace` | End recording, get insights |

### Workflow: Debug Console Errors

```
1. Navigate to problem page
   → Use browser_navigate to open the URL

2. Capture initial state
   → Use browser_take_screenshot for evidence

3. Check for errors
   → Use browser_console_messages to read console

4. Identify error source
   → Analyze error messages and stack traces

5. Apply fix in codebase
   → Edit the relevant source files

6. Verify fix
   → Use browser_navigate to reload
   → Use browser_console_messages to confirm no errors
   → Use browser_take_screenshot for comparison
```

**Example prompts**:
```
"Use Chrome DevTools MCP to navigate to localhost:3000 and check for console errors"

"Take a screenshot of the current page state and show me any JavaScript errors in the console"

"Inspect the network requests on the /api/users endpoint"
```

### Workflow: Performance Analysis

```
1. Start performance trace
   → Use performance_start_trace

2. Interact with page
   → Use browser_navigate, browser_click to simulate user flow

3. Stop trace and analyze
   → Use performance_stop_trace
   → Review LCP, CLS, FID metrics

4. Identify bottlenecks
   → Look for long tasks, render blocking resources

5. Apply optimizations
   → Implement fixes (lazy loading, code splitting, etc.)

6. Re-test
   → Run another trace to compare
```

**Example prompts**:
```
"Analyze the performance of my homepage and identify the Largest Contentful Paint element"

"Start a performance trace, navigate through the checkout flow, and show me any layout shifts"

"Check the Core Web Vitals for web.dev"
```

### Workflow: Responsive Testing

```
1. Navigate to page
   → Use browser_navigate

2. Set viewport (via browser settings)
   → Test mobile (375x667), tablet (768x1024), desktop (1440x900)

3. Capture each breakpoint
   → Use browser_take_screenshot at each size

4. Verify layout
   → Check for overflow, hidden elements, broken layouts

5. Fix issues
   → Update CSS/responsive styles

6. Re-test all breakpoints
```

### Workflow: Accessibility Testing

```
1. Navigate to page
   → Use browser_navigate

2. Get accessibility tree
   → Use browser_accessibility_tree

3. Analyze structure
   → Check for proper headings, ARIA labels, roles

4. Test keyboard navigation
   → Use browser_click with focus elements
   → Verify tab order

5. Fix issues
   → Add missing labels, fix heading hierarchy

6. Verify fixes
   → Re-check accessibility tree
```

## Playwright MCP Workflows

### Configuration

**Claude Code (terminal)**:
```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

**MCP Config file**:
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

**With options**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--browser=chromium"
      ]
    }
  }
}
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to URL |
| `browser_click` | Click elements by selector or text |
| `browser_type` | Enter text into fields |
| `browser_wait_for` | Wait for element/text/condition |
| `browser_evaluate` | Execute JavaScript in page context |
| `browser_take_screenshot` | Capture page state |
| `browser_select_option` | Select dropdown options |
| `browser_check` | Check/uncheck checkboxes |
| `browser_press` | Press keyboard keys |

### Workflow: Generate E2E Test

```
1. Define user scenario
   → "User logs in, adds item to cart, checks out"

2. Execute steps with MCP
   → browser_navigate to login page
   → browser_type email and password
   → browser_click submit button
   → browser_wait_for dashboard element
   → Continue through flow...

3. Capture evidence
   → browser_take_screenshot at key steps

4. Generate Playwright test file
   → Convert MCP steps to Playwright test syntax

5. Run test locally
   → npx playwright test
```

**Example prompts**:
```
"Use Playwright MCP to test the login flow on localhost:3000. Navigate to /login, enter test@example.com and password123, click submit, and verify the dashboard loads"

"Generate a Playwright test for the shopping cart flow"

"Test that the modal opens when clicking the 'Learn More' button"
```

### Workflow: Cross-Browser Testing

```
1. Configure browsers
   → --browser=chromium, firefox, or webkit

2. Run same test flow
   → Execute user scenario on each browser

3. Compare results
   → Check for browser-specific issues

4. Fix compatibility issues
   → Update CSS prefixes, polyfills

5. Verify across browsers
```

### Workflow: Visual Regression

```
1. Capture baseline screenshots
   → browser_take_screenshot on main pages

2. Make code changes
   → Update styles/components

3. Capture new screenshots
   → browser_take_screenshot same pages

4. Compare visually
   → Identify unintended changes

5. Update or fix
   → Intentional: update baseline
   → Unintentional: fix regression
```

### Test Template Generation

After completing a flow with MCP, generate a Playwright test:

```typescript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test';

test('user can complete checkout', async ({ page }) => {
  // Navigate to product page
  await page.goto('http://localhost:3000/products');
  
  // Add item to cart
  await page.click('[data-testid="add-to-cart"]');
  await expect(page.locator('.cart-count')).toHaveText('1');
  
  // Go to checkout
  await page.click('[data-testid="checkout-button"]');
  await expect(page).toHaveURL(/.*checkout/);
  
  // Fill shipping info
  await page.fill('[name="address"]', '123 Main St');
  await page.fill('[name="city"]', 'New York');
  
  // Submit order
  await page.click('[data-testid="place-order"]');
  await expect(page.locator('.confirmation')).toBeVisible();
});
```

## Figma MCP Workflows

### Configuration

**Desktop MCP** (requires Figma desktop app):
1. Open Figma Desktop App
2. Open a Design file
3. Toggle to Dev Mode (Shift+D)
4. Enable MCP server in inspect panel

```json
{
  "mcpServers": {
    "figma-desktop": {
      "url": "http://127.0.0.1:3845/mcp"
    }
  }
}
```

**Remote MCP** (browser-based):
```json
{
  "mcpServers": {
    "figma-remote": {
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

**Claude Code (desktop MCP)**:
```bash
claude mcp add figma-desktop --transport http --url http://127.0.0.1:3845/mcp
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `get_design_context` | Extract layout, tokens, structure |
| `get_code_connect` | Map to codebase components |
| `get_variables` | Extract design system variables |
| `get_styles` | Get text/color/effect styles |

### Workflow: Design to Code

```
1. Select frame in Figma
   → Choose the component/screen to implement

2. Extract design context
   → MCP retrieves: node tree, variants, constraints, tokens

3. Review extracted data
   → Understand structure, spacing, typography

4. Generate React component
   → Map Figma layers to JSX elements
   → Apply extracted styles via Tailwind or CSS

5. Verify with Chrome DevTools MCP
   → Compare implementation to design

6. Iterate
   → Adjust until pixel-perfect
```

**Example prompts**:
```
"Use Figma MCP to get the design context for my current selection and generate a React component"

"Extract the design tokens from the Figma file at [URL] and create CSS variables"

"Implement the navigation bar from my Figma design using shadcn/ui components"
```

### Workflow: Design System Sync

```
1. Extract all variables from Figma
   → Colors, typography, spacing

2. Generate design tokens file
   → Create CSS variables or Tailwind config

3. Map components with Code Connect
   → Link Figma components to codebase

4. Update existing components
   → Ensure code matches design specs

5. Document mappings
   → Create reference for team
```

### Workflow: Handoff Optimization

**Before starting implementation**:
1. Open Figma file in Dev Mode
2. Review auto-layout settings (flex/grid)
3. Check component variants
4. Note design tokens used
5. Copy frame link for reference

**During implementation**:
1. Reference Figma link in prompts
2. Request specific frames by selection
3. Compare MCP output to visual
4. Iterate on details

### Best Practices for Figma-to-Code

```
✓ Use auto-layout in Figma → Clean flexbox/grid output
✓ Name layers descriptively → Better component mapping
✓ Use components, not copies → Consistent code generation
✓ Apply design tokens → Maintainable CSS variables
✓ Set constraints properly → Correct responsive behavior

✗ Avoid absolute positioning → Poor responsive output
✗ Avoid unnamed groups → Generic div soup
✗ Avoid inline styles → Hard to maintain
```

## Combined Workflows

### Full Development Cycle

```
1. Design Phase (Figma MCP)
   → Extract design context
   → Generate initial component

2. Implementation Phase (Code)
   → Build out component
   → Add interactions and animations

3. Testing Phase (Playwright MCP)
   → Test user flows
   → Generate test specs

4. Debugging Phase (Chrome DevTools MCP)
   → Check for console errors
   → Analyze performance
   → Verify accessibility

5. Iteration
   → Fix issues
   → Re-test
   → Deploy
```

### Rapid Prototyping

```
1. Get design from Figma MCP
2. Generate React component
3. Add Motion animations
4. Test with Chrome DevTools MCP
5. Generate tests with Playwright MCP
6. Iterate based on feedback
```

### Bug Investigation

```
1. Reproduce with Chrome DevTools MCP
   → Navigate, take screenshots

2. Identify cause
   → Console errors, network issues

3. Fix codebase
   → Apply solution

4. Verify with Playwright MCP
   → Automated regression test

5. Document
   → Add test to CI/CD
```

## Troubleshooting

### MCP Server Not Starting

```bash
# Check if Chrome DevTools MCP is working
npx chrome-devtools-mcp@latest --version

# Check if Playwright MCP is working
npx @playwright/mcp@latest --help

# View MCP logs in Claude Code
claude mcp list
claude mcp get chrome-devtools
```

### Browser Not Opening

```bash
# Install Playwright browsers
npx playwright install

# Ensure Chrome is installed for Chrome DevTools MCP
which google-chrome
```

### Figma MCP Not Connecting

```
1. Ensure Figma Desktop App is running
2. Check Dev Mode is enabled
3. Verify MCP server is running (check inspect panel)
4. Confirm correct URL: http://127.0.0.1:3845/mcp
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Browser crashed" | Restart MCP server, check memory |
| "Element not found" | Wait longer, check selector |
| "Timeout exceeded" | Increase timeout, check network |
| "Permission denied" | Run without sandbox in containers |
| "Cannot connect to Figma" | Restart Figma Desktop, re-enable MCP |
