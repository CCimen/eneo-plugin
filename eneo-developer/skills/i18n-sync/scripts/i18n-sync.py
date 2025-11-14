#!/usr/bin/env python3
"""
i18n-sync.py - Bidirectional synchronization for Paraglide translation files

Synchronizes Swedish (sv.json) and English (en.json) translation files:
- Detects missing keys in either direction
- Auto-adds missing keys with [TODO: translate] placeholder
- Validates snake_case naming conventions
- Sorts keys alphabetically
- Preserves parameter placeholders ({variable})
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple, List
import click


class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def find_workspace_root() -> Path:
    """Auto-detect workspace root (/workspace for devcontainer or current dir)"""
    # Check for /workspace (devcontainer)
    if Path("/workspace").exists() and Path("/workspace/frontend").exists():
        return Path("/workspace")
    # Check for workspace env var
    elif os.getenv("WORKSPACE_ROOT"):
        return Path(os.getenv("WORKSPACE_ROOT"))
    # Fall back to current directory
    else:
        return Path.cwd()


def find_translation_files() -> Tuple[Path, Path]:
    """Auto-locate sv.json and en.json"""
    workspace = find_workspace_root()

    # Try common locations
    locations = [
        workspace / "frontend/apps/web/messages",
        workspace / "apps/web/messages",
        workspace / "messages",
    ]

    for loc in locations:
        sv_file = loc / "sv.json"
        en_file = loc / "en.json"
        if sv_file.exists() and en_file.exists():
            return sv_file, en_file

    # Fall back to defaults
    return (
        workspace / "frontend/apps/web/messages/sv.json",
        workspace / "frontend/apps/web/messages/en.json",
    )


def load_json(file_path: Path) -> Tuple[Dict[str, str], bool]:
    """Load JSON file with error handling"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, True
    except FileNotFoundError:
        click.echo(
            f"{Colors.RED}❌ Error: File not found: {file_path}{Colors.END}", err=True
        )
        return {}, False
    except json.JSONDecodeError as e:
        click.echo(
            f"{Colors.RED}❌ JSON syntax error in {file_path}:{Colors.END}", err=True
        )
        click.echo(f"   Line {e.lineno}, Column {e.colno}: {e.msg}", err=True)
        return {}, False


def save_json(file_path: Path, data: Dict[str, str], dry_run: bool = False) -> bool:
    """Save JSON file with pretty formatting"""
    if dry_run:
        click.echo(
            f"{Colors.YELLOW}  [DRY RUN] Would write to: {file_path}{Colors.END}"
        )
        return True

    try:
        # Create backup
        if file_path.exists():
            backup_path = file_path.with_suffix(".json.backup")
            file_path.rename(backup_path)

        # Write with pretty formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")  # Add trailing newline

        # Remove backup on success
        if file_path.with_suffix(".json.backup").exists():
            file_path.with_suffix(".json.backup").unlink()

        return True
    except Exception as e:
        click.echo(
            f"{Colors.RED}❌ Error writing {file_path}: {e}{Colors.END}", err=True
        )
        # Restore backup
        backup_path = file_path.with_suffix(".json.backup")
        if backup_path.exists():
            backup_path.rename(file_path)
        return False


def validate_snake_case(key: str) -> bool:
    """Validate that key follows snake_case convention"""
    # Allow: lowercase letters, numbers, underscores
    # Must start with letter
    pattern = r"^[a-z][a-z0-9_]*$"
    return bool(re.match(pattern, key))


def suggest_snake_case(key: str) -> str:
    """Suggest snake_case version of key"""
    # Convert camelCase/PascalCase to snake_case
    # Example: camelCase → camel_case, PascalCase → pascal_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    # Remove consecutive underscores
    s3 = re.sub("_+", "_", s2)
    # Remove leading/trailing underscores
    return s3.strip("_")


def extract_parameters(value: str) -> Set[str]:
    """Extract parameter placeholders like {variable} from translation"""
    return set(re.findall(r"\{(\w+)\}", value))


