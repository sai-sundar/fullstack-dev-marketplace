# Codebase Analysis

Automatically analyze codebases to generate learning materials, identify technologies, and create onboarding content.

## Table of Contents
1. Project Detection
2. Architecture Mapping
3. Technology Identification
4. Learning Content Generation
5. Complexity Assessment

---

## 1. Project Detection

### Detect Project Type

```python
def detect_project_type(project_dir: Path) -> dict:
    """Analyze project to determine type and structure."""
    
    result = {
        'type': 'unknown',
        'frontend': None,
        'backend': None,
        'database': None,
        'monorepo': False,
    }
    
    # Check for monorepo
    if (project_dir / 'apps').exists() or (project_dir / 'packages').exists():
        result['monorepo'] = True
        result['type'] = 'fullstack-monorepo'
    
    # Detect frontend
    if (project_dir / 'package.json').exists():
        pkg = json.loads((project_dir / 'package.json').read_text())
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        
        if 'react' in deps:
            result['frontend'] = 'react'
        elif 'vue' in deps:
            result['frontend'] = 'vue'
        elif 'svelte' in deps:
            result['frontend'] = 'svelte'
        elif 'next' in deps:
            result['frontend'] = 'nextjs'
    
    # Detect backend
    if 'express' in deps:
        result['backend'] = 'express'
    elif 'fastify' in deps:
        result['backend'] = 'fastify'
    elif (project_dir / 'requirements.txt').exists():
        reqs = (project_dir / 'requirements.txt').read_text()
        if 'fastapi' in reqs:
            result['backend'] = 'fastapi'
        elif 'django' in reqs:
            result['backend'] = 'django'
    
    # Detect database
    if '@supabase/supabase-js' in deps:
        result['database'] = 'supabase'
    elif 'prisma' in deps:
        result['database'] = 'prisma'
    elif 'pg' in deps:
        result['database'] = 'postgresql'
    
    return result
```

### Identify Key Files

```python
KEY_FILES = {
    'config': [
        'package.json',
        'tsconfig.json',
        'vite.config.ts',
        '.env.example',
        'turbo.json',
    ],
    'contracts': [
        'contracts/database.sql',
        'contracts/types.ts',
        'contracts/endpoints.ts',
    ],
    'documentation': [
        'README.md',
        'CONTRIBUTING.md',
        'docs/architecture.md',
    ],
    'entry_points': [
        'apps/web/src/main.tsx',
        'apps/server/src/index.ts',
        'src/index.ts',
    ],
}

def find_key_files(project_dir: Path) -> dict:
    """Find important files for learning."""
    found = {}
    for category, patterns in KEY_FILES.items():
        found[category] = []
        for pattern in patterns:
            path = project_dir / pattern
            if path.exists():
                found[category].append(str(path))
    return found
```

---

## 2. Architecture Mapping

### Generate Architecture Diagram

```python
def generate_architecture_diagram(project_dir: Path) -> str:
    """Generate Mermaid diagram of project architecture."""
    
    project = detect_project_type(project_dir)
    
    if project['monorepo']:
        return generate_monorepo_diagram(project_dir)
    else:
        return generate_simple_diagram(project_dir)


def generate_monorepo_diagram(project_dir: Path) -> str:
    """Generate diagram for monorepo structure."""
    
    apps = list((project_dir / 'apps').iterdir()) if (project_dir / 'apps').exists() else []
    packages = list((project_dir / 'packages').iterdir()) if (project_dir / 'packages').exists() else []
    
    diagram = """```mermaid
graph TB
    subgraph Apps
"""
    
    for app in apps:
        if app.is_dir():
            diagram += f"        {app.name}[{app.name}]\n"
    
    diagram += """    end
    
    subgraph Packages
"""
    
    for pkg in packages:
        if pkg.is_dir():
            diagram += f"        {pkg.name}[{pkg.name}]\n"
    
    diagram += """    end
    
    subgraph External
        DB[(Database)]
        Auth[Auth Provider]
    end
