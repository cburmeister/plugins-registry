#!/usr/bin/env bash
# Build the merged registry (dist/plugins.yml) from the per-category source
# files in plugins/*.yml. This is the single source of truth for dist
# generation; both the merge-plugins and update-stars workflows call it so the
# emitted field set cannot drift between them.
#
# Star counts and added_date are read from the source files as-is; this script
# does not hit the network. Populate those fields before calling it.
set -euo pipefail

echo "categories:" > dist/plugins.yml

for f in plugins/*.yml; do
  cat=$(basename "$f" .yml)
  echo "  - $cat" >> dist/plugins.yml
done

echo "" >> dist/plugins.yml
echo "plugins:" >> dist/plugins.yml

for f in plugins/*.yml; do
  cat=$(basename "$f" .yml)
  count=$(yq eval 'length' "$f")
  if [ "$count" = "0" ]; then continue; fi

  for i in $(seq 0 $(( count - 1 ))); do
    repo=$(yq eval ".[$i].repo" "$f")
    desc=$(yq eval ".[$i].description" "$f")
    author=$(yq eval ".[$i].author" "$f")
    stars=$(yq eval ".[$i].stars // 0" "$f")
    host=$(yq eval ".[$i].host // \"\"" "$f")
    added_date=$(yq eval ".[$i].added_date // \"\"" "$f")

    echo "  - repo: $repo" >> dist/plugins.yml
    echo "    description: \"$desc\"" >> dist/plugins.yml
    echo "    author: $author" >> dist/plugins.yml
    echo "    category: $cat" >> dist/plugins.yml
    echo "    stars: $stars" >> dist/plugins.yml
    if [ -n "$host" ]; then
      echo "    host: $host" >> dist/plugins.yml
    fi
    if [ -n "$added_date" ]; then
      echo "    added_date: \"$added_date\"" >> dist/plugins.yml
    fi
  done
done
