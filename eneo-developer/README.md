# Eneo Developer Plugin

Specialized agents and automation Skills for Eneo AI platform development.

## Installation

### Add Marketplace

```bash
/plugin marketplace add ./eneo-dev-marketplace
```

### Install Plugin

```bash
/plugin install eneo-developer@eneo-dev-marketplace
```

**Restart Claude Code after installation.**

## Included Agents

1. **eneo-ddd-architect** - Architecture decisions, domain modeling, API design
2. **eneo-python-implementation** - Backend Python/FastAPI implementation
3. **eneo-frontend-svelte-expert** - Frontend Svelte 5/SvelteKit development
4. **eneo-code-reviewer** - Code quality, security, and maintainability review
5. **eneo-ui-ux-designer** - UI/UX design specifications

## Included Skills

### Phase 1 (High Value)

- **scaffold-domain** - Generate DDD 4-layer structure (2-3h → 10min)
- **generate-migration** - Create Alembic migrations (30min → 5min)
- **i18n-sync** - Sync sv.json/en.json translations (15min → 2min)
- **space-permission-validator** - Validate permission checks (security-critical)

### Phase 2 (Medium Value)

- **test-fixture-generator** - Generate pytest fixtures (45min → 10min)
- **eager-loading-analyzer** - Detect N+1 queries (1h → 5min)
- **svelte-component-scaffold** - Scaffold Svelte 5 components (30min → 5min)

## Prerequisites

- Claude Code 1.0+
- Eneo project context (CLAUDE.md in your Eneo project)
- Python 3.11+ with uv (for Skills)
- Bun (for frontend Skills and MCP servers)

### Python Dependencies for Skills

```bash
pip install jinja2 click
```

### Included MCP Servers

The plugin automatically configures these MCP servers:

1. **Svelte MCP** (https://mcp.svelte.dev/mcp)
   - Required by: eneo-frontend-svelte-expert
   - Provides: Svelte 5 documentation, code validation, playground links

2. **Sequential Thinking MCP** (@modelcontextprotocol/server-sequential-thinking)
   - Enhances: All agents with structured reasoning
   - Provides: Multi-step problem solving, hypothesis testing

**MCP servers are installed automatically** when you install the plugin (no manual setup needed).

## Quick Start

After installation, agents and Skills are automatically available:

### Using Agents

```bash
# View available agents
/agents

# Agents activate automatically based on context
# Example: "Design a new notifications domain with DDD"
# → eneo-ddd-architect will be invoked
```

### Using Skills

Skills activate automatically when Claude detects relevant context:

```
# Example: "Create a new notifications domain"
# → scaffold-domain Skill activates automatically

# Example: "Sync translations for notification UI"
# → i18n-sync Skill activates automatically
```

## Agent Workflow Examples

### Full Feature Development

1. **Design**: "Design a notifications domain with DDD and Space scoping"
   - Uses: eneo-ddd-architect

2. **Implementation**: "Implement the notification service and API"
   - Uses: eneo-python-implementation, scaffold-domain Skill

3. **Frontend**: "Create notification center page with Svelte 5"
   - Uses: eneo-frontend-svelte-expert, eneo-ui-ux-designer

4. **Review**: "Review the notifications implementation for security"
   - Uses: eneo-code-reviewer, space-permission-validator Skill

### Skill Usage

Skills are invoked automatically by Claude:

**scaffold-domain**:
```
"Create a new webhooks domain with tenant and space scoping"
```

**i18n-sync**:
```
"Add translation keys for webhook_title and webhook_description"
```

**space-permission-validator**:
```
"Validate permissions for the webhooks domain"
```

## Development Workflow

1. Start Claude Code in Eneo project directory
2. Ask for architectural design or implementation
3. Agents and Skills work together automatically
4. Review generated code and customize business logic
5. Run tests: `uv run pytest`

## Notes

- **scaffold-domain** has full implementation with templates
- Other Skills have placeholder implementations (marked with "⚠️ Full implementation coming soon")
- All agents work immediately after installation
- Skills require Python dependencies (`jinja2`, `click`)
- No SuperClaude framework required

## Architecture

The plugin follows Eneo's patterns:
- DDD 4-layer structure (api/, application/, domain/, infrastructure/)
- Multi-tenancy (tenant_id on all entities)
- Space-scoped permissions
- UUID primary keys
- Soft deletes (deleted_at)
- SQLAlchemy async with N+1 prevention
- Pydantic v2 validation
- FastAPI with OpenAPI docs

## License

AGPL-3.0 (matching Eneo platform)

## Support

For issues or questions:
- Check SKILL.md files for detailed documentation
- Review agent descriptions with `/agents`
- Ask Claude: "What Skills are available?"

---

**Version**: 1.0.0
**Created**: 2025-11-13
**Eneo Core Team**
