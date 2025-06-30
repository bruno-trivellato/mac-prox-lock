#!/bin/bash

# Start Mac Proximity Lock Service

PLIST_FILE="$HOME/Library/LaunchAgents/com.proximity.lock.plist"

if [ ! -f "$PLIST_FILE" ]; then
    echo "❌ Service not installed. Run ./install.sh first."
    exit 1
fi

echo "🚀 Starting Mac Proximity Lock service..."

# Load the service
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Service started successfully!"
    echo "📝 Check logs with: tail -f proximity_lock.log"
else
    echo "❌ Failed to start service"
    exit 1
fi 