#!/usr/bin/env python3
"""
NetDash Applet - A simple GUI network management tool
Provides network scanning, monitoring, and management capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import platform
import socket
import ipaddress
import re
from datetime import datetime
import json
import os

class NetworkDevice:
    """Represents a network device"""
    def __init__(self, ip, hostname="Unknown", mac="Unknown", status="Unknown"):
        self.ip = ip
        self.hostname = hostname
        self.mac = mac
        self.status = status
        self.last_seen = datetime.now()
        self.manufacturer = self._detect_manufacturer()
    
    def _detect_manufacturer(self):
        """Detect manufacturer based on hostname, MAC, or other characteristics"""
        hostname_lower = self.hostname.lower()
        mac_upper = self.mac.upper()
        
        # Check hostname patterns
        if any(x in hostname_lower for x in ['cisco', 'catalyst', 'nexus', 'asa']):
            return 'cisco'
        elif any(x in hostname_lower for x in ['unifi', 'ubiquiti', 'uap', 'usw', 'udm']):
            return 'ubiquiti'
        elif any(x in hostname_lower for x in ['netgear', 'orbi', 'nighthawk']):
            return 'netgear'
        elif any(x in hostname_lower for x in ['tp-link', 'tplink', 'archer', 'deco']):
            return 'tplink'
        elif any(x in hostname_lower for x in ['router', 'gateway', 'modem']):
            return 'router'
        
        # Check MAC address OUI (first 6 characters)
        # Common manufacturer OUIs (selected verified examples)
        if mac_upper.startswith('00:1B:D5') or mac_upper.startswith('C4:64:13'):
            return 'cisco'
        elif mac_upper.startswith('F0:9F:C2') or mac_upper.startswith('74:83:C2'):
            return 'ubiquiti'
        elif mac_upper.startswith('A0:40:A0') or mac_upper.startswith('20:E5:2A'):
            return 'netgear'
        elif mac_upper.startswith('98:DE:D0') or mac_upper.startswith('A4:2B:B0'):
            return 'tplink'
        
        return 'generic'

class NetDashApplet:
    """Main application class for the network management applet"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NetDash - Network Management Applet")
        self.root.geometry("1000x700")
        
        # Data storage
        self.devices = {}
        self.scanning = False
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create UI
        self.create_menu()
        self.create_main_layout()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Devices", command=self.save_devices)
        file_menu.add_command(label="Load Devices", command=self.load_devices)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Scan Network", command=self.start_network_scan)
        tools_menu.add_command(label="Clear All Devices", command=self.clear_devices)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_layout(self):
        """Create main layout with tabs"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_network_map_tab()
        self.create_tools_tab()
        self.create_logs_tab()
        
    def create_dashboard_tab(self):
        """Create dashboard tab showing devices"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Top control panel
        control_frame = ttk.Frame(dashboard_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Scan Network", 
                  command=self.start_network_scan).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_devices).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Add Device", 
                  command=self.add_device_dialog).pack(side='left', padx=5)
        
        self.scan_status_label = ttk.Label(control_frame, text="Ready")
        self.scan_status_label.pack(side='left', padx=20)
        
        # Device list with treeview
        list_frame = ttk.Frame(dashboard_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview for devices
        columns = ('IP', 'Hostname', 'MAC', 'Status', 'Last Seen')
        self.device_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show='tree headings', 
                                        yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.device_tree.yview)
        
        # Configure columns
        self.device_tree.column('#0', width=50)
        self.device_tree.heading('#0', text='#')
        
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=150)
        
        self.device_tree.pack(fill='both', expand=True)
        
        # Context menu for device tree
        self.device_menu = tk.Menu(self.device_tree, tearoff=0)
        self.device_menu.add_command(label="Ping Device", command=self.ping_selected_device)
        self.device_menu.add_command(label="Trace Route", command=self.trace_selected_device)
        self.device_menu.add_command(label="Remove Device", command=self.remove_selected_device)
        
        self.device_tree.bind("<Button-3>", self.show_device_context_menu)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Statistics")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Devices: 0 | Online: 0 | Offline: 0")
        self.stats_label.pack(padx=5, pady=5)
        
    def create_network_map_tab(self):
        """Create network map visualization tab"""
        map_frame = ttk.Frame(self.notebook)
        self.notebook.add(map_frame, text="Network Map")
        
        # Control panel
        control_frame = ttk.Frame(map_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="Network Subnet:").pack(side='left', padx=5)
        self.subnet_entry = ttk.Entry(control_frame, width=20)
        self.subnet_entry.insert(0, "192.168.1.0/24")
        self.subnet_entry.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Generate Map", 
                  command=self.generate_network_map).pack(side='left', padx=5)
        
        # Map display area (GUI-based canvas)
        map_display_frame = ttk.LabelFrame(map_frame, text="Network Topology")
        map_display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(map_display_frame)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        # Canvas for drawing network map
        self.map_canvas = tk.Canvas(canvas_frame, bg='white', 
                                    xscrollcommand=h_scrollbar.set,
                                    yscrollcommand=v_scrollbar.set)
        self.map_canvas.pack(side='left', fill='both', expand=True)
        
        h_scrollbar.config(command=self.map_canvas.xview)
        v_scrollbar.config(command=self.map_canvas.yview)
        
        # Bind mouse events for interactivity
        self.map_canvas.bind('<Button-1>', self.on_map_click)
        self.map_canvas.bind('<Leave>', self.on_map_leave)
        
        # Store device positions and canvas items for interactivity
        self.device_canvas_items = {}
        self.device_positions = {}
        
        # Tooltip label
        self.tooltip_label = None
        
    def create_tools_tab(self):
        """Create network tools tab"""
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="Network Tools")
        
        # Ping tool
        ping_frame = ttk.LabelFrame(tools_frame, text="Ping Tool")
        ping_frame.pack(fill='x', padx=5, pady=5)
        
        ping_input_frame = ttk.Frame(ping_frame)
        ping_input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(ping_input_frame, text="Host:").pack(side='left', padx=5)
        self.ping_entry = ttk.Entry(ping_input_frame, width=30)
        self.ping_entry.pack(side='left', padx=5)
        ttk.Button(ping_input_frame, text="Ping", 
                  command=self.run_ping_tool).pack(side='left', padx=5)
        
        self.ping_result = scrolledtext.ScrolledText(ping_frame, height=6, wrap=tk.WORD)
        self.ping_result.pack(fill='x', padx=5, pady=5)
        
        # Traceroute tool
        trace_frame = ttk.LabelFrame(tools_frame, text="Traceroute Tool")
        trace_frame.pack(fill='x', padx=5, pady=5)
        
        trace_input_frame = ttk.Frame(trace_frame)
        trace_input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(trace_input_frame, text="Host:").pack(side='left', padx=5)
        self.trace_entry = ttk.Entry(trace_input_frame, width=30)
        self.trace_entry.pack(side='left', padx=5)
        ttk.Button(trace_input_frame, text="Trace", 
                  command=self.run_traceroute_tool).pack(side='left', padx=5)
        
        self.trace_result = scrolledtext.ScrolledText(trace_frame, height=6, wrap=tk.WORD)
        self.trace_result.pack(fill='x', padx=5, pady=5)
        
        # Port scan tool
        port_frame = ttk.LabelFrame(tools_frame, text="Port Scanner")
        port_frame.pack(fill='x', padx=5, pady=5)
        
        port_input_frame = ttk.Frame(port_frame)
        port_input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(port_input_frame, text="Host:").pack(side='left', padx=5)
        self.port_host_entry = ttk.Entry(port_input_frame, width=20)
        self.port_host_entry.pack(side='left', padx=5)
        
        ttk.Label(port_input_frame, text="Ports:").pack(side='left', padx=5)
        self.port_range_entry = ttk.Entry(port_input_frame, width=15)
        self.port_range_entry.insert(0, "20-80,443,8080")
        self.port_range_entry.pack(side='left', padx=5)
        
        ttk.Button(port_input_frame, text="Scan", 
                  command=self.run_port_scan).pack(side='left', padx=5)
        
        self.port_result = scrolledtext.ScrolledText(port_frame, height=6, wrap=tk.WORD)
        self.port_result.pack(fill='x', padx=5, pady=5)
        
    def create_logs_tab(self):
        """Create logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Control panel
        control_frame = ttk.Frame(logs_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side='left', padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD,
                                                   font=('Courier', 9))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log("NetDash Applet started")
        
    def log(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear all logs"""
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared")
        
    def start_network_scan(self):
        """Start network scanning in background thread"""
        if self.scanning:
            messagebox.showwarning("Scan in Progress", "A network scan is already running")
            return
            
        self.scanning = True
        self.scan_status_label.config(text="Scanning...")
        self.log("Starting network scan...")
        
        # Run scan in background thread
        thread = threading.Thread(target=self.perform_network_scan, daemon=True)
        thread.start()
        
    def perform_network_scan(self):
        """Perform the actual network scan"""
        try:
            # Get local IP and subnet
            local_ip = self.get_local_ip()
            if not local_ip:
                self.log("Could not determine local IP address")
                self.scanning = False
                self.scan_status_label.config(text="Ready")
                return
                
            self.log(f"Local IP: {local_ip}")
            
            # Calculate subnet
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            self.log(f"Scanning subnet: {network}")
            
            count = 0
            for ip in network.hosts():
                if not self.scanning:
                    break
                    
                ip_str = str(ip)
                
                # Try to ping the host
                if self.ping_host(ip_str, timeout=1):
                    count += 1
                    hostname = self.get_hostname(ip_str)
                    
                    device = NetworkDevice(ip_str, hostname=hostname, status="Online")
                    self.devices[ip_str] = device
                    
                    self.log(f"Found device: {ip_str} ({hostname})")
                    
                    # Update UI
                    self.root.after(0, self.refresh_devices)
            
            self.log(f"Scan complete. Found {count} devices")
            
        except Exception as e:
            self.log(f"Error during scan: {str(e)}")
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_status_label.config(text="Ready"))
            
    def ping_host(self, host, timeout=2):
        """Ping a host to check if it's alive"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
            
            command = ['ping', param, '1', timeout_param, str(timeout), host]
            result = subprocess.run(command, stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, timeout=timeout+1)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            return False
            
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except (socket.error, OSError):
            return None
            
    def get_hostname(self, ip):
        """Get hostname for IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            return "Unknown"
            
    def refresh_devices(self):
        """Refresh device list in UI"""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
            
        # Add devices
        online_count = 0
        for idx, (ip, device) in enumerate(sorted(self.devices.items()), 1):
            status = device.status
            if status == "Online":
                online_count += 1
                
            last_seen = device.last_seen.strftime("%Y-%m-%d %H:%M:%S")
            
            self.device_tree.insert('', 'end', text=str(idx),
                                   values=(device.ip, device.hostname, 
                                          device.mac, status, last_seen))
        
        # Update stats
        total = len(self.devices)
        offline_count = total - online_count
        self.stats_label.config(text=f"Devices: {total} | Online: {online_count} | Offline: {offline_count}")
        
    def add_device_dialog(self):
        """Show dialog to manually add a device"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Device")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ip_entry = ttk.Entry(dialog, width=30)
        ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Hostname:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        hostname_entry = ttk.Entry(dialog, width=30)
        hostname_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="MAC Address:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        mac_entry = ttk.Entry(dialog, width=30)
        mac_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def add_device():
            ip = ip_entry.get().strip()
            hostname = hostname_entry.get().strip() or "Unknown"
            mac = mac_entry.get().strip() or "Unknown"
            
            if not ip:
                messagebox.showwarning("Invalid Input", "IP address is required")
                return
                
            device = NetworkDevice(ip, hostname=hostname, mac=mac, status="Unknown")
            self.devices[ip] = device
            self.log(f"Manually added device: {ip}")
            self.refresh_devices()
            dialog.destroy()
            
        ttk.Button(dialog, text="Add", command=add_device).grid(row=3, column=0, 
                                                                columnspan=2, pady=10)
        
    def show_device_context_menu(self, event):
        """Show context menu for device"""
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
            self.device_menu.post(event.x_root, event.y_root)
            
    def ping_selected_device(self):
        """Ping the selected device"""
        selection = self.device_tree.selection()
        if not selection:
            return
            
        values = self.device_tree.item(selection[0])['values']
        if values:
            ip = values[0]
            self.ping_entry.delete(0, tk.END)
            self.ping_entry.insert(0, ip)
            self.notebook.select(2)  # Switch to tools tab
            self.run_ping_tool()
            
    def trace_selected_device(self):
        """Trace route to selected device"""
        selection = self.device_tree.selection()
        if not selection:
            return
            
        values = self.device_tree.item(selection[0])['values']
        if values:
            ip = values[0]
            self.trace_entry.delete(0, tk.END)
            self.trace_entry.insert(0, ip)
            self.notebook.select(2)  # Switch to tools tab
            self.run_traceroute_tool()
            
    def remove_selected_device(self):
        """Remove selected device"""
        selection = self.device_tree.selection()
        if not selection:
            return
            
        values = self.device_tree.item(selection[0])['values']
        if values:
            ip = values[0]
            if messagebox.askyesno("Confirm", f"Remove device {ip}?"):
                if ip in self.devices:
                    del self.devices[ip]
                    self.log(f"Removed device: {ip}")
                    self.refresh_devices()
                    
    def generate_network_map(self):
        """Generate a GUI-based network map with visual device representations"""
        # Clear existing map
        self.map_canvas.delete('all')
        self.device_canvas_items.clear()
        self.device_positions.clear()
        
        subnet = self.subnet_entry.get()
        
        if not self.devices:
            self.map_canvas.create_text(400, 300, text="No devices found. Run a network scan first.",
                                       font=('Arial', 14), fill='gray')
            return
        
        # Draw title
        self.map_canvas.create_text(400, 30, text=f"Network Topology Map - {subnet}",
                                   font=('Arial', 16, 'bold'), fill='#2c3e50')
        
        # Draw Internet and Gateway
        gateway_x, gateway_y = 400, 100
        self._draw_internet_gateway(gateway_x, gateway_y)
        
        # Group devices by status
        online_devices = [d for d in self.devices.values() if d.status == "Online"]
        offline_devices = [d for d in self.devices.values() if d.status != "Online"]
        
        # Calculate layout
        all_display_devices = online_devices + offline_devices
        num_devices = len(all_display_devices)
        
        if num_devices == 0:
            return
        
        # Layout devices in a grid below the gateway
        start_y = 250
        devices_per_row = min(5, max(3, num_devices))
        spacing_x = 150
        spacing_y = 180
        
        # Calculate starting x position to center the layout
        total_width = devices_per_row * spacing_x
        start_x = max(100, (800 - total_width) // 2 + spacing_x // 2)
        
        # Draw connection lines from gateway to devices
        for idx, device in enumerate(all_display_devices):
            row = idx // devices_per_row
            col = idx % devices_per_row
            
            device_x = start_x + col * spacing_x
            device_y = start_y + row * spacing_y
            
            # Draw line from gateway to device
            line_color = '#27ae60' if device.status == "Online" else '#95a5a6'
            self.map_canvas.create_line(gateway_x, gateway_y + 40, device_x, device_y - 40,
                                       fill=line_color, width=2, dash=(5, 3))
        
        # Draw devices
        for idx, device in enumerate(all_display_devices):
            row = idx // devices_per_row
            col = idx % devices_per_row
            
            device_x = start_x + col * spacing_x
            device_y = start_y + row * spacing_y
            
            # Draw device with image and label
            self._draw_device_node(device, device_x, device_y)
        
        # Update scroll region
        self.map_canvas.configure(scrollregion=self.map_canvas.bbox('all'))
        
        self.log("Generated GUI-based network map")
    
    def _draw_internet_gateway(self, x, y):
        """Draw the Internet and Gateway/Router representation"""
        # Draw Internet cloud (top)
        cloud_y = y - 80
        self._draw_cloud(x, cloud_y, 'Internet', '#3498db')
        
        # Draw connection line
        self.map_canvas.create_line(x, cloud_y + 25, x, y - 40,
                                   fill='#2c3e50', width=3)
        
        # Draw Gateway/Router
        self._draw_router_device(x, y, 'Gateway/Router', '#e74c3c')
    
    def _draw_cloud(self, x, y, label, color):
        """Draw a cloud shape to represent Internet"""
        # Simple cloud using ovals
        self.map_canvas.create_oval(x - 40, y - 15, x - 10, y + 15, fill=color, outline=color)
        self.map_canvas.create_oval(x - 20, y - 20, x + 20, y + 10, fill=color, outline=color)
        self.map_canvas.create_oval(x + 10, y - 15, x + 40, y + 15, fill=color, outline=color)
        
        # Label
        self.map_canvas.create_text(x, y + 35, text=label, font=('Arial', 10, 'bold'),
                                   fill='#2c3e50')
    
    def _draw_router_device(self, x, y, label, color):
        """Draw a router device representation"""
        # Router body (rectangle with antenna)
        self.map_canvas.create_rectangle(x - 30, y - 20, x + 30, y + 20,
                                        fill=color, outline='#c0392b', width=2)
        
        # Antenna
        self.map_canvas.create_line(x - 15, y - 20, x - 15, y - 35, fill='#2c3e50', width=2)
        self.map_canvas.create_oval(x - 18, y - 40, x - 12, y - 34, fill='#2c3e50', outline='#2c3e50')
        
        self.map_canvas.create_line(x + 15, y - 20, x + 15, y - 35, fill='#2c3e50', width=2)
        self.map_canvas.create_oval(x + 12, y - 40, x + 18, y - 34, fill='#2c3e50', outline='#2c3e50')
        
        # LED indicators
        for i in range(3):
            self.map_canvas.create_oval(x - 15 + i * 15, y - 5, x - 10 + i * 15, y,
                                       fill='#2ecc71', outline='#27ae60')
        
        # Label
        self.map_canvas.create_text(x, y + 35, text=label, font=('Arial', 9, 'bold'),
                                   fill='#2c3e50')
    
    def _draw_device_node(self, device, x, y):
        """Draw a device node with manufacturer-specific icon and label"""
        # Get manufacturer-specific colors and icon
        manufacturer = device.manufacturer
        icon_color = self._get_manufacturer_color(manufacturer)
        
        # Draw device icon based on manufacturer
        items = []
        if manufacturer == 'cisco':
            items = self._draw_cisco_icon(x, y, icon_color, device.status)
        elif manufacturer == 'ubiquiti':
            items = self._draw_ubiquiti_icon(x, y, icon_color, device.status)
        elif manufacturer == 'netgear':
            items = self._draw_netgear_icon(x, y, icon_color, device.status)
        elif manufacturer == 'tplink':
            items = self._draw_tplink_icon(x, y, icon_color, device.status)
        elif manufacturer == 'router':
            items = self._draw_router_icon(x, y, icon_color, device.status)
        else:
            items = self._draw_generic_icon(x, y, icon_color, device.status)
        
        # Draw device labels
        # Hostname
        hostname_text = device.hostname if device.hostname != "Unknown" else "Unknown Device"
        if len(hostname_text) > 15:
            hostname_text = hostname_text[:12] + "..."
        
        text_item = self.map_canvas.create_text(x, y + 45, text=hostname_text,
                                               font=('Arial', 9, 'bold'),
                                               fill='#2c3e50')
        items.append(text_item)
        
        # IP address
        ip_item = self.map_canvas.create_text(x, y + 60, text=device.ip,
                                             font=('Arial', 8),
                                             fill='#7f8c8d')
        items.append(ip_item)
        
        # Status indicator
        status_color = '#27ae60' if device.status == "Online" else '#95a5a6'
        status_item = self.map_canvas.create_oval(x + 35, y - 35, x + 45, y - 25,
                                                 fill=status_color, outline=status_color)
        items.append(status_item)
        
        # Store device info for interactivity
        self.device_canvas_items[device.ip] = items
        self.device_positions[device.ip] = (x, y, device)
        
        # Bind events to all items
        for item in items:
            self.map_canvas.tag_bind(item, '<Enter>', lambda e, d=device: self._on_device_hover_enter(e, d))
            self.map_canvas.tag_bind(item, '<Leave>', lambda e: self._on_device_hover_leave(e))
            self.map_canvas.tag_bind(item, '<Button-1>', lambda e, d=device: self._on_device_click(e, d))
    
    def _get_manufacturer_color(self, manufacturer):
        """Get color scheme for manufacturer"""
        colors = {
            'cisco': '#049fd9',      # Cisco blue
            'ubiquiti': '#0572d4',   # Ubiquiti blue
            'netgear': '#fdb714',    # Netgear yellow
            'tplink': '#009cde',     # TP-Link blue
            'router': '#e74c3c',     # Red for routers
            'generic': '#95a5a6'     # Gray for generic
        }
        return colors.get(manufacturer, '#95a5a6')
    
    def _draw_cisco_icon(self, x, y, color, status):
        """Draw Cisco device icon"""
        items = []
        # Cisco-style rack mount device
        opacity = 1.0 if status == "Online" else 0.5
        
        # Main body
        rect = self.map_canvas.create_rectangle(x - 30, y - 25, x + 30, y + 25,
                                               fill=color, outline='#2c3e50', width=2)
        items.append(rect)
        
        # Cisco stripes pattern
        for i in range(3):
            line = self.map_canvas.create_line(x - 25 + i * 8, y - 20,
                                              x - 25 + i * 8, y + 20,
                                              fill='white', width=2)
            items.append(line)
        
        # Front panel LEDs
        for i in range(4):
            led = self.map_canvas.create_rectangle(x - 20 + i * 12, y + 15,
                                                  x - 15 + i * 12, y + 20,
                                                  fill='#2ecc71' if status == "Online" else '#7f8c8d',
                                                  outline='#2c3e50')
            items.append(led)
        
        return items
    
    def _draw_ubiquiti_icon(self, x, y, color, status):
        """Draw Ubiquiti/UniFi device icon"""
        items = []
        
        # UniFi access point style - circular
        circle = self.map_canvas.create_oval(x - 28, y - 28, x + 28, y + 28,
                                            fill=color, outline='#2c3e50', width=2)
        items.append(circle)
        
        # UniFi logo pattern (simplified U shape)
        arc = self.map_canvas.create_arc(x - 15, y - 15, x + 15, y + 15,
                                        start=180, extent=180,
                                        outline='white', width=4, style='arc')
        items.append(arc)
        
        # LED ring indicator
        if status == "Online":
            led_ring = self.map_canvas.create_oval(x - 22, y - 22, x + 22, y + 22,
                                                  outline='#2ecc71', width=2)
            items.append(led_ring)
        
        return items
    
    def _draw_netgear_icon(self, x, y, color, status):
        """Draw Netgear device icon"""
        items = []
        
        # Netgear router/switch style
        rect = self.map_canvas.create_rectangle(x - 32, y - 22, x + 32, y + 22,
                                               fill=color, outline='#2c3e50', width=2)
        items.append(rect)
        
        # Netgear logo stripe
        stripe = self.map_canvas.create_rectangle(x - 32, y - 10, x + 32, y,
                                                 fill='#2c3e50', outline='')
        items.append(stripe)
        
        # Port indicators
        for i in range(5):
            port = self.map_canvas.create_rectangle(x - 25 + i * 11, y + 10,
                                                   x - 20 + i * 11, y + 17,
                                                   fill='#2c3e50', outline='#2c3e50')
            items.append(port)
            
            if status == "Online":
                led = self.map_canvas.create_oval(x - 24 + i * 11, y + 5,
                                                 x - 21 + i * 11, y + 8,
                                                 fill='#2ecc71', outline='#2ecc71')
                items.append(led)
        
        return items
    
    def _draw_tplink_icon(self, x, y, color, status):
        """Draw TP-Link device icon"""
        items = []
        
        # TP-Link router with antennas
        body = self.map_canvas.create_rectangle(x - 28, y - 18, x + 28, y + 22,
                                               fill=color, outline='#2c3e50', width=2)
        items.append(body)
        
        # Antennas
        ant1 = self.map_canvas.create_line(x - 20, y - 18, x - 25, y - 32,
                                          fill='#2c3e50', width=3)
        items.append(ant1)
        
        ant2 = self.map_canvas.create_line(x + 20, y - 18, x + 25, y - 32,
                                          fill='#2c3e50', width=3)
        items.append(ant2)
        
        # Logo area
        logo = self.map_canvas.create_rectangle(x - 15, y - 10, x + 15, y + 5,
                                               fill='white', outline='')
        items.append(logo)
        
        # Power LED
        if status == "Online":
            led = self.map_canvas.create_oval(x - 5, y + 10, x + 5, y + 18,
                                             fill='#2ecc71', outline='#27ae60')
            items.append(led)
        
        return items
    
    def _draw_router_icon(self, x, y, color, status):
        """Draw generic router icon"""
        items = []
        
        # Router body
        body = self.map_canvas.create_rectangle(x - 30, y - 20, x + 30, y + 20,
                                               fill=color, outline='#2c3e50', width=2)
        items.append(body)
        
        # Single antenna
        ant = self.map_canvas.create_line(x, y - 20, x, y - 35,
                                         fill='#2c3e50', width=3)
        items.append(ant)
        
        tip = self.map_canvas.create_oval(x - 3, y - 40, x + 3, y - 34,
                                         fill='#2c3e50', outline='#2c3e50')
        items.append(tip)
        
        # LEDs
        if status == "Online":
            for i in range(3):
                led = self.map_canvas.create_oval(x - 15 + i * 15, y - 5,
                                                 x - 10 + i * 15, y,
                                                 fill='#2ecc71', outline='#27ae60')
                items.append(led)
        
        return items
    
    def _draw_generic_icon(self, x, y, color, status):
        """Draw generic device icon"""
        items = []
        
        # Generic computer/device
        # Monitor
        monitor = self.map_canvas.create_rectangle(x - 25, y - 25, x + 25, y + 15,
                                                  fill=color, outline='#2c3e50', width=2)
        items.append(monitor)
        
        # Screen
        screen = self.map_canvas.create_rectangle(x - 20, y - 20, x + 20, y + 10,
                                                 fill='#34495e', outline='')
        items.append(screen)
        
        # Stand
        stand = self.map_canvas.create_rectangle(x - 5, y + 15, x + 5, y + 25,
                                               fill='#2c3e50', outline='')
        items.append(stand)
        
        # Base
        base = self.map_canvas.create_rectangle(x - 15, y + 25, x + 15, y + 30,
                                               fill='#2c3e50', outline='')
        items.append(base)
        
        # Power indicator
        if status == "Online":
            led = self.map_canvas.create_oval(x + 18, y + 8, x + 23, y + 13,
                                             fill='#2ecc71', outline='#27ae60')
            items.append(led)
        
        return items
    
    def _on_device_hover_enter(self, event, device):
        """Handle mouse entering device area"""
        # Highlight device
        if device.ip in self.device_canvas_items:
            for item in self.device_canvas_items[device.ip]:
                try:
                    self.map_canvas.itemconfig(item, width=3)
                except (tk.TclError, AttributeError):
                    pass  # Text items and some shapes don't have width property
        
        # Show tooltip
        self._show_tooltip(event.x_root, event.y_root, device)
    
    def _on_device_hover_leave(self, event):
        """Handle mouse leaving device area"""
        # Remove highlight from all devices
        for items in self.device_canvas_items.values():
            for item in items:
                try:
                    self.map_canvas.itemconfig(item, width=2)
                except (tk.TclError, AttributeError):
                    pass  # Text items and some shapes don't have width property
        
        # Hide tooltip
        self._hide_tooltip()
    
    def _on_device_click(self, event, device):
        """Handle device click to show detailed information"""
        info_text = f"""Device Information

