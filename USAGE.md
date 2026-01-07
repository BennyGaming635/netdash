# NetDash Applet - Usage Guide

## Overview

NetDash Applet is a lightweight, standalone Python GUI application for network management. It provides tools for discovering, monitoring, and managing devices on your local network.

## Getting Started

### Installation

No installation required! The applet uses only Python's standard library.

**Prerequisites:**
- Python 3.7 or higher
- tkinter (included with most Python distributions)

**To verify tkinter is available:**
```bash
python -c "import tkinter"
```

If this command runs without errors, you're ready to go!

### Running the Applet

**Linux/macOS:**
```bash
python netdash_applet.py
```

Or make it executable:
```bash
chmod +x netdash_applet.py
./netdash_applet.py
```

**Windows:**
```cmd
python netdash_applet.py
```

Or simply double-click `netdash_applet.py` in File Explorer.

## User Interface

The applet has a tabbed interface with four main sections:

### 1. Dashboard Tab

The main view showing all discovered and added devices.

**Features:**
- **Scan Network**: Automatically discovers devices on your local subnet
- **Refresh**: Updates the device list display
- **Add Device**: Manually add a device by IP address
- **Device List**: Shows all devices with their details:
  - IP Address
  - Hostname
  - MAC Address (when available)
  - Status (Online/Offline/Unknown)
  - Last Seen timestamp
- **Statistics**: Real-time count of total, online, and offline devices

**Right-Click Menu:**
Right-click any device to:
- Ping the device
- Trace route to the device
- Remove the device from the list

### 2. Network Map Tab

Visual representation of your network topology.

**Features:**
- **Subnet Entry**: Enter a custom subnet (default: 192.168.1.0/24)
- **Generate Map**: Creates a text-based network visualization
- **Device Grouping**: Shows online and offline devices separately
- **Topology Diagram**: ASCII-art representation of network structure

**Example Output:**
```
Network Map for 192.168.1.0/24
================================================================================

ONLINE DEVICES:
--------------------------------------------------------------------------------
  [192.168.1.1    ] Main-Router
    MAC: 00:11:22:33:44:55

  [192.168.1.100  ] Desktop-PC
  
  [192.168.1.150  ] Laptop

NETWORK TOPOLOGY:
--------------------------------------------------------------------------------

                    [Internet]
                         |
                    [Router/Gateway]
                         |
          _______________│_______________
         |               |               |
          [Main-Router]   [Desktop-PC]    [Laptop]
           192.168.1.1     192.168.1.100   192.168.1.150
```

### 3. Network Tools Tab

Collection of network diagnostic utilities.

#### Ping Tool
Test connectivity to any host.

**How to use:**
1. Enter hostname or IP address
2. Click "Ping"
3. View results showing round-trip times and packet loss

**Example:**
```
Host: 8.8.8.8
Results:
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=12.3 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=118 time=11.9 ms
```

#### Traceroute Tool
Trace the network path to a destination.

**How to use:**
1. Enter hostname or IP address
2. Click "Trace"
3. View the hop-by-hop route

**Example:**
```
Host: google.com
Results:
 1  192.168.1.1 (192.168.1.1)  1.234 ms
 2  10.0.0.1 (10.0.0.1)  5.678 ms
 3  203.0.113.1 (203.0.113.1)  15.432 ms
```

#### Port Scanner
Scan for open ports on a target host.

**How to use:**
1. Enter hostname or IP address
2. Enter port specification:
   - Single port: `80`
   - Range: `20-80`
   - Multiple: `22,80,443,8080`
   - Combination: `20-25,80,443,8000-9000`
3. Click "Scan"
4. View open ports

**Example:**
```
Host: 192.168.1.1
Ports: 20-80,443,8080

Results:
Port 22: OPEN
Port 80: OPEN
Port 443: OPEN

Scan complete. Found 3 open ports
```

### 4. Logs Tab

Activity log showing all operations.

**Features:**
- Timestamped entries for all actions
- Scan progress updates
- Error messages
- Tool execution results
- **Clear Logs**: Button to clear the log display

**Example Log:**
```
[2026-01-07 04:47:23] NetDash Applet started
[2026-01-07 04:47:30] Starting network scan...
[2026-01-07 04:47:31] Local IP: 192.168.1.100
[2026-01-07 04:47:31] Scanning subnet: 192.168.1.0/24
[2026-01-07 04:47:35] Found device: 192.168.1.1 (Router)
[2026-01-07 04:47:40] Found device: 192.168.1.50 (Desktop-PC)
[2026-01-07 04:48:15] Scan complete. Found 5 devices
```

## Common Tasks

### Scanning Your Network

1. Open the applet
2. Click **"Scan Network"** in the Dashboard tab
3. Wait for the scan to complete (may take 1-5 minutes depending on subnet size)
4. Devices will appear in the list as they're discovered

**Note:** The scan checks every IP in your local /24 subnet (254 addresses).

### Adding a Device Manually