"""
    
    # Add connections
    if 'web' in [a.name for a in apps] and 'server' in [a.name for a in apps]:
        diagram += "    web --> server\n"
    if 'server' in [a.name for a in apps]:
        diagram += "    server --> DB\n"
        diagram += "    server --> Auth\n"
    if 'shared' in [p.name for p in packages]:
        diagram += "    web --> shared\n"
        diagram += "    server --> shared\n"
    
    diagram += "```"
    
    return diagram
```

### Map Data Flow

```python
def trace_data_flow(project_dir: Path, feature: str) -> list:
    """Trace data flow for a specific feature."""
    
    flow = []
    
    # Find frontend component
    frontend_files = list((project_dir / 'apps' / 'web' / 'src').rglob(f'*{feature}*.tsx'))
    if frontend_files:
        flow.append({
            'layer': 'Frontend Component',
            'file': str(frontend_files[0]),
            'description': 'User interface for the feature',
        })
    
    # Find API calls
    # (simplified - real implementation would parse AST)
    flow.append({
        'layer': 'API Call',
        'file': 'apps/web/src/api/client.ts',
        'description': 'HTTP request to backend',
    })
    
    # Find backend route
    route_files = list((project_dir / 'apps' / 'server' / 'src').rglob('*route*.ts'))
    if route_files:
        flow.append({
            'layer': 'Backend Route',
            'file': str(route_files[0]),
            'description': 'Handles incoming HTTP request',
        })
    
    # Find service
    service_files = list((project_dir / 'apps' / 'server' / 'src' / 'services').rglob('*.ts'))
    if service_files:
        flow.append({
            'layer': 'Service Layer',
            'file': str(service_files[0]),
            'description': 'Business logic processing',
        })
    
    # Database
    flow.append({
        'layer': 'Database',
        'file': 'contracts/database.sql',
        'description': 'Data persistence',
    })
    
    return flow
```

---

## 3. Technology Identification

### Extract Tech Stack

```python
def extract_tech_stack(project_dir: Path) -> dict:
    """Extract complete technology stack from project."""
    
    stack = {
        'languages': set(),
        'frameworks': set(),
        'libraries': set(),
        'tools': set(),
        'services': set(),
    }
    
    # Check package.json
    pkg_path = project_dir / 'package.json'
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text())
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        
        stack['languages'].add('TypeScript' if 'typescript' in deps else 'JavaScript')
        
        # Frameworks
        framework_map = {
            'react': 'React',
            'next': 'Next.js',
            'vue': 'Vue.js',
            'express': 'Express',
            'fastify': 'Fastify',
        }
        for dep, name in framework_map.items():
            if dep in deps:
                stack['frameworks'].add(name)
        
        # Libraries
        library_map = {
            'zod': 'Zod (validation)',
            '@tanstack/react-query': 'TanStack Query (data fetching)',
            'zustand': 'Zustand (state management)',
            '@supabase/supabase-js': 'Supabase Client',
            'tailwindcss': 'Tailwind CSS',
            'framer-motion': 'Framer Motion (animations)',
        }
        for dep, name in library_map.items():
            if dep in deps:
                stack['libraries'].add(name)
        
        # Tools
        tool_map = {
            'vite': 'Vite (build tool)',
            'vitest': 'Vitest (testing)',
            'eslint': 'ESLint (linting)',
            'prettier': 'Prettier (formatting)',
            'turbo': 'Turborepo (monorepo)',
        }
        for dep, name in tool_map.items():
            if dep in deps:
                stack['tools'].add(name)
    
    # Check for services in code
    if (project_dir / 'contracts' / 'database.sql').exists():
        stack['services'].add('PostgreSQL (via Supabase)')
    
    return {k: list(v) for k, v in stack.items()}
```

### Generate Learning Resources

```python
LEARNING_RESOURCES = {
    'React': {
        'official': 'https://react.dev',
        'tutorial': 'https://react.dev/learn',
        'key_concepts': ['Components', 'Props', 'State', 'Hooks', 'Effects'],
    },
    'TypeScript': {
        'official': 'https://www.typescriptlang.org',
        'tutorial': 'https://www.typescriptlang.org/docs/handbook/',
        'key_concepts': ['Types', 'Interfaces', 'Generics', 'Type Guards'],
    },
    'Express': {
        'official': 'https://expressjs.com',
        'tutorial': 'https://expressjs.com/en/starter/installing.html',
        'key_concepts': ['Routing', 'Middleware', 'Request/Response', 'Error Handling'],
    },
    'Supabase': {
        'official': 'https://supabase.com/docs',
        'tutorial': 'https://supabase.com/docs/guides/getting-started',
        'key_concepts': ['Auth', 'Database', 'Storage', 'RLS Policies'],
    },
    'Zod': {
        'official': 'https://zod.dev',
        'tutorial': 'https://zod.dev/?id=basic-usage',
        'key_concepts': ['Schemas', 'Parsing', 'Validation', 'Type Inference'],
    },
}

def get_learning_resources(stack: dict) -> list:
    """Get relevant learning resources based on tech stack."""
    
    resources = []
    
    for category in stack.values():
        for tech in category:
            # Extract base name (remove parenthetical descriptions)
            base_name = tech.split(' (')[0]
            if base_name in LEARNING_RESOURCES:
                resources.append({
                    'technology': base_name,
                    **LEARNING_RESOURCES[base_name]
                })
    
    return resources
```

---

## 4. Learning Content Generation

### Generate Codebase Overview

```python
def generate_overview(project_dir: Path) -> str:
    """Generate human-readable codebase overview."""
    
    project = detect_project_type(project_dir)
    stack = extract_tech_stack(project_dir)
    key_files = find_key_files(project_dir)
    
    overview = f"""# Codebase Overview