def sort_keys_alphabetically(data: Dict[str, str]) -> Dict[str, str]:
    """Sort dictionary keys alphabetically, but keep $schema at top if present"""
    sorted_data = {}

    # Handle $schema separately (should be first)
    if "$schema" in data:
        sorted_data["$schema"] = data["$schema"]

    # Sort remaining keys
    for key in sorted(k for k in data.keys() if k != "$schema"):
        sorted_data[key] = data[key]

    return sorted_data


def find_missing_keys(
    sv_data: Dict[str, str], en_data: Dict[str, str]
) -> Tuple[Set[str], Set[str]]:
    """Find keys missing in each direction"""
    sv_keys = set(k for k in sv_data.keys() if k != "$schema")
    en_keys = set(k for k in en_data.keys() if k != "$schema")

    missing_in_en = sv_keys - en_keys
    missing_in_sv = en_keys - sv_keys

    return missing_in_en, missing_in_sv


def find_naming_violations(data: Dict[str, str]) -> List[Tuple[str, str]]:
    """Find keys that violate snake_case convention"""
    violations = []
    for key in data.keys():
        if key == "$schema":
            continue
        if not validate_snake_case(key):
            suggestion = suggest_snake_case(key)
            violations.append((key, suggestion))
    return violations


def find_duplicate_values(data: Dict[str, str]) -> Dict[str, List[str]]:
    """Find duplicate translation values (different keys with same text)"""
    from collections import defaultdict

    value_to_keys = defaultdict(list)

    for key, value in data.items():
        if key == "$schema":
            continue

        # Skip empty values
        if not value or not value.strip():
            continue

        # Skip single-character values (too common: "×", "·", etc.)
        if len(value.strip()) <= 1:
            continue

        # Skip TODO placeholders (not real duplicates)
        if "[TODO" in value or "TODO" in value:
            continue

        value_to_keys[value].append(key)

    # Return only values with 2+ keys (actual duplicates)
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}

    return duplicates


