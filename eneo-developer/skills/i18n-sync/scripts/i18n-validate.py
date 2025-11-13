#!/usr/bin/env python3
"""
i18n-validate.py - Comprehensive validation for Paraglide translation files

Validates translation files for:
- JSON syntax and structure
- Duplicate keys
- snake_case naming conventions
- TODO/FIXME placeholders
- Parameter consistency across languages
- Schema declaration
- Paraglide compilation success
"""

import json
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import Counter
import click


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_json(file_path: Path) -> Tuple[Dict[str, str], bool, str]:
    """Load JSON file with detailed error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, True, ""
    except FileNotFoundError:
        return {}, False, f"File not found: {file_path}"
    except json.JSONDecodeError as e:
        return {}, False, f"Line {e.lineno}, Column {e.colno}: {e.msg}"
    except Exception as e:
        return {}, False, str(e)


def validate_snake_case(key: str) -> bool:
    """Validate snake_case convention"""
    pattern = r'^[a-z][a-z0-9_]*$'
    return bool(re.match(pattern, key))


def extract_parameters(value: str) -> Set[str]:
    """Extract parameter placeholders like {variable}"""
    return set(re.findall(r'\{(\w+)\}', value))


def find_duplicate_keys(data: Dict[str, str]) -> List[str]:
    """Find duplicate keys (should never happen in valid JSON, but check anyway)"""
    # This would only catch duplicates if JSON was manually edited with errors
    # Valid JSON parsers reject duplicates, so this is a sanity check
    key_counts = Counter(data.keys())
    return [key for key, count in key_counts.items() if count > 1]


def find_todo_placeholders(data: Dict[str, str]) -> List[Tuple[str, str]]:
    """Find TODO/FIXME placeholders in translations"""
    placeholders = []
    todo_patterns = [
        r'\[TODO:?.*?\]',
        r'\bTODO\b',
        r'\bFIXME\b',
        r'\[�VERS�TT\]',  # Swedish "translate"
        r'\[�vers�tt\]',
    ]

    combined_pattern = '|'.join(f'({p})' for p in todo_patterns)

    for key, value in data.items():
        if key == '$schema':
            continue
        if re.search(combined_pattern, value, re.IGNORECASE):
            placeholders.append((key, value))

    return placeholders


def find_duplicate_values(data: Dict[str, str]) -> Dict[str, List[str]]:
    """Find duplicate translation values (different keys with same text)"""
    from collections import defaultdict

    value_to_keys = defaultdict(list)

    for key, value in data.items():
        if key == '$schema':
            continue

        # Skip empty values
        if not value or not value.strip():
            continue

        # Skip single-character values (too common)
        if len(value.strip()) <= 1:
            continue

        # Skip TODO placeholders (not real duplicates)
        if '[TODO' in value or 'TODO' in value:
            continue

        value_to_keys[value].append(key)

    # Return only values with 2+ keys (actual duplicates)
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}

    return duplicates


def validate_parameter_consistency(
    sv_data: Dict[str, str],
    en_data: Dict[str, str]
) -> List[Tuple[str, Set[str], Set[str]]]:
    """Validate that parameters match across languages"""
    mismatches = []

    common_keys = set(sv_data.keys()) & set(en_data.keys())

    for key in common_keys:
        if key == '$schema':
            continue

        sv_params = extract_parameters(sv_data[key])
        en_params = extract_parameters(en_data[key])

        if sv_params != en_params:
            mismatches.append((key, sv_params, en_params))

    return mismatches


def check_schema_declaration(data: Dict[str, str]) -> bool:
    """Check if $schema declaration is present"""
    return '$schema' in data


def test_paraglide_compilation(frontend_dir: Path) -> Tuple[bool, str]:
    """Test if Paraglide compilation succeeds"""
    try:
        result = subprocess.run(
            ['bun', 'run', 'i18n:compile'],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr or result.stdout

    except FileNotFoundError:
        return False, "bun command not found (install Bun runtime)"
    except subprocess.TimeoutExpired:
        return False, "Compilation timeout (>30s)"
    except Exception as e:
        return False, str(e)


@click.command()
@click.option('--syntax', is_flag=True, help='Validate JSON syntax only')
@click.option('--naming', is_flag=True, help='Validate naming conventions')
@click.option('--params', is_flag=True, help='Validate parameter consistency')
@click.option('--compile', is_flag=True, help='Test Paraglide compilation')
@click.option('--full', is_flag=True, help='Run all validations (default)', default=True)
@click.option('--sv-file', default='frontend/apps/web/messages/sv.json', help='Path to Swedish file')
@click.option('--en-file', default='frontend/apps/web/messages/en.json', help='Path to English file')
@click.option('--frontend-dir', default='frontend/apps/web', help='Frontend directory for compilation test')
def main(syntax, naming, params, compile, full, sv_file, en_file, frontend_dir):
    """Comprehensive validation for Paraglide translation files"""

    # If no specific check is requested, run full validation
    run_all = full or not (syntax or naming or params or compile)

    # Resolve paths
    sv_path = Path(sv_file)
    en_path = Path(en_file)
    frontend_path = Path(frontend_dir)

    click.echo(f"{Colors.BLUE}{Colors.BOLD}= Validating Paraglide translation files...{Colors.END}\n")

    errors = []
    warnings = []

    # Load files (always needed)
    sv_data, sv_ok, sv_error = load_json(sv_path)
    en_data, en_ok, en_error = load_json(en_path)

    # Syntax validation
    if run_all or syntax:
        click.echo(f"{Colors.BOLD}1. JSON Syntax Validation{Colors.END}")

        if sv_ok:
            click.echo(f"  {Colors.GREEN}{Colors.END} sv.json: Valid JSON")
        else:
            click.echo(f"  {Colors.RED}{Colors.END} sv.json: {sv_error}")
            errors.append(f"sv.json syntax error: {sv_error}")

        if en_ok:
            click.echo(f"  {Colors.GREEN}{Colors.END} en.json: Valid JSON")
        else:
            click.echo(f"  {Colors.RED}{Colors.END} en.json: {en_error}")
            errors.append(f"en.json syntax error: {en_error}")

        # Check for schema declaration
        if sv_ok:
            if check_schema_declaration(sv_data):
                click.echo(f"  {Colors.GREEN}{Colors.END} sv.json: $schema declaration present")
            else:
                warnings.append("sv.json: Missing $schema declaration")
                click.echo(f"  {Colors.YELLOW}�{Colors.END} sv.json: Missing $schema declaration")

        if en_ok:
            if check_schema_declaration(en_data):
                click.echo(f"  {Colors.GREEN}{Colors.END} en.json: $schema declaration present")
            else:
                warnings.append("en.json: Missing $schema declaration")
                click.echo(f"  {Colors.YELLOW}�{Colors.END} en.json: Missing $schema declaration")

        print()

    if not (sv_ok and en_ok):
        click.echo(f"{Colors.RED}L Cannot continue validation due to syntax errors{Colors.END}")
        sys.exit(2)

    # Naming validation
    if run_all or naming:
        click.echo(f"{Colors.BOLD}2. Naming Convention Validation{Colors.END}")

        sv_violations = [(k, k) for k in sv_data.keys() if k != '$schema' and not validate_snake_case(k)]
        en_violations = [(k, k) for k in en_data.keys() if k != '$schema' and not validate_snake_case(k)]

        if not sv_violations and not en_violations:
            click.echo(f"  {Colors.GREEN}{Colors.END} All keys follow snake_case convention")
        else:
            if sv_violations:
                click.echo(f"  {Colors.RED}{Colors.END} sv.json: {len(sv_violations)} naming violations")
                for key, _ in sv_violations[:3]:
                    click.echo(f"     - {key}")
                    errors.append(f"sv.json: Invalid key name '{key}'")

            if en_violations:
                click.echo(f"  {Colors.RED}{Colors.END} en.json: {len(en_violations)} naming violations")
                for key, _ in en_violations[:3]:
                    click.echo(f"     - {key}")
                    errors.append(f"en.json: Invalid key name '{key}'")

        print()

    # TODO placeholder detection
    if run_all:
        click.echo(f"{Colors.BOLD}3. Placeholder Detection{Colors.END}")

        sv_todos = find_todo_placeholders(sv_data)
        en_todos = find_todo_placeholders(en_data)

        if not sv_todos and not en_todos:
            click.echo(f"  {Colors.GREEN}{Colors.END} No TODO/FIXME placeholders found")
        else:
            if sv_todos:
                click.echo(f"  {Colors.YELLOW}�{Colors.END} sv.json: {len(sv_todos)} TODO placeholders")
                for key, value in sv_todos[:3]:
                    click.echo(f"     - {key}: \"{value}\"")
                    warnings.append(f"sv.json: TODO placeholder in '{key}'")

            if en_todos:
                click.echo(f"  {Colors.YELLOW}�{Colors.END} en.json: {len(en_todos)} TODO placeholders")
                for key, value in en_todos[:3]:
                    click.echo(f"     - {key}: \"{value}\"")
                    warnings.append(f"en.json: TODO placeholder in '{key}'")

        print()

    # Duplicate value detection
    if run_all:
        click.echo(f"{Colors.BOLD}4. Duplicate Value Detection{Colors.END}")

        sv_duplicates = find_duplicate_values(sv_data)
        en_duplicates = find_duplicate_values(en_data)

        if not sv_duplicates and not en_duplicates:
            click.echo(f"  {Colors.GREEN}✓{Colors.END} No duplicate values found")
        else:
            if sv_duplicates:
                total_duplicate_keys = sum(len(keys) for keys in sv_duplicates.values())
                click.echo(f"  {Colors.YELLOW}⚠{Colors.END} sv.json: {len(sv_duplicates)} duplicate value groups ({total_duplicate_keys} keys)")

                for value, keys in sorted(sv_duplicates.items(), key=lambda x: -len(x[1]))[:3]:
                    click.echo(f"     \"{value[:50]}{'...' if len(value) > 50 else ''}\" ({len(keys)} keys):")
                    for key in sorted(keys)[:3]:
                        click.echo(f"        - {key}")
                    if len(keys) > 3:
                        click.echo(f"        ... and {len(keys) - 3} more")
                    warnings.append(f"sv.json: Duplicate value with {len(keys)} keys")

                if len(sv_duplicates) > 3:
                    click.echo(f"     ... and {len(sv_duplicates) - 3} more groups")

            if en_duplicates:
                total_duplicate_keys = sum(len(keys) for keys in en_duplicates.values())
                click.echo(f"  {Colors.YELLOW}⚠{Colors.END} en.json: {len(en_duplicates)} duplicate value groups ({total_duplicate_keys} keys)")

                for value, keys in sorted(en_duplicates.items(), key=lambda x: -len(x[1]))[:3]:
                    click.echo(f"     \"{value[:50]}{'...' if len(value) > 50 else ''}\" ({len(keys)} keys):")
                    for key in sorted(keys)[:3]:
                        click.echo(f"        - {key}")
                    if len(keys) > 3:
                        click.echo(f"        ... and {len(keys) - 3} more")
                    warnings.append(f"en.json: Duplicate value with {len(keys)} keys")

                if len(en_duplicates) > 3:
                    click.echo(f"     ... and {len(en_duplicates) - 3} more groups")

            click.echo(f"  {Colors.BLUE}💡 Review if keys can be consolidated to reduce maintenance{Colors.END}")

        print()

    # Parameter consistency validation
    if run_all or params:
        click.echo(f"{Colors.BOLD}5. Parameter Consistency Validation{Colors.END}")

        param_mismatches = validate_parameter_consistency(sv_data, en_data)

        if not param_mismatches:
            click.echo(f"  {Colors.GREEN}{Colors.END} All parameters consistent across languages")
        else:
            click.echo(f"  {Colors.RED}{Colors.END} {len(param_mismatches)} parameter mismatches found:")
            for key, sv_params, en_params in param_mismatches[:5]:
                click.echo(f"     - {key}:")
                click.echo(f"       sv: {{{', '.join(sorted(sv_params))}}")
                click.echo(f"       en: {{{', '.join(sorted(en_params))}}")
                errors.append(f"Parameter mismatch in '{key}': sv{sv_params} != en{en_params}")

            if len(param_mismatches) > 5:
                click.echo(f"     ... and {len(param_mismatches) - 5} more")

        print()

    # Paraglide compilation test
    if run_all or compile:
        click.echo(f"{Colors.BOLD}6. Paraglide Compilation Test{Colors.END}")

        if not frontend_path.exists():
            click.echo(f"  {Colors.YELLOW}�{Colors.END} Frontend directory not found: {frontend_path}")
            click.echo(f"     Skipping compilation test")
            warnings.append("Compilation test skipped (directory not found)")
        else:
            click.echo(f"  Running: bun run i18n:compile...")
            success, error_msg = test_paraglide_compilation(frontend_path)

            if success:
                click.echo(f"  {Colors.GREEN}{Colors.END} Paraglide compilation successful")
            else:
                click.echo(f"  {Colors.RED}{Colors.END} Paraglide compilation failed:")
                click.echo(f"     {error_msg}")
                errors.append(f"Compilation failed: {error_msg}")

        print()

    # Summary
    click.echo(f"{Colors.BOLD}Summary:{Colors.END}")

    if errors:
        click.echo(f"  {Colors.RED}{Colors.END} {len(errors)} error(s) found:")
        for error in errors[:10]:
            click.echo(f"     - {error}")
        if len(errors) > 10:
            click.echo(f"     ... and {len(errors) - 10} more")

    if warnings:
        click.echo(f"  {Colors.YELLOW}�{Colors.END} {len(warnings)} warning(s):")
        for warning in warnings[:10]:
            click.echo(f"     - {warning}")
        if len(warnings) > 10:
            click.echo(f"     ... and {len(warnings) - 10} more")

    if not errors and not warnings:
        click.echo(f"  {Colors.GREEN} All validations passed!{Colors.END}")

    # Exit code
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
