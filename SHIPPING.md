# Eneo Developer Plugin - Shipping Guide

Complete guide to shipping and using the eneo-developer plugin.

## 📦 What's in the Plugin

### ✅ Complete Features (Ready to Use)

**5 Specialized Agents** (61KB):
1. eneo-ddd-architect - Architecture & domain modeling
2. eneo-python-implementation - Backend Python/FastAPI
3. eneo-frontend-svelte-expert - Frontend Svelte 5/SvelteKit
4. eneo-code-reviewer - Code quality & security
5. eneo-ui-ux-designer - UI/UX design

**3 Fully Implemented Skills** (~1,644 lines):
1. scaffold-domain - DDD 4-layer generation (188 lines + 9 templates)
2. i18n-sync - Paraglide translation management (992 lines, 3 scripts)
3. generate-migration - Alembic migration enhancer (464 lines, 5 commands)

**2 MCP Servers**:
1. Svelte MCP - Svelte 5 documentation & validation
2. Sequential Thinking - Enhanced reasoning for all agents

**4 Placeholder Skills** (documentation complete, implementation pending):
1. space-permission-validator
2. test-fixture-generator
3. eager-loading-analyzer
4. svelte-component-scaffold

---

## 🚀 Shipping Options

### Option 1: Local Installation (Testing & Personal Use)

**Current setup** - Already ready! The plugin is in:
```
/Users/ccimen/dev/eneo/eneo-dev-marketplace/
```

**To use it now:**

```bash
# Start Claude Code from your Eneo project
cd /Users/ccimen/dev/eneo
claude

# Add marketplace
/plugin marketplace add ./eneo-dev-marketplace

# Install plugin
/plugin install eneo-developer@eneo-dev-marketplace

# Restart Claude Code
# (Close and reopen)
```

**Verify installation:**
```bash
# Check agents
/agents
# Should show 5 eneo agents

# Check Skills
"What Skills are available?"
# Should list 7 Skills

# Test a Skill
"Check my translation files for missing keys"
# → i18n-sync Skill activates
```

---

### Option 2: Git Repository (Team Sharing)

**Best for**: Sharing with your Eneo core team

#### Step 1: Create Git Repository

```bash
cd /Users/ccimen/dev/eneo/eneo-dev-marketplace

# Initialize git
git init
git add .
git commit -m "feat: initial eneo-developer plugin with 5 agents, 3 Skills, and 2 MCP servers"

# Create GitHub repo (via gh CLI or web)
gh repo create eneo-developer-plugin --public --source=. --push

# Or push to existing repo
git remote add origin https://github.com/YOUR-ORG/eneo-developer-plugin.git
git push -u origin main
```

#### Step 2: Team Members Install

```bash
# In their Claude Code session
/plugin marketplace add https://github.com/YOUR-ORG/eneo-developer-plugin

# Install the plugin
/plugin install eneo-developer@eneo-developer-plugin

# Restart Claude Code
```

---

### Option 3: Project-Level Auto-Install (Enterprise)

**Best for**: Automatic installation for all Eneo developers

#### Step 1: Add to Eneo Project Settings

Create or update `/Users/ccimen/dev/eneo/.claude/settings.json`:

```json
{
  "pluginMarketplaces": [
    {
      "name": "eneo-developer-plugin",
      "source": "https://github.com/YOUR-ORG/eneo-developer-plugin"
    }
  ],
  "plugins": [
    {
      "name": "eneo-developer",
      "marketplace": "eneo-developer-plugin",
      "enabled": true
    }
  ]
}
```

#### Step 2: Team Members Auto-Install

When developers:
1. Clone the Eneo repo
2. Trust the folder in Claude Code
3. The plugin **automatically installs**!

---

## 🧪 Testing Before Shipping

### Test 1: i18n-sync (Most Critical)

```bash
cd /Users/ccimen/dev/eneo/frontend/apps/web

# Test with real Eneo data
python ../../eneo-dev-marketplace/eneo-developer/skills/i18n-sync/scripts/i18n-sync.py --check

# Expected: Shows missing keys (34 English keys)
python ../../eneo-dev-marketplace/eneo-developer/skills/i18n-sync/scripts/i18n-extract.py --full

# Expected: Shows usage statistics (~987 used, 472 unused)
python ../../eneo-dev-marketplace/eneo-developer/skills/i18n-sync/scripts/i18n-validate.py --full

# Expected: 6 validation checks complete
```

### Test 2: generate-migration

```bash
cd /Users/ccimen/dev/eneo/backend

# Test doctor command
python ../eneo-dev-marketplace/eneo-developer/skills/generate-migration/scripts/generate-migration.py doctor

# Expected: Shows single HEAD and 263 migrations

# Test patterns reference
python ../eneo-dev-marketplace/eneo-developer/skills/generate-migration/scripts/generate-migration.py patterns

# Expected: Shows 4 migration patterns
```

### Test 3: scaffold-domain

```bash
cd /Users/ccimen/dev/eneo

# Test on a dummy domain (won't commit)
python eneo-dev-marketplace/eneo-developer/skills/scaffold-domain/scripts/scaffold-domain.py \
  --name test_dummy \
  --tenant-scoped \
  --space-scoped \
  --permissions "read,edit" \
  --output-dir "/tmp/test-eneo-domain"

# Expected: Creates /tmp/test-eneo-domain/test_dummy/ with DDD structure

# Verify files exist
ls -la /tmp/test-eneo-domain/test_dummy/

# Clean up
rm -rf /tmp/test-eneo-domain
```

### Test 4: Plugin Installation