## Project Type
This is a **{project['type']}** project.

## Technology Stack

### Languages
{chr(10).join(f'- {lang}' for lang in stack['languages'])}

### Frameworks
{chr(10).join(f'- {fw}' for fw in stack['frameworks'])}

### Key Libraries
{chr(10).join(f'- {lib}' for lib in stack['libraries'])}

### Development Tools
{chr(10).join(f'- {tool}' for tool in stack['tools'])}

## Architecture

"""
    
    if project['monorepo']:
        overview += """This is a monorepo structure:

```
├── apps/
│   ├── web/        # Frontend React application
│   └── server/     # Backend Express API
├── packages/
│   └── shared/     # Shared types, schemas, utilities
└── contracts/      # API contracts and database schema
```

### Data Flow
1. User interacts with **web** app
2. **web** makes API calls to **server**
3. **server** processes requests using services
4. Services interact with **Supabase** database
5. Shared types in **packages/shared** ensure type safety

"""
    
    overview += """## Key Files to Explore

"""
    
    for category, files in key_files.items():
        if files:
            overview += f"### {category.title()}\n"
            for f in files:
                overview += f"- `{f}`\n"
            overview += "\n"
    
    return overview
```

### Generate Learning Path from Codebase

```python
def generate_learning_path(project_dir: Path, skill_level: str) -> str:
    """Generate personalized learning path based on codebase and skill level."""
    
    stack = extract_tech_stack(project_dir)
    resources = get_learning_resources(stack)
    
    path = f"""# Learning Path for This Codebase

## Your Level: {skill_level.title()}

"""
    
    if skill_level == 'junior':
        path += """## Week 1-2: Foundations

Before diving into the codebase, make sure you understand:

"""
        for resource in resources[:3]:
            path += f"""### {resource['technology']}
- **Official Docs**: {resource['official']}
- **Key Concepts to Learn**: {', '.join(resource['key_concepts'][:3])}

"""
        
        path += """## Week 3-4: Codebase Exploration

Now explore the actual codebase:

1. **Day 1-2**: Run the project locally
   - Follow README setup instructions
   - Make sure all services start correctly
   
2. **Day 3-5**: Explore the structure
   - Use the dev-teacher skill: "Give me a tour of this codebase"
   - Take notes on what each folder contains
   
3. **Day 6-10**: Trace a feature
   - Pick one feature (e.g., CV upload)
   - Follow the data from UI to database
   - Ask: "Explain how CV upload works"

"""
    
    elif skill_level == 'mid':
        path += """## Week 1: Architecture Deep Dive

