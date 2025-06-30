#!/usr/bin/env python3
"""
Mac Proximity Lock
Automatically locks your MacBook when your Android device moves away.
"""

import subprocess
import time
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

class ProximityLock:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.setup_logging()
        self.last_seen = datetime.now()
        self.is_locked = False
        self.last_connection_state = None
        self.reconnect_attempts = 0
        
    def setup_logging(self):
        """Configure logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('proximity_lock.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "device_name": "",
            "device_mac": "",
            "timeout_seconds": 30,
            "scan_interval": 5,
            "log_level": "INFO",
            "lock_command": "pmset displaysleepnow",
            "auto_reconnect": True,
            "max_reconnect_attempts": 3,
            "reconnect_delay": 2
        }
        
        if not self.config_path.exists():
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created config file: {self.config_path}")
            print("Please edit the config file with your device information.")
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def save_config(self):
        """Save current configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def scan_bluetooth_devices(self):
        """Scan for Bluetooth devices using blueutil"""
        devices = []
        
        try:
            # Get connected devices
            result = subprocess.run([
                'blueutil', '--connected', '--format', 'json'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                connected_devices = json.loads(result.stdout)
                for device in connected_devices:
                    devices.append({
                        'name': device.get('name', 'Unknown'),
                        'address': device.get('address', '').replace('-', ':'),
                        'connected': True,
                        'rssi': device.get('RSSI', 'N/A'),
                        'type': 'Mobile Phone' if 'phone' in device.get('name', '').lower() else 'Unknown'
                    })
            
            # Get paired but not connected devices
            result = subprocess.run([
                'blueutil', '--paired', '--format', 'json'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                paired_devices = json.loads(result.stdout)
                connected_addresses = [d['address'].lower() for d in devices]
                
                for device in paired_devices:
                    device_addr = device.get('address', '').replace('-', ':').lower()
                    if device_addr not in connected_addresses:
                        devices.append({
                            'name': device.get('name', 'Unknown'),
                            'address': device_addr,
                            'connected': False,
                            'rssi': 'N/A',
                            'type': 'Mobile Phone' if 'phone' in device.get('name', '').lower() else 'Unknown'
                        })
                        
        except subprocess.TimeoutExpired:
            self.logger.warning("Bluetooth scan timed out")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse blueutil JSON output: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning Bluetooth devices: {e}")
            
        return devices
    
    def get_device_info_direct(self, device_id):
        """Get device info directly using blueutil for faster response"""
        try:
            result = subprocess.run([
                'blueutil', '--info', device_id, '--format', 'json'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0 and result.stdout.strip():
                device_info = json.loads(result.stdout)
                return {
                    'name': device_info.get('name', 'Unknown'),
                    'address': device_info.get('address', '').replace('-', ':'),
                    'connected': device_info.get('connected', False),
                    'rssi': device_info.get('RSSI', 'N/A'),
                    'type': 'Mobile Phone' if 'phone' in device_info.get('name', '').lower() else 'Unknown',
                    'paired': device_info.get('paired', False)
                }
        except Exception as e:
            self.logger.debug(f"Failed to get direct device info: {e}")
            
        return None

    def is_device_nearby(self):
        """Check if the target device is nearby and return device info"""
        # Try direct lookup first (faster)
        if self.config['device_mac']:
            # Format MAC address for blueutil (it accepts various formats)
            mac_for_blueutil = self.config['device_mac'].replace(':', '-')
            device_info = self.get_device_info_direct(mac_for_blueutil)
            if device_info:
                return device_info
        
        if self.config['device_name']:
            device_info = self.get_device_info_direct(self.config['device_name'])
            if device_info:
                return device_info
                
        # Fallback to full scan if direct lookup fails
        devices = self.scan_bluetooth_devices()
        for device in devices:
            # Check by MAC address (preferred) or name
            if (self.config['device_mac'] and 
                device['address'].lower() == self.config['device_mac'].lower()):
                return device
            elif (self.config['device_name'] and 
                  self.config['device_name'].lower() in device['name'].lower()):
                return device
                
        return None
    
    def is_screen_locked(self):
        """Check if the screen is currently locked using native macOS APIs"""
        try:
            # Method 1: Try PyObjC with Quartz/CoreGraphics
            try:
                import Quartz
                session_dict = Quartz.CGSessionCopyCurrentDictionary()
                if session_dict:
                    # Check for screen lock indicators
                    is_locked = session_dict.get('CGSSessionScreenIsLocked', False)
                    return bool(is_locked)
            except ImportError:
                self.logger.debug("PyObjC/Quartz not available, trying alternative methods")
            
            # Method 2: Use ioreg to check screen state
            result = subprocess.run([
                'ioreg', '-n', 'IOHIDSystem', '-d1'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                # Look for HIDIdleTime - if present and accessible, screen likely unlocked
                if 'HIDIdleTime' in result.stdout:
                    return False
                    
            # Method 3: Check if screensaver is running
            result = subprocess.run([
                'pgrep', 'ScreenSaverEngine'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                return True  # Screensaver is running
                
            # Method 4: Try to access window server (requires screen access)
            result = subprocess.run([
                'osascript', '-e', 'tell application "System Events" to get name of first desktop'
            ], capture_output=True, text=True, timeout=2)
            
            # If osascript succeeds, screen is probably not locked
            return result.returncode != 0
                
        except Exception as e:
            self.logger.debug(f"All screen lock detection methods failed: {e}")
            # Fallback to internal state
            return self.is_locked

    def attempt_reconnect(self, device_address):
        """Try to reconnect to the device using blueutil"""
        try:
            self.logger.info(f"🔄 Attempting to reconnect to {device_address}...")
            
            # Format address for blueutil
            formatted_address = device_address.replace(':', '-')
            
            result = subprocess.run([
                'blueutil', '--connect', formatted_address
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info("✅ Reconnection successful!")
                self.reconnect_attempts = 0
                return True
            else:
                self.logger.warning(f"❌ Reconnection failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.warning("⏰ Reconnection attempt timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ Reconnection error: {e}")
            return False

    def lock_screen(self):
        """Lock the MacBook screen"""
        try:
            subprocess.run(self.config['lock_command'].split(), check=True)
            self.logger.info("Screen locked successfully")
            self.is_locked = True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to lock screen: {e}")
    
    def run_setup(self):
        """Interactive setup for device configuration"""
        print("\n=== Mac Proximity Lock Setup ===")
        print("Scanning for Bluetooth devices...")
        
        devices = self.scan_bluetooth_devices()
        if not devices:
            print("No Bluetooth devices found. Make sure your Android device is paired and connected.")
            return
        
        print("\nFound devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['name']} ({device['address']}) - {'Connected' if device['connected'] else 'Not Connected'}")
        
        try:
            choice = int(input(f"\nSelect your device (1-{len(devices)}): ")) - 1
            if 0 <= choice < len(devices):
                selected_device = devices[choice]
                self.config['device_name'] = selected_device['name']
                self.config['device_mac'] = selected_device['address']
                
                timeout = input(f"Timeout in seconds (default {self.config['timeout_seconds']}): ")
                if timeout.strip():
                    self.config['timeout_seconds'] = int(timeout)
                
                scan_interval = input(f"Scan interval in seconds (default {self.config['scan_interval']}): ")
                if scan_interval.strip():
                    self.config['scan_interval'] = int(scan_interval)
                
                self.save_config()
                print(f"\nConfiguration saved! Your device: {selected_device['name']}")
            else:
                print("Invalid selection")
        except (ValueError, KeyboardInterrupt):
            print("\nSetup cancelled")
    
    def monitor(self):
        """Main monitoring loop"""
        if not self.config['device_name'] and not self.config['device_mac']:
            print("No device configured. Run with --setup first.")
            return
        
        self.logger.info("Starting proximity monitoring...")
        self.logger.info(f"Target device: {self.config['device_name']} ({self.config['device_mac']})")
        self.logger.info(f"Timeout: {self.config['timeout_seconds']} seconds")
        self.logger.info(f"Scan interval: {self.config['scan_interval']} seconds")
        self.logger.info("=" * 60)
        
        try:
            cycle = 0
            while True:
                cycle += 1
                device_info = self.is_device_nearby()
                current_connected = device_info and device_info['connected']
                
                # Detect connection state changes
                if self.last_connection_state is not None:
                    if not self.last_connection_state and current_connected:
                        # Device just reconnected - user probably returned and unlocked
                        self.logger.info("🔄 Device RECONNECTED - assuming user returned and unlocked screen")
                        self.is_locked = False
                    elif self.last_connection_state and not current_connected:
                        # Device just disconnected
                        self.logger.warning("📡 Device DISCONNECTED - starting timeout countdown")
                
                self.last_connection_state = current_connected
                
                if current_connected:
                    self.last_seen = datetime.now()
                    
                    # Extract signal strength info
                    rssi = device_info.get('rssi', 'N/A')
                    device_name = device_info.get('name', 'Unknown')
                    
                    # RSSI quality indicator (but don't rely on it for proximity)
                    if isinstance(rssi, int):
                        if rssi > -40:
                            signal_quality = "📶 Excellent"
                        elif rssi > -60:
                            signal_quality = "📶 Good"
                        elif rssi > -80:
                            signal_quality = "📶 Fair"
                        else:
                            signal_quality = "📶 Weak"
                    else:
                        signal_quality = "📶 Unknown"
                    
                    if self.is_locked:
                        self.logger.info(f"[Cycle {cycle:03d}] ✅ {device_name} CONNECTED | RSSI: {rssi}dBm | {signal_quality} | 🔒 Screen locked")
                    else:
                        self.logger.info(f"[Cycle {cycle:03d}] ✅ {device_name} CONNECTED | RSSI: {rssi}dBm | {signal_quality} | 🔓 Screen unlocked")
                    
                else:
                    time_since_seen = datetime.now() - self.last_seen
                    time_elapsed = time_since_seen.total_seconds()
                    
                    # Check if screen was manually unlocked
                    actual_screen_locked = self.is_screen_locked()
                    if self.is_locked and not actual_screen_locked:
                        self.logger.info("🔓 Screen was manually unlocked - user is back!")
                        self.is_locked = False
                        
                        # If device is still disconnected, try to reconnect immediately
                        if (device_info is not None and 
                            device_info.get('paired', False) and 
                            not device_info.get('connected', False) and
                            self.config.get('auto_reconnect', True)):
                            
                            self.logger.info("📱 Device still disconnected, attempting immediate reconnection...")
                            if self.attempt_reconnect(device_info.get('address', '')):
                                # Reconnection successful, reset timer and continue
                                self.last_seen = datetime.now()
                                self.reconnect_attempts = 0
                                self.logger.info("✅ Reconnected successfully! Resetting timer.")
                                continue
                            else:
                                self.logger.warning("❌ Immediate reconnection failed, starting normal timeout countdown")
                    
                    # Try to reconnect if device is paired but disconnected (during timeout period)
                    if (device_info is not None and 
                        device_info.get('paired', False) and 
                        not device_info.get('connected', False) and
                        self.reconnect_attempts < self.config['max_reconnect_attempts'] and
                        time_elapsed < self.config['timeout_seconds'] and
                        self.config.get('auto_reconnect', True)):
                        
                        self.reconnect_attempts += 1
                        self.logger.info(f"🔄 Device away for {time_elapsed:.1f}s, attempting reconnection {self.reconnect_attempts}/{self.config['max_reconnect_attempts']}...")
                        
                        if self.attempt_reconnect(device_info.get('address', '')):
                            # Reconnection successful, reset everything and restart monitoring cycle
                            self.last_seen = datetime.now()
                            self.reconnect_attempts = 0
                            self.logger.info("✅ Device reconnected! User likely returned.")
                            continue
                    
                    # Status based on how long device has been away
                    if device_info is not None and device_info.get('paired', False):
                        device_name = device_info.get('name', 'Device')
                        status = f"📱 {device_name} PAIRED but disconnected"
                        if self.reconnect_attempts > 0:
                            status += f" (reconnect attempts: {self.reconnect_attempts}/{self.config['max_reconnect_attempts']})"
                    elif device_info is not None:
                        device_name = device_info.get('name', 'Device')
                        status = f"🔍 {device_name} found but not connected"
                    else:
                        status = f"❌ Device NOT FOUND"
                    
                    remaining_time = max(0, self.config['timeout_seconds'] - time_elapsed)
                    
                    if time_elapsed < self.config['timeout_seconds']:
                        screen_status = "🔒 locked" if self.is_locked else "🔓 unlocked"
                        self.logger.info(f"[Cycle {cycle:03d}] {status} | Away: {time_elapsed:.1f}s | Lock in: {remaining_time:.1f}s | Screen: {screen_status}")
                    else:
                        self.logger.warning(f"[Cycle {cycle:03d}] {status} | Away: {time_elapsed:.1f}s | ⚠️  TIMEOUT REACHED!")
                        
                        # Reset reconnect attempts when timeout is reached
                        if self.reconnect_attempts > 0:
                            self.logger.info("🔄 Resetting reconnection attempts after timeout")
                            self.reconnect_attempts = 0
                        
                        if not self.is_locked:
                            self.logger.critical("🔒 LOCKING SCREEN NOW!")
                            self.lock_screen()
                        else:
                            screen_status = "🔒 locked" if actual_screen_locked else "🔓 unlocked (manually)"
                            self.logger.info(f"🔒 Screen status: {screen_status} | Device still away")
                
                time.sleep(self.config['scan_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Monitoring stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Mac Proximity Lock')
    parser.add_argument('--setup', action='store_true', help='Run interactive setup')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--list-devices', action='store_true', help='List paired Bluetooth devices')
    
    args = parser.parse_args()
    
    lock = ProximityLock(args.config)
    
    if args.setup:
        lock.run_setup()
    elif args.list_devices:
        print("Scanning for Bluetooth devices...")
        devices = lock.scan_bluetooth_devices()
        for device in devices:
            status = "Connected" if device['connected'] else "Paired"
            rssi = f" | RSSI: {device['rssi']}" if device['rssi'] != 'N/A' else ""
            device_type = f" | Type: {device['type']}" if device['type'] != 'Unknown' else ""
            print(f"- {device['name']} ({device['address']}) - {status}{rssi}{device_type}")
    else:
        lock.monitor()

if __name__ == "__main__":
    main() 