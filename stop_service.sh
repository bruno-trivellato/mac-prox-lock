#!/bin/bash

# Stop Mac Proximity Lock Service

PLIST_FILE="$HOME/Library/LaunchAgents/com.proximity.lock.plist"

if [ ! -f "$PLIST_FILE" ]; then
    echo "❌ Service not installed."
    exit 1
fi

echo "🛑 Stopping Mac Proximity Lock service..."

# Unload the service
launchctl unload "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Service stopped successfully!"
else
    echo "❌ Failed to stop service (it may not have been running)"
fi 