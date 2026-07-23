# Docker Self-Hosting Plan for CGM-Remote-Monitor

This document describes the strategy for self-hosting CGM-Remote-Monitor (Nightscout)
using Docker while maintaining synchronization with the official upstream repository.

## Goals

- Keep repository synchronized with `nightscout/cgm-remote-monitor` upstream
- Build Docker deployment artifacts without modifying source code
- Maintain clean separation between upstream code and custom configuration
- Enable easy updates when new versions are released

## Repository Structure

```
cgm-remote-monitor/
├── (upstream code - untouched)
└── nightscout-builder/
    ├── build.py      # Python build script
    ├── docker-compose.yml    # Docker compose template
    ├── .env.example         # Environment template
    ├── ENVIRONMENT.md       # Environment documentation
    ├── README.md            # Build instructions
    ├── doc/
    │   └── docker-hosting.md # This document
    └── released/            # Build output (zip files only)
        └── cgm-remote-monitor-v15.0.7.zip
```

### Release Zip Contents

Each `cgm-remote-monitor-vX.Y.Z.zip` contains:

```
cgm-remote-monitor-vX.Y.Z.zip
├── docker-compose.yml       # Production docker-compose
├── cgm-remote-monitor.tar  # Docker image export
├── ENVIRONMENT.md          # Environment variable docs
└── .env.example            # Environment template
```

## Synchronization Strategy

### Upstream Remote Setup

Add official repository as upstream remote:

```bash
git remote add upstream https://github.com/nightscout/cgm-remote-monitor.git
git fetch upstream
```

### Build Workflow

When new version is released:

```bash
# In cgm-remote-monitor repository
cd cgm-remote-monitor
git fetch upstream --tags

# Checkout new release tag
git checkout tags/15.0.7  # Replace with latest tag

# Build release artifacts from nightscout-builder
cd ../nightscout-builder
python3 build.py

# Result: released/cgm-remote-monitor-v15.0.7.zip
```

## Build System

### Build Script (`build.py`)

The Python build script:

1. Verifies clean git state at a version tag
2. Builds Docker image using official Dockerfile
3. Exports image as `cgm-remote-monitor.tar`
4. Packages with docker-compose.yml and env templates
5. Creates versioned zip in `nightscout-builder/released/`

### Usage

```bash
# Build from current checkout (must be on a version tag)
python3 build.py

# Build with verbose output
python3 build.py --verbose
```

### Prerequisites

- Python 3.8+
- Docker with sufficient disk space (~500MB for image)
- Clean git checkout at a version tag

## Docker Compose Configuration

### Production Compose File

The `nightscout-builder/docker-compose.yml` template:

- Removes Traefik (using nginx instead)
- Exposes port directly (configurable via `.env`)
- Externalizes all configuration to environment variables
- Uses MongoDB 7.0 (instead of 4.4 in official)
- Includes health checks for MongoDB

### Key Differences from Official

| Aspect | Official | Self-Host |
| ------ | -------- | --------- |
| Reverse Proxy | Traefik | Nginx (external) |
| Port Exposure | 80/443 via Traefik | 1337 direct (or custom) |
| TLS | Traefik manages | Nginx manages |
| MongoDB | 4.4 | 7.0 |

## Configuration Management

### Environment Variables

The `nightscout-builder/.env.example` template includes:

- Required: `API_SECRET` (12+ characters)
- Database: `MONGO_CONNECTION`, `NS_MONGO_DATA_DIR`
- Server: `NS_PORT`, `NS_TZ`
- Features: `NS_ENABLE`, `NS_AUTH_DEFAULT_ROLES`, `NS_DISPLAY_UNITS`
- Alarms: `NS_BG_HIGH`, `NS_BG_TARGET_TOP`, etc.
- Display: `NS_TIME_FORMAT`, `NS_LANGUAGE`, `NS_CUSTOM_TITLE`

See `nightscout-builder/ENVIRONMENT.md` for complete documentation.

