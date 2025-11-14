#!/usr/bin/env python3
"""
Scaffold Domain - Generate complete DDD 4-layer structure for Eneo

Usage:
    python scaffold-domain.py --name notifications --tenant-scoped --space-scoped --permissions read,edit,delete
"""

import sys
from pathlib import Path
import click
from jinja2 import Environment, FileSystemLoader


@click.command()
@click.option("--name", required=True, help="Domain name (singular, snake_case)")
@click.option(
    "--tenant-scoped",
    is_flag=True,
    default=True,
    help="Add tenant_id column (default: True)",
)
@click.option(
    "--space-scoped",
    is_flag=True,
    default=False,
    help="Add space_id column and Space permissions",
)
@click.option(
    "--permissions", default="read,edit,delete", help="Comma-separated permissions"
)
@click.option(
    "--relationships", default="", help="Comma-separated foreign keys (field:table)"
)
@click.option("--output-dir", default="backend/src/intric", help="Output directory")
def scaffold_domain(
    name: str,
    tenant_scoped: bool,
    space_scoped: bool,
    permissions: str,
    relationships: str,
    output_dir: str,
):
    """Generate complete DDD 4-layer domain structure for Eneo"""

    # Validate domain name
    if not name.islower() or " " in name:
        click.echo(
            f"❌ Error: Domain name must be lowercase with no spaces: {name}", err=True
        )
        sys.exit(1)

    # Parse relationships
    parsed_relationships = []
    if relationships:
        for rel in relationships.split(","):
            if ":" not in rel:
                click.echo(f"❌ Error: Invalid relationship format: {rel}", err=True)
                click.echo(
                    "   Expected format: field:table (e.g., user_id:users)", err=True
                )
                sys.exit(1)
            field, table = rel.strip().split(":")
            parsed_relationships.append({"field": field, "table": table})

    # Parse permissions
    permission_list = [p.strip() for p in permissions.split(",")]

    # Build context for templates
    context = {
        "domain_name": name,
        "domain_class": to_pascal_case(name),
        "tenant_scoped": tenant_scoped,
        "space_scoped": space_scoped,
        "permissions": permission_list,
        "relationships": parsed_relationships,
    }

    # Get template directory
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / "templates" / "domain"

    if not template_dir.exists():
        click.echo(f"❌ Error: Template directory not found: {template_dir}", err=True)
        sys.exit(1)

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    env.filters["pascal_case"] = to_pascal_case
    env.filters["camel_case"] = to_camel_case

    # Create output directory structure
    domain_dir = Path(output_dir) / name
    create_directory_structure(domain_dir)

    # Generate files from templates
    files_created = []

    # Domain layer
    files_created.append(
        render_template(
            env, "entity.py.j2", domain_dir / "domain" / f"{name}.py", context
        )
    )
    files_created.append(
        render_template(
            env, "entity_repo.py.j2", domain_dir / "domain" / f"{name}_repo.py", context
        )
    )

    # Infrastructure layer
    files_created.append(
        render_template(
            env,
            "entity_repo_impl.py.j2",
            domain_dir / "infrastructure" / f"{name}_repo_impl.py",
            context,
        )
    )

    # Application layer
    files_created.append(
        render_template(
            env,
            "entity_service.py.j2",
            domain_dir / "application" / f"{name}_service.py",
            context,
        )
    )

    # API layer
    files_created.append(
        render_template(
            env,
            "api/entity_models.py.j2",
            domain_dir / "api" / f"{name}_models.py",
            context,
        )
    )
    files_created.append(
        render_template(
            env,
            "api/entity_router.py.j2",
            domain_dir / "api" / f"{name}_router.py",
            context,
        )
    )
    files_created.append(
        render_template(
            env,
            "api/entity_assembler.py.j2",
            domain_dir / "api" / f"{name}_assembler.py",
            context,
        )
    )

    # Table layer
    files_created.append(
        render_template(
            env,
            "table/entity_table.py.j2",
            domain_dir / "table" / f"{name}_table.py",
            context,
        )
    )

    # Factory
    files_created.append(
        render_template(
            env, "entity_factory.py.j2", domain_dir / f"{name}_factory.py", context
        )
    )

    # Print success message
    click.echo("\n✅ Domain scaffolding completed successfully!\n")
    click.echo(f"📁 Created domain: {domain_dir}\n")
    click.echo("📄 Files created:")
    for file in files_created:
        click.echo(f"   ✓ {file}")

    click.echo("\n🔧 Next steps:")
    click.echo("   1. Review generated code and customize business logic")
    click.echo(
        "   2. Create Alembic migration: uv run alembic revision --autogenerate -m 'add {name} table'"
    )
    click.echo("   3. Run migration: uv run alembic upgrade head")
    click.echo("   4. Register router in backend/src/intric/server/app.py")
    click.echo("   5. Write tests in tests/integration/")
    click.echo("   6. Run tests: uv run pytest\n")


def create_directory_structure(domain_dir: Path):
    """Create the DDD 4-layer directory structure"""
    directories = [
        domain_dir / "api",
        domain_dir / "application",
        domain_dir / "domain",
        domain_dir / "infrastructure",
        domain_dir / "table",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        (directory / "__init__.py").touch(exist_ok=True)

    # Create root __init__.py
    (domain_dir / "__init__.py").touch(exist_ok=True)


def render_template(
    env: Environment, template_name: str, output_path: Path, context: dict
) -> str:
    """Render a Jinja2 template and write to file"""
    try:
        template = env.get_template(template_name)
        content = template.render(**context)

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, "w") as f:
            f.write(content)

        return str(output_path.relative_to(Path.cwd()))
    except Exception as e:
        click.echo(f"❌ Error rendering {template_name}: {e}", err=True)
        raise


def to_pascal_case(s: str) -> str:
    """Convert snake_case to PascalCase"""
    return "".join(word.capitalize() for word in s.split("_"))


def to_camel_case(s: str) -> str:
    """Convert snake_case to camelCase"""
    words = s.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


if __name__ == "__main__":
    scaffold_domain()