IP Address: {device.ip}
Hostname: {device.hostname}
MAC Address: {device.mac}
Status: {device.status}
Manufacturer: {device.manufacturer.upper()}
Last Seen: {device.last_seen.strftime('%Y-%m-%d %H:%M:%S')}"""
        
        messagebox.showinfo(f"Device: {device.hostname}", info_text)
        self.log(f"Clicked on device: {device.ip} ({device.hostname})")
    
    def _show_tooltip(self, x, y, device):
        """Show tooltip with device information"""
        self._hide_tooltip()
        
        tooltip_text = f"{device.hostname}\n{device.ip}\n{device.manufacturer.upper()}"
        
        # Create tooltip window
        self.tooltip_label = tk.Toplevel(self.root)
        self.tooltip_label.wm_overrideredirect(True)
        self.tooltip_label.wm_geometry(f"+{x + 10}+{y + 10}")
        
        label = tk.Label(self.tooltip_label, text=tooltip_text,
                        background="#ffffe0", relief='solid',
                        borderwidth=1, font=('Arial', 9),
                        justify='left', padx=5, pady=3)
        label.pack()
    
    def _hide_tooltip(self):
        """Hide tooltip"""
        if self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None
    
    def on_map_click(self, event):
        """Handle click on map canvas"""
        # Hide tooltip on background click
        self._hide_tooltip()
    
    def on_map_leave(self, event):
        """Handle mouse leaving map canvas"""
        self._hide_tooltip()
        
    def run_ping_tool(self):
        """Run ping tool"""
        host = self.ping_entry.get().strip()
        if not host:
            messagebox.showwarning("Invalid Input", "Please enter a host")
            return
            
        self.ping_result.delete(1.0, tk.END)
        self.ping_result.insert(tk.END, f"Pinging {host}...\n\n")
        
        def ping_thread():
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '4', host]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, text=True, timeout=10)
                
                output = result.stdout + result.stderr
                self.root.after(0, lambda: self.ping_result.insert(tk.END, output))
                self.log(f"Ping completed for {host}")
                
            except Exception as e:
                self.root.after(0, lambda: self.ping_result.insert(tk.END, f"Error: {str(e)}\n"))
                
        thread = threading.Thread(target=ping_thread, daemon=True)
        thread.start()
        
    def run_traceroute_tool(self):
        """Run traceroute tool"""
        host = self.trace_entry.get().strip()
        if not host:
            messagebox.showwarning("Invalid Input", "Please enter a host")
            return
            
        self.trace_result.delete(1.0, tk.END)
        self.trace_result.insert(tk.END, f"Tracing route to {host}...\n\n")
        
        def trace_thread():
            try:
                command = ['tracert' if platform.system().lower() == 'windows' else 'traceroute', host]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, text=True, timeout=60)
                
                output = result.stdout + result.stderr
                self.root.after(0, lambda: self.trace_result.insert(tk.END, output))
                self.log(f"Traceroute completed for {host}")
                
            except Exception as e:
                self.root.after(0, lambda: self.trace_result.insert(tk.END, f"Error: {str(e)}\n"))
                
        thread = threading.Thread(target=trace_thread, daemon=True)
        thread.start()
        
    def run_port_scan(self):
        """Run port scan"""
        host = self.port_host_entry.get().strip()
        ports_str = self.port_range_entry.get().strip()
        
        if not host or not ports_str:
            messagebox.showwarning("Invalid Input", "Please enter host and ports")
            return
            
        self.port_result.delete(1.0, tk.END)
        self.port_result.insert(tk.END, f"Scanning {host}...\n\n")
        
        def scan_thread():
            try:
                # Parse port specification
                ports = []
                for part in ports_str.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        ports.extend(range(start, end + 1))
                    else:
                        ports.append(int(part))
                        
                open_ports = []
                for port in ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((host, port))
                        sock.close()
                        
                        if result == 0:
                            open_ports.append(port)
                            msg = f"Port {port}: OPEN\n"
                            self.root.after(0, lambda m=msg: self.port_result.insert(tk.END, m))
                    except (socket.error, OSError):
                        pass
                        
                summary = f"\nScan complete. Found {len(open_ports)} open ports\n"
                self.root.after(0, lambda: self.port_result.insert(tk.END, summary))
                self.log(f"Port scan completed for {host}")
                
            except Exception as e:
                self.root.after(0, lambda: self.port_result.insert(tk.END, f"Error: {str(e)}\n"))
                
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
        
    def save_devices(self):
        """Save devices to file"""
        try:
            data = {
                ip: {
                    'hostname': device.hostname,
                    'mac': device.mac,
                    'status': device.status,
                    'last_seen': device.last_seen.isoformat()
                }
                for ip, device in self.devices.items()
            }
            
            with open('netdash_devices.json', 'w') as f:
                json.dump(data, f, indent=2)
                
            self.log("Devices saved to netdash_devices.json")
            messagebox.showinfo("Success", "Devices saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save devices: {str(e)}")
            
    def load_devices(self):
        """Load devices from file"""
        try:
            if not os.path.exists('netdash_devices.json'):
                messagebox.showwarning("Not Found", "No saved devices file found")
                return
                
            with open('netdash_devices.json', 'r') as f:
                data = json.load(f)
                
            self.devices.clear()
            for ip, info in data.items():
                device = NetworkDevice(
                    ip=ip,
                    hostname=info['hostname'],
                    mac=info['mac'],
                    status=info['status']
                )
                self.devices[ip] = device
                
            self.refresh_devices()
            self.log(f"Loaded {len(self.devices)} devices from file")
            messagebox.showinfo("Success", f"Loaded {len(self.devices)} devices")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load devices: {str(e)}")
            
    def clear_devices(self):
        """Clear all devices"""
        if messagebox.askyesno("Confirm", "Clear all devices?"):
            self.devices.clear()
            self.refresh_devices()
            self.log("All devices cleared")
            
    def show_about(self):
        """Show about dialog"""
        about_text = """NetDash Applet v1.0

A simple network management tool for:
- Network scanning and discovery
- Device monitoring
- Network diagnostics (ping, traceroute, port scan)
- Network topology mapping

Built with Python and tkinter
Part of the NetDash project"""
        
        messagebox.showinfo("About NetDash Applet", about_text)

def main():
    """Main entry point"""
    root = tk.Tk()
    app = NetDashApplet(root)
    root.mainloop()

if __name__ == '__main__':
    main()
