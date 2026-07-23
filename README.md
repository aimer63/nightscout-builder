# CGM-Remote-Monitor Self-Host Build System

This directory contains the build system for creating Docker deployment artifacts
for CGM-Remote-Monitor (Nightscout).

## Philosophy

- **No code modifications**: Keep repository synchronized with upstream
- **Clean separation**: Build artifacts separate from source
- **Version tracking**: Clear versioning tied to upstream releases
- **Simple deployment**: Single zip file contains everything needed

## Directory Structure

```
nightscout-builder/
├── build.py               # Main build script
├── docker-compose.yml     # Docker compose template
├── .env.example          # Environment variable template
├── ENVIRONMENT.md        # Environment documentation
├── README.md             # This file
├── doc/
│   └── docker-hosting.md # High-level plan
└── released/             # Build output directory
    └── cgm-remote-monitor-v15.0.7.zip

# Assumes cgm-remote-monitor repo at:
~/devel/cgm-remote-monitor/
```

## Build Output

Each release zip contains:

```
cgm-remote-monitor-vX.Y.Z.zip
├── docker-compose.yml       # Production docker-compose
├── cgm-remote-monitor.tar  # Docker image export
├── ENVIRONMENT.md          # Environment variable docs
└── .env.example            # Environment template
```

## Prerequisites

- Python 3.8+
- Docker with buildx
- Git
- Sufficient disk space (Docker image ~500MB)

## Usage

### 1. Sync with Upstream

```bash
# Add upstream remote (one-time setup)
git remote add upstream https://github.com/nightscout/cgm-remote-monitor.git

# Fetch latest releases
git fetch upstream --tags

# See available versions
git tag -l | grep -E '^[0-9]+\.[0-9]+' | sort -V
```

### 2. Build Release

```bash
# Checkout desired version
git checkout tags/15.0.7

# Run build script
python3 build.py
```

The script will:

1. Extract version from git tag
2. Build Docker image from official Dockerfile
3. Export image as tarball
4. Package into zip file in `nightscout-builder/released/`

### 3. Deploy

```bash
# Unzip release
cd /opt/nightscout
unzip cgm-remote-monitor-v15.0.7.zip

# Configure
cp .env.example .env
nano .env  # Edit with your settings

# Load Docker image
docker load < cgm-remote-monitor.tar

# Start services
docker compose up -d
```

## Nginx Reverse Proxy

Since this setup exposes Nightscout directly on a port, use nginx as reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name nightscout.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:1337;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 80;
    server_name nightscout.example.com;
    return 301 https://$server_name$request_uri;
}
```

## Update Process

```bash
# Fetch new upstream tags
git fetch upstream --tags

# Checkout new version
git checkout tags/15.0.8

# Rebuild
python3 build.py

# Deploy new version
docker compose down
docker load < cgm-remote-monitor.tar
docker compose up -d
```

## Rollback

```bash
# If new version has issues, restore previous
docker compose down
docker load < cgm-remote-monitor-v15.0.7.tar
docker compose up -d
```

## Versioning

- Upstream tags: `15.0.7`, `15.0.8`, etc.
- Our build zips: `cgm-remote-monitor-v15.0.7.zip`
- Docker image inside: `cgm-remote-monitor:local` (tagged at build time)

## Troubleshooting

### Build fails

- Check Docker is running: `docker info`
- Check disk space: `df -h`
- Verify clean git state: `git status`

### Container won't start

- Check logs: `docker compose logs -f nightscout`
- Verify `.env` file exists and is configured
- Check MongoDB is healthy: `docker compose ps`

### Cannot connect

- Verify port not in use: `netstat -tlnp | grep 1337`
- Check firewall rules
- Verify nginx configuration if using reverse proxy

## Security Notes

- Never commit `.env` files with real secrets
- Keep `API_SECRET` strong (12+ random characters)
- Use HTTPS in production (via nginx)
- Regularly update to latest upstream version
- Monitor upstream security advisories

## Contributing

To modify build process:

1. Edit files in `nightscout-builder/` directory
2. Test build: `python3 build.py`
3. Update this README if needed

Do not modify upstream code in repository root.
