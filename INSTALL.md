# Installation Guide - Eneo Developer Plugin

Quick guide to install and use the eneo-developer plugin.

## Installation

### Step 1: Add Marketplace

```bash
/plugin marketplace add https://github.com/CCimen/eneo-plugin
```

### Step 2: Install Plugin

```bash
/plugin install eneo-developer@eneo-plugin
```

### Step 3: Restart

Close and reopen your CLI to activate the plugin.

---

## Verify Installation

### Check Agents

```bash
/agents
```

Should show 5 eneo agents:
- eneo-ddd-architect
- eneo-python-implementation
- eneo-frontend-svelte-expert
- eneo-code-reviewer
- eneo-ui-ux-designer

### Check Skills

Ask:
```
What Skills are available?
```

Should list 7 Skills:
- scaffold-domain (COMPLETE)
- i18n-sync (COMPLETE)
- generate-migration (COMPLETE)
- space-permission-validator (placeholder)
- test-fixture-generator (placeholder)
- eager-loading-analyzer (placeholder)
- svelte-component-scaffold (placeholder)

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

## Prerequisites

Before installation, ensure you have:

- Python 3.11+ with uv
- Bun (for frontend)
- Git

### Python Dependencies

```bash
pip install jinja2 click
```

---

## Quick Test

After installation, test with:

```bash
# Test i18n-sync
cd frontend/apps/web
python ../../eneo-plugin-repo/eneo-developer/skills/i18n-sync/scripts/i18n-sync.py --check

# Test migration doctor
cd backend
python ../eneo-plugin-repo/eneo-developer/skills/generate-migration/scripts/generate-migration.py doctor
```

---

## Updating the Plugin

To get the latest updates:

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

## Troubleshooting

### Plugin Not Showing Up

1. Restart after installation
2. Check: `/plugin` to see installed plugins
3. Verify marketplace: `/plugin marketplace list`

### Skills Not Activating

1. Check Python dependencies: `pip install jinja2 click`
2. Make scripts executable: `chmod +x skills/*/scripts/*.py`
3. Check SKILL.md files for errors

### MCP Server Errors

1. Verify Bun is installed: `which bun`
2. Check version: `bun --version` (requires recent version)
3. Restart after MCP installation

---

## Support

- Repository: https://github.com/CCimen/eneo-plugin
- Issues: https://github.com/CCimen/eneo-plugin/issues
- Documentation: See README.md and SHIPPING.md
