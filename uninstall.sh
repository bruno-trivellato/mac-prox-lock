#!/bin/bash

# Mac Proximity Lock - Uninstall Script

echo "🗑️  Mac Proximity Lock Uninstaller"
echo ""

PLIST_FILE="$HOME/Library/LaunchAgents/com.proximity.lock.plist"

# Stop the service if running
if [ -f "$PLIST_FILE" ]; then
    echo "🛑 Stopping service..."
    launchctl unload "$PLIST_FILE" 2>/dev/null
    
    echo "🗂️  Removing launch daemon..."
    rm "$PLIST_FILE"
    echo "✅ Removed $PLIST_FILE"
else
    echo "ℹ️  Service not installed"
fi

# Ask before removing project files
echo ""
read -p "Do you want to remove all project files? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    cd ..
    rm -rf "$CURRENT_DIR"
    echo "✅ Project files removed"
    echo "👋 Mac Proximity Lock has been completely uninstalled"
else
    echo "ℹ️  Project files kept. Only the background service was removed."
    echo "📁 You can manually delete this folder if desired"
fi

echo ""
echo "✅ Uninstall complete!" 