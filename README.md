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
```

**Note:** The build script expects to find the `cgm-remote-monitor` repository
at `../cgm-remote-monitor/` (sibling directory). See build.py to customize this path.

## Build Output

Each release zip contains:

```
cgm-remote-monitor-vX.Y.Z.zip
├── docker-compose.yml       # Production docker-compose
├── cgm-remote-monitor.tar  # Docker image export
├── ENVIRONMENT.md          # Environment variable docs
├── .env.example            # Environment template
├── README.md               # Deployment instructions
└── nginx-template.conf     # Nginx reverse proxy template
```

## Prerequisites

- Python 3.8+
- Docker with buildx
- Git
- Sufficient disk space (Docker image ~500MB)

### Required Repositories

This build system requires two repositories:

1. **cgm-remote-monitor** - The upstream Nightscout source code
   - Clone from: <https://github.com/nightscout/cgm-remote-monitor.git>
   - Build script looks for it at: `../cgm-remote-monitor/` (relative to this repo)

2. **nightscout-builder** (this repository) - Build scripts and templates

## Usage

### 1. Set Up Upstream Repository

```bash
# Clone the upstream repository (one-time)
git clone https://github.com/nightscout/cgm-remote-monitor.git

# Enter the upstream repository
cd cgm-remote-monitor

# Add upstream remote to track official releases
git remote add upstream https://github.com/nightscout/cgm-remote-monitor.git
git fetch upstream --tags
```

### 2. Select Version

```bash
# In cgm-remote-monitor repository
cd cgm-remote-monitor

# See available versions
git tag -l | grep -E '^[0-9]+\.[0-9]+' | sort -V

# Checkout desired version
git checkout tags/15.0.7
```

### 3. Build Release

```bash
# In nightscout-builder repository
cd nightscout-builder

# Run build script
python3 build.py
```

The script will:

1. Read the upstream source from `cgm-remote-monitor/` directory
2. Extract version from git tag
3. Build Docker image from official Dockerfile
4. Export image as tarball
5. Package into zip file in `released/`

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

Since this setup exposes Nightscout directly on a port, use nginx as reverse proxy
for HTTPS termination.

The release includes `nginx-template.conf` - a production-tested configuration
with SSL, security headers, and proxy settings. It defaults to `localhost:1337`.

**To use:**

1. Copy `nginx-template.conf` to your nginx config directory
2. Customize: `server_name`, SSL certificate paths, and upstream URL if needed
3. Reload nginx: `sudo nginx -s reload`

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
