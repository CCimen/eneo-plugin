---
name: scaffold-domain
description: Generates complete DDD 4-layer domain structure with multi-tenancy support, UUID primary keys, soft deletes, and Eneo architectural patterns. Use when creating new domain modules, entities, or business capabilities for the Eneo platform. Requires Python 3.11+ with jinja2 and click packages installed.
allowed-tools: Write, Bash
---

# Scaffold Domain Skill

Automatically generates a complete Domain-Driven Design (DDD) 4-layer structure for Eneo AI platform, following the established 57-domain pattern.

## What this Skill does

Creates the complete directory structure and boilerplate code for a new Eneo domain with:

- **Domain Layer**: Entities with multi-tenancy (tenant_id, space_id), UUID primary keys, soft deletes
- **Application Layer**: Service layer with business logic and Space permission checks
- **Infrastructure Layer**: Repository implementation with SQLAlchemy async, N+1 prevention
- **Presentation Layer**: FastAPI routes, Pydantic schemas, OpenAPI documentation
- **Factory Pattern**: Entity creation and test data generation

## When to use this Skill

- Creating a new business domain (e.g., notifications, webhooks, reports)
- Adding a new entity that requires DDD structure
- Starting implementation after architectural design
- When eneo-ddd-architect agent requests domain scaffolding

## Generated Structure

```
backend/src/intric/{domain_name}/
├── api/
│   ├── {domain}_models.py      # Pydantic schemas (Create, Update, Public)
│   ├── {domain}_router.py      # FastAPI routes with OpenAPI docs
│   └── {domain}_assembler.py   # Domain ↔ API transformation
├── application/
│   └── {domain}_service.py     # Business logic with permissions
├── domain/
│   ├── {domain}.py             # Domain entities
│   └── {domain}_repo.py        # Repository interface
├── infrastructure/
│   └── {domain}_repo_impl.py   # SQLAlchemy async implementation
├── table/
│   └── {domain}_table.py       # Database table definition
└── {domain}_factory.py         # Factory for entity creation
```

## Usage

The script will be invoked automatically by Claude when you request domain scaffolding:

```bash
python scripts/scaffold-domain.py \
  --name "notifications" \
  --tenant-scoped \
  --space-scoped \
  --permissions "read,edit,delete" \
  --relationships "user_id:users,space_id:spaces"
```

### Parameters

- `--name`: Domain name (singular, snake_case)
- `--tenant-scoped`: Add tenant_id column (always recommended)
- `--space-scoped`: Add space_id column and Space permissions
- `--permissions`: Comma-separated list of permissions (read, edit, delete, manage)
- `--relationships`: Comma-separated foreign keys (field:table format)

## Key Features

### Multi-Tenancy Built-in
- `tenant_id` UUID column on all entities
- Tenant filtering in all repository queries
- Tenant isolation in service layer

### Space-Scoped Support
- `space_id` UUID column for space-scoped entities
- Space membership validation
- Space permission decorators on API routes

### Security by Default
- Soft deletes (`deleted_at` timestamp)
- UUID primary keys (prevents enumeration attacks)
- Permission checks at service layer
- Audit timestamps (`created_at`, `updated_at`)

### Performance Optimized
- SQLAlchemy selectinload patterns (prevents N+1 queries)
- Eager loading templates for relationships
- Optimized indexes on tenant_id and space_id

### Production Ready
- OpenAPI/Swagger documentation
- Pydantic v2 validation with examples
- Proper error handling
- Transaction management

## Example Output

### Domain Entity
```python
@dataclass
class Notification:
    id: UUID
    tenant_id: UUID
    space_id: UUID | None
    user_id: UUID
    title: str
    content: str
    is_read: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
```

### Repository Query (with N+1 prevention)
```python
async def get_notifications(
    tenant_id: UUID,
    space_id: UUID,
    db: AsyncSession
) -> list[Notification]:
    result = await db.execute(
        select(NotificationInDB)
        .where(NotificationInDB.tenant_id == tenant_id)
        .where(NotificationInDB.space_id == space_id)
        .where(NotificationInDB.deleted_at.is_(None))
        .options(
            selectinload(NotificationInDB.user),
            selectinload(NotificationInDB.space)
        )
    )
    return result.scalars().all()
```

### Service Layer (with Space permissions)
```python
async def create_notification(
    tenant_id: UUID,
    space_id: UUID,
    user: User,
    data: CreateNotification,
    db: AsyncSession
) -> Notification:
    # Validate Space membership
    await space_service.validate_membership(tenant_id, space_id, user.id)

    # Create entity
    notification = Notification(
        id=uuid4(),
        tenant_id=tenant_id,
        space_id=space_id,
        user_id=user.id,
        **data.model_dump()
    )

    # Save via repository
    return await notification_repo.create(notification, db)
```

## Dependencies

- **jinja2**: Template rendering
- **click**: CLI argument parsing

Install with:
```bash
pip install jinja2 click
```

## Integration with Eneo Agents

This Skill is primarily used by:
- **eneo-ddd-architect**: Generates structure after domain modeling
- **eneo-python-implementation**: Rapid backend implementation
- **eneo-code-reviewer**: Validates generated code follows patterns

## Notes

- Generated code follows Eneo's KISS principle (simple, maintainable)
- All entities include multi-tenancy by default (security requirement)
- Templates include TODO comments for custom business logic
- Code is production-ready but requires business logic implementation
- Always run tests after scaffolding (`pytest tests/`)
