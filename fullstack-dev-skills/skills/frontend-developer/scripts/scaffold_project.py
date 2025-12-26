#!/usr/bin/env python3
"""
React Project Scaffolder with Design Tokens

Creates a new React project with:
- Vite + React + TypeScript
- Tailwind CSS configured with design tokens
- Motion (Framer Motion) ready
- shadcn/ui initialized
- Distinctive styling (no generic AI aesthetics)

Usage:
    scaffold_project.py <project-name> [--theme <theme>]
    
Themes: brutalist, editorial, retro-futuristic, luxury, playful, organic

Example:
    scaffold_project.py my-app --theme editorial
"""

import sys
import os
import subprocess
from pathlib import Path

THEMES = {
    "brutalist": {
        "colors": {
            "primary": "#000000",
            "secondary": "#FFFFFF",
            "accent": "#FF0000",
            "background": "#FFFFFF",
            "surface": "#F0F0F0",
            "text-primary": "#000000",
            "text-secondary": "#333333",
        },
        "fonts": {
            "display": "'Helvetica Now', 'Helvetica Neue', sans-serif",
            "body": "'Akkurat', 'Arial', sans-serif",
        }
    },
    "editorial": {
        "colors": {
            "primary": "#2C2C2C",
            "secondary": "#8B7355",
            "accent": "#C9B896",
            "background": "#FDFCFA",
            "surface": "#FFFFFF",
            "text-primary": "#1A1A1A",
            "text-secondary": "#4A4A4A",
        },
        "fonts": {
            "display": "'Playfair Display', serif",
            "body": "'Source Serif Pro', serif",
        }
    },
    "retro-futuristic": {
        "colors": {
            "primary": "#FF6B35",
            "secondary": "#7B2CBF",
            "accent": "#00F5D4",
            "background": "#0D0D0D",
            "surface": "#1A1A2E",
            "text-primary": "#FFFFFF",
            "text-secondary": "#B0B0B0",
        },
        "fonts": {
            "display": "'Orbitron', sans-serif",
            "body": "'IBM Plex Sans', sans-serif",
        }
    },
    "luxury": {
        "colors": {
            "primary": "#1A1A1A",
            "secondary": "#B8860B",
            "accent": "#D4AF37",
            "background": "#FAFAFA",
            "surface": "#FFFFFF",
            "text-primary": "#1A1A1A",
            "text-secondary": "#666666",
        },
        "fonts": {
            "display": "'Didot', 'Bodoni Moda', serif",
            "body": "'Lato', sans-serif",
        }
    },
    "playful": {
        "colors": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#FFE66D",
            "background": "#F7F7F7",
            "surface": "#FFFFFF",
            "text-primary": "#2D3436",
            "text-secondary": "#636E72",
        },
        "fonts": {
            "display": "'Fredoka', sans-serif",
            "body": "'Nunito', sans-serif",
        }
    },
    "organic": {
        "colors": {
            "primary": "#6B7F6B",
            "secondary": "#C4A77D",
            "accent": "#E07A5F",
            "background": "#FAF7F2",
            "surface": "#FFFFFF",
            "text-primary": "#2D3A2D",
            "text-secondary": "#5A6B5A",
        },
        "fonts": {
            "display": "'Cormorant', serif",
            "body": "'Karla', sans-serif",
        }
    },
}

def generate_globals_css(theme):
    """Generate globals.css with design tokens"""
    colors = theme["colors"]
    fonts = theme["fonts"]
    
    return f'''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {{
  :root {{
    /* Colors */
    --color-primary: {colors["primary"]};
    --color-secondary: {colors["secondary"]};
    --color-accent: {colors["accent"]};
    --color-background: {colors["background"]};
    --color-surface: {colors["surface"]};
    --color-text-primary: {colors["text-primary"]};
    --color-text-secondary: {colors["text-secondary"]};
    
    /* Typography */
    --font-display: {fonts["display"]};
    --font-body: {fonts["body"]};
    
    /* Spacing */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-12: 3rem;
    --space-16: 4rem;
    --space-24: 6rem;
    
    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-default: 200ms ease;
    --transition-slow: 300ms ease;
  }}
  
  * {{
    box-sizing: border-box;
  }}
  
  body {{
    background-color: var(--color-background);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    line-height: 1.6;
  }}
  
  h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-display);
    line-height: 1.2;
  }}
}}

@layer components {{
  .container {{
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 var(--space-4);
  }}
  
  .btn-primary {{
    background-color: var(--color-primary);
    color: white;
    padding: var(--space-3) var(--space-6);
    border: none;
    cursor: pointer;
    font-family: var(--font-display);
    font-weight: 600;
    transition: transform var(--transition-fast), opacity var(--transition-fast);
  }}
  
  .btn-primary:hover {{
    opacity: 0.9;
  }}
  
  .btn-primary:active {{
    transform: scale(0.98);
  }}
}}
'''