1. Click **"Add Device"** in the Dashboard
2. Enter the device IP address (required)
3. Optionally enter hostname and MAC address
4. Click **"Add"**

### Testing Connectivity

**Quick method:**
1. Right-click a device in the Dashboard
2. Select "Ping Device"
3. View results in the Network Tools tab

**Manual method:**
1. Go to Network Tools tab
2. Enter IP or hostname in Ping Tool
3. Click "Ping"

### Saving and Loading Devices

**Save devices:**
1. File menu → "Save Devices"
2. Devices are saved to `netdash_devices.json` in the same directory

**Load devices:**
1. File menu → "Load Devices"
2. Previously saved devices are restored

**Note:** This is useful to avoid rescanning every time you run the applet.

### Port Scanning

1. Go to Network Tools tab
2. Enter target IP in Port Scanner
3. Specify ports to scan:
   - Common ports: `20-25,80,443,3389,8080`
   - Web ports: `80,443,8000-8100`
   - All common: `20-1000`
4. Click "Scan"

**Warning:** Scanning large port ranges can be slow. Be patient!

### Generating Network Map

1. Go to Network Map tab
2. Enter subnet (or use default)
3. Click "Generate Map"
4. View text-based topology

## Tips and Tricks

### Performance

- **Scan Time**: Network scans can take 2-5 minutes for a /24 subnet
- **Faster Scans**: Manually add known devices instead of scanning
- **Background Scanning**: The UI remains responsive during scans

### Permissions

Some operations may require elevated privileges:

**Linux/macOS:**
```bash
sudo python netdash_applet.py
```

**Why?**
- Raw socket operations
- ICMP (ping) operations
- Some network discovery features

### Network Configuration

The applet automatically detects your local network:
- Determines your IP address
- Calculates /24 subnet
- Scans all possible hosts (x.x.x.1-254)

**Custom Subnets:**
Currently, the applet scans /24 networks only. For different subnet sizes, you can modify the code or manually add devices.

### Troubleshooting

**"Scan not finding devices"**
- Ensure devices respond to ICMP (ping)
- Check firewall settings
- Verify you're on the same network
- Try manually adding known devices

**"Permission denied"**
- Run with sudo/administrator privileges
- Some network operations require elevated access

**"Tools not working"**
- Verify system commands are available:
  - `ping` command
  - `traceroute` or `tracert` command
- Check the Logs tab for error details

**"tkinter not found"**
- Linux: `sudo apt-get install python3-tk`
- macOS: Should be included with Python
- Windows: Reinstall Python with tkinter option checked

## Advanced Usage

### Data Persistence

Device data is stored in `netdash_devices.json`:
```json
{
  "192.168.1.1": {
    "hostname": "Router",
    "mac": "00:11:22:33:44:55",
    "status": "Online",
    "last_seen": "2026-01-07T04:47:35.123456"
  }
}
```

You can manually edit this file to add devices or update information.

### Keyboard Shortcuts

- **Ctrl+Q**: Quit (on some systems)
- **Right-click**: Context menu on device list

### Command Line Usage

While the applet is a GUI application, you can verify it works:

```bash
# Check syntax
python -m py_compile netdash_applet.py

# Run with Python interpreter
python netdash_applet.py
```

## Use Cases

### Home Network Management
- Discover all devices on your home network
- Monitor which devices are online
- Identify unknown devices
- Test connectivity issues

### Small Office Network
- Map out office network topology
- Identify IP conflicts
- Test server accessibility
- Monitor network devices

### Network Troubleshooting
- Diagnose connectivity problems
- Trace network routes
- Identify firewall issues
- Find open services/ports

### Learning and Education
- Understand network structure
- Learn about IP addresses and subnets
- Practice with network tools
- Visualize network topology

## Security Considerations

### Scanning Ethics
- Only scan networks you own or have permission to scan
- Port scanning unauthorized networks may be illegal
- Be responsible with network tools

### Privacy
- Device hostnames may reveal user information
- MAC addresses are unique identifiers
- Store saved device lists securely

### Best Practices
- Use strong network security (WPA3, etc.)
- Regularly review discovered devices
- Investigate unknown devices
- Keep devices updated and secured

## Limitations

- **Scan Speed**: Sequential scanning can be slow for large networks
- **Subnet Size**: Currently limited to /24 networks (254 hosts)
- **MAC Address**: Not always detectable (depends on OS and privileges)
- **Advanced Features**: No SNMP, WMI, or advanced protocol support
- **GUI Only**: No command-line or API interface

## Future Enhancements

Possible improvements:
- Concurrent scanning for faster results
- Custom subnet sizes
- SNMP integration
- Device type detection
- Bandwidth monitoring
- Alert notifications
- Export to various formats
- Database integration

## Support

For issues or questions:
- Check the Logs tab for error messages
- Review this usage guide
- Visit the GitHub repository
- Submit an issue on GitHub

## License

MIT License - See LICENSE file for details.

---

**Happy Network Managing!** 🌐
