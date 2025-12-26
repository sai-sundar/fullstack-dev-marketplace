#!/bin/bash
#
# Initialize a Turborepo monorepo with shared packages
#
# Usage:
#   ./init_monorepo.sh my-app
#   ./init_monorepo.sh my-app --with-trpc
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_NAME="${1:-my-app}"
WITH_TRPC=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-trpc)
            WITH_TRPC=true
            shift
            ;;
    esac
done

echo -e "${GREEN}Creating monorepo: ${PROJECT_NAME}${NC}"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Initialize pnpm
echo -e "${YELLOW}Initializing pnpm workspace...${NC}"

cat > package.json << 'EOF'
{
  "name": "PROJECT_NAME",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.4.0"
  },
  "packageManager": "pnpm@8.15.0"
}
EOF

sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" package.json

cat > pnpm-workspace.yaml << 'EOF'
packages:
  - "apps/*"
  - "packages/*"
EOF

cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "lint": {},
    "type-check": {
      "dependsOn": ["^build"]
    },
    "clean": {
      "cache": false
    }
  }
}
EOF

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p apps/web/src
mkdir -p apps/server/src
mkdir -p packages/shared/src/{types,schemas,utils,constants}
mkdir -p packages/config-typescript
mkdir -p packages/config-eslint

# Shared TypeScript config
cat > packages/config-typescript/base.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "declaration": true,
    "declarationMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true
  },
  "exclude": ["node_modules"]
}
EOF

cat > packages/config-typescript/package.json << 'EOF'
{
  "name": "@PROJECT_NAME/config-typescript",
  "version": "0.0.0",
  "private": true,
  "files": ["*.json"]
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" packages/config-typescript/package.json

# Shared package
cat > packages/shared/package.json << 'EOF'
{
  "name": "@PROJECT_NAME/shared",
  "version": "0.0.0",
  "main": "./dist/index.js",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
    "clean": "rm -rf dist",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "@PROJECT_NAME/config-typescript": "workspace:*",
    "tsup": "^8.0.0",
    "typescript": "^5.4.0"
  },
  "dependencies": {
    "zod": "^3.23.0"
  }
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" packages/shared/package.json

cat > packages/shared/tsconfig.json << 'EOF'
{
  "extends": "@PROJECT_NAME/config-typescript/base.json",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src"]
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" packages/shared/tsconfig.json

# Shared types
cat > packages/shared/src/types/index.ts << 'EOF'
// Common types shared between frontend and backend

export interface User {
  id: string;
  email: string;
  username: string;
  displayName?: string;
  avatarUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  content: string;
  published: boolean;
  authorId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface ApiError {
  error: string;
  code: string;
  details?: Record<string, string[]>;
}
EOF

# Shared schemas
cat > packages/shared/src/schemas/index.ts << 'EOF'
import { z } from 'zod';

export const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

export const UpdatePostSchema = CreatePostSchema.partial();

export type CreatePostInput = z.infer<typeof CreatePostSchema>;
export type UpdatePostInput = z.infer<typeof UpdatePostSchema>;
EOF

# Shared utils
cat > packages/shared/src/utils/index.ts << 'EOF'
export function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function formatDate(date: Date | string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}
EOF

# Shared constants
cat > packages/shared/src/constants/index.ts << 'EOF'
export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;
EOF

# Main shared index
cat > packages/shared/src/index.ts << 'EOF'
export * from './types';
export * from './schemas';
export * from './utils';
export * from './constants';
EOF

# Web app
cat > apps/web/package.json << 'EOF'
{
  "name": "@PROJECT_NAME/web",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@PROJECT_NAME/shared": "workspace:*",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@PROJECT_NAME/config-typescript": "workspace:*",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0"
  }
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/web/package.json

cat > apps/web/tsconfig.json << 'EOF'
{
  "extends": "@PROJECT_NAME/config-typescript/base.json",
  "compilerOptions": {
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/web/tsconfig.json

cat > apps/web/vite.config.ts << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
});
EOF

cat > apps/web/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PROJECT_NAME</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/web/index.html

cat > apps/web/src/main.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > apps/web/src/App.tsx << 'EOF'
import { formatDate } from '@PROJECT_NAME/shared';

function App() {
  return (
    <div>
      <h1>Welcome to PROJECT_NAME</h1>
      <p>Today is {formatDate(new Date())}</p>
    </div>
  );
}

export default App;
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/web/src/App.tsx

# Server app
cat > apps/server/package.json << 'EOF'
{
  "name": "@PROJECT_NAME/server",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "lint": "eslint src",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@PROJECT_NAME/shared": "workspace:*",
    "@supabase/supabase-js": "^2.43.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.0",
    "express": "^4.19.0",
    "helmet": "^7.1.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@PROJECT_NAME/config-typescript": "workspace:*",
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/node": "^20.12.0",
    "tsx": "^4.7.0",
    "typescript": "^5.4.0"
  }
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/server/package.json

cat > apps/server/tsconfig.json << 'EOF'
{
  "extends": "@PROJECT_NAME/config-typescript/base.json",
  "compilerOptions": {
    "outDir": "dist",
    "noEmit": false
  },
  "include": ["src"]
}
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/server/tsconfig.json

cat > apps/server/src/index.ts << 'EOF'
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { config } from 'dotenv';
import { ERROR_CODES } from '@PROJECT_NAME/shared';

config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Example route using shared constants
app.get('/api/posts', (req, res) => {
  res.json({
    data: [],
    pagination: { page: 1, limit: 20, total: 0, pages: 0 },
  });
});

// Error handler
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err);
  res.status(500).json({
    error: 'Internal server error',
    code: ERROR_CODES.INTERNAL_ERROR,
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" apps/server/src/index.ts

cat > apps/server/.env << 'EOF'
PORT=3001
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
EOF

# Git ignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Build outputs
dist/
.next/
build/

# Environment
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# Turbo
.turbo/

# Misc
*.log
.DS_Store
EOF

# README
cat > README.md << 'EOF'
# PROJECT_NAME

Monorepo built with Turborepo.

## Structure

```
apps/
├── web/        # React frontend
└── server/     # Express backend

packages/
├── shared/     # Shared types, schemas, utilities
└── config-*/   # Shared configurations
```

## Development

```bash
# Install dependencies
pnpm install

# Start all apps in dev mode
pnpm dev

# Build all packages
pnpm build

# Run tests
pnpm test
```

## Environment

Copy `.env` files and fill in values:
- `apps/server/.env` - Backend configuration
EOF
sed -i "s/PROJECT_NAME/$PROJECT_NAME/g" README.md

echo -e "${GREEN}✓ Monorepo created successfully!${NC}"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  pnpm install"
echo "  pnpm dev"
echo ""
echo "Structure:"
echo "  apps/web     - React frontend (port 5173)"
echo "  apps/server  - Express backend (port 3001)"
echo "  packages/shared - Shared code"
