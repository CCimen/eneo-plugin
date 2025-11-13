---
name: space-permission-validator
description: Validates space-scoped entities have correct permission checks (read, edit, delete) at repository, service, and API layers. Detects missing tenant_id filters and space membership checks. Use for security validation and preventing data leaks.
allowed-tools: Read, Grep, Write
---

# Space Permission Validator Skill

Security-critical validation of permission checks across all DDD layers.

## What this Skill does

- Scans repository methods for missing tenant_id filters
- Validates space membership checks in services
- Checks permission decorators on API routes
- Generates permission integration tests
- Reports critical security issues

## Usage

```bash
python scripts/validate-permissions.py --domain notifications
```

## Key Features

- Prevents data leaks (security-critical)
- AST parsing for accurate detection
- Generates actionable fix suggestions
- Creates security test cases

## Integration

Used by:
- **eneo-code-reviewer**: Primary security validation
- **eneo-ddd-architect**: Design-time checks
- **eneo-python-implementation**: Implementation validation
