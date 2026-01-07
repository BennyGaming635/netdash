"""
Main Flask application with WebSocket support for the network dashboard.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
from datetime import datetime
import threading
import time

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage (replace with database in production)
devices = [
    {
        'id': 1,
        'name': 'Main Router',
        'type': 'router',
        'ip': '192.168.1.1',
        'mac': '00:11:22:33:44:55',
        'status': 'online',
        'uptime': 99.9,
        'last_seen': datetime.now().isoformat()
    },
    {
        'id': 2,
        'name': 'Access Point 1',
        'type': 'access_point',
        'ip': '192.168.1.10',
        'mac': 'AA:BB:CC:DD:EE:FF',
        'status': 'online',
        'uptime': 98.5,
        'last_seen': datetime.now().isoformat()
    },
    {
        'id': 3,
        'name': 'Switch 1',
        'type': 'switch',
        'ip': '192.168.1.20',
        'mac': '11:22:33:44:55:66',
        'status': 'online',
        'uptime': 99.2,
        'last_seen': datetime.now().isoformat()
    }
]

alerts = [
    {
        'id': 1,
        'device_id': 2,
        'severity': 'warning',
        'message': 'High latency detected',
        'timestamp': datetime.now().isoformat()
    }
]

uptime_history = {}

# API Routes
@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    return jsonify(devices)

@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get specific device"""
    device = next((d for d in devices if d['id'] == device_id), None)
    if device:
        return jsonify(device)
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/devices', methods=['POST'])
def add_device():
    """Add a new device"""
    data = request.json
    new_device = {
        'id': len(devices) + 1,
        'name': data.get('name'),
        'type': data.get('type'),
        'ip': data.get('ip'),
        'mac': data.get('mac'),
        'status': 'offline',
        'uptime': 0,
        'last_seen': datetime.now().isoformat()
    }
    devices.append(new_device)
    socketio.emit('device_added', new_device)
    return jsonify(new_device), 201

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    severity = request.args.get('severity')
    if severity:
        filtered = [a for a in alerts if a['severity'] == severity]
        return jsonify(filtered)
    return jsonify(alerts)

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    global alerts
    alerts = [a for a in alerts if a['id'] != alert_id]
    return jsonify({'success': True})

@app.route('/api/uptime/<int:device_id>', methods=['GET'])
def get_uptime(device_id):
    """Get uptime history for a device"""
    history = uptime_history.get(device_id, [])
    return jsonify(history)

@app.route('/api/topology', methods=['GET'])
def get_topology():
    """Get network topology data"""
    # Build topology from devices
    nodes = [
        {
            'id': str(d['id']),
            'label': d['name'],
            'type': d['type'],
            'status': d['status']
        }
        for d in devices
    ]
    
    # Create edges (connections between devices)
    edges = [
        {'from': '1', 'to': '2'},  # Router to AP
        {'from': '1', 'to': '3'},  # Router to Switch
    ]
    
    return jsonify({'nodes': nodes, 'edges': edges})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('request_devices')
def handle_request_devices():
    """Send device list to client"""
    emit('devices_update', devices)

# Background monitoring task
def monitoring_task():
    """Background task to monitor devices and emit updates"""
    while True:
        time.sleep(5)  # Check every 5 seconds
        
        # Simulate device status changes
        for device in devices:
            # In production, this would ping/SNMP the device
            # For now, we'll just emit updates
            socketio.emit('device_status_update', {
                'id': device['id'],
                'status': device['status'],
                'last_seen': datetime.now().isoformat()
            })

# Start monitoring thread
def start_monitoring():
    """Start the background monitoring thread"""
    thread = threading.Thread(target=monitoring_task)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_monitoring()
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
