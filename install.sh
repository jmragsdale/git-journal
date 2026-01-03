#!/bin/bash
# Git Journal - Installation Script

# Determine install directory (where this script is located)
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="gitjournal"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Git Journal - Installation           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Installing from: $INSTALL_DIR"
echo ""

# Determine shell config file
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Check if alias already exists
if grep -q "alias gitjournal=" "$SHELL_CONFIG" 2>/dev/null; then
    echo "✅ gitjournal alias already exists in $SHELL_CONFIG"
    # Update the path in case it changed
    sed -i.bak "s|alias gitjournal=.*|alias gitjournal='python3 $INSTALL_DIR/gitjournal.py'|" "$SHELL_CONFIG"
    echo "   Updated path to: $INSTALL_DIR"
else
    echo "" >> "$SHELL_CONFIG"
    echo "# Git Journal - auto-changelog tool" >> "$SHELL_CONFIG"
    echo "alias gitjournal='python3 $INSTALL_DIR/gitjournal.py'" >> "$SHELL_CONFIG"
    echo "✅ Added gitjournal alias to $SHELL_CONFIG"
fi

# Create symlink in /usr/local/bin (optional)
echo ""
read -p "Create system-wide command in /usr/local/bin? (requires sudo) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo ln -sf "$INSTALL_DIR/gitjournal.py" /usr/local/bin/gitjournal
    sudo chmod +x /usr/local/bin/gitjournal
    echo "✅ Created /usr/local/bin/gitjournal"
fi

echo ""
echo "════════════════════════════════════════"
echo "Installation complete!"
echo ""
echo "To start using gitjournal, either:"
echo "  1. Restart your terminal, or"
echo "  2. Run: source $SHELL_CONFIG"
echo ""
echo "Usage:"
echo "  gitjournal              # Generate devlog for current repo"
echo "  gitjournal --init       # Initialize journaling + install hook"
echo "  gitjournal --changelog  # Generate categorized changelog"
echo "  gitjournal --export-html # Export for OneNote"
echo "  gitjournal --all-repos  # Combined log from all repos"
echo "  gitjournal --list       # List tracked repos"
echo ""
echo "════════════════════════════════════════"