You likely know the basics. Focus on:

1. **Day 1-2**: Understand the contracts/ pattern
   - Why shared types?
   - How does this prevent bugs?
   
2. **Day 3-4**: Service layer architecture
   - Why separate routes, controllers, services?
   - How is dependency injection used?
   
3. **Day 5**: Testing patterns
   - How are services tested?
   - Integration vs unit tests

## Week 2: Hands-On Contribution

1. **Day 1-3**: Fix a medium-complexity bug
2. **Day 4-5**: Add a small feature end-to-end

"""
    
    else:  # senior
        path += """## Quick Onboarding (3 days)

You know the technologies. Focus on:

1. **Day 1**: Architecture decisions
   - Read all ADRs in docs/decisions/
   - Ask: "Explain the key architecture decisions"
   
2. **Day 2**: Code patterns and conventions
   - Review PR history for patterns
   - Ask: "What conventions does this codebase follow?"
   
3. **Day 3**: Improvement opportunities
   - Identify technical debt
   - Propose architectural improvements

"""
    
    return path
```

---

## 5. Complexity Assessment

### Assess Learning Curve

```python
def assess_complexity(project_dir: Path) -> dict:
    """Assess project complexity for learning purposes."""
    
    metrics = {
        'file_count': 0,
        'loc': 0,  # lines of code
        'unique_dependencies': 0,
        'custom_patterns': [],
        'estimated_learning_hours': 0,
    }
    
    # Count files
    for ext in ['*.ts', '*.tsx', '*.js', '*.jsx']:
        metrics['file_count'] += len(list(project_dir.rglob(ext)))
    
    # Count lines (simplified)
    for ts_file in project_dir.rglob('*.ts'):
        try:
            metrics['loc'] += len(ts_file.read_text().splitlines())
        except:
            pass
    
    # Count dependencies
    pkg_path = project_dir / 'package.json'
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text())
        deps = pkg.get('dependencies', {})
        dev_deps = pkg.get('devDependencies', {})
        metrics['unique_dependencies'] = len(deps) + len(dev_deps)
    
    # Detect custom patterns
    if (project_dir / 'contracts').exists():
        metrics['custom_patterns'].append('Contracts Pattern')
    if (project_dir / 'apps' / 'server' / 'src' / 'services').exists():
        metrics['custom_patterns'].append('Service Layer')
    
    # Estimate learning hours
    # Base: 1 hour per 1000 LOC, adjusted for complexity
    base_hours = metrics['loc'] / 1000
    pattern_multiplier = 1 + (len(metrics['custom_patterns']) * 0.2)
    dep_multiplier = 1 + (metrics['unique_dependencies'] / 100)
    
    metrics['estimated_learning_hours'] = round(base_hours * pattern_multiplier * dep_multiplier)
    
    return metrics


def generate_complexity_report(project_dir: Path) -> str:
    """Generate complexity report for learners."""
    
    metrics = assess_complexity(project_dir)
    
    report = f"""# Codebase Complexity Report

## Size Metrics
- **Total Files**: {metrics['file_count']}
- **Lines of Code**: {metrics['loc']:,}
- **Dependencies**: {metrics['unique_dependencies']}

## Custom Patterns to Learn
{chr(10).join(f'- {p}' for p in metrics['custom_patterns']) or '- None detected'}

## Estimated Learning Time
**{metrics['estimated_learning_hours']} hours** to understand the codebase well enough to contribute confidently.

## Breakdown Suggestion
- 20% - Setup and running locally
- 30% - Understanding architecture
- 30% - Tracing features through code
- 20% - Making first contributions

"""
    
    return report
```

---

## Usage in Teaching

When a learner says "teach me this codebase", run:

```python
# 1. Detect project type
project = detect_project_type(project_dir)

# 2. Generate overview
overview = generate_overview(project_dir)

# 3. Assess complexity
complexity = generate_complexity_report(project_dir)

# 4. Create personalized learning path
path = generate_learning_path(project_dir, learner_level)

# 5. Start interactive session with context
```

This gives the teacher enough context to guide the learner effectively through the specific codebase.
