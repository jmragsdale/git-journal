# Git Journal

Universal changelog and devlog generator for all your Git repositories.

## Features

- 📝 **Auto-generate DEVLOG.md** - Journal of all commits
- 📋 **Auto-generate CHANGELOG.md** - Categorized by type (Added, Fixed, etc.)
- 🔗 **Git hooks** - Auto-update devlog on every commit
- 📓 **OneNote export** - HTML format ready to paste
- 🗂️ **Multi-repo support** - Aggregate logs across all your projects
- 🔍 **Batch operations** - Scan and initialize all repos at once

## Installation

### Option 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/jmragsdale/git-journal.git ~/.git-journal

# Run the installer
cd ~/.git-journal
bash install.sh
```

### Option 2: Manual Setup

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias gitjournal='python3 ~/.git-journal/gitjournal.py'
```

Then reload your shell:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Quick Start

### Initialize All Repos at Once

```bash
# Scan a directory and initialize all git repos found
gitjournal --scan ~/Projects

# Scan with custom depth (default is 3)
gitjournal --scan ~/Code --depth 5
```

### Generate Logs for All Repos

```bash
# Generate devlogs for all tracked repos
gitjournal --generate-all

# Generate both devlogs and changelogs
gitjournal --generate-all --changelog
```

## Usage

### Single Repository Commands

```bash
# Initialize current repo (creates devlog + installs hook)
gitjournal --init

# Generate devlog
gitjournal

# Generate changelog
gitjournal --changelog

# Export for OneNote
gitjournal --export-html
```

### Multi-Repo Commands

```bash
# List all tracked repositories
gitjournal --list

# Scan directory and initialize all repos
gitjournal --scan ~/Projects

# Generate logs for all tracked repos
gitjournal --generate-all

# Generate devlogs + changelogs for all
gitjournal --generate-all --changelog

# Combined log from all repos (single file)
gitjournal --all-repos
```

## Command Reference

| Command | Description |
|---------|-------------|
| `gitjournal` | Generate devlog for current repo |
| `gitjournal --init` | Initialize repo (devlog + hook) |
| `gitjournal --changelog` | Generate categorized changelog |
| `gitjournal --export-html` | Export for OneNote |
| `gitjournal --list` | List tracked repositories |
| `gitjournal --scan <dir>` | Find & initialize all repos in directory |
| `gitjournal --generate-all` | Generate logs for all tracked repos |
| `gitjournal --all-repos` | Combined log from all repos |

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

Repos are tracked in `~/.gitjournal/repos.json` after running `--init` or `--scan`.

## OneNote Integration

Export devlog to HTML and paste into OneNote:

```bash
gitjournal --export-html
```

This opens a styled HTML file - just Cmd+A (or Ctrl+A), Cmd+C (or Ctrl+C), then paste into OneNote.

## License

MIT License - Feel free to use, modify, and distribute.
