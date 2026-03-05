# Agent-Centric Development Infrastructure

This directory is the **canonical location** for all AI agent configurations, skills, commands, workflows, and tool-specific plugins used in this project.

## Directory Structure

```
.agents/
├── skills/              # Reusable skill definitions (SKILL.md + scripts)
├── commands/            # Slash-commands (/setup, /test, /lint, /deploy)
├── workflows/           # Multi-step development workflows
├── hooks/               # Git lifecycle hooks for agents
├── plugins/             # Tool-specific configs (cursor, windsurf, claude, gemini)
└── config.yaml          # Global agent configuration
```

## How It Works

Different AI tools expect configuration in different locations. This project uses **symlinks** to map tool-specific paths back to this canonical `.agents/` directory:

| Tool | Expected Path | Symlink Target |
|------|--------------|----------------|
| Cursor | `.cursor/rules/` | `.agents/plugins/cursor/` |
| Windsurf | `windsurf-configs/` | `.agents/plugins/windsurf/` |
| Claude | `.claude/` | `.agents/plugins/claude/` |
| Gemini/Antigravity | `.agents/` | *(canonical, no symlink needed)* |

## Skills

Skills are self-contained, reusable capabilities with a `SKILL.md` frontmatter format:

```yaml
---
name: skill-name
description: What this skill does
---
Detailed instructions...
```

## Adding New Skills

1. Create a folder under `skills/` with a descriptive name
2. Add a `SKILL.md` with YAML frontmatter
3. Optionally add `scripts/`, `examples/`, `resources/` subdirectories