@click.command()
@click.option("--check", is_flag=True, help="Check for issues without making changes")
@click.option(
    "--add-keys",
    is_flag=True,
    help="Add missing keys with [TODO: translate] placeholder",
)
@click.option("--fix", is_flag=True, help="Fix naming violations and add missing keys")
@click.option("--auto-fix", is_flag=True, help="Auto-fix everything and write files")
@click.option(
    "--sv-file",
    default=None,
    help="Path to Swedish file (auto-detected if not provided)",
)
@click.option(
    "--en-file",
    default=None,
    help="Path to English file (auto-detected if not provided)",
)
@click.option("--dry-run", is_flag=True, help="Simulate changes without writing files")
def main(check, add_keys, fix, auto_fix, sv_file, en_file, dry_run):
    """Synchronize Paraglide translation files (sv.json ↔ en.json)"""

    # Auto-detect paths if not provided
    if not sv_file or not en_file:
        auto_sv, auto_en = find_translation_files()
        sv_path = Path(sv_file) if sv_file else auto_sv
        en_path = Path(en_file) if en_file else auto_en
    else:
        sv_path = Path(sv_file)
        en_path = Path(en_file)

    click.echo(
        f"{Colors.BLUE}{Colors.BOLD}🔍 Scanning translation files...{Colors.END}\n"
    )

    # Load files
    sv_data, sv_ok = load_json(sv_path)
    en_data, en_ok = load_json(en_path)

    if not (sv_ok and en_ok):
        sys.exit(2)

    # Count keys (excluding $schema)
    sv_count = len([k for k in sv_data.keys() if k != "$schema"])
    en_count = len([k for k in en_data.keys() if k != "$schema"])

    click.echo(f"{Colors.GREEN}✓{Colors.END} sv.json: {sv_count} keys")
    click.echo(f"{Colors.GREEN}✓{Colors.END} en.json: {en_count} keys")

    # Find issues
    missing_in_en, missing_in_sv = find_missing_keys(sv_data, en_data)
    sv_violations = find_naming_violations(sv_data)
    en_violations = find_naming_violations(en_data)
    sv_duplicates = find_duplicate_values(sv_data)
    en_duplicates = find_duplicate_values(en_data)

    has_issues = bool(missing_in_en or missing_in_sv or sv_violations or en_violations)
    has_warnings = bool(sv_duplicates or en_duplicates)

    # Report missing keys
    if missing_in_en:
        click.echo(
            f"\n{Colors.YELLOW}⚠️  Missing in en.json ({len(missing_in_en)} keys):{Colors.END}"
        )
        for key in sorted(missing_in_en)[:10]:  # Show first 10
            click.echo(f"   - {key}")
        if len(missing_in_en) > 10:
            click.echo(f"   ... and {len(missing_in_en) - 10} more")

    if missing_in_sv:
        click.echo(
            f"\n{Colors.YELLOW}⚠️  Missing in sv.json ({len(missing_in_sv)} keys):{Colors.END}"
        )
        for key in sorted(missing_in_sv)[:10]:
            click.echo(f"   - {key}")
        if len(missing_in_sv) > 10:
            click.echo(f"   ... and {len(missing_in_sv) - 10} more")

    # Report naming violations
    if sv_violations:
        click.echo(
            f"\n{Colors.RED}❌ Invalid naming in sv.json ({len(sv_violations)} keys):{Colors.END}"
        )
        for key, suggestion in sv_violations[:5]:
            click.echo(f"   - {key} → {Colors.GREEN}{suggestion}{Colors.END}")
        if len(sv_violations) > 5:
            click.echo(f"   ... and {len(sv_violations) - 5} more")

    if en_violations:
        click.echo(
            f"\n{Colors.RED}❌ Invalid naming in en.json ({len(en_violations)} keys):{Colors.END}"
        )
        for key, suggestion in en_violations[:5]:
            click.echo(f"   - {key} → {Colors.GREEN}{suggestion}{Colors.END}")
        if len(en_violations) > 5:
            click.echo(f"   ... and {len(en_violations) - 5} more")

    # Report duplicate values (consolidation opportunities)
    if sv_duplicates:
        total_duplicate_keys = sum(len(keys) for keys in sv_duplicates.values())
        click.echo(
            f"\n{Colors.YELLOW}⚠️  Duplicate values in sv.json ({len(sv_duplicates)} groups, {total_duplicate_keys} keys):{Colors.END}"
        )
        for value, keys in sorted(sv_duplicates.items(), key=lambda x: -len(x[1]))[:5]:
            click.echo(f'   "{value}" ({len(keys)} keys):')
            for key in sorted(keys)[:3]:
                click.echo(f"      - {key}")
            if len(keys) > 3:
                click.echo(f"      ... and {len(keys) - 3} more")
            click.echo(
                f"   {Colors.BLUE}💡 Consider consolidating to single key{Colors.END}"
            )

        if len(sv_duplicates) > 5:
            remaining_groups = len(sv_duplicates) - 5
            remaining_keys = sum(
                len(keys) for value, keys in list(sv_duplicates.items())[5:]
            )
            click.echo(
                f"   ... and {remaining_groups} more groups ({remaining_keys} keys)"
            )

    if en_duplicates:
        total_duplicate_keys = sum(len(keys) for keys in en_duplicates.values())
        click.echo(
            f"\n{Colors.YELLOW}⚠️  Duplicate values in en.json ({len(en_duplicates)} groups, {total_duplicate_keys} keys):{Colors.END}"
        )
        for value, keys in sorted(en_duplicates.items(), key=lambda x: -len(x[1]))[:5]:
            click.echo(f'   "{value}" ({len(keys)} keys):')
            for key in sorted(keys)[:3]:
                click.echo(f"      - {key}")
            if len(keys) > 3:
                click.echo(f"      ... and {len(keys) - 3} more")
            click.echo(
                f"   {Colors.BLUE}💡 Consider consolidating to single key{Colors.END}"
            )

        if len(en_duplicates) > 5:
            remaining_groups = len(en_duplicates) - 5
            remaining_keys = sum(
                len(keys) for value, keys in list(en_duplicates.items())[5:]
            )
            click.echo(
                f"   ... and {remaining_groups} more groups ({remaining_keys} keys)"
            )

    # --check mode: report only
    if check or not (add_keys or fix or auto_fix):
        if not has_issues and not has_warnings:
            click.echo(
                f"\n{Colors.GREEN}✅ All translation files are synchronized!{Colors.END}"
            )
            sys.exit(0)
        else:
            if has_issues:
                click.echo(
                    f"\n{Colors.YELLOW}Run with --add-keys or --fix to resolve issues{Colors.END}"
                )
            if has_warnings:
                click.echo(
                    f"\n{Colors.BLUE}💡 {len(sv_duplicates) + len(en_duplicates)} duplicate value groups found (consolidation opportunities){Colors.END}"
                )
            sys.exit(1 if has_issues else 0)

    # Apply fixes
    modified = False

    # Add missing keys
    if add_keys or fix or auto_fix:
        if missing_in_en:
            click.echo(
                f"\n{Colors.BLUE}Adding {len(missing_in_en)} missing keys to en.json...{Colors.END}"
            )
            for key in missing_in_en:
                en_data[key] = "[TODO: translate]"
                click.echo(f"  + {key}")
            modified = True

        if missing_in_sv:
            click.echo(
                f"\n{Colors.BLUE}Adding {len(missing_in_sv)} missing keys to sv.json...{Colors.END}"
            )
            for key in missing_in_sv:
                sv_data[key] = "[TODO: översätt]"  # Swedish placeholder
                click.echo(f"  + {key}")
            modified = True

    # Fix naming violations (only in --fix or --auto-fix mode)
    if fix or auto_fix:
        if sv_violations:
            click.echo(
                f"\n{Colors.YELLOW}⚠️  Naming violations detected in sv.json{Colors.END}"
            )
            click.echo(
                "   Manual fix required (auto-rename not implemented to prevent data loss)"
            )
            for key, suggestion in sv_violations:
                click.echo(f"   - Rename: {key} → {suggestion}")

        if en_violations:
            click.echo(
                f"\n{Colors.YELLOW}⚠️  Naming violations detected in en.json{Colors.END}"
            )
            click.echo(
                "   Manual fix required (auto-rename not implemented to prevent data loss)"
            )
            for key, suggestion in en_violations:
                click.echo(f"   - Rename: {key} → {suggestion}")

    # Sort keys alphabetically
    if modified or auto_fix:
        sv_data = sort_keys_alphabetically(sv_data)
        en_data = sort_keys_alphabetically(en_data)
        click.echo(f"\n{Colors.GREEN}✓{Colors.END} Sorted keys alphabetically")

    # Save files
    if modified:
        click.echo(f"\n{Colors.BLUE}{Colors.BOLD}💾 Saving changes...{Colors.END}")

        sv_saved = save_json(sv_path, sv_data, dry_run)
        en_saved = save_json(en_path, en_data, dry_run)

        if sv_saved and en_saved:
            if dry_run:
                click.echo(
                    f"\n{Colors.YELLOW}[DRY RUN] No files were modified{Colors.END}"
                )
            else:
                click.echo(
                    f"\n{Colors.GREEN}✅ Translation files synchronized!{Colors.END}"
                )
                click.echo(f"\n{Colors.BLUE}Next steps:{Colors.END}")
                click.echo(f"  1. Review changes: git diff {sv_file} {en_file}")
                click.echo("  2. Compile Paraglide: bun run i18n:compile")
                click.echo("  3. Validate: python scripts/i18n-validate.py --full")
        else:
            click.echo(f"\n{Colors.RED}❌ Failed to save files{Colors.END}")
            sys.exit(2)
    else:
        click.echo(f"\n{Colors.GREEN}✅ No changes needed{Colors.END}")


if __name__ == "__main__":
    main()
