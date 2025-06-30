#!/bin/bash

# Bluetooth Helper Script for Mac Proximity Lock

echo "🔵 Mac Proximity Lock - Bluetooth Helper"
echo ""

case "$1" in
    "reset")
        echo "🔄 Resetting Bluetooth stack..."
        sudo pkill bluetoothd
        sudo launchctl load /System/Library/LaunchDaemons/com.apple.bluetoothd.plist
        sleep 3
        echo "✅ Bluetooth reset complete"
        ;;
    
    "connect")
        if [ -z "$2" ]; then
            echo "Usage: $0 connect <device_address>"
            echo "Example: $0 connect 60:68:4E:E1:61:71"
            exit 1
        fi
        
        DEVICE_ADDR=$(echo "$2" | tr ':' '-')
        echo "🔗 Attempting to connect to $2..."
        blueutil --connect "$DEVICE_ADDR"
        
        if [ $? -eq 0 ]; then
            echo "✅ Connection successful!"
        else
            echo "❌ Connection failed"
        fi
        ;;
    
    "disconnect")
        if [ -z "$2" ]; then
            echo "Usage: $0 disconnect <device_address>"
            exit 1
        fi
        
        DEVICE_ADDR=$(echo "$2" | tr ':' '-')
        echo "🔌 Disconnecting from $2..."
        blueutil --disconnect "$DEVICE_ADDR"
        ;;
    
    "status")
        echo "📊 Bluetooth Status:"
        echo "Power: $(blueutil --power)"
        echo "Discoverable: $(blueutil --discoverable)"
        echo ""
        echo "Connected devices:"
        blueutil --connected --format json | python3 -m json.tool 2>/dev/null || echo "No connected devices"
        ;;
    
    "pair")
        if [ -z "$2" ]; then
            echo "Usage: $0 pair <device_address>"
            exit 1
        fi
        
        DEVICE_ADDR=$(echo "$2" | tr ':' '-')
        echo "📱 Attempting to pair with $2..."
        echo "Make sure your device is discoverable!"
        blueutil --pair "$DEVICE_ADDR"
        ;;
    
    "scan")
        echo "🔍 Scanning for devices (10 seconds)..."
        blueutil --inquiry 10
        ;;
    
    "auto-reconnect")
        if [ -z "$2" ]; then
            echo "Usage: $0 auto-reconnect <device_address>"
            exit 1
        fi
        
        DEVICE_ADDR=$(echo "$2" | tr ':' '-')
        echo "🔄 Starting auto-reconnect monitor for $2..."
        echo "Press Ctrl+C to stop"
        
        while true; do
            if ! blueutil --is-connected "$DEVICE_ADDR" >/dev/null 2>&1; then
                echo "$(date): Device disconnected, attempting reconnection..."
                blueutil --connect "$DEVICE_ADDR"
                
                if [ $? -eq 0 ]; then
                    echo "$(date): ✅ Reconnected successfully!"
                else
                    echo "$(date): ❌ Reconnection failed, will retry in 30s"
                fi
            else
                echo "$(date): Device connected ✅"
            fi
            
            sleep 30
        done
        ;;
    
    *)
        echo "Usage: $0 {reset|connect|disconnect|status|pair|scan|auto-reconnect} [device_address]"
        echo ""
        echo "Commands:"
        echo "  reset                    - Reset Bluetooth stack"
        echo "  connect <address>        - Connect to device"
        echo "  disconnect <address>     - Disconnect from device"  
        echo "  status                   - Show Bluetooth status"
        echo "  pair <address>          - Pair with device"
        echo "  scan                    - Scan for nearby devices"
        echo "  auto-reconnect <address> - Monitor and auto-reconnect"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 connect 60:68:4E:E1:61:71"
        echo "  $0 auto-reconnect 60:68:4E:E1:61:71"
        ;;
esac 