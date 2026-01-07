# NetDash - UniFi-Style Network Dashboard

A modern, real-time network monitoring dashboard inspired by UniFi, built with React and Flask.

![NetDash](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### 🖥️ Devices Overview
- Display connected devices with comprehensive attributes (name, type, IP, MAC address)
- Live connection status indicators with real-time updates
- Device categorization (routers, access points, switches)
- Visual status representation with color-coded indicators

### 📊 Uptime Monitoring
- Real-time device and network uptime tracking
- Percentage-based uptime metrics
- Interactive charts and graphs using Chart.js
- Historical uptime data visualization

### 🚨 Alerts & Notifications
- Real-time alerts for offline devices
- High latency detection
- Timestamped alert logs with severity levels (error, warning, info)
- Alert filtering and dismissal capabilities

### 🌐 Topology Visualization
- Interactive network topology map using Cytoscape.js
- Dynamic device connection visualization
- Drag-and-drop node positioning
- Color-coded status representation
- Multiple device type shapes (diamond for routers, triangle for APs, rectangle for switches)

## Tech Stack

### Frontend
- **React 18** with Vite for fast development
- **Tailwind CSS** for responsive, modern UI
- **Chart.js** and **react-chartjs-2** for data visualization
- **Cytoscape.js** with Cola layout for network topology
- **Socket.IO Client** for real-time updates
- **Axios** for API communication

### Backend
- **Python Flask** for REST API
- **Flask-SocketIO** for WebSocket real-time communication
- **PostgreSQL** for data persistence
- **SNMP** and **Ping** for device monitoring
- **Threading** for background monitoring tasks

### Infrastructure
- **Docker** and **Docker Compose** for containerization
- **Nginx** for frontend serving and reverse proxy
- **PostgreSQL** database with health checks

## Project Structure

```
netdash/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── monitoring.py       # Device monitoring service
│   ├── database.py         # Database models and utilities
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend Docker configuration
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DeviceCard.jsx      # Device display component
│   │   │   ├── AlertList.jsx       # Alerts management
│   │   │   ├── UptimeChart.jsx     # Uptime visualization
│   │   │   └── TopologyView.jsx    # Network topology map
│   │   ├── services/
│   │   │   ├── api.js              # API client
│   │   │   └── websocket.js        # WebSocket client
│   │   ├── App.jsx                 # Main application component
│   │   ├── main.jsx                # Application entry point
│   │   └── index.css               # Global styles
│   ├── package.json        # Frontend dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   ├── Dockerfile          # Frontend Docker configuration
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Docker Compose orchestration
└── README.md               # This file

```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/BennyGaming635/netdash.git
cd netdash
```

2. Start the application:
```bash
docker-compose up -d
```

3. Access the dashboard:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

4. Stop the application:
```bash
docker-compose down
```

### Local Development

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Start the backend:
```bash
python app.py
```

The backend will be available at http://localhost:5000

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

### Devices
- `GET /api/devices` - Get all devices
- `GET /api/devices/:id` - Get specific device
- `POST /api/devices` - Add new device

### Alerts
- `GET /api/alerts` - Get all alerts
- `GET /api/alerts?severity=error` - Filter alerts by severity
- `DELETE /api/alerts/:id` - Delete an alert

### Uptime
- `GET /api/uptime/:deviceId` - Get uptime history for a device

### Topology
- `GET /api/topology` - Get network topology data

## WebSocket Events

### Client → Server
- `connect` - Client connection
- `disconnect` - Client disconnection
- `request_devices` - Request device list

### Server → Client
- `connection_response` - Connection acknowledgment
- `device_status_update` - Device status change
- `device_status_change` - Significant status change
- `new_alert` - New alert created
- `uptime_update` - Uptime data update
- `device_added` - New device added

## Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://netdash:netdash@localhost:5432/netdash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000
```

#### Frontend
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

## Monitoring Features

The application includes a background monitoring service that:
- Pings devices every 10 seconds to check availability
- Updates device status in real-time
- Calculates uptime percentages
- Generates alerts for offline devices
- Broadcasts updates via WebSocket

## Deployment

### Production Deployment with Docker

1. Set production environment variables:
```bash
export SECRET_KEY="your-secure-secret-key"
```

2. Build and run:
```bash
docker-compose up -d --build
```

3. Monitor logs:
```bash
docker-compose logs -f
```

### Database Backup

```bash
docker exec netdash-db pg_dump -U netdash netdash > backup.sql
```

### Database Restore

```bash
cat backup.sql | docker exec -i netdash-db psql -U netdash netdash
```

## Development

### Adding New Devices

Devices can be added via the API:

```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Router",
    "type": "router",
    "ip": "192.168.1.1",
    "mac": "00:11:22:33:44:55"
  }'
```

### Customizing the UI

The UI uses Tailwind CSS for styling. Main color scheme:
- Primary: `#0ea5e9` (Sky Blue)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Amber)
- Danger: `#ef4444` (Red)
- Background: `#0f172a` (Slate)

## Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Verify PostgreSQL is running
- Check database credentials in .env

### Frontend won't connect to backend
- Verify backend is running on port 5000
- Check CORS settings in Flask app
- Ensure WebSocket connection is not blocked by firewall

### No device updates
- Verify devices have correct IP addresses
- Check if ping is allowed in your network
- Review backend logs for monitoring errors

## Future Enhancements

- [ ] SNMP integration for detailed device statistics
- [ ] User authentication and authorization
- [ ] Custom alert rules and thresholds
- [ ] Email/SMS notifications
- [ ] Historical data analytics
- [ ] Multi-site support
- [ ] Mobile responsive optimizations
- [ ] Dark/Light theme toggle
- [ ] Export reports (PDF, CSV)
- [ ] Device grouping and tagging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Inspired by Ubiquiti UniFi Network Application
- Built with open-source technologies
- Community-driven development

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/BennyGaming635/netdash).