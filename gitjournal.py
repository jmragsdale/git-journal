#!/usr/bin/env python3
"""
Git Journal - Universal changelog and devlog generator for all repositories

Features:
- Generate DEVLOG.md for any git repository
- Generate CHANGELOG.md with categorized commits
- Export to OneNote-friendly HTML
- Install git hooks for auto-journaling
- Aggregate logs from multiple repos

Installation:
    # Add to PATH (add to ~/.zshrc or ~/.bashrc)
    export PATH="$PATH:/Users/jermaineragsdale/Documents/jmragsdale/git-journal"
    
    # Or create alias
    alias gitjournal='python3 /Users/jermaineragsdale/Documents/jmragsdale/git-journal/gitjournal.py'

Usage:
    gitjournal                     # Generate devlog for current repo
    gitjournal --changelog         # Generate changelog
    gitjournal --install-hook      # Install auto-update hook
    gitjournal --export-html       # Export for OneNote
    gitjournal --all-repos         # Aggregate all repos
    gitjournal --init              # Initialize journaling for current repo
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
CONFIG_DIR = os.path.expanduser("~/.gitjournal")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
REPOS_FILE = os.path.join(CONFIG_DIR, "repos.json")


class GitJournal:
    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.getcwd()
        self._ensure_config_dir()
        self.config = self._load_config()
        self.repos = self._load_repos()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    def _load_config(self):
        """Load global configuration"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'default_devlog': 'DEVLOG.md',
            'default_changelog': 'CHANGELOG.md',
            'max_commits_in_devlog': 50,
            'auto_commit_devlog': False,
            'onenote_client_id': None
        }
    
    def _save_config(self):
        """Save global configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_repos(self):
        """Load tracked repositories"""
        if os.path.exists(REPOS_FILE):
            with open(REPOS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_repos(self):
        """Save tracked repositories"""
        with open(REPOS_FILE, 'w') as f:
            json.dump(self.repos, f, indent=2)
    
    def _run_git(self, *args, cwd=None):
        """Run a git command and return output"""
        cmd = ['git'] + list(args)
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=cwd or self.repo_path
        )
        return result.stdout.strip(), result.returncode
    
    def _is_git_repo(self, path=None):
        """Check if path is a git repository"""
        _, code = self._run_git('rev-parse', '--git-dir', cwd=path or self.repo_path)
        return code == 0
    
    def _get_repo_name(self, path=None):
        """Get repository name from remote or folder"""
        remote, _ = self._run_git('remote', 'get-url', 'origin', cwd=path or self.repo_path)
        if remote:
            # Extract repo name from URL
            name = remote.split('/')[-1].replace('.git', '')
            return name
        return os.path.basename(path or self.repo_path)
    
    def _get_commits(self, limit=None, since_tag=None, cwd=None):
        """Get commits from repository"""
        cmd_args = ['log', '--pretty=format:%H|%ad|%s|%b', '--date=short']
        if limit:
            cmd_args.append(f'-{limit}')
        if since_tag:
            cmd_args.append(f'{since_tag}..HEAD')
        
        output, code = self._run_git(*cmd_args, cwd=cwd or self.repo_path)
        
        if code != 0 or not output:
            return []
        
        commits = []
        for line in output.split('\n'):
            if '|' not in line:
                continue
            parts = line.split('|', 3)
            if len(parts) >= 3:
                commits.append({
                    'hash': parts[0][:7],
                    'date': parts[1],
                    'message': parts[2],
                    'body': parts[3] if len(parts) > 3 else ''
                })
        
        return commits
    
    def _categorize_commit(self, message):
        """Categorize commit based on conventional commit format"""
        import re
        
        message_lower = message.lower()
        
        # Conventional commits: type(scope): message
        match = re.match(r'^(\w+)(?:\([^)]+\))?:\s*(.+)$', message)
        if match:
            commit_type = match.group(1).lower()
            description = match.group(2)
            
            type_mapping = {
                'feat': 'Added',
                'fix': 'Fixed',
                'docs': 'Documentation',
                'refactor': 'Changed',
                'perf': 'Performance',
                'test': 'Testing',
                'chore': 'Maintenance',
                'breaking': 'Breaking Changes',
                'security': 'Security',
                'deprecate': 'Deprecated',
                'remove': 'Removed'
            }
            return type_mapping.get(commit_type, 'Changed'), description
        
        # Fallback: keyword detection
        if any(w in message_lower for w in ['add', 'new', 'create', 'implement', 'feature']):
            return 'Added', message
        elif any(w in message_lower for w in ['fix', 'bug', 'patch', 'resolve', 'correct']):
            return 'Fixed', message
        elif any(w in message_lower for w in ['remove', 'delete', 'drop']):
            return 'Removed', message
        elif any(w in message_lower for w in ['update', 'change', 'modify', 'refactor', 'improve']):
            return 'Changed', message
        elif any(w in message_lower for w in ['doc', 'readme', 'comment']):
            return 'Documentation', message
        elif any(w in message_lower for w in ['security', 'vulnerability', 'cve']):
            return 'Security', message
        
        return 'Changed', message
    
    def generate_devlog(self, output_file=None):
        """Generate DEVLOG.md for current repository"""
        if not self._is_git_repo():
            print(f"❌ Not a git repository: {self.repo_path}")
            return None
        
        repo_name = self._get_repo_name()
        commits = self._get_commits(limit=self.config['max_commits_in_devlog'])
        
        if not commits:
            print("No commits found")
            return None
        
        devlog = f"""# Development Log - {repo_name}

