# Git Journal

Universal changelog and devlog generator for all your Git repositories.

## Features

- 📝 **Auto-generate DEVLOG.md** - Journal of all commits
- 📋 **Auto-generate CHANGELOG.md** - Categorized by type (Added, Fixed, etc.)
- 🔗 **Git hooks** - Auto-update devlog on every commit
- 📓 **OneNote export** - HTML format ready to paste
- 🗂️ **Multi-repo support** - Aggregate logs across all your projects

## Installation

```bash
cd ~/Documents/jmragsdale/git-journal
bash install.sh
```

Or manually add to your `~/.zshrc`:

```bash
alias gitjournal='python3 ~/Documents/jmragsdale/git-journal/gitjournal.py'
```

## Usage

### Initialize a Repository

```bash
cd /path/to/your/repo
gitjournal --init
```

This will:
- Generate initial DEVLOG.md
- Install post-commit hook for auto-updates
- Track the repo in ~/.gitjournal/repos.json

### Generate Logs

```bash
# Generate devlog (commit journal)
gitjournal

# Generate changelog (categorized)
gitjournal --changelog

# Export for OneNote
gitjournal --export-html
```

### Multi-Repo Features

```bash
# List all tracked repositories
gitjournal --list

# Generate combined devlog from all repos
gitjournal --all-repos
```

## Conventional Commits

For best changelog categorization, use conventional commit format:

| Prefix | Category |
|--------|----------|
| `feat:` | Added |
| `fix:` | Fixed |
| `docs:` | Documentation |
| `refactor:` | Changed |
| `security:` | Security |
| `perf:` | Performance |
| `test:` | Testing |
| `chore:` | Maintenance |

Example:
```bash
git commit -m "feat: Add user authentication"
git commit -m "fix: Resolve login timeout issue"
```

## Configuration

Config stored in `~/.gitjournal/config.json`:

```json
{
  "default_devlog": "DEVLOG.md",
  "default_changelog": "CHANGELOG.md", 
  "max_commits_in_devlog": 50,
  "auto_commit_devlog": false
}
```

## Tracked Repositories

Repos are tracked in `~/.gitjournal/repos.json` after running `--init`.

## OneNote Integration

Export devlog to HTML and paste into OneNote:

```bash
gitjournal --export-html
```

This opens a styled HTML file - just Cmd+A, Cmd+C, then paste into OneNote.
