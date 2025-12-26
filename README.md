# Full-Stack Dev Marketplace

A Claude Code plugin marketplace with full-stack development skills.

## Installation

```bash
# Add this marketplace
/plugin marketplace add sai-sundar/fullstack-dev-skills

# Install the plugin
/plugin install fullstack-dev-skills@fullstack-dev-marketplace
```

## Plugins Available

### fullstack-dev-skills

5 comprehensive skills for full-stack development:

| Skill | Description |
|-------|-------------|
| 🎓 dev-teacher | Learn codebases, onboard developers, interactive Q&A |
| 🏗️ technical-architect | System design, API contracts, database schemas |
| ⚙️ backend-developer | Node.js/Express, Supabase, authentication |
| 🎨 frontend-developer | React/Vite, animations, design systems |
| 🧪 qa-engineer | Testing, validation, design benchmarking |

## Structure

```
fullstack-dev-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
└── fullstack-dev-skills/     # Plugin
    ├── .claude-plugin/
    │   └── plugin.json       # Plugin manifest
    ├── skills/
    │   ├── dev-teacher/
    │   ├── technical-architect/
    │   ├── backend-developer/
    │   ├── frontend-developer/
    │   └── qa-engineer/
    └── README.md
```

## License

MIT
