# Deployment Guide

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (for production)
- Redis 6+ (for caching and task queue)
- API keys for:
  - Blockchain explorers (Etherscan, BSCScan, etc.)
  - Social media platforms (Twitter, Reddit)
  - Telegram/Discord bots

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/k2pitel/Crypto-Risk-Alert.git
cd Crypto-Risk-Alert
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example config
cp config/config.example.yml config/config.yml

# Edit config with your API keys
nano config/config.yml
```

### 5. Run Services

#### Start Main System
```bash
python src/main.py
```

#### Start API Server
```bash
python src/api/app.py
# Or with uvicorn
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Start Telegram Bot
```bash
python src/bots/telegram_bot.py
```

#### Start Discord Bot
```bash
python src/bots/discord_bot.py
```

## Docker Deployment

### 1. Build Docker Image
```bash
docker build -t crypto-risk-alert .
```

### 2. Run with Docker Compose
```bash
docker-compose up -d
```

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/crypto_risk
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config

  telegram-bot:
    build: .
    command: python src/bots/telegram_bot.py
    depends_on:
      - api
    volumes:
      - ./config:/app/config

  discord-bot:
    build: .
    command: python src/bots/discord_bot.py
    depends_on:
      - api
    volumes:
      - ./config:/app/config

  worker:
    build: .
    command: celery -A src.tasks worker --loglevel=info
    depends_on:
      - redis
    volumes:
      - ./config:/app/config

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=crypto_risk
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl create namespace crypto-risk-alert
```

### 2. Create ConfigMap
```bash
kubectl create configmap crypto-config \
  --from-file=config/config.yml \
  -n crypto-risk-alert
```

### 3. Create Secrets
```bash
kubectl create secret generic crypto-secrets \
  --from-literal=db-password=your_password \
  --from-literal=telegram-token=your_token \
  --from-literal=discord-token=your_token \
  -n crypto-risk-alert
```

### 4. Deploy Application
```bash
kubectl apply -f k8s/deployment.yml -n crypto-risk-alert
```

### Example Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-risk-api
  namespace: crypto-risk-alert
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-risk-api
  template:
    metadata:
      labels:
        app: crypto-risk-api
    spec:
      containers:
      - name: api
        image: crypto-risk-alert:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: crypto-secrets
              key: db-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: crypto-risk-api
  namespace: crypto-risk-alert
spec:
  selector:
    app: crypto-risk-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Production Setup

### 1. Database Setup

#### PostgreSQL
```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE crypto_risk_alert;
CREATE USER crypto_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE crypto_risk_alert TO crypto_user;
```

#### Run Migrations
```bash
alembic upgrade head
```

### 2. Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. Process Management with Systemd

#### API Service
```ini
# /etc/systemd/system/crypto-risk-api.service
[Unit]
Description=Crypto Risk Alert API
After=network.target

[Service]
Type=simple
User=crypto
WorkingDirectory=/opt/crypto-risk-alert
Environment="PATH=/opt/crypto-risk-alert/venv/bin"
ExecStart=/opt/crypto-risk-alert/venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Telegram Bot Service
```ini
# /etc/systemd/system/crypto-risk-telegram.service
[Unit]
Description=Crypto Risk Alert Telegram Bot
After=network.target

[Service]
Type=simple
User=crypto
WorkingDirectory=/opt/crypto-risk-alert
Environment="PATH=/opt/crypto-risk-alert/venv/bin"
ExecStart=/opt/crypto-risk-alert/venv/bin/python src/bots/telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl start crypto-risk-api
sudo systemctl start crypto-risk-telegram
sudo systemctl enable crypto-risk-api
sudo systemctl enable crypto-risk-telegram
```

### 4. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/crypto-risk-alert
server {
    listen 80;
    server_name api.cryptoriskalert.io;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/crypto-risk-alert /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.cryptoriskalert.io
```

## Monitoring & Logging

### 1. Application Logs
```bash
# View API logs
sudo journalctl -u crypto-risk-api -f

# View Telegram bot logs
sudo journalctl -u crypto-risk-telegram -f
```

### 2. Prometheus Metrics
Add to your config:
```yaml
monitoring:
  enable_metrics: true
  prometheus_port: 9090
```

### 3. Grafana Dashboards
Import pre-built dashboards for:
- API performance
- Alert delivery rates
- Risk score distributions
- User subscriptions

## Backup & Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
pg_dump -U crypto_user crypto_risk_alert | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Configuration Backup
```bash
# Backup config files
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

## Scaling Considerations

### Horizontal Scaling
1. Use load balancer (nginx, HAProxy)
2. Deploy multiple API instances
3. Use Redis for shared state
4. Database read replicas

### Vertical Scaling
1. Increase worker threads
2. Optimize database queries
3. Implement caching strategy

## Troubleshooting

### Common Issues

#### 1. API Not Starting
```bash
# Check logs
sudo journalctl -u crypto-risk-api -n 50

# Verify config
python -c "import yaml; yaml.safe_load(open('config/config.yml'))"

# Check port availability
sudo lsof -i :8000
```

#### 2. Bot Not Responding
```bash
# Verify token
# Check network connectivity
curl https://api.telegram.org/bot<TOKEN>/getMe

# Restart service
sudo systemctl restart crypto-risk-telegram
```

#### 3. Database Connection Issues
```bash
# Test connection
psql -U crypto_user -d crypto_risk_alert -h localhost

# Check credentials in config
# Verify PostgreSQL is running
sudo systemctl status postgresql
```

## Performance Optimization

### 1. Database Indexing
```sql
CREATE INDEX idx_transfers_timestamp ON whale_transfers(timestamp);
CREATE INDEX idx_alerts_risk_level ON alerts(risk_level);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
```

### 2. Redis Caching
```python
# Cache risk assessments
redis_client.setex(f"risk:{symbol}", 300, json.dumps(assessment))
```

### 3. Rate Limiting
```python
# Implement rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Security Checklist

- [ ] API keys stored in environment variables
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Database credentials secured
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Monitoring and alerting enabled
- [ ] Backup strategy in place
- [ ] Incident response plan documented

## Update & Maintenance

### Update Application
```bash
cd /opt/crypto-risk-alert
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart crypto-risk-*
```

### Database Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
