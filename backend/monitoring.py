"""
Device monitoring service using ping and SNMP.
"""
import subprocess
import time
from datetime import datetime
import threading

class DeviceMonitor:
    def __init__(self, devices, socketio):
        self.devices = devices
        self.socketio = socketio
        self.running = False
        self.uptime_data = {}
        
    def ping_device(self, ip):
        """Ping a device to check if it's online"""
        try:
            # Use ping command (works on Linux/Unix)
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Ping error for {ip}: {e}")
            return False
    
    def update_device_status(self, device):
        """Update device status based on ping"""
        is_online = self.ping_device(device['ip'])
        old_status = device['status']
        new_status = 'online' if is_online else 'offline'
        
        if old_status != new_status:
            device['status'] = new_status
            device['last_seen'] = datetime.now().isoformat()
            
            # Emit status change
            self.socketio.emit('device_status_change', {
                'id': device['id'],
                'name': device['name'],
                'status': new_status,
                'timestamp': device['last_seen']
            })
            
            # Create alert if device went offline
            if new_status == 'offline':
                self.socketio.emit('new_alert', {
                    'device_id': device['id'],
                    'device_name': device['name'],
                    'severity': 'error',
                    'message': f"{device['name']} is offline",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Update uptime tracking
        device_id = device['id']
        if device_id not in self.uptime_data:
            self.uptime_data[device_id] = {'total': 0, 'online': 0}
        
        self.uptime_data[device_id]['total'] += 1
        if is_online:
            self.uptime_data[device_id]['online'] += 1
        
        # Calculate uptime percentage
        uptime_pct = (self.uptime_data[device_id]['online'] / 
                     self.uptime_data[device_id]['total']) * 100
        device['uptime'] = round(uptime_pct, 2)
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            for device in self.devices:
                self.update_device_status(device)
            
            # Emit uptime update every cycle
            self.socketio.emit('uptime_update', {
                'timestamp': datetime.now().isoformat(),
                'devices': [
                    {
                        'id': d['id'],
                        'name': d['name'],
                        'uptime': d['uptime']
                    }
                    for d in self.devices
                ]
            })
            
            time.sleep(10)  # Check every 10 seconds
    
    def start(self):
        """Start monitoring"""
        self.running = True
        thread = threading.Thread(target=self.monitor_loop)
        thread.daemon = True
        thread.start()
        print("Device monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        print("Device monitoring stopped")
