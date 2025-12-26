---
name: front-end-engineer
description: Full-stack frontend engineering skill for building, improving, and debugging React applications with distinctive design. Use when building new frontend projects, improving existing codebases, implementing Figma designs, debugging UI issues, or creating interactive components. Integrates with Chrome DevTools MCP, Playwright MCP, and Figma MCP for real browser testing, automation, and design-to-code workflows. Emphasizes non-generic aesthetics that avoid typical AI-generated blue-tone patterns.
---

# Front-End Engineer

Build production-grade, visually distinctive React applications. This skill combines modern libraries (React Bits, Motion/Framer Motion, shadcn/ui), MCP integrations (Chrome DevTools, Playwright, Figma), and design principles that avoid generic AI aesthetics.

## Workflow Decision Tree

```
User Request
├─► "Build new frontend/app/component"
│   └─► New Project Workflow → Design Direction → Implementation
├─► "Improve/refactor existing frontend"
│   └─► Audit Workflow → Identify Issues → Apply Improvements
├─► "Debug/fix UI issue"
│   └─► Debug Workflow → Use Chrome DevTools MCP → Fix & Verify
├─► "Implement this Figma design"
│   └─► Figma MCP Workflow → Extract Context → Generate Code
└─► "Add animations/interactions"
    └─► Animation Workflow → Select Library → Implement
```

## Core Principles

### Anti-AI Aesthetics
NEVER produce generic AI-generated frontend with:
- Blue/purple gradients on white backgrounds
- Inter, Roboto, Arial, or system fonts
- Predictable card layouts with rounded corners
- Cookie-cutter component patterns
- Overused shadows and generic hover states

INSTEAD commit to bold, intentional design:
- Distinctive typography (display + body font pairing)
- Unexpected color palettes with personality
- Asymmetric layouts, diagonal flow, grid-breaking elements
- Context-specific character matching the domain
- Textures, gradients, and atmospheric backgrounds

### Design Direction Selection
Before any implementation, commit to an aesthetic:

| Direction | Character | Use When |
|-----------|-----------|----------|
| Brutalist | Raw, honest, bold typography | Developer tools, portfolios |
| Editorial | Magazine-like, sophisticated | Content sites, blogs |
| Organic | Natural, flowing, warm | Wellness, creative |
| Retro-Futuristic | Neon, grid, synthwave | Gaming, entertainment |
| Luxury | Refined, minimal, premium | E-commerce, SaaS |
| Playful | Vibrant, animated, toy-like | Consumer apps, kids |
| Industrial | Utilitarian, functional | Enterprise, dashboards |
| Art Deco | Geometric, golden, ornate | Events, hospitality |

## Tech Stack

### Core Libraries

```bash
# React + Build Tool
npm create vite@latest my-app -- --template react-ts

# Essential Libraries
npm install motion                    # Animation (formerly Framer Motion)
npm install @radix-ui/react-*         # Headless primitives
npm install tailwindcss postcss autoprefixer
npm install lucide-react              # Icons
npm install clsx tailwind-merge       # Utility classes
```

### React Bits Components
Copy animated components directly from reactbits.dev:
```bash
# Install via shadcn CLI or jsrepo
npx shadcn@latest add [component-name]
# Or copy component code directly from reactbits.dev
```

Available statement pieces: Hyperspeed, True Focus, Crosshair, Aurora, Blob Cursor, Magnet Lines, Pixel Trail, Letter Swap, Split Text, Shiny Button, Elastic Slider, Magnetic Button, Tilted Scroll, Infinite Scroll, Blur Text, Gradient Text, Decrypted Text, Variable Proximity.

### shadcn/ui Setup
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card dialog dropdown-menu
```

## MCP Integrations

### Chrome DevTools MCP
Debug, inspect, and verify frontend code in a real browser.

**Configuration** (add to `.claude/mcp.json` or `claude_desktop_config.json`):
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

**Claude Code setup**:
```bash
claude mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

