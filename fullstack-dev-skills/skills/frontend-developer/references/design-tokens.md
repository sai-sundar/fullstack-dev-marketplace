# Design Tokens Reference

Comprehensive patterns for implementing design tokens in React applications.

## CSS Variables Setup

### Base Token Structure
```css
:root {
  /* Colors - Semantic */
  --color-primary: #C4A77D;
  --color-secondary: #8B4513;
  --color-accent: #2C5530;
  
  /* Colors - Surfaces */
  --color-background: #FAF7F2;
  --color-surface: #FFFFFF;
  --color-surface-elevated: #FFFFFF;
  
  /* Colors - Text */
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-text-inverse: #FFFFFF;
  
  /* Colors - States */
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  
  /* Typography - Scale */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  --font-size-5xl: 3rem;      /* 48px */
  --font-size-6xl: 3.75rem;   /* 60px */
  
  /* Typography - Families */
  --font-display: 'Clash Display', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Typography - Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Typography - Line Heights */
  --line-height-tight: 1.1;
  --line-height-snug: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Typography - Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  
  /* Spacing */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
  
  /* Border Radius */
  --radius-none: 0;
  --radius-sm: 0.125rem;
  --radius-default: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-default: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-default: 200ms ease;
  --transition-slow: 300ms ease;
  --transition-slower: 500ms ease;
  
  /* Z-Index Scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}
```

### Dark Mode Tokens
```css
[data-theme="dark"] {
  --color-background: #0D0D0D;
  --color-surface: #1A1A1A;
  --color-surface-elevated: #262626;
  
  --color-text-primary: #F5F5F5;
  --color-text-secondary: #A3A3A3;
  --color-text-muted: #737373;
  
  /* Adjust shadows for dark mode */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-default: 0 1px 3px 0 rgb(0 0 0 / 0.4);
}
```

## Tailwind Integration

### tailwind.config.js
```js
export default {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
      },
      fontFamily: {
        display: ['var(--font-display)'],
        body: ['var(--font-body)'],
        mono: ['var(--font-mono)'],
      },
      fontSize: {
        xs: 'var(--font-size-xs)',
        sm: 'var(--font-size-sm)',
        base: 'var(--font-size-base)',
        lg: 'var(--font-size-lg)',
        xl: 'var(--font-size-xl)',
        '2xl': 'var(--font-size-2xl)',
        '3xl': 'var(--font-size-3xl)',
        '4xl': 'var(--font-size-4xl)',
        '5xl': 'var(--font-size-5xl)',
        '6xl': 'var(--font-size-6xl)',
      },
      spacing: {
        1: 'var(--space-1)',
        2: 'var(--space-2)',
        3: 'var(--space-3)',
        4: 'var(--space-4)',
        5: 'var(--space-5)',
        6: 'var(--space-6)',
        8: 'var(--space-8)',
        10: 'var(--space-10)',
        12: 'var(--space-12)',
        16: 'var(--space-16)',
        20: 'var(--space-20)',
        24: 'var(--space-24)',
      },
      borderRadius: {
        none: 'var(--radius-none)',
        sm: 'var(--radius-sm)',
        DEFAULT: 'var(--radius-default)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
        '2xl': 'var(--radius-2xl)',
        full: 'var(--radius-full)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        DEFAULT: 'var(--shadow-default)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
        '2xl': 'var(--shadow-2xl)',
      },
    },
  },
};
```

## Theme Palettes by Direction

### Brutalist
```css
:root[data-theme="brutalist"] {
  --color-primary: #000000;
  --color-secondary: #FFFFFF;
  --color-accent: #FF0000;
  --color-background: #FFFFFF;
  --color-surface: #F0F0F0;
  --color-text-primary: #000000;
  --font-display: 'Helvetica Now', 'Helvetica Neue', sans-serif;
  --font-body: 'Akkurat', 'Arial', sans-serif;
}
```

### Editorial
```css
:root[data-theme="editorial"] {
  --color-primary: #2C2C2C;
  --color-secondary: #8B7355;
  --color-accent: #C9B896;
  --color-background: #FDFCFA;
  --color-surface: #FFFFFF;
  --color-text-primary: #1A1A1A;
  --font-display: 'Playfair Display', serif;
  --font-body: 'Source Serif Pro', serif;
}
```

### Retro-Futuristic
```css
:root[data-theme="retro-futuristic"] {
  --color-primary: #FF6B35;
  --color-secondary: #7B2CBF;
  --color-accent: #00F5D4;
  --color-background: #0D0D0D;
  --color-surface: #1A1A2E;
  --color-text-primary: #FFFFFF;
  --font-display: 'Orbitron', sans-serif;
  --font-body: 'IBM Plex Sans', sans-serif;
}
```

### Luxury
```css
:root[data-theme="luxury"] {
  --color-primary: #1A1A1A;
  --color-secondary: #B8860B;
  --color-accent: #D4AF37;
  --color-background: #FAFAFA;
  --color-surface: #FFFFFF;
  --color-text-primary: #1A1A1A;
  --font-display: 'Didot', 'Bodoni Moda', serif;
  --font-body: 'Lato', sans-serif;
}
```

### Playful
```css
:root[data-theme="playful"] {
  --color-primary: #FF6B6B;
  --color-secondary: #4ECDC4;
  --color-accent: #FFE66D;
  --color-background: #F7F7F7;
  --color-surface: #FFFFFF;
  --color-text-primary: #2D3436;
  --font-display: 'Fredoka', sans-serif;
  --font-body: 'Nunito', sans-serif;
}
```

## Responsive Tokens

### Fluid Typography
```css
:root {
  --font-size-fluid-sm: clamp(0.875rem, 0.8rem + 0.25vw, 1rem);
  --font-size-fluid-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  --font-size-fluid-lg: clamp(1.25rem, 1rem + 1vw, 2rem);
  --font-size-fluid-xl: clamp(1.5rem, 1rem + 2vw, 3rem);
  --font-size-fluid-2xl: clamp(2rem, 1.5rem + 3vw, 4.5rem);
  --font-size-fluid-display: clamp(2.5rem, 2rem + 4vw, 6rem);
}
```

### Container Widths
```css
:root {
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;
}
```

## Usage in Components

### TypeScript Types
```typescript
type ColorToken = 
  | 'primary' 
  | 'secondary' 
  | 'accent' 
  | 'background' 
  | 'surface';

type SpaceToken = 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 24;

type FontSizeToken = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl';

interface ThemeTokens {
  color: Record<ColorToken, string>;
  space: Record<SpaceToken, string>;
  fontSize: Record<FontSizeToken, string>;
}
```

### Token Utility
```typescript
// lib/tokens.ts
export const getToken = (token: string): string => {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--${token}`)
    .trim();
};

export const setToken = (token: string, value: string): void => {
  document.documentElement.style.setProperty(`--${token}`, value);
};
```
