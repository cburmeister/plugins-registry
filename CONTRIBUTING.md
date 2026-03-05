# Contributing to plugins-registry

Thank you for contributing to the tpack plugin registry!

## Adding a Plugin

1. Fork this repository
2. Add your plugin to the appropriate category file in `plugins/`
3. Submit a pull request

### Category Files

| File | Description |
|------|-------------|
| `plugins/theme.yml` | Visual themes and color schemes |
| `plugins/statusbar.yml` | Status bar enhancements |
| `plugins/navigation.yml` | Pane/window navigation |
| `plugins/session.yml` | Session management and persistence |
| `plugins/utility.yml` | General-purpose utilities |
| `plugins/development.yml` | Developer tools and integrations |

### Entry Format

Add your plugin to the appropriate category file:

```yaml
# GitHub (default)
- repo: your-username/your-plugin
  description: A short description of what the plugin does
  author: your-username

# Non-GitHub host (e.g. GitLab)
- repo: your-username/your-plugin
  host: gitlab.com
  description: A short description of what the plugin does
  author: your-username
```

### Requirements

- **repo**: Must be in `user/repo` format and point to a valid public repository
- **host** *(optional)*: The git host domain (e.g. `gitlab.com`). Omit for GitHub repos
- **description**: Between 10 and 200 characters
- **author**: Your username on the host
- **stars**: Do NOT add this field — it is managed automatically by CI

### What Happens Next

1. CI will automatically validate your entry (YAML syntax, repo exists, no duplicates)
2. A maintainer will review and merge your PR
3. Your plugin will appear in tpack's search screen
