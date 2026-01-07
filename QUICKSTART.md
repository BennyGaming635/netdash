# NetDash Quick Start Guide

Get NetDash up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Ports 3000, 5000, and 5432 available

## Step 1: Clone the Repository

```bash
git clone https://github.com/BennyGaming635/netdash.git
cd netdash
```

## Step 2: Start the Application

```bash
docker compose up -d
```

This will:
- Start PostgreSQL database
- Build and start the Flask backend
- Build and start the React frontend

## Step 3: Access the Dashboard

Open your browser and navigate to:

**http://localhost:3000**

You should see the NetDash dashboard with sample devices!

## Step 4: View Logs (Optional)

To monitor the application:

```bash
docker compose logs -f
```

## Step 5: Add Your Own Devices

Using curl:

```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Router",
    "type": "router",
    "ip": "192.168.1.1",
    "mac": "00:11:22:33:44:55"
  }'
```

Or use the examples in the `examples/devices.json` file.

## Step 6: Explore Features

### Devices View
- See all connected devices
- Monitor status in real-time
- View uptime percentages

### Topology View
- Interactive network map
- Drag and rearrange nodes
- Visual device connections

### Uptime View
- Bar chart of device uptime
- Average uptime statistics
- Online/offline counts

### Alerts View
- Real-time notifications
- Filter by severity
- Dismiss alerts

## Stopping the Application

```bash
docker compose down
```

## Troubleshooting

### Can't access the dashboard?

Check if all containers are running:
```bash
docker compose ps
```

### Database errors?

Wait a few seconds for PostgreSQL to initialize, then restart:
```bash
docker compose restart backend
```

### Port conflicts?

If ports are in use, edit `docker-compose.yml` to change port mappings.

## Next Steps

- Read the [Full Documentation](README.md)
- Check the [Deployment Guide](DEPLOYMENT.md)
- Add your network devices
- Customize the monitoring intervals

## Need Help?

- GitHub Issues: https://github.com/BennyGaming635/netdash/issues
- Documentation: README.md and DEPLOYMENT.md

Enjoy monitoring your network with NetDash! 🚀
