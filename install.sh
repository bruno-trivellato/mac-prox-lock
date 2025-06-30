#!/bin/bash

# Mac Proximity Lock - Installation Script

echo "=== Mac Proximity Lock Installation ==="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Make main script executable
chmod +x main.py

echo "✅ Made main.py executable"

# Create launch daemon directory if it doesn't exist
LAUNCH_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_DIR"

# Create the launch daemon plist
PLIST_FILE="$LAUNCH_DIR/com.proximity.lock.plist"
CURRENT_DIR=$(pwd)

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.proximity.lock</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>$CURRENT_DIR/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/proximity_lock.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/proximity_lock.log</string>
</dict>
</plist>
EOF

echo "✅ Created launch daemon at $PLIST_FILE"

echo ""
echo "=== Next Steps ==="
echo "1. Run the setup: python3 main.py --setup"
echo "2. Make sure your Android device is paired and connected"
echo "3. Test the script: python3 main.py"
echo "4. To start the background service: launchctl load $PLIST_FILE"
echo "5. To stop the background service: launchctl unload $PLIST_FILE"
echo ""
echo "For more help, check the README.md file" 