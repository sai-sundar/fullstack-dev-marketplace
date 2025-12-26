# Full-Stack Development Skills Plugin

A Claude Code plugin with **5 comprehensive skills** for full-stack development teams.

## Installation

### Option 1: From GitHub (Recommended)

```bash
# In Claude Code, run:
/plugin marketplace add YOUR_USERNAME/fullstack-dev-skills

# Then install:
/plugin install fullstack-dev-skills@YOUR_USERNAME
```

### Option 2: From Local Marketplace

```bash
# Create a local marketplace
mkdir -p ~/claude-marketplace
cp -r fullstack-dev-plugin ~/claude-marketplace/

# Create marketplace.json
cat > ~/claude-marketplace/.claude-plugin/marketplace.json << 'EOF'
{
  "name": "my-marketplace",
  "description": "My local plugin marketplace",
  "plugins": ["fullstack-dev-plugin"]
}
EOF

# Add marketplace in Claude Code
/plugin marketplace add ~/claude-marketplace

# Install plugin
/plugin install fullstack-dev-skills@my-marketplace
```

## Skills Included (5 Total)

### 🎓 dev-teacher
**Learn codebases and onboard developers**

Triggers on:
- "Teach me this codebase"
- "Explain how X works"
- "Quiz me on [topic]"
- "What should I learn next?"
- "Help onboard a new developer"

Features:
- Socratic method teaching
- Interactive Q&A
- Codebase tours
- Personalized learning paths
- Quiz generation
- Onboarding document creation

### 🏗️ technical-architect
**System design and API contracts**

Triggers on:
- "Design the architecture"
- "Create API contracts"
- "Plan the database schema"
- "Set up project structure"
- "What's the best approach for..."

Features:
- Binding contracts (database.sql, types.ts, endpoints.ts)
- OpenAPI specification generation
- Database schema design
- Monorepo setup
- Architecture Decision Records (ADRs)
- Mermaid diagrams

### ⚙️ backend-developer
**Node.js/Express API development with Supabase**

Triggers on:
- "Build the API endpoint"
- "Create the database schema"
- "Implement authentication"
- "Write backend tests"
- "Set up Supabase"

Features:
- Express route patterns
- Supabase integration (auth, database, storage)
- Service layer architecture
- API validation with Zod
- Backend testing patterns
- RLS policy implementation

### 🎨 frontend-developer
**React/Vite frontend development**

Triggers on:
- "Build the UI component"
- "Create the dashboard"
- "Implement the form"
- "Add animations"
- "Style this component"

Features:
- React component patterns
- Custom hooks
- Tailwind CSS styling
- Framer Motion animations
- Chrome DevTools MCP integration
- Playwright MCP for E2E testing
- Non-generic, distinctive design aesthetics

### 🧪 qa-engineer
**Testing and validation**

Triggers on:
- "Write tests for this"
- "Check for errors"
- "Run E2E tests"
- "Validate the UI"
- "Check frontend-backend integration"
- "Compare design to competitors"

Features:
- Unit/integration/E2E test patterns
- Browser validation (Chrome DevTools MCP)
- Playwright MCP integration
- Frontend-backend sync validation
- Accessibility audits
- Design benchmarking against competitors

## Workflow

```
┌─────────────────────────────────────────┐
│            dev-teacher                  │
│        "Teach me this codebase"         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        technical-architect              │
│      "Design the new feature"           │
│      Creates contracts/ directory       │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   backend-    │   │   frontend-   │
│   developer   │   │   developer   │
│ (from shared  │   │ (from shared  │
│   contracts)  │   │   contracts)  │
└───────┬───────┘   └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  ▼
┌─────────────────────────────────────────┐
│            qa-engineer                  │
│    "Validate the integration"           │
└─────────────────────────────────────────┘
```

## Usage Examples

### Learning a New Codebase
```
You: "Teach me this codebase"
Claude: [Uses dev-teacher skill to give guided tour with questions]
```

### Designing a Feature
```
You: "Design the API for user authentication"
Claude: [Uses technical-architect to create contracts/]
```

### Validating Integration
```
You: "Check if frontend and backend are in sync"
Claude: [Uses qa-engineer to validate contracts match implementation]
```

### Running Tests
```
You: "Write E2E tests for the login flow"
Claude: [Uses qa-engineer to generate Playwright tests]
```

## Team Sharing

### Share via Git Repository

1. Push this plugin to your GitHub:
```bash
cd fullstack-dev-plugin
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/fullstack-dev-skills.git
git push -u origin main
```

2. Team members install with:
```bash
/plugin marketplace add YOUR_USERNAME/fullstack-dev-skills
/plugin install fullstack-dev-skills@YOUR_USERNAME
```

### Share via Organization Marketplace

Create a shared marketplace for your team:

1. Create marketplace repo with multiple plugins
2. Team adds the marketplace once
3. All plugins available to install

## Customizing Skills

After installation, skills are at `~/.claude/plugins/...`

To customize for your project:
```bash
# Copy to project level
cp -r ~/.claude/skills/dev-teacher ./.claude/skills/

# Edit SKILL.md to add project-specific patterns
```

## Requirements

- Claude Code v2.0.12 or higher
- For browser testing: Chrome DevTools MCP, Playwright MCP

## License

MIT License - Use freely, modify as needed, share with your team.
