#!/usr/bin/env python3
"""Compare the local plugin registry against upstream sources and report missing plugins.

Upstream sources:
  - https://github.com/rothgar/awesome-tmux
  - https://github.com/tmux-plugins/list

Usage:
  python scripts/find_missing.py
"""

import re
import sys
import urllib.request
from pathlib import Path

REGISTRY_DIR = Path(__file__).resolve().parent.parent / "plugins"

SOURCES = {
    "awesome-tmux": "https://raw.githubusercontent.com/rothgar/awesome-tmux/master/README.md",
    "tmux-plugins/list": "https://raw.githubusercontent.com/tmux-plugins/list/master/README.md",
}

GITHUB_REPO_PATTERN = re.compile(
    r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
)


def load_registry_repos() -> set[str]:
    """Read all plugins/*.yml and return a set of lowercased owner/repo strings."""
    repos: set[str] = set()
    for yml_path in sorted(REGISTRY_DIR.glob("*.yml")):
        for line in yml_path.read_text().splitlines():
            line = line.strip()
            if "repo:" in line:
                repo = line.split("repo:", 1)[1].strip()
                if repo:
                    repos.add(repo.lower())
    return repos


def fetch_repos_from_url(url: str) -> set[str]:
    """Fetch a README and extract all github.com/<owner>/<repo> references."""
    req = urllib.request.Request(url, headers={"User-Agent": "find-missing-plugins/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    repos: set[str] = set()
    for match in GITHUB_REPO_PATTERN.finditer(text):
        repo = match.group(1).rstrip("/").rstrip(")")
        # Strip trailing anchors or fragments
        repo = repo.split("#")[0].split("?")[0].rstrip("/")
        # Only keep owner/name (no deeper paths)
        parts = repo.split("/")
        if len(parts) >= 2:
            owner_repo = f"{parts[0]}/{parts[1]}"
            repos.add(owner_repo.lower())
    return repos


SKIP_REPOS = {
    # Meta / ecosystem repos (not installable tmux plugins)
    "tmux-plugins/tpm",
    "tmux-plugins/list",
    "tmux-plugins/vim-tmux",
    "rothgar/awesome-tmux",
    "gpakosz/.tmux",
    "tmux/tmux",
    # Standalone CLI tools (not tmux plugins)
    "junegunn/fzf",
    "ajeetdsouza/zoxide",
    "jesseduffield/lazygit",
    "nvim-tree/nvim-tree.lua",
    "rigellute/spotify-tui",
    "powerline/powerline",
    # Session managers / tmux wrappers (not TPM plugins)
    "tmuxinator/tmuxinator",
    "tmux-python/tmuxp",
    "tmux-python/libtmux",
    "tony/tmuxp",
    "tony/tmux-config",
    "jimeh/tmuxifier",
    "ivaaaan/smug",
    "remi/teamocil",
    "ryandotsmith/tat",
    "vinnymeller/twm",
    "evnp/tmex",
    "sriramkandukuri/automux",
    # Color schemes (not tmux-specific plugins)
    "chriskempson/base16-shell",
    "chriskempson/tomorrow-theme",
    "morhetz/gruvbox",
    # Gists and non-repos
    "rothgar/719ef460efc214c8d222",
    "mohamedalaa/2961058",
    "james1236/73bb8b7279dca0bc821518abada38f1e",
    # Misc tools that happen to mention tmux
    "samg/timetrap",
    "csdvrx/sixel-tmux",
    "goerz/tmuxpair",
    "huntie/sublime-tmux",
    "brandur/tmux-extra",
    "jamesottaway/tmux-up",
    "mapio/tmux-tail-f",
    "bfly123/claude_code_bridge",
}

# Repos that appear under a different owner in the registry (aliases).
# Maps lowercased upstream name -> lowercased registry name.
ALIASES = {
    "thuanpham2311/tmux-fzf-session-switch": "thuanowa/tmux-fzf-session-switch",
    "crispy1989/tmux-copy-toolkit": "crispyconductor/tmux-copy-toolkit",
    "chanderg/tmux-notify": "rickstaa/tmux-notify",
    "nordtheme/tmux": "arcticicestudio/nord-tmux",
}


def main() -> int:
    registry = load_registry_repos()
    print(f"Registry contains {len(registry)} plugins\n")

    total_missing = 0

    for name, url in SOURCES.items():
        print(f"--- {name} ({url}) ---")
        try:
            upstream = fetch_repos_from_url(url)
        except Exception as e:
            print(f"  ERROR fetching: {e}\n")
            continue

        # Resolve aliases so upstream names match registry names
        resolved_registry = registry | {k for k, v in ALIASES.items() if v in registry}
        missing = sorted(
            upstream - resolved_registry - {r.lower() for r in SKIP_REPOS}
        )

        if not missing:
            print("  All repos accounted for.\n")
            continue

        print(f"  {len(missing)} potentially missing:\n")
        for repo in missing:
            print(f"    https://github.com/{repo}")
        print()
        total_missing += len(missing)

    if total_missing:
        print(f"Total: {total_missing} potentially missing repos across all sources.")
        print("Review each link — some may be tools, not tmux plugins.")
    else:
        print("Registry is fully up to date with all sources.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