Auto-generated journal of project changes.
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""
        
        for commit in commits:
            if commit['message'].startswith('Merge'):
                continue
            
            devlog += f"""## {commit['date']}

**Commit:** `{commit['hash']}`

{commit['message']}

"""
            if commit['body'].strip():
                devlog += f"{commit['body'].strip()}\n\n"
            
            devlog += "---\n\n"
        
        output_file = output_file or os.path.join(self.repo_path, self.config['default_devlog'])
        
        with open(output_file, 'w') as f:
            f.write(devlog)
        
        print(f"✅ Generated: {output_file}")
        return output_file
    
    def generate_changelog(self, output_file=None):
        """Generate CHANGELOG.md with categorized commits"""
        if not self._is_git_repo():
            print(f"❌ Not a git repository: {self.repo_path}")
            return None
        
        repo_name = self._get_repo_name()
        commits = self._get_commits()
        
        if not commits:
            print("No commits found")
            return None
        
        # Group by category
        categories = defaultdict(list)
        for commit in commits:
            if commit['message'].startswith('Merge'):
                continue
            category, description = self._categorize_commit(commit['message'])
            categories[category].append({
                'description': description,
                'hash': commit['hash'],
                'date': commit['date']
            })
        
        changelog = f"""# Changelog - {repo_name}

All notable changes to this project will be documented in this file.
Auto-generated from git commits.

## [Unreleased] - {datetime.now().strftime('%Y-%m-%d')}

"""
        
        category_order = [
            'Breaking Changes', 'Added', 'Changed', 'Fixed',
            'Security', 'Deprecated', 'Removed', 'Documentation',
            'Performance', 'Testing', 'Maintenance'
        ]
        
        for category in category_order:
            if category in categories:
                changelog += f"### {category}\n\n"
                for item in categories[category]:
                    changelog += f"- {item['description']} (`{item['hash']}`)\n"
                changelog += "\n"
        
        output_file = output_file or os.path.join(self.repo_path, self.config['default_changelog'])
        
        with open(output_file, 'w') as f:
            f.write(changelog)
        
        print(f"✅ Generated: {output_file}")
        return output_file
    
    def install_hook(self):
        """Install post-commit hook for auto-updating devlog"""
        if not self._is_git_repo():
            print(f"❌ Not a git repository: {self.repo_path}")
            return False
        
        hooks_dir = os.path.join(self.repo_path, '.git', 'hooks')
        hook_file = os.path.join(hooks_dir, 'post-commit')
        
        hook_content = '''#!/bin/bash
# Auto-update DEVLOG.md after each commit
# Installed by gitjournal

DEVLOG="DEVLOG.md"

# Get commit info
COMMIT_HASH=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M')
COMMIT_MSG=$(git log -1 --format=%s)
COMMIT_BODY=$(git log -1 --format=%b)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD | tr '\\n' ', ' | sed 's/,$//')

# Create entry
ENTRY="## $COMMIT_DATE

**Commit:** `$COMMIT_HASH`

$COMMIT_MSG

"

if [ -n "$COMMIT_BODY" ]; then
    ENTRY+="$COMMIT_BODY

"
fi

ENTRY+="**Files:** $FILES_CHANGED

---

"

# Update DEVLOG.md
if [ -f "$DEVLOG" ]; then
    head -5 "$DEVLOG" > "$DEVLOG.tmp"
    echo "$ENTRY" >> "$DEVLOG.tmp"
    tail -n +6 "$DEVLOG" >> "$DEVLOG.tmp"
    mv "$DEVLOG.tmp" "$DEVLOG"
else
    REPO_NAME=$(basename $(git rev-parse --show-toplevel))
    echo "# Development Log - $REPO_NAME

Auto-generated journal of project changes.

$ENTRY" > "$DEVLOG"
fi

git add "$DEVLOG" 2>/dev/null || true
echo "📝 DEVLOG.md updated"
'''
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        os.chmod(hook_file, 0o755)
        print(f"✅ Installed post-commit hook: {hook_file}")
        
        # Track this repo
        repo_name = self._get_repo_name()
        self.repos[repo_name] = {
            'path': self.repo_path,
            'added': datetime.now().isoformat(),
            'hook_installed': True
        }
        self._save_repos()
        
        return True
    
    def init_repo(self):
        """Initialize journaling for current repository"""
        if not self._is_git_repo():
            print(f"❌ Not a git repository: {self.repo_path}")
            return False
        
        print(f"\n📁 Initializing journaling for: {self._get_repo_name()}\n")
        
        # Generate initial devlog
        self.generate_devlog()
        
        # Install hook
        self.install_hook()
        
        # Add to .gitignore if needed
        gitignore_path = os.path.join(self.repo_path, '.gitignore')
        gitignore_entries = ['*_onenote.html']
        
        existing = ''
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                existing = f.read()
        
        with open(gitignore_path, 'a') as f:
            for entry in gitignore_entries:
                if entry not in existing:
                    f.write(f"\n{entry}")
        
        print(f"\n✅ Repository initialized for journaling!")
        print(f"   - DEVLOG.md created")
        print(f"   - Post-commit hook installed")
        print(f"   - Repository tracked in ~/.gitjournal/repos.json")
        
        return True
    
    def export_html(self, markdown_file=None):
        """Export devlog to OneNote-friendly HTML"""
        markdown_file = markdown_file or os.path.join(self.repo_path, self.config['default_devlog'])
        
        if not os.path.exists(markdown_file):
            print(f"File not found: {markdown_file}")
            print("Run 'gitjournal' first to generate the devlog")
            return None
        
        with open(markdown_file, 'r') as f:
            content = f.read()
        
        html_content = self._markdown_to_html(content)
        repo_name = self._get_repo_name()
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{repo_name} - Development Log</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #1f2937;
        }}
        h1 {{ color: #1e40af; border-bottom: 3px solid #1e40af; padding-bottom: 10px; }}
        h2 {{ color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-top: 25px; }}
        h3 {{ color: #059669; }}
        code {{ 
            background-color: #f3f4f6; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'SF Mono', Consolas, monospace;
            color: #dc2626;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9em;
        }}
        hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
        strong {{ color: #4f46e5; }}
        .header-info {{
            background: #eff6ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #2563eb;
        }}
    </style>
</head>
<body>
    <div class="header-info">
        <strong>📋 To copy to OneNote:</strong> Select all (Cmd+A), Copy (Cmd+C), paste into OneNote
    </div>
    {html_content}
</body>
</html>
"""
        
        output_file = markdown_file.replace('.md', '_onenote.html')
        
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Exported: {output_file}")
        
        # Open in browser
        subprocess.run(['open', output_file])
        
        return output_file
    
    def _markdown_to_html(self, text):
        """Convert markdown to HTML"""
        import re
        
        lines = text.split('\n')
        html = []
        in_code = False
        
        for line in lines:
            if line.startswith('```'):
                html.append('</pre>' if in_code else '<pre>')
                in_code = not in_code
                continue
            
            if in_code:
                html.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                continue
            
            if line.startswith('## '):
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('# '):
                html.append(f'<h1>{line[2:]}</h1>')
            elif line.strip() == '---':
                html.append('<hr/>')
            elif line.startswith('- '):
                html.append(f'<li>{line[2:]}</li>')
            elif '**' in line:
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                html.append(f'<p>{line}</p>')
            elif '`' in line:
                line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
                html.append(f'<p>{line}</p>')
            elif line.strip():
                html.append(f'<p>{line}</p>')
        
        return '\n'.join(html)
    
    def aggregate_all_repos(self, output_file=None):
        """Generate combined devlog from all tracked repositories"""
        if not self.repos:
            print("No repositories tracked yet.")
            print("Run 'gitjournal --init' in your repositories first.")
            return None
        
        all_commits = []
        
        for repo_name, repo_info in self.repos.items():
            repo_path = repo_info['path']
            if not os.path.exists(repo_path):
                print(f"⚠️  Repository not found: {repo_path}")
                continue
            
            commits = self._get_commits(limit=20, cwd=repo_path)
            for commit in commits:
                commit['repo'] = repo_name
                all_commits.append(commit)
        
        # Sort by date (newest first)
        all_commits.sort(key=lambda x: x['date'], reverse=True)
        
        devlog = f"""# Combined Development Log

Activity across all tracked repositories.
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Repositories: {', '.join(self.repos.keys())}

"""
        
        current_date = None
        for commit in all_commits[:100]:  # Last 100 commits across all repos
            if commit['message'].startswith('Merge'):
                continue
            
            if commit['date'] != current_date:
                current_date = commit['date']
                devlog += f"\n## {current_date}\n\n"
            
            devlog += f"**[{commit['repo']}]** {commit['message']} (`{commit['hash']}`)\n\n"
        
        output_file = output_file or os.path.join(CONFIG_DIR, 'COMBINED_DEVLOG.md')
        
        with open(output_file, 'w') as f:
            f.write(devlog)
        
        print(f"✅ Generated combined devlog: {output_file}")
        return output_file
    
    def list_repos(self):
        """List all tracked repositories"""
        if not self.repos:
            print("\nNo repositories tracked yet.")
            print("Run 'gitjournal --init' in your repositories to start tracking.\n")
            return
        
        print("\n📚 Tracked Repositories:\n")
        for name, info in self.repos.items():
            status = "✅" if os.path.exists(info['path']) else "❌"
            hook = "🔗" if info.get('hook_installed') else "  "
            print(f"  {status} {hook} {name}")
            print(f"       {info['path']}")
        print(f"\n  Total: {len(self.repos)} repositories\n")
    
    def find_repos(self, search_path, max_depth=3):
        """Find all git repositories under a directory"""
        repos_found = []
        search_path = os.path.expanduser(search_path)
        
        if not os.path.exists(search_path):
            print(f"❌ Path not found: {search_path}")
            return repos_found
        
        print(f"\n🔍 Scanning for git repositories in: {search_path}")
        print(f"   (max depth: {max_depth})\n")
        
        for root, dirs, files in os.walk(search_path):
            # Calculate depth
            depth = root.replace(search_path, '').count(os.sep)
            if depth >= max_depth:
                dirs[:] = []  # Don't go deeper
                continue
            
            # Skip hidden directories and common non-repo folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', 'venv', 'env', '__pycache__', 'vendor', 'build', 'dist']]
            
            # Check if this is a git repo
            if '.git' in os.listdir(root):
                repos_found.append(root)
                dirs[:] = []  # Don't go into subdirectories of a repo
        
        return repos_found
    
    def scan_and_init(self, search_path, max_depth=3):
        """Scan directory for repos and initialize all of them"""
        repos = self.find_repos(search_path, max_depth)
        
        if not repos:
            print("No git repositories found.")
            return
        
        print(f"Found {len(repos)} repositories:\n")
        for i, repo in enumerate(repos, 1):
            print(f"  {i}. {os.path.basename(repo)}")
            print(f"     {repo}")
        
        print("")
        confirm = input(f"Initialize journaling for all {len(repos)} repos? [y/N]: ").strip().lower()
        
        if confirm != 'y':
            print("Cancelled.")
            return
        
        print("\n" + "="*60)
        
        initialized = 0
        for repo_path in repos:
            print(f"\n📁 {os.path.basename(repo_path)}")
            
            # Create a new journal instance for this repo
            journal = GitJournal(repo_path=repo_path)
            
            try:
                journal.init_repo()
                initialized += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "="*60)
        print(f"\n✅ Initialized {initialized}/{len(repos)} repositories")
        print(f"\nRun 'gitjournal --list' to see all tracked repos")
    
    def generate_all_logs(self, changelog=False):
        """Generate devlogs (and optionally changelogs) for all tracked repos"""
        if not self.repos:
            print("No repositories tracked yet.")
            print("Run 'gitjournal --scan <directory>' to find and initialize repos.")
            return
        
        print(f"\n📝 Generating logs for {len(self.repos)} repositories...\n")
        print("="*60)
        
        success = 0
        for repo_name, repo_info in self.repos.items():
            repo_path = repo_info['path']
            
            if not os.path.exists(repo_path):
                print(f"\n❌ {repo_name}: Path not found")
                continue
            
            print(f"\n📁 {repo_name}")
            
            journal = GitJournal(repo_path=repo_path)
            
            try:
                journal.generate_devlog()
                if changelog:
                    journal.generate_changelog()
                success += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "="*60)
        print(f"\n✅ Generated logs for {success}/{len(self.repos)} repositories")


def main():
    parser = argparse.ArgumentParser(
        description='Git Journal - Universal changelog and devlog generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitjournal                  Generate devlog for current repo
  gitjournal --changelog      Generate categorized changelog
  gitjournal --init           Initialize journaling (devlog + hook)
  gitjournal --export-html    Export to OneNote-friendly HTML
  gitjournal --all-repos      Combined log from all tracked repos
  gitjournal --list           List tracked repositories
  
  # Batch operations:
  gitjournal --scan ~/Projects          Scan & initialize all repos in directory
  gitjournal --generate-all             Generate devlogs for all tracked repos
  gitjournal --generate-all --changelog Generate devlogs + changelogs for all
        """
    )
    
    parser.add_argument('--changelog', action='store_true', help='Generate CHANGELOG.md')
    parser.add_argument('--init', action='store_true', help='Initialize journaling for current repo')
    parser.add_argument('--install-hook', action='store_true', help='Install post-commit hook only')
    parser.add_argument('--export-html', action='store_true', help='Export to OneNote HTML')
    parser.add_argument('--all-repos', action='store_true', help='Aggregate all tracked repos into one log')
    parser.add_argument('--list', action='store_true', help='List tracked repositories')
    parser.add_argument('--path', help='Repository path (default: current directory)')
    
    # Batch operations
    parser.add_argument('--scan', metavar='DIR', help='Scan directory for repos and initialize all')
    parser.add_argument('--depth', type=int, default=3, help='Max depth for --scan (default: 3)')
    parser.add_argument('--generate-all', action='store_true', help='Generate logs for all tracked repos')
    
    args = parser.parse_args()
    
    journal = GitJournal(repo_path=args.path)
    
    if args.scan:
        journal.scan_and_init(args.scan, max_depth=args.depth)
    elif args.generate_all:
        journal.generate_all_logs(changelog=args.changelog)
    elif args.list:
        journal.list_repos()
    elif args.all_repos:
        journal.aggregate_all_repos()
    elif args.init:
        journal.init_repo()
    elif args.install_hook:
        journal.install_hook()
    elif args.changelog:
        journal.generate_changelog()
    elif args.export_html:
        journal.export_html()
    else:
        journal.generate_devlog()


if __name__ == "__main__":
    main()
