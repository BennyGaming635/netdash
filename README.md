# NetDash - Network Management Applet

A simple Python GUI applet for managing and monitoring your local network.

![NetDash](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### 🖥️ Device Management
- Automatic network scanning and device discovery
- Manual device addition and removal
- Device list with IP, hostname, MAC address, and status
- Save and load device lists

### 🗺️ Network Mapping
- Visual network topology display
- Text-based network map showing device connections
- Automatic subnet detection

### 🛠️ Network Tools
- **Ping Tool** - Test connectivity to devices
- **Traceroute** - Trace the path to network hosts
- **Port Scanner** - Scan for open ports on devices

### 📊 Dashboard
- Real-time device statistics
- Online/offline device counts
- Last seen timestamps
- Activity logging

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- Standard library modules (subprocess, socket, threading, etc.)

No additional dependencies required!

## Quick Start

### Running the Applet

1. Clone the repository:
```bash
git clone https://github.com/BennyGaming635/netdash.git
cd netdash
```

2. Run the applet:
```bash
python netdash_applet.py
```

Or make it executable:
```bash
chmod +x netdash_applet.py
./netdash_applet.py
```

### Windows

Double-click `netdash_applet.py` or run from command prompt:
```cmd
python netdash_applet.py
```

## Usage

### Scanning Your Network

1. Click **"Scan Network"** in the Dashboard tab
2. The applet will automatically detect your local subnet and scan for devices
3. Found devices will appear in the device list

### Managing Devices

- **Add Device**: Click "Add Device" to manually add a device by IP address
- **Remove Device**: Right-click a device and select "Remove Device"
- **Save/Load**: Use File menu to save or load device lists

### Network Tools

Switch to the **"Network Tools"** tab to access:

- **Ping**: Enter a hostname or IP and click "Ping" to test connectivity
- **Traceroute**: Trace the network path to a destination
- **Port Scan**: Scan for open ports (e.g., "20-80,443,8080")

### Network Map

Go to the **"Network Map"** tab to:

1. View a text-based visualization of your network
2. See device groupings (online/offline)
3. View network topology diagram

### Logs

The **"Logs"** tab shows all activity and operations performed by the applet.

## Features Detail

### Dashboard Tab
- Device list with sortable columns
- Context menu for quick actions (right-click on devices)
- Real-time statistics
- Network scanning controls

### Network Map Tab
- Enter custom subnet ranges
- Generate visual network maps
- ASCII-art topology diagrams

### Network Tools Tab
- Integrated ping utility
- Traceroute functionality
- Custom port scanning

### Logs Tab
- Timestamped activity log
- Operation tracking
- Error reporting

## Platform Support

- **Linux**: Full support (requires appropriate permissions for network operations)
- **macOS**: Full support
- **Windows**: Full support

### Permissions

On Linux/macOS, you may need to run with elevated privileges for some network operations:
```bash
sudo python netdash_applet.py
```

## Tips

- Network scans can take a few minutes depending on your subnet size
- Save your device list to avoid rescanning every time
- Use the right-click context menu on devices for quick actions
- Check the Logs tab if something isn't working as expected

## Troubleshooting

### Scan not finding devices
- Ensure you're on the same network as the devices
- Check firewall settings (ICMP/ping must be allowed)
- Try manually adding devices if automatic scanning fails

### Tools not working
- On Linux/macOS, some tools may require sudo privileges
- Ensure the commands (ping, traceroute) are available on your system
- Check the Logs tab for error messages

### Application won't start
- Verify Python 3.7+ is installed: `python --version`
- Ensure tkinter is available: `python -c "import tkinter"`
- Check for error messages in the terminal

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python's tkinter for maximum compatibility
- Cross-platform network utilities
- Simple and lightweight design

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/BennyGaming635/netdash).