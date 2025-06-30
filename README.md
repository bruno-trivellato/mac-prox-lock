# Mac Proximity Lock

🔒 Automatically locks your MacBook when your Android smartphone moves away from it.

## How It Works

The system continuously monitors the Bluetooth connection with your Android device (Samsung A53). When the smartphone moves away for more than 30 seconds (configurable), the MacBook is automatically locked.

## Requirements

- macOS (tested on M4)
- Python 3.6+
- Android device paired via Bluetooth
- Permissions to execute system commands

## Prerequisites: Connect your Android to Mac via Bluetooth

Before installing the system, you need to pair your Samsung A53 with the MacBook:

### 1. On your Android (Samsung A53):
1. Go to **Settings** → **Connections** → **Bluetooth**
2. Make sure Bluetooth is **on**
3. Tap **Make device discoverable** or similar
4. Keep the screen open on this section

### 2. On your MacBook:
1. Click the **Apple** icon → **System Settings**
2. Go to **Bluetooth** in the sidebar
3. Make sure Bluetooth is **on**
4. You should see your "SM-A536B" (or similar) in the list of nearby devices
5. Click **Connect** next to your device
6. Confirm the code that appears on both screens (if requested)

### 3. Verify the connection:
1. On Mac: The device should appear as "Connected" in the list
2. On Android: Should show "Connected to [Your Mac Name]"

### 4. Quick test:
```bash
# Clone the project first, then run:
python3 main.py --list-devices
```

You should see your Samsung A53 listed as a connected device.

## Quick Installation

1. **Clone and install:**
```bash
git clone <repository-url>
cd mac-prox-lock
chmod +x install.sh
./install.sh
```

2. **Configure your device:**
```bash
python3 main.py --setup
```

3. **Test functionality:**
```bash
python3 main.py
```

## Usage

### Initial Setup

Run the interactive setup to configure your Android device:
```bash
python3 main.py --setup
```

The script will:
- Scan paired Bluetooth devices
- Allow you to select your Samsung A53
- Configure timeout and scan interval

### Run Manually

To test the system manually:
```bash
python3 main.py
```

### Run as Background Service

For the system to work automatically whenever you turn on your Mac:

**Start service:**
```bash
launchctl load ~/Library/LaunchAgents/com.proximity.lock.plist
```

**Stop service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.proximity.lock.plist
```

### Useful Commands

**List Bluetooth devices:**
```bash
python3 main.py --list-devices
```

**View logs:**
```bash
tail -f proximity_lock.log
```

**Bluetooth help:**
```bash
# Check Bluetooth status
./bluetooth_helper.sh status

# Manually connect to device
./bluetooth_helper.sh connect 60:68:4E:E1:61:71