### Nginx Configuration

Example nginx reverse proxy config:

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

## Deployment Workflow

### Initial Setup

```bash
# 1. Clone upstream repo
git clone https://github.com/nightscout/cgm-remote-monitor.git
cd cgm-remote-monitor
git remote add upstream https://github.com/nightscout/cgm-remote-monitor.git

# 2. Checkout desired version
git checkout tags/15.0.7

# 3. Build release from nightscout-builder
cd ../nightscout-builder
python3 build.py

# 4. Copy release to deployment location
cp released/cgm-remote-monitor-v15.0.7.zip /opt/nightscout/
cd /opt/nightscout
unzip cgm-remote-monitor-v15.0.7.zip

# 5. Configure
cp .env.example .env
nano .env  # Edit with your settings

# 6. Deploy
docker load < cgm-remote-monitor.tar
docker compose up -d
```

### Update to New Version

```bash
# 1. In cgm-remote-monitor repository, fetch upstream tags
cd cgm-remote-monitor
git fetch upstream --tags

# 2. Checkout new version
git checkout tags/15.0.8  # Latest version

# 3. Rebuild from nightscout-builder
cd ../nightscout-builder
python3 build.py

# 4. Deploy update
cd /opt/nightscout
docker compose down
cp /path/to/nightscout-builder/released/cgm-remote-monitor-v15.0.8.zip .
rm -f cgm-remote-monitor-v15.0.7.zip  # Cleanup old version
unzip -o cgm-remote-monitor-v15.0.8.zip
docker load < cgm-remote-monitor.tar
docker compose up -d
```

## Version Tracking

### Release Tags

- `15.0.7` - Official upstream tag (lightweight)
- Build zips named: `cgm-remote-monitor-v15.0.7.zip`

### Build Artifacts

Store only in `nightscout-builder/released/`:

- `cgm-remote-monitor-v15.0.7.zip` - Complete deployment package
- No other files in released/ (only versioned zips)

## Rollback Strategy

If new version has issues:

```bash
cd /opt/nightscout
docker compose down
unzip -o cgm-remote-monitor-v15.0.7.zip  # Previous version
docker load < cgm-remote-monitor.tar
docker compose up -d
```

## Security Considerations

- Never commit `.env` file with real secrets
- Keep `API_SECRET` strong (12+ characters)
- Use HTTPS in production (via nginx)
- Regularly update to latest upstream version
- Monitor upstream for security advisories
- MongoDB data directory should have proper permissions

## File Reference

### Build Files (in `nightscout-builder/`)

| File | Purpose |
| ---- | ------- |
| `build.py` | Main build script |
| `docker-compose.yml` | Docker compose template |
| `.env.example` | Environment variable template |
| `ENVIRONMENT.md` | Environment documentation |
| `README.md` | Build and deployment instructions |

### Release Output (in `nightscout-builder/released/`)

| File | Contents |
| ---- | -------- |
| `cgm-remote-monitor-vX.Y.Z.zip` | Deployment package with image and configs |

### Zip Contents

| File | Description |
| ---- | ----------- |
| `docker-compose.yml` | Production Docker Compose config |
| `cgm-remote-monitor.tar` | Exported Docker image |
| `.env.example` | Environment variable template |
| `ENVIRONMENT.md` | Environment variable documentation |

## References

- **CGM-Remote-Monitor Repository**: <https://github.com/nightscout/cgm-remote-monitor>
- **Nightscout Documentation**: <https://nightscout.github.io/>

## Next Steps

1. ✅ Create `build.py`
2. ✅ Create `nightscout-builder/docker-compose.yml`
3. ✅ Create `nightscout-builder/.env.example`
4. ✅ Create `nightscout-builder/ENVIRONMENT.md`
5. ✅ Create `nightscout-builder/README.md`
6. ✅ Create `nightscout-builder/doc/docker-hosting.md`
7. Test build process with current version
8. Deploy and verify