**Available Tools**:
- `browser_navigate` - Open pages
- `browser_click`, `browser_type` - Interact with elements
- `browser_take_screenshot` - Capture current state
- `browser_console_messages` - Read console logs
- `browser_network_requests` - Inspect network activity
- `performance_start_trace` / `performance_stop_trace` - Performance analysis

**Use Cases**:
- Verify fixes work in real browser
- Debug console errors and network issues
- Analyze LCP, CLS, and Core Web Vitals
- Screenshot-based verification

### Playwright MCP
Automate browser testing and generate E2E tests.

**Configuration**:
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

**Claude Code setup**:
```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

**Available Tools**:
- `browser_navigate`, `browser_click`, `browser_type`
- `browser_wait_for` - Wait for elements/text
- `browser_evaluate` - Execute JavaScript
- `browser_take_screenshot` - Capture evidence
- Accessibility tree snapshots (no vision model needed)

**Use Cases**:
- Generate Playwright test specs from user scenarios
- Automated regression testing
- Cross-browser verification
- Accessibility testing

### Figma MCP
Extract design context for accurate design-to-code.

**Desktop MCP** (via Figma app):
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

**Available Tools**:
- `get_design_context` - Extract layout, components, tokens
- `get_code_connect` - Map to existing codebase components
- Variable and style token extraction
- Auto-layout rule interpretation

**Workflow**:
1. Select frame in Figma (desktop) or copy link (remote)
2. Prompt: "Implement this Figma design as a React component"
3. MCP extracts: node tree, variants, constraints, tokens
4. Generate code matching design system

## Animation Implementation

### Motion (Framer Motion)
```tsx
import { motion, AnimatePresence } from "motion/react";

// Basic animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
>
  Content
</motion.div>

// Scroll-triggered
<motion.div
  initial={{ opacity: 0, x: -50 }}
  whileInView={{ opacity: 1, x: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.6 }}
/>

// Gesture-based
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
/>

// Layout animations
<motion.div layout layoutId="shared-element" />

// Staggered children
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};
```

### CSS-Only Animations
For simpler effects without JS overhead:
```css
/* Scroll-triggered reveal */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.reveal {
  animation: fadeInUp 0.6s ease-out forwards;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}

/* Hover micro-interaction */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}
```

## New Project Workflow

1. **Understand Requirements**
   - Domain/purpose (e-commerce, dashboard, portfolio, etc.)
   - Target audience
   - Key features and pages

2. **Commit to Design Direction**
   - Select aesthetic from direction table
   - Choose typography pairing (display + body)
   - Define color palette (dominant + accents)
   - Plan motion strategy (subtle vs. dramatic)

3. **Initialize Project**
   ```bash
   npm create vite@latest project-name -- --template react-ts
   cd project-name
   npm install
   npm install motion lucide-react clsx tailwind-merge
   npx tailwindcss init -p
   ```

4. **Setup shadcn/ui** (if using)
   ```bash
   npx shadcn-ui@latest init
   # Select style, colors, CSS variables
   ```

5. **Implement with Design System**
   - Create design tokens in CSS variables
   - Build base components first
   - Add animations and interactions
   - Test with Chrome DevTools MCP

## Improvement Workflow

1. **Audit Current Codebase**
   - Review component structure
   - Check for accessibility issues
   - Analyze performance (bundle size, render performance)
   - Identify design inconsistencies

2. **Identify Anti-Patterns**
   - Generic/AI-looking styling
   - Inconsistent spacing/typography
   - Missing animations/interactions
   - Poor responsive behavior

3. **Apply Improvements**
   - Refactor to design system approach
   - Add distinctive styling
   - Implement micro-interactions
   - Improve accessibility

4. **Verify with MCP Tools**
   - Use Chrome DevTools MCP to test changes
   - Run Playwright MCP for E2E verification

## Debug Workflow

1. **Reproduce Issue**
   - Use Chrome DevTools MCP to navigate to problem page
   - Take screenshot of current state

2. **Investigate**
   - Check console messages for errors
   - Inspect network requests
   - Analyze accessibility tree
   - Run performance trace if needed

3. **Fix and Verify**
   - Apply fix in codebase
   - Navigate with MCP to verify
   - Take screenshot confirming fix
   - Generate test case with Playwright MCP

## Typography Guidelines

### Distinctive Font Pairings

| Style | Display Font | Body Font |
|-------|-------------|-----------|
| Modern Geometric | Clash Display, Satoshi | DM Sans, General Sans |
| Editorial | Playfair Display, Cormorant | Source Serif Pro, Libre Baskerville |
| Technical | JetBrains Mono, Space Mono | IBM Plex Sans, Manrope |
| Playful | Fredoka, Quicksand | Nunito, Poppins |
| Luxury | Didot, Bodoni | Lato, Outfit |
| Brutalist | Neue Haas Grotesk, Helvetica Now | Akkurat, Suisse Int'l |

### Loading Fonts
```html
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
```

```css
/* Variable fonts for performance */
@font-face {
  font-family: 'ClashDisplay';
  src: url('/fonts/ClashDisplay-Variable.woff2') format('woff2');
  font-weight: 200 700;
  font-display: swap;
}
```

## Color Palette Examples

### Avoiding Generic Blue
```css
/* ❌ Generic AI palette */
--primary: #3B82F6; /* Blue-500 */
--background: #FFFFFF;