# Reset Bluetooth if having issues
./bluetooth_helper.sh reset
```

## Configuration

The `config.json` file is automatically created with the following options:

```json
{
  "device_name": "SM-A536B",
  "device_mac": "AA:BB:CC:DD:EE:FF", 
  "timeout_seconds": 30,
  "scan_interval": 5,
  "log_level": "INFO",
  "lock_command": "pmset displaysleepnow"
}
```

### Configurable Parameters

- **device_name**: Name of your Android device
- **device_mac**: MAC address of the device (more reliable)
- **timeout_seconds**: Seconds to lock after losing connection (default: 30)
- **scan_interval**: Interval between checks in seconds (default: 5)
- **log_level**: Log level (DEBUG, INFO, WARNING, ERROR)
- **lock_command**: Command to lock the screen
- **auto_reconnect**: Try to reconnect automatically (default: true)
- **max_reconnect_attempts**: Reconnection attempts before giving up (default: 3)
- **reconnect_delay**: Delay between attempts in seconds (default: 2)

## Troubleshooting

### Bluetooth Issues

**Device doesn't appear in list:**
1. Make sure Bluetooth is on in both Mac and Android
2. On Android: Go to Bluetooth → **Advanced** → check "Make discoverable"
3. On Mac: Try removing and pairing the device again
4. Restart Bluetooth on both devices
5. Run `python3 main.py --list-devices` to verify

**Device paired but doesn't connect:**
1. On Android: Go to Bluetooth → find your Mac → **Unpair**
2. On Mac: Bluetooth → find your Android → **Remove**  
3. Redo the pairing process from scratch
4. Some Androids require you to accept all sharing permissions

**Unstable connection:**
1. Keep devices close (< 2 meters) during testing
2. Avoid interference (other Bluetooth devices, 2.4GHz Wi-Fi)
3. On Android: Disable "Battery optimization" for Bluetooth
4. Adjust `scan_interval` in config to larger values (e.g. 10 seconds)

**Mac doesn't automatically reconnect to Android:**
1. **Use the helper script**: `./bluetooth_helper.sh connect 60:68:4E:E1:61:71`
2. **Reset Bluetooth**: `./bluetooth_helper.sh reset` (may need sudo)
3. **Android configuration**:
   - Go to Bluetooth → Advanced Settings
   - Enable "Automatically connect to known devices"
   - Disable "Connection timeout"
4. **On macOS**: 
   - Preferences → Bluetooth → Advanced Options
   - Enable "Allow Bluetooth devices to wake this computer"
5. **The system now has integrated auto-reconnection** - it will try to reconnect up to 3 times

### Device not found by script
1. Make sure the device is **connected** (not just paired)
2. Run `python3 main.py --list-devices` to see all devices
3. Verify that the name/MAC address in config.json is correct
4. Try using the MAC address instead of the device name

### Not locking
1. Check the logs: `tail -f proximity_lock.log`
2. Test the lock command manually: `pmset displaysleepnow`
3. Adjust the timeout if necessary

### Service doesn't start automatically
1. Check if the plist file was created: `ls ~/Library/LaunchAgents/com.proximity.lock.plist`
2. Reload the service: `launchctl unload` followed by `launchctl load`

## Security

- The system uses only public macOS APIs
- Does not collect or transmit personal data
- Works completely offline
- Logs are stored locally

## Uninstallation

To completely remove the system:

```bash
# Stop the service
launchctl unload ~/Library/LaunchAgents/com.proximity.lock.plist

# Remove files
rm ~/Library/LaunchAgents/com.proximity.lock.plist
rm -rf ~/path/to/mac-prox-lock
```

## Contributing

Feel free to report bugs, suggest improvements, or contribute code!

## Summary: Complete Flow from Zero

Here's the complete step-by-step to set everything up from scratch:

### 1. Prepare Bluetooth (FIRST STEP!)
- Android: Settings → Bluetooth → Turn on → Make discoverable
- Mac: Settings → Bluetooth → Turn on → Connect to your Samsung A53
- Confirm it shows "Connected" on both devices

### 2. Install the System
```bash
# Clone the project
git clone <repository-url>
cd mac-prox-lock

# Run installation
./install.sh
```

### 3. Configure the Device
```bash
# Run interactive setup
python3 main.py --setup

# Choose your Samsung A53 from the list
# Set timeout (recommended: 30 seconds)
```

### 4. Test Functionality
```bash
# Test manually
python3 main.py

# Move phone away and see if it locks after 30s
# Ctrl+C to stop
```

### 5. Activate Automatic Service
```bash
# Start background service
./start_service.sh

# Check logs
tail -f proximity_lock.log
```

### 6. Done! 🎉
Now whenever your Samsung A53 moves away from the MacBook for more than 30 seconds, the screen will be automatically locked.

**To stop:** `./stop_service.sh`  
**To uninstall:** `./uninstall.sh`

## TODO

- [ ] **Fix import and get linter errors** - Resolve PyObjC import and None.get() warnings
- [ ] **Refactor Python script with better architecture** - Separate into smaller classes/modules, improve organization

## License

This project is under the MIT license. See the LICENSE file for details.