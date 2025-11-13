# Eneo Developer Plugin

Specialized agents and automation Skills for Eneo AI platform development.

## Installation

### Quick Start

```bash
# Add marketplace
/plugin marketplace add https://github.com/CCimen/eneo-plugin

# Install plugin
/plugin install eneo-developer@eneo-plugin
```

**Restart after installation.**

---

## What's Included

### 5 Specialized Agents

1. **eneo-ddd-architect** - Architecture decisions, domain modeling, API design
2. **eneo-python-implementation** - Backend Python/FastAPI implementation
3. **eneo-frontend-svelte-expert** - Frontend Svelte 5/SvelteKit development
4. **eneo-code-reviewer** - Code quality, security, and maintainability review
5. **eneo-ui-ux-designer** - UI/UX design specifications

### 7 Automation Skills

**Fully Implemented** (3 Skills):
- **scaffold-domain** - Generate DDD 4-layer structure (2-3h → 10min)
- **i18n-sync** - Sync sv.json/en.json translations (15min → 2min)
- **generate-migration** - Enhance Alembic migrations (30min → 5min)

**Documented** (4 Skills - ready for future):
- **space-permission-validator** - Validate permission checks
- **test-fixture-generator** - Generate pytest fixtures
- **eager-loading-analyzer** - Detect N+1 queries
- **svelte-component-scaffold** - Scaffold Svelte 5 components

### 2 MCP Servers

1. **Svelte MCP** - Svelte 5 documentation & validation (required for frontend agent)
2. **Sequential Thinking** - Enhanced reasoning for all agents

---

## Prerequisites

- Python 3.11+ with uv
- Bun (for frontend)
- Git

### Python Dependencies

```bash
pip install jinja2 click
```

---

## Verify Installation

### Check Agents

```bash
/agents
```

Should show 5 eneo agents.

### Check Skills

Ask:
```
What Skills are available?
```

Should list 7 Skills.

---

## Usage Examples

### Using Agents

Agents activate automatically based on context:

```
"Design a new notifications domain with DDD and multi-tenancy"
→ eneo-ddd-architect activates

"Implement the notification service layer"
→ eneo-python-implementation activates

"Create a notification center page with Svelte 5"
→ eneo-frontend-svelte-expert activates

"Review the notifications code for security"
→ eneo-code-reviewer activates
```

### Using Skills

Skills activate automatically when relevant:

```
"Create a new webhooks domain with tenant and space scoping"
→ scaffold-domain Skill activates

"Check my translation files for missing keys"
→ i18n-sync Skill activates

"I just ran alembic autogenerate, help me add tenant indexes"
→ generate-migration Skill activates
```

---

## Testing the Skills

### Test i18n-sync (Paraglide)

```bash
cd frontend/apps/web

# Check for missing translation keys
python scripts/i18n-sync.py --check

# Extract usage from Svelte files
python scripts/i18n-extract.py --full

# Validate everything
python scripts/i18n-validate.py --full
```

### Test generate-migration (Alembic)

```bash
cd backend

# Check Alembic health
python scripts/generate-migration.py doctor

# View migration patterns
python scripts/generate-migration.py patterns
```

### Test scaffold-domain

```bash
# Generate a test domain (won't commit)
python scripts/scaffold-domain.py \
  --name test_notifications \
  --tenant-scoped \
  --space-scoped \
  --output-dir "/tmp/test-domain"

# Verify structure created
ls -la /tmp/test-domain/test_notifications/

# Clean up
rm -rf /tmp/test-domain
```

---

## Full Development Workflow

### Complete Feature Example

```
1. Design Phase:
   "Design a notifications domain with DDD and Space scoping"
   → eneo-ddd-architect

2. Scaffold Phase:
   "Create the notifications domain structure"
   → scaffold-domain Skill

3. Migration Phase:
   uv run alembic revision --autogenerate -m "add notifications table"
   "Enhance this migration with tenant indexes"
   → generate-migration Skill

4. Implementation Phase:
   "Implement the notification service and API"
   → eneo-python-implementation

5. Frontend Phase:
   "Create notification center page with Svelte 5"
   → eneo-frontend-svelte-expert + i18n-sync Skill

6. Review Phase:
   "Review the notifications implementation for security"
   → eneo-code-reviewer
```

---

## Updating the Plugin

To get the latest version:

```bash
/plugin update eneo-developer@eneo-plugin
```

Restart after updating.

---

## Uninstalling

If needed:

```bash
/plugin uninstall eneo-developer@eneo-plugin
```

---

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
- Svelte 5 with runes
- Paraglide i18n (sv/en)

---

## Troubleshooting

### Plugin Not Showing

1. Restart after installation
2. Check: `/plugin` to see installed plugins
3. Verify marketplace: `/plugin marketplace list`

### Skills Not Activating

1. Install Python deps: `pip install jinja2 click`
2. Make scripts executable: `chmod +x skills/*/scripts/*.py`
3. Check SKILL.md frontmatter syntax

### MCP Server Errors

1. Verify Bun: `which bun`
2. Check version: `bun --version`
3. Restart after installation

---

## Documentation

- **INSTALL.md** - Detailed installation guide
- **SHIPPING.md** - Shipping and distribution guide
- **eneo-developer/README.md** - Plugin features and usage
- **Skills/\*/SKILL.md** - Individual Skill documentation

---

## License

AGPL-3.0 (matching Eneo platform)

---

## Version

**1.0.0** (2025-11-13)

## Repository

https://github.com/CCimen/eneo-plugin

---

**Ready to accelerate Eneo development!** 🚀
