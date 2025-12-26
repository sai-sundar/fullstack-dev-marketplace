#!/usr/bin/env python3
"""
Scaffold a new backend project with Supabase integration.

Usage:
    python scaffold_project.py <project-name> [--stack node|python] [--path <output-dir>]

Examples:
    python scaffold_project.py my-api
    python scaffold_project.py my-api --stack python
    python scaffold_project.py my-api --path ./projects
"""

import argparse
import os
import sys

def create_file(path: str, content: str):
    """Create a file with the given content."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  ✅ Created {path}")

def scaffold_node_project(project_path: str, project_name: str):
    """Scaffold a Node.js + Express + TypeScript project."""
    
    # package.json
    create_file(f"{project_path}/package.json", f'''{{\n  "name": "{project_name}",
  "version": "1.0.0",
  "main": "dist/server.js",
  "scripts": {{
    "dev": "nodemon --exec ts-node src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "test": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src --ext .ts"
  }},
  "dependencies": {{
    "@supabase/supabase-js": "^2.39.0",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "helmet": "^7.1.0",
    "zod": "^3.22.4"
  }},
  "devDependencies": {{
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "nodemon": "^3.0.2",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.2",
    "vitest": "^1.0.0"
  }}
}}
''')

    # tsconfig.json
    create_file(f"{project_path}/tsconfig.json", '''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
''')

    # .env.example
    create_file(f"{project_path}/.env.example", '''NODE_ENV=development
PORT=3000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Optional
CORS_ORIGIN=http://localhost:5173
LOG_LEVEL=debug
''')

    # .gitignore
    create_file(f"{project_path}/.gitignore", '''node_modules/
dist/
.env
.env.local
*.log
.DS_Store
coverage/
''')

    # src/config/env.ts
    create_file(f"{project_path}/src/config/env.ts", '''import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  supabaseUrl: process.env.SUPABASE_URL!,
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY!,
  supabaseServiceKey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
  corsOrigin: process.env.CORS_ORIGIN || '*',
  logLevel: process.env.LOG_LEVEL || 'info',
};

// Validate required env vars
const required = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}
''')

    # src/services/supabase.ts
    create_file(f"{project_path}/src/services/supabase.ts", '''import {{ createClient }} from '@supabase/supabase-js';
import {{ config }} from '../config/env';

// Public client (respects RLS)
export const supabase = createClient(config.supabaseUrl, config.supabaseAnonKey);

// Admin client (bypasses RLS - use carefully)
export const supabaseAdmin = createClient(config.supabaseUrl, config.supabaseServiceKey);
''')

    # src/middleware/auth.ts
    create_file(f"{project_path}/src/middleware/auth.ts", '''import {{ Request, Response, NextFunction }} from 'express';
import {{ supabase }} from '../services/supabase';

export interface AuthRequest extends Request {{
  user?: {{ id: string; email: string; role: string }};
}}

export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {{
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {{
    return res.status(401).json({{ error: 'No token provided' }});
  }}

  const {{ data: {{ user }}, error }} = await supabase.auth.getUser(token);
  
  if (error || !user) {{
    return res.status(401).json({{ error: 'Invalid token' }});
  }}

  req.user = {{ id: user.id, email: user.email!, role: user.role || 'user' }};
  next();
}};
''')

    # src/middleware/error.ts
    create_file(f"{project_path}/src/middleware/error.ts", '''import {{ Request, Response, NextFunction }} from 'express';

export class AppError extends Error {{
  constructor(
    public statusCode: number,
    public message: string,
    public code?: string
  ) {{
    super(message);
  }}
}}

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {{
  console.error(err);

  if (err instanceof AppError) {{
    return res.status(err.statusCode).json({{
      error: err.message,
      code: err.code,
    }});
  }}

  res.status(500).json({{ error: 'Internal server error' }});
}};
''')

    # src/routes/health.ts
    create_file(f"{project_path}/src/routes/health.ts", '''import {{ Router }} from 'express';
import {{ supabase }} from '../services/supabase';

const router = Router();

router.get('/health', async (req, res) => {{
  try {{
    const start = Date.now();
    
    res.json({{
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      responseTime: Date.now() - start,
    }});
  }} catch (err) {{
    res.status(503).json({{
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
    }});
  }}
}});

export default router;
''')

    # src/routes/auth.ts
    create_file(f"{project_path}/src/routes/auth.ts", '''import {{ Router }} from 'express';
import {{ supabase }} from '../services/supabase';

const router = Router();

router.post('/signup', async (req, res) => {{
  const {{ email, password }} = req.body;
  const {{ data, error }} = await supabase.auth.signUp({{ email, password }});
  
  if (error) return res.status(400).json({{ error: error.message }});
  res.status(201).json({{ user: data.user, session: data.session }});
}});

router.post('/signin', async (req, res) => {{
  const {{ email, password }} = req.body;
  const {{ data, error }} = await supabase.auth.signInWithPassword({{ email, password }});
  
  if (error) return res.status(401).json({{ error: error.message }});
  res.json({{ user: data.user, session: data.session }});
}});

router.post('/signout', async (req, res) => {{
  const {{ error }} = await supabase.auth.signOut();
  
  if (error) return res.status(400).json({{ error: error.message }});
  res.json({{ message: 'Signed out successfully' }});
}});

export default router;
''')

    # src/routes/index.ts
    create_file(f"{project_path}/src/routes/index.ts", '''import {{ Router }} from 'express';
import healthRoutes from './health';
import authRoutes from './auth';

const router = Router();

router.use(healthRoutes);
router.use('/auth', authRoutes);

export default router;
''')

    # src/app.ts
    create_file(f"{project_path}/src/app.ts", '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import {{ config }} from './config/env';
import {{ errorHandler }} from './middleware/error';
import routes from './routes';

export const app = express();

// Security middleware
app.use(helmet());
app.use(cors({{ origin: config.corsOrigin }}));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);
''')

    # src/server.ts
    create_file(f"{project_path}/src/server.ts", '''import {{ app }} from './app';
import {{ config }} from './config/env';

const server = app.listen(config.port, () => {{
  console.log(`🚀 Server running on port ${{config.port}}`);
  console.log(`📍 Environment: ${{config.nodeEnv}}`);
}});

// Graceful shutdown
const shutdown = (signal: string) => {{
  console.log(`${{signal}} received, shutting down gracefully`);
  server.close(() => {{
    console.log('HTTP server closed');
    process.exit(0);
  }});

  setTimeout(() => {{
    console.error('Forced shutdown');
    process.exit(1);
  }}, 10000);
}};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
''')

    # vitest.config.ts
    create_file(f"{project_path}/vitest.config.ts", '''import {{ defineConfig }} from 'vitest/config';

export default defineConfig({{
  test: {{
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {{
      provider: 'v8',
      reporter: ['text', 'html'],
    }},
  }},
}});
''')

    # tests/unit/.gitkeep
    os.makedirs(f"{project_path}/tests/unit", exist_ok=True)
    create_file(f"{project_path}/tests/unit/.gitkeep", '')

    # tests/integration/.gitkeep
    os.makedirs(f"{project_path}/tests/integration", exist_ok=True)
    create_file(f"{project_path}/tests/integration/.gitkeep", '')

    print(f"\n✅ Node.js project scaffolded successfully!")
    print(f"\nNext steps:")
    print(f"  1. cd {project_name}")
    print(f"  2. cp .env.example .env")
    print(f"  3. Update .env with your Supabase credentials")
    print(f"  4. npm install")
    print(f"  5. npm run dev")


def scaffold_python_project(project_path: str, project_name: str):
    """Scaffold a Python + FastAPI project."""
    
    # requirements.txt
    create_file(f"{project_path}/requirements.txt", '''fastapi==0.108.0
uvicorn[standard]==0.25.0
python-dotenv==1.0.0
supabase==2.3.0
pydantic==2.5.0
pydantic-settings==2.1.0
''')

    # requirements-dev.txt
    create_file(f"{project_path}/requirements-dev.txt", '''-r requirements.txt
pytest==7.4.0
pytest-asyncio==0.23.0
httpx==0.26.0
''')

    # .env.example
    create_file(f"{project_path}/.env.example", '''ENV=development
PORT=8000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Optional
CORS_ORIGIN=http://localhost:5173
''')

    # .gitignore
    create_file(f"{project_path}/.gitignore", '''__pycache__/
*.py[cod]
*$py.class
.env
.env.local
venv/
.venv/
*.log
.DS_Store
.pytest_cache/
htmlcov/
.coverage
''')

    # app/config.py
    create_file(f"{project_path}/app/config.py", '''from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "development"
    port: int = 8000
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    cors_origin: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
''')

    # app/services/supabase.py
    create_file(f"{project_path}/app/services/supabase.py", '''from supabase import create_client, Client
from app.config import settings

# Public client (respects RLS)
supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)

# Admin client (bypasses RLS - use carefully)
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
''')

    # app/middleware/auth.py
    create_file(f"{project_path}/app/middleware/auth.py", '''from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.supabase import supabase

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    try:
        response = supabase.auth.get_user(token)
        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
''')

    # app/routes/health.py
    create_file(f"{project_path}/app/routes/health.py", '''from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
''')

    # app/routes/auth.py
    create_file(f"{project_path}/app/routes/auth.py", '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.supabase import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(request: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })
        return {"user": response.user, "session": response.session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin")
async def signin(request: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })
        return {"user": response.user, "session": response.session}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/signout")
async def signout():
    try:
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
''')

    # app/main.py
    create_file(f"{project_path}/app/main.py", '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, auth

app = FastAPI(
    title="''' + project_name + '''",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
''')

    # app/__init__.py
    create_file(f"{project_path}/app/__init__.py", '')
    create_file(f"{project_path}/app/routes/__init__.py", '')
    create_file(f"{project_path}/app/services/__init__.py", '')
    create_file(f"{project_path}/app/middleware/__init__.py", '')

    # tests directory
    os.makedirs(f"{project_path}/tests", exist_ok=True)
    create_file(f"{project_path}/tests/__init__.py", '')
    create_file(f"{project_path}/tests/conftest.py", '''import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
''')

    print(f"\n✅ Python/FastAPI project scaffolded successfully!")
    print(f"\nNext steps:")
    print(f"  1. cd {project_name}")
    print(f"  2. python -m venv venv")
    print(f"  3. source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
    print(f"  4. pip install -r requirements.txt")
    print(f"  5. cp .env.example .env")
    print(f"  6. Update .env with your Supabase credentials")
    print(f"  7. uvicorn app.main:app --reload")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new backend project with Supabase integration"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--stack",
        choices=["node", "python"],
        default="node",
        help="Tech stack (default: node)"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    project_path = os.path.join(args.path, args.name)

    if os.path.exists(project_path):
        print(f"❌ Error: Directory '{project_path}' already exists")
        sys.exit(1)

    print(f"🚀 Creating {args.stack} backend project: {args.name}")
    print(f"   Location: {os.path.abspath(project_path)}\n")

    os.makedirs(project_path)

    if args.stack == "node":
        scaffold_node_project(project_path, args.name)
    else:
        scaffold_python_project(project_path, args.name)


if __name__ == "__main__":
    main()
