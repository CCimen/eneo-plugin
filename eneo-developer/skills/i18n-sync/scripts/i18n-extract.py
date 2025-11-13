#!/usr/bin/env python3
"""
i18n-extract.py - Extract and analyze Paraglide translation key usage

Scans Svelte files for translation key usage:
- Extracts all m.key_name() patterns from Svelte components
- Compares used keys against sv.json/en.json
- Reports unused keys (cleanup candidates)
- Reports missing keys (code references non-existent translations)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import click


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_json(file_path: Path) -> Dict[str, str]:
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"{Colors.RED}L Error: File not found: {file_path}{Colors.END}", err=True)
        sys.exit(2)
    except json.JSONDecodeError as e:
        click.echo(f"{Colors.RED}L JSON syntax error in {file_path}: {e}{Colors.END}", err=True)
        sys.exit(2)


def find_svelte_files(scan_dir: Path) -> List[Path]:
    """Recursively find all .svelte files"""
    svelte_files = []
    try:
        svelte_files = list(scan_dir.rglob('*.svelte'))
    except Exception as e:
        click.echo(f"{Colors.RED}L Error scanning directory {scan_dir}: {e}{Colors.END}", err=True)
        sys.exit(2)
    return svelte_files


def extract_translation_keys(svelte_file: Path) -> Dict[str, List[int]]:
    """Extract translation keys from Svelte file with line numbers"""
    keys_found = defaultdict(list)

    try:
        content = svelte_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Pattern to match: m.key_name or m.key_name(
        # Handles: m.key(), m.key({ param }), {m.key()}
        pattern = re.compile(r'\bm\.([a-z][a-z0-9_]*)\b')

        for line_num, line in enumerate(lines, start=1):
            matches = pattern.findall(line)
            for key in matches:
                keys_found[key].append(line_num)

    except UnicodeDecodeError:
        click.echo(f"{Colors.YELLOW}   Warning: Could not read {svelte_file} (encoding issue){Colors.END}")
    except Exception as e:
        click.echo(f"{Colors.YELLOW}   Warning: Error reading {svelte_file}: {e}{Colors.END}")

    return keys_found


def scan_all_svelte_files(scan_dir: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Dict[str, List[int]]]]:
    """
    Scan all Svelte files and extract translation keys

    Returns:
        - used_keys: Set of all unique keys found
        - key_locations: Dict mapping keys to files and line numbers
    """
    svelte_files = find_svelte_files(scan_dir)

    if not svelte_files:
        click.echo(f"{Colors.YELLOW}   No .svelte files found in {scan_dir}{Colors.END}")
        return set(), {}

    click.echo(f"{Colors.BLUE}Scanning {len(svelte_files)} Svelte files...{Colors.END}")

    used_keys = set()
    key_locations = defaultdict(dict)  # key -> {file: [line_numbers]}

    for svelte_file in svelte_files:
        keys_in_file = extract_translation_keys(svelte_file)

        for key, line_numbers in keys_in_file.items():
            used_keys.add(key)
            key_locations[key][str(svelte_file.relative_to(Path.cwd()))] = line_numbers

    return used_keys, key_locations


@click.command()
@click.option('--check', is_flag=True, help='Show usage statistics only')
@click.option('--unused', is_flag=True, help='List unused translation keys')
@click.option('--missing', is_flag=True, help='List keys used in code but not in JSON')
@click.option('--full', is_flag=True, help='Full report (all checks)')
@click.option('--scan', default='frontend/apps/web/src', help='Directory to scan for Svelte files')
@click.option('--sv-file', default='frontend/apps/web/messages/sv.json', help='Path to Swedish file')
@click.option('--en-file', default='frontend/apps/web/messages/en.json', help='Path to English file')
@click.option('--limit', default=20, help='Limit number of results shown per category')
def main(check, unused, missing, full, scan, sv_file, en_file, limit):
    """Extract and analyze Paraglide translation key usage from Svelte files"""

    # Resolve paths
    scan_dir = Path(scan)
    sv_path = Path(sv_file)
    en_path = Path(en_file)

    # Validate scan directory
    if not scan_dir.exists():
        click.echo(f"{Colors.RED}L Error: Scan directory does not exist: {scan_dir}{Colors.END}", err=True)
        sys.exit(2)

    click.echo(f"{Colors.BLUE}{Colors.BOLD}= Extracting translation key usage...{Colors.END}\n")

    # Load translation files
    sv_data = load_json(sv_path)
    en_data = load_json(en_path)

    # Get translation keys (excluding $schema)
    sv_keys = set(k for k in sv_data.keys() if k != '$schema')
    en_keys = set(k for k in en_data.keys() if k != '$schema')
    all_translation_keys = sv_keys | en_keys

    # Scan Svelte files
    used_keys, key_locations = scan_all_svelte_files(scan_dir)

    # Calculate statistics
    total_translation_keys = len(all_translation_keys)
    total_used_keys = len(used_keys)
    unused_keys = all_translation_keys - used_keys
    missing_keys = used_keys - all_translation_keys
    total_unused = len(unused_keys)
    total_missing = len(missing_keys)

    usage_percentage = (total_used_keys / total_translation_keys * 100) if total_translation_keys > 0 else 0

    # Always show basic statistics
    click.echo(f"{Colors.BOLD}=Ê Usage Statistics:{Colors.END}")
    click.echo(f"  Total keys in translations: {total_translation_keys}")
    click.echo(f"  Keys used in code: {total_used_keys} ({usage_percentage:.1f}%)")
    click.echo(f"  Unused keys: {total_unused} ({100 - usage_percentage:.1f}%)")

    if total_missing > 0:
        click.echo(f"  {Colors.RED}Missing keys: {total_missing}{Colors.END}")

    # Report unused keys
    if unused or full:
        if unused_keys:
            click.echo(f"\n{Colors.YELLOW}   Unused Keys ({len(unused_keys)} cleanup candidates):{Colors.END}")

            # Sort by key name
            sorted_unused = sorted(unused_keys)

            for key in sorted_unused[:limit]:
                # Check if in sv or en or both
                in_sv = key in sv_keys
                in_en = key in en_keys

                location = ""
                if in_sv and in_en:
                    location = "sv + en"
                elif in_sv:
                    location = "sv only"
                elif in_en:
                    location = "en only"

                click.echo(f"   - {key} ({location})")

            if len(unused_keys) > limit:
                click.echo(f"   ... and {len(unused_keys) - limit} more")
                click.echo(f"\n{Colors.BLUE}=¡ Tip: Use --limit to see more results{Colors.END}")
        else:
            click.echo(f"\n{Colors.GREEN} All translation keys are used in code!{Colors.END}")

    # Report missing keys (used in code but not in translations)
    if missing or full:
        if missing_keys:
            click.echo(f"\n{Colors.RED}L Missing Keys ({len(missing_keys)} used in code but not in JSON):{Colors.END}")

            sorted_missing = sorted(missing_keys)

            for key in sorted_missing[:limit]:
                # Show where it's used
                if key in key_locations:
                    locations = key_locations[key]
                    first_file = list(locations.keys())[0]
                    first_line = locations[first_file][0]
                    click.echo(f"   - {key}")
                    click.echo(f"     Used in: {first_file}:{first_line}")

                    if len(locations) > 1:
                        click.echo(f"     ... and {len(locations) - 1} more file(s)")
                else:
                    click.echo(f"   - {key}")

            if len(missing_keys) > limit:
                click.echo(f"   ... and {len(missing_keys) - limit} more")

            click.echo(f"\n{Colors.YELLOW}=¡ Action: Add these keys to sv.json and en.json{Colors.END}")
        else:
            click.echo(f"\n{Colors.GREEN} All used keys exist in translation files!{Colors.END}")

    # Summary
    if check or full:
        click.echo(f"\n{Colors.BOLD}Summary:{Colors.END}")
        if total_unused > 0:
            click.echo(f"  {Colors.YELLOW}’{Colors.END} Consider removing {total_unused} unused keys to reduce file size")
        if total_missing > 0:
            click.echo(f"  {Colors.RED}’{Colors.END} Add {total_missing} missing keys to prevent runtime errors")
        if total_unused == 0 and total_missing == 0:
            click.echo(f"  {Colors.GREEN}’{Colors.END} Translation files are perfectly synchronized with code!")

        # Calculate potential file size reduction
        if total_unused > 0:
            reduction_percentage = (total_unused / total_translation_keys * 100)
            click.echo(f"\n{Colors.BLUE}=¾ Potential file size reduction: ~{reduction_percentage:.1f}%{Colors.END}")

    # Exit code
    if total_missing > 0:
        sys.exit(1)  # Missing keys is an error
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
