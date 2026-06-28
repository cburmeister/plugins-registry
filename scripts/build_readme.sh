#!/usr/bin/env bash
# Build README.md from the per-category source files in plugins/*.yml. Shared by
# the merge-plugins and update-stars workflows so the rendered table cannot drift
# between them.
set -euo pipefail

# Pin collation so row ordering is deterministic across runner locales.
export LC_ALL=C

{
  echo "# tpack Plugin Registry"
  echo ""
  echo "Community-maintained plugin list for [tpack](https://github.com/tmuxpack/tpack)."
  echo ""
  echo "## Adding a Plugin"
  echo ""
  echo "See [CONTRIBUTING.md](CONTRIBUTING.md)."
  echo ""

  for f in plugins/*.yml; do
    cat=$(basename "$f" .yml)
    echo "## ${cat^}"
    echo ""
    echo "| Plugin | Description | Stars |"
    echo "|--------|-------------|-------|"

    count=$(yq eval 'length' "$f")
    if [ "$count" = "0" ]; then
      echo "| *No plugins yet* | | |"
      echo ""
      continue
    fi

    tmpfile=$(mktemp)
    for i in $(seq 0 $(( count - 1 ))); do
      repo=$(yq eval ".[$i].repo" "$f")
      desc=$(yq eval ".[$i].description" "$f")
      stars=$(yq eval ".[$i].stars // 0" "$f")
      host=$(yq eval ".[$i].host // \"\"" "$f")
      name="${repo#*/}"
      owner="${repo%%/*}"
      link_host="${host:-github.com}"
      printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$owner" "$repo" "$desc" "$stars" "$link_host" >> "$tmpfile"
    done
    sort -t$'\t' -k1,1 -f "$tmpfile" | while IFS=$'\t' read -r name owner repo desc stars link_host; do
      echo "| ${owner}/[**${name}**](https://${link_host}/${repo}) | ${desc} | ${stars} |"
    done
    rm -f "$tmpfile"
    echo ""
  done
} > README.md
