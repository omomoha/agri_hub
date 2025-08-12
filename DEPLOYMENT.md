# 🚀 AgriLink Deployment Guide

This guide provides step-by-step instructions for deploying the AgriLink platform to production.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Docker & Docker Compose**: Installed and running
- **Git**: For cloning the repository
- **SSL Certificates**: For HTTPS support (optional but recommended)
- **Domain Name**: For production deployment (optional)

## 🏗️ Repository Setup

The AgriLink project is now available on GitHub:

```bash
# Clone the repository
git clone https://github.com/omomoha/agri_hub.git
cd agri_hub

# Checkout the main branch
git checkout main
```

## 🐳 Quick Start (Development)

For development and testing:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Nginx: http://localhost:80

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Run the production deployment script
./deploy-prod.sh
```

The script will:
- Check Docker and Docker Compose availability
- Create production environment file (`.env.prod`)
- Set up SSL certificates directory
- Configure monitoring
- Deploy all services
- Perform health checks

### 2. Manual Environment Configuration

If you prefer manual setup:

```bash
# Copy and edit environment file
cp .env.prod.example .env.prod
nano .env.prod
```

**Required Environment Variables:**
```bash
# Database
DB_PASSWORD=your_secure_db_password_here

# Security
SECRET_KEY=your_super_secret_key_here
PSP_MOCK_SECRET=your_psp_secret_here

# Frontend
NEXT_PUBLIC_API_BASE=https://your-domain.com

# General
ENVIRONMENT=production
```

### 3. SSL Certificates

For HTTPS support, add your SSL certificates:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Add your certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem
```

**Self-signed certificates (testing only):**
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

### 4. Deploy Services

```bash
# Start production services
docker compose -f docker-compose.prod.yml up -d --build

# Check service status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## 📊 Monitoring & Health Checks

### Health Endpoints

The application provides several health check endpoints:

- **`/health`**: General health status (for load balancers)
- **`/health/ready`**: Readiness probe (for Kubernetes)
- **`/health/live`**: Liveness probe (for application monitoring)

### Prometheus Monitoring

Access Prometheus metrics at:
- **Prometheus**: http://localhost:9090

### Service Health

Check individual service health:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Nginx health
curl http://localhost/health
```

## 🔧 Management Commands

### Service Management

```bash
# Start specific service
docker compose -f docker-compose.prod.yml up -d backend

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down

# View service status
docker compose -f docker-compose.prod.yml ps
```

### Database Operations

```bash
# Access database
docker compose -f docker-compose.prod.yml exec db psql -U agrilink_user -d agri_hub

# Backup database
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U agrilink_user agri_hub > backup.sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T db psql -U agrilink_user -d agri_hub < backup.sql
```

### Logs and Debugging

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs

# View specific service logs
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs nginx

# Follow logs in real-time
docker compose -f docker-compose.prod.yml logs -f
```

## 🔒 Security Considerations

### Production Security

1. **Environment Variables**: Never commit sensitive data to git
2. **SSL Certificates**: Use valid SSL certificates for production
3. **Database Passwords**: Use strong, unique passwords
4. **Firewall**: Configure firewall rules appropriately
5. **Updates**: Regularly update dependencies and base images

### Security Headers

The production Nginx configuration includes:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Content-Security-Policy

## 📈 Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use external load balancer (HAProxy, Nginx)
2. **Multiple Backend Instances**: Scale backend services
3. **Database Clustering**: Consider PostgreSQL clustering
4. **Redis Clustering**: For session and cache distribution

### Resource Limits

Monitor resource usage:

```bash
# View resource usage
docker stats

# Set resource limits in docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   lsof -i :8000
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker compose -f docker-compose.prod.yml logs db
   ```

3. **Service Health Issues**
   ```bash
   # Check service health
   curl http://localhost:8000/health
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG

# Restart services
docker compose -f docker-compose.prod.yml restart
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **GitHub Repository**: https://github.com/omomoha/agri_hub
- **Docker Documentation**: https://docs.docker.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs

## 🆘 Support

For deployment issues:

1. Check the troubleshooting section above
2. Review service logs
3. Verify environment configuration
4. Create an issue on GitHub
5. Check the API documentation

---

**Happy Deploying! 🚀**
