#!/usr/bin/env python3
"""Backfill added_date for all plugins by mining git history.

For each plugin missing added_date, this script:
1. Runs git log with patches to find the commit that first added the repo: line
2. Extracts the author date from that commit
3. Writes added_date: "YYYY-MM-DD" into the YAML source file
"""

import glob
import re
import subprocess
import yaml

REGISTRY_ROOT = "/home/antoinegs/gits/plugins-registry"


def find_added_date(filepath: str, repo: str) -> str | None:
    """Find the date when a repo: line was first added to a file via git log."""
    # Get full diff log for the file
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%aI", "-p", "--", filepath],
        capture_output=True,
        text=True,
        cwd=REGISTRY_ROOT,
    )

    if result.returncode != 0:
        return None

    output = result.stdout
    current_date = None
    # Pattern to match the repo line being added in a diff
    repo_pattern = re.compile(r"^\+.*repo:\s*" + re.escape(repo) + r"\s*$")
    # Pattern to match ISO date format from --format=%aI
    date_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}T[\d:+-]+)")

    for line in output.splitlines():
        date_match = date_pattern.match(line)
        if date_match:
            current_date = date_match.group(1)[:10]  # Extract YYYY-MM-DD
        if repo_pattern.match(line) and current_date:
            return current_date

    # The --diff-filter=A only shows file-creation commits. If the plugin was
    # added to an already-existing file, we need the full log.
    result = subprocess.run(
        ["git", "log", "--format=%aI", "-p", "--", filepath],
        capture_output=True,
        text=True,
        cwd=REGISTRY_ROOT,
    )

    if result.returncode != 0:
        return None

    output = result.stdout
    current_date = None
    last_match_date = None

    for line in output.splitlines():
        date_match = date_pattern.match(line)
        if date_match:
            current_date = date_match.group(1)[:10]
        if repo_pattern.match(line) and current_date:
            last_match_date = current_date

    # git log is newest-first, so the last match with +repo: is the earliest commit
    if last_match_date:
        return last_match_date

    # Fallback: use the earliest commit date for the file
    result = subprocess.run(
        [
            "git",
            "log",
            "--diff-filter=A",
            "--format=%aI",
            "--reverse",
            "--",
            filepath,
        ],
        capture_output=True,
        text=True,
        cwd=REGISTRY_ROOT,
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().splitlines()[0][:10]

    return None


def main():
    plugin_files = sorted(glob.glob(f"{REGISTRY_ROOT}/plugins/*.yml"))
    total_updated = 0

    for filepath in plugin_files:
        with open(filepath) as f:
            plugins = yaml.safe_load(f)

        if not plugins:
            continue

        modified = False
        relative_path = filepath.replace(REGISTRY_ROOT + "/", "")

        for plugin in plugins:
            if "added_date" in plugin:
                continue

            repo = plugin.get("repo", "")
            if not repo:
                continue

            date = find_added_date(relative_path, repo)
            if date:
                plugin["added_date"] = date
                modified = True
                total_updated += 1
                print(f"  {repo} -> {date}")
            else:
                print(f"  WARNING: Could not find date for {repo}")

        if modified:
            with open(filepath, "w") as f:
                yaml.dump(plugins, f, default_flow_style=False, sort_keys=False)
            print(f"Updated {filepath}")

    print(f"\nTotal plugins updated: {total_updated}")


if __name__ == "__main__":
    main()