```bash
# Install the plugin
/plugin marketplace add ./eneo-dev-marketplace
/plugin install eneo-developer@eneo-dev-marketplace

# Restart Claude Code

# Verify
/agents  # Should show 5 eneo agents
```

---

## 📋 Pre-Shipping Checklist

- [ ] All 3 Skills tested with real data
- [ ] Plugin installs without errors
- [ ] All 5 agents appear in `/agents`
- [ ] Skills listed in "What Skills are available?"
- [ ] MCP servers load (check for errors)
- [ ] README.md is complete
- [ ] Git repository created (if sharing via Git)
- [ ] Version number is correct (1.0.0)

---

## 🎯 Shipping Decision Matrix

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Local Marketplace** | Already working, zero setup | Only you can use it | Testing, personal use |
| **Git Repository** | Easy sharing, version control | Requires GitHub/GitLab | Team of 2-10 devs |
| **Project Auto-Install** | Fully automatic for team | Requires repo settings | Enterprise, 10+ devs |

---

## 📄 Files Created (Summary)

```
eneo-dev-marketplace/
├── .claude-plugin/
│   └── marketplace.json           ✅ Marketplace manifest
├── SHIPPING.md                     ✅ This file
└── eneo-developer/
    ├── .claude-plugin/
    │   └── plugin.json             ✅ Plugin metadata
    ├── .mcp.json                   ✅ MCP server config (NEW!)
    ├── README.md                   ✅ User documentation
    ├── agents/ (5 files, 61KB)     ✅ All agents
    ├── skills/
    │   ├── scaffold-domain/        ✅ COMPLETE (188 lines + 9 templates)
    │   ├── i18n-sync/              ✅ COMPLETE (992 lines, 3 scripts)
    │   ├── generate-migration/     ✅ COMPLETE (464 lines, 5 commands)
    │   ├── space-permission-validator/ ⚠️ PLACEHOLDER
    │   ├── test-fixture-generator/     ⚠️ PLACEHOLDER
    │   ├── eager-loading-analyzer/     ⚠️ PLACEHOLDER
    │   └── svelte-component-scaffold/  ⚠️ PLACEHOLDER
```

**Total**: 38 files

---

## 🔄 Iteration Workflow (After Shipping)

### Making Updates

```bash
# 1. Uninstall current version
/plugin uninstall eneo-developer@eneo-dev-marketplace

# 2. Make changes to agents/Skills
# Edit files in eneo-dev-marketplace/eneo-developer/

# 3. Update version in plugin.json
# Change "version": "1.0.0" → "1.0.1"

# 4. Reinstall
/plugin install eneo-developer@eneo-dev-marketplace

# 5. Restart Claude Code
```

### If Using Git

```bash
# 1. Make changes
# 2. Commit
git add .
git commit -m "feat: implement space-permission-validator Skill"
git push

# 3. Team members update
/plugin update eneo-developer@eneo-developer-plugin
```

---

## 📚 What Developers Need to Know

### Installation

Share this with your team:

```markdown
# Installing eneo-developer Plugin

## Prerequisites
- Claude Code 1.0+
- Python 3.11+ (`pip install jinja2 click`)
- Node.js/npx for MCP servers

## Install

```bash
# Add marketplace
/plugin marketplace add ./eneo-dev-marketplace

# OR from Git (after you push)
/plugin marketplace add https://github.com/YOUR-ORG/eneo-developer-plugin

# Install plugin
/plugin install eneo-developer@eneo-dev-marketplace

# Restart Claude Code
```

## Verify

```bash
/agents  # See 5 eneo agents
"What Skills are available?"  # See 7 Skills
```
```

---

## 🎉 You're Ready to Ship!

### Immediate Next Step

**Test locally first**:

```bash
cd /Users/ccimen/dev/eneo
claude

/plugin marketplace add ./eneo-dev-marketplace
/plugin install eneo-developer@eneo-dev-marketplace
# Restart Claude Code
```

Then:
1. Test agents work
2. Test Skills activate
3. If all good → Create Git repo and share!

---

## 📞 Support Information

Add this to your plugin's README or docs:

```markdown
## Troubleshooting

### Plugin Installation Issues
- Restart Claude Code after installation
- Check `/agents` and `/skills` commands
- Review plugin status: `/plugin`

### Skill Not Activating
- Check Python dependencies: `pip install jinja2 click`
- Verify file permissions: `chmod +x skills/*/scripts/*.py`
- Check SKILL.md frontmatter for syntax errors

### MCP Server Errors
- Verify npx is installed: `which npx`
- Check Node.js version: `node --version` (requires 18+)
- Disable problematic MCP: Edit `.mcp.json` and set `disabled: true`

### Agent Not Appearing
- Verify agent file has YAML frontmatter
- Check for syntax errors in agent .md file
- Restart Claude Code

## Support
- GitHub Issues: https://github.com/YOUR-ORG/eneo-developer-plugin/issues
- Internal: #eneo-development channel
```

---

## 🎁 Future Enhancements

After shipping v1.0.0, you can:

1. **Implement remaining Skills** (v1.1.0):
   - space-permission-validator
   - test-fixture-generator
   - eager-loading-analyzer
   - svelte-component-scaffold

2. **Add more MCP servers** (v1.2.0):
   - Context7 for library documentation
   - Playwright for E2E testing

3. **Add slash commands** (v1.3.0):
   - `/eneo-scaffold` - Quick scaffold command
   - `/eneo-i18n` - Quick i18n check

4. **Add hooks** (v1.4.0):
   - Pre-commit: Run i18n-validate
   - Post-scaffold: Auto-run alembic autogenerate

---

**Your plugin is READY TO SHIP!** 🚀

Choose your shipping method and go! 🎉
