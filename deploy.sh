#!/bin/bash

# AgriLink Production Deployment Script
# This script deploys the AgriLink platform to production

set -e

echo "🚀 AgriLink Production Deployment"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Configuration
PRODUCTION_DOMAIN=${1:-"your-domain.com"}
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

echo "📋 Configuration:"
echo "   Domain: $PRODUCTION_DOMAIN"
echo "   Database Password: $DB_PASSWORD"
echo "   Secret Key: $SECRET_KEY"

# Create production environment files
echo "📁 Creating production environment files..."

# Backend .env
cat > backend/.env << EOF
# Production Environment Variables
DATABASE_URL=postgresql+psycopg2://agrilink_user:${DB_PASSWORD}@db:5432/agrilink
SECRET_KEY=${SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=120
PSP_MOCK_SECRET=prod-psp-secret-$(openssl rand -hex 16)
FILE_STORAGE_DIR=/app/storage
ALLOWED_ORIGINS=["https://${PRODUCTION_DOMAIN}"]
EOF

# Frontend .env.local
cat > frontend/.env.local << EOF
# Production Environment Variables
NEXT_PUBLIC_API_BASE=https://${PRODUCTION_DOMAIN}
EOF

# Update docker-compose.yml for production
echo "🔧 Updating Docker Compose for production..."
sed -i.bak "s/localhost/${PRODUCTION_DOMAIN}/g" docker-compose.yml

# Create production Nginx configuration
echo "🌐 Creating production Nginx configuration..."
cat > nginx/nginx.prod.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/s;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    server {
        listen 80;
        server_name ${PRODUCTION_DOMAIN};
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ${PRODUCTION_DOMAIN};

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/${PRODUCTION_DOMAIN}/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/${PRODUCTION_DOMAIN}/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' https: data: blob: 'unsafe-inline'" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend routes
        location / {
            limit_req zone=general burst=20 nodelay;
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' 'https://${PRODUCTION_DOMAIN}' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            
            if (\$request_method = 'OPTIONS') {
                add_header 'Access-Control-Allow-Origin' 'https://${PRODUCTION_DOMAIN}';
                add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
                add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Content-Type' 'text/plain; charset=utf-8';
                add_header 'Content-Length' 0;
                return 204;
            }
        }

        # Static files (KYC documents)
        location /storage/ {
            limit_req zone=general burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Create SSL directory
mkdir -p nginx/ssl

# Create production docker-compose override
echo "🐳 Creating production Docker Compose override..."
cat > docker-compose.prod.yml << EOF
version: '3.9'

services:
  nginx:
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    environment:
      - DOMAIN=${PRODUCTION_DOMAIN}

  backend:
    environment:
      - DATABASE_URL=postgresql+psycopg2://agrilink_user:${DB_PASSWORD}@db:5432/agrilink
      - SECRET_KEY=${SECRET_KEY}
      - ACCESS_TOKEN_EXPIRE_MINUTES=120
      - PSP_MOCK_SECRET=prod-psp-secret-$(openssl rand -hex 16)
      - FILE_STORAGE_DIR=/app/storage
      - ALLOWED_ORIGINS=["https://${PRODUCTION_DOMAIN}"]

  frontend:
    environment:
      - NEXT_PUBLIC_API_BASE=https://${PRODUCTION_DOMAIN}

volumes:
  postgres_data:
    driver: local
EOF

echo ""
echo "✅ Production configuration created successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Update your DNS to point ${PRODUCTION_DOMAIN} to this server"
echo "2. Obtain SSL certificate:"
echo "   sudo certbot certonly --standalone -d ${PRODUCTION_DOMAIN}"
echo "3. Deploy the platform:"
echo "   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
echo "4. Set up admin user:"
echo "   python3 scripts/setup_admin.py"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "🔐 Production credentials:"
echo "   Database Password: ${DB_PASSWORD}"
echo "   Secret Key: ${SECRET_KEY}"
echo ""
echo "⚠️  IMPORTANT: Store these credentials securely!"
