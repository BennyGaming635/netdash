# NetDash Deployment Guide

This guide provides detailed instructions for deploying NetDash in various environments.

## Table of Contents

1. [Quick Start with Docker](#quick-start-with-docker)
2. [Production Deployment](#production-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Local Development](#local-development)
5. [Troubleshooting](#troubleshooting)

## Quick Start with Docker

The fastest way to get NetDash running is using Docker Compose.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 2GB of RAM
- Port 3000, 5000, and 5432 available

### Steps

1. Clone the repository:
```bash
git clone https://github.com/BennyGaming635/netdash.git
cd netdash
```

2. Start the application:
```bash
docker compose up -d
```

3. Verify all services are running:
```bash
docker compose ps
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api/devices

5. View logs:
```bash
docker compose logs -f
```

## Production Deployment

### Security Considerations

Before deploying to production:

1. **Change the SECRET_KEY**:
```bash
export SECRET_KEY=$(openssl rand -hex 32)
```

2. **Update database credentials** in docker-compose.yml:
```yaml
environment:
  POSTGRES_PASSWORD: your-secure-password
  DATABASE_URL: postgresql://netdash:your-secure-password@postgres:5432/netdash
```

3. **Enable HTTPS** using a reverse proxy (Nginx, Traefik, or Caddy)

4. **Set up firewall rules**:
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Production Docker Compose

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: netdash
      POSTGRES_USER: netdash
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    networks:
      - netdash-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      DATABASE_URL: postgresql://netdash:${DB_PASSWORD}@postgres:5432/netdash
      FLASK_ENV: production
      SECRET_KEY: ${SECRET_KEY}
      PORT: 5000
    depends_on:
      - postgres
    networks:
      - netdash-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - backend
    networks:
      - netdash-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - netdash-network

volumes:
  postgres_data:

networks:
  netdash-network:
    driver: bridge
```

### Using the Production Configuration

```bash
# Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -hex 16)

# Start services
docker compose -f docker-compose.prod.yml up -d

# Monitor
docker compose -f docker-compose.prod.yml logs -f
```

## Cloud Deployment

### AWS EC2

1. Launch an EC2 instance (t2.medium or larger recommended)
2. Install Docker and Docker Compose
3. Configure security groups (ports 80, 443)
4. Deploy using Docker Compose
5. (Optional) Set up RDS for PostgreSQL

### DigitalOcean Droplet

1. Create a Droplet (2GB RAM minimum)
2. Use the Docker One-Click App
3. Clone and deploy NetDash
4. Configure a domain and SSL with Let's Encrypt

### Kubernetes

Example Kubernetes deployment:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: netdash-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: netdash-backend
  template:
    metadata:
      labels:
        app: netdash-backend
    spec:
      containers:
      - name: backend
        image: netdash-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: netdash-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: netdash-backend-service
spec:
  selector:
    app: netdash-backend
  ports:
  - port: 5000
    targetPort: 5000
  type: LoadBalancer
```

Deploy with:
```bash
kubectl apply -f k8s/
```

## Local Development

### Backend Development

1. Set up Python environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the backend:
```bash
python app.py
```

Backend will be available at http://localhost:5000

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### Database Setup (Local)

If running without Docker:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE netdash;
CREATE USER netdash WITH PASSWORD 'netdash';
GRANT ALL PRIVILEGES ON DATABASE netdash TO netdash;
\q
```

## Environment Variables

### Backend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `postgresql://netdash:netdash@localhost:5432/netdash` |
| FLASK_ENV | Environment (development/production) | `development` |
| SECRET_KEY | Flask secret key for sessions | Random on startup |
| PORT | Backend port | `5000` |

### Frontend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | `http://localhost:5000/api` |
| VITE_SOCKET_URL | WebSocket server URL | `http://localhost:5000` |

## Database Management

### Backup Database

```bash
# With Docker
docker exec netdash-db pg_dump -U netdash netdash > backup-$(date +%Y%m%d).sql

# Without Docker
pg_dump -U netdash netdash > backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
# With Docker
cat backup.sql | docker exec -i netdash-db psql -U netdash netdash

# Without Docker
psql -U netdash netdash < backup.sql
```

### Database Migrations

Currently, the application creates tables automatically on startup. For production, consider using a migration tool like Alembic:

```bash
pip install alembic
alembic init migrations
# Edit alembic.ini and migrations/env.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Monitoring and Logging

### View Docker Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100
```

### Health Checks

Check if services are running:

```bash
# Backend health
curl http://localhost:5000/api/devices

# Database health
docker exec netdash-db pg_isready -U netdash
```

### Performance Monitoring

Consider adding monitoring tools:
- Prometheus for metrics
- Grafana for visualization
- ELK stack for log aggregation

## Troubleshooting

### Backend Won't Start

**Symptom**: Backend container exits immediately

**Solutions**:
1. Check logs: `docker compose logs backend`
2. Verify database connection
3. Check if port 5000 is available
4. Ensure .env file is properly configured

### Frontend Can't Connect to Backend

**Symptom**: "Network Error" in browser console

**Solutions**:
1. Verify backend is running: `curl http://localhost:5000/api/devices`
2. Check CORS configuration in backend
3. Verify WebSocket connection is not blocked
4. Check browser console for specific errors

### Database Connection Failed

**Symptom**: "Connection refused" or "Could not connect to database"

**Solutions**:
1. Wait for database to be ready (use health checks)
2. Verify credentials in environment variables
3. Check if PostgreSQL port 5432 is accessible
4. Ensure database container is running: `docker compose ps`

### High Memory Usage

**Solutions**:
1. Limit container resources in docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```
2. Optimize queries and reduce polling frequency
3. Add connection pooling

### Devices Not Updating

**Symptom**: Device status doesn't change

**Solutions**:
1. Verify devices have correct IP addresses
2. Check if ICMP (ping) is allowed in network
3. Review monitoring service logs
4. Ensure WebSocket connection is established

## Scaling

### Horizontal Scaling

To scale the backend:

```bash
docker compose up -d --scale backend=3
```

Add a load balancer (Nginx example):

```nginx
upstream backend {
    server backend_1:5000;
    server backend_2:5000;
    server backend_3:5000;
}
```

### Database Optimization

1. Add indexes for frequently queried fields
2. Implement connection pooling
3. Consider read replicas for high traffic

## Security Best Practices

1. **Use HTTPS in production**
2. **Implement authentication** (JWT recommended)
3. **Sanitize all inputs**
4. **Use environment variables** for secrets
5. **Regular security updates**: `docker compose pull && docker compose up -d`
6. **Limit network exposure**: Use private networks
7. **Enable audit logging**
8. **Regular backups**: Automate database backups

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Clean Up

```bash
# Remove stopped containers
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Remove unused images
docker image prune -a
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/BennyGaming635/netdash/issues
- Documentation: README.md

## License

MIT License - See LICENSE file for details
