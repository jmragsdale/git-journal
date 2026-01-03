#!/bin/bash
# Git Journal - Installation Script

INSTALL_DIR="$HOME/Documents/jmragsdale/git-journal"
SCRIPT_NAME="gitjournal"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Git Journal - Installation           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Create alias in shell config
SHELL_CONFIG="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Check if alias already exists
if grep -q "gitjournal" "$SHELL_CONFIG" 2>/dev/null; then
    echo "✅ gitjournal alias already configured in $SHELL_CONFIG"
else
    echo "" >> "$SHELL_CONFIG"
    echo "# Git Journal - auto-changelog tool" >> "$SHELL_CONFIG"
    echo "alias gitjournal='python3 $INSTALL_DIR/gitjournal.py'" >> "$SHELL_CONFIG"
    echo "✅ Added gitjournal alias to $SHELL_CONFIG"
fi

# Create symlink in /usr/local/bin (optional, requires sudo)
echo ""
read -p "Create system-wide command? (requires sudo) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo ln -sf "$INSTALL_DIR/gitjournal.py" /usr/local/bin/gitjournal
    echo "✅ Created /usr/local/bin/gitjournal"
fi

echo ""
echo "════════════════════════════════════════"
echo "Installation complete!"
echo ""
echo "Usage (after restarting terminal or running 'source $SHELL_CONFIG'):"
echo ""
echo "  gitjournal              # Generate devlog for current repo"
echo "  gitjournal --init       # Initialize journaling + install hook"
echo "  gitjournal --changelog  # Generate categorized changelog"
echo "  gitjournal --export-html # Export for OneNote"
echo "  gitjournal --all-repos  # Combined log from all repos"
echo "  gitjournal --list       # List tracked repos"
echo ""
echo "════════════════════════════════════════"