/* ✅ Distinctive palettes */

/* Warm Earth */
--primary: #C4A77D;
--secondary: #8B4513;
--background: #FAF7F2;
--accent: #2C5530;

/* Neon Night */
--primary: #FF6B35;
--secondary: #7B2CBF;
--background: #0D0D0D;
--accent: #00F5D4;

/* Muted Sage */
--primary: #6B7F6B;
--secondary: #4A5568;
--background: #F7F7F5;
--accent: #E07A5F;

/* Electric Coral */
--primary: #FF6F61;
--secondary: #1A1A2E;
--background: #FFFBF5;
--accent: #6C63FF;
```

## Component Patterns

### Distinctive Button
```tsx
import { motion } from "motion/react";

const Button = ({ children, variant = "primary" }) => (
  <motion.button
    className={cn(
      "relative overflow-hidden px-6 py-3",
      "font-display font-semibold tracking-wide",
      "border-2 border-current",
      variant === "primary" && "bg-primary text-white",
      variant === "outline" && "bg-transparent text-primary"
    )}
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
  >
    <motion.span
      className="absolute inset-0 bg-white/20"
      initial={{ x: "-100%" }}
      whileHover={{ x: "100%" }}
      transition={{ duration: 0.5 }}
    />
    <span className="relative">{children}</span>
  </motion.button>
);
```

### Animated Card
```tsx
const Card = ({ children, index }) => (
  <motion.div
    className="group relative bg-surface p-6 border border-muted"
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay: index * 0.1, duration: 0.5 }}
  >
    <motion.div
      className="absolute inset-0 bg-gradient-to-br from-accent/10 to-transparent"
      initial={{ opacity: 0 }}
      whileHover={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    />
    <div className="relative">{children}</div>
  </motion.div>
);
```

## File Structure

```
src/
├── components/
│   ├── ui/           # Base components (Button, Card, Input)
│   ├── layout/       # Layout components (Header, Footer, Container)
│   └── features/     # Feature-specific components
├── hooks/            # Custom React hooks
├── lib/
│   └── utils.ts      # Utility functions (cn, etc.)
├── styles/
│   ├── globals.css   # Global styles, CSS variables
│   └── fonts.css     # Font definitions
├── pages/            # Page components (if not using router)
└── App.tsx
```

## Testing Strategy

1. **Visual Testing**
   - Use Chrome DevTools MCP to capture screenshots
   - Compare before/after for changes

2. **E2E Testing**
   - Generate tests with Playwright MCP
   - Cover critical user flows

3. **Accessibility**
   - Use accessibility tree inspection
   - Verify keyboard navigation
   - Check color contrast

4. **Performance**
   - Run performance traces
   - Monitor Core Web Vitals (LCP, CLS, FID)

## Additional References

See the `references/` directory for:
- `design-tokens.md` - Design token patterns and examples
- `animation-patterns.md` - Animation recipes and patterns
- `mcp-workflows.md` - Detailed MCP usage examples