def generate_tailwind_config(theme):
    """Generate tailwind.config.js"""
    return '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
      },
      fontFamily: {
        display: ['var(--font-display)'],
        body: ['var(--font-body)'],
      },
      spacing: {
        1: 'var(--space-1)',
        2: 'var(--space-2)',
        3: 'var(--space-3)',
        4: 'var(--space-4)',
        6: 'var(--space-6)',
        8: 'var(--space-8)',
        12: 'var(--space-12)',
        16: 'var(--space-16)',
        24: 'var(--space-24)',
      },
      transitionDuration: {
        fast: '150ms',
        default: '200ms',
        slow: '300ms',
      },
    },
  },
  plugins: [],
}
'''

def generate_app_tsx():
    """Generate a sample App.tsx with Motion"""
    return '''import { motion } from "motion/react";

function App() {
  return (
    <div className="min-h-screen bg-background">
      <header className="container py-8">
        <motion.h1 
          className="font-display text-5xl text-primary"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Welcome
        </motion.h1>
      </header>
      
      <main className="container py-16">
        <motion.div
          className="grid gap-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <motion.section
            className="p-8 bg-surface border border-secondary/20"
            whileHover={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h2 className="font-display text-2xl text-primary mb-4">
              Distinctive Design
            </h2>
            <p className="text-text-secondary">
              This project uses a carefully crafted design system with
              intentional typography, color, and spacing choices.
            </p>
          </motion.section>
          
          <motion.button
            className="btn-primary w-fit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Get Started
          </motion.button>
        </motion.div>
      </main>
    </div>
  );
}

export default App;
'''

def generate_utils_ts():
    """Generate utility functions"""
    return '''import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
'''

def print_usage():
    print(__doc__)
    print("\nAvailable themes:")
    for theme in THEMES.keys():
        print(f"  - {theme}")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    project_name = sys.argv[1]
    theme_name = "editorial"  # Default theme
    
    # Parse --theme argument
    if "--theme" in sys.argv:
        theme_idx = sys.argv.index("--theme")
        if theme_idx + 1 < len(sys.argv):
            theme_name = sys.argv[theme_idx + 1]
    
    if theme_name not in THEMES:
        print(f"❌ Unknown theme: {theme_name}")
        print(f"Available themes: {', '.join(THEMES.keys())}")
        sys.exit(1)
    
    theme = THEMES[theme_name]
    
    print(f"🚀 Scaffolding {project_name} with {theme_name} theme...")
    
    # Instructions for manual execution
    print(f"""
📋 Run these commands to create your project:

# 1. Create Vite project
npm create vite@latest {project_name} -- --template react-ts

# 2. Install dependencies
cd {project_name}
npm install
npm install motion lucide-react clsx tailwind-merge

# 3. Setup Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Create files with the content below

📁 Files to create:
""")
    
    print("=" * 60)
    print("📄 src/index.css (replace content)")
    print("=" * 60)
    print(generate_globals_css(theme))
    
    print("\n" + "=" * 60)
    print("📄 tailwind.config.js (replace content)")
    print("=" * 60)
    print(generate_tailwind_config(theme))
    
    print("\n" + "=" * 60)
    print("📄 src/App.tsx (replace content)")
    print("=" * 60)
    print(generate_app_tsx())
    
    print("\n" + "=" * 60)
    print("📄 src/lib/utils.ts (create new)")
    print("=" * 60)
    print(generate_utils_ts())
    
    print(f"""
✅ Theme: {theme_name}
   Primary: {theme["colors"]["primary"]}
   Background: {theme["colors"]["background"]}
   Display Font: {theme["fonts"]["display"]}
   Body Font: {theme["fonts"]["body"]}

🎨 Remember: This is a starting point. Make it distinctive!
""")

if __name__ == "__main__":
    main()
