# CGM-Remote-Monitor Deployment

This package contains everything needed to run CGM-Remote-Monitor (Nightscout).

## Prerequisites

- Docker and Docker Compose installed
- At least 1GB free disk space
- Port 1337 available (or configure custom port in .env)

## Quick Start

1. **Configure environment:**

   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

2. **Load Docker image:**

   ```bash
   docker load < cgm-remote-monitor.tar
   ```

3. **Start services:**

   ```bash
   docker compose up -d
   ```

4. **Access Nightscout:**
   Open <http://localhost:1337> in your browser

## Configuration

Edit `.env` file to customize:

- `API_SECRET` - Required: Admin passphrase (12+ characters)
- `NS_PORT` - Port to expose Nightscout (default: 1337)
- `NS_TZ` - Timezone (default: Etc/UTC)
- `NS_DISPLAY_UNITS` - mg/dl or mmol/L
- `NS_ENABLE` - Enabled plugins

See `ENVIRONMENT.md` for complete documentation.

## Managing Services

```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart
docker compose restart

# Check status
docker compose ps
```

## Data Persistence

MongoDB data is stored in `./mongo-data/` directory (relative to docker-compose.yml).

## Troubleshooting

**Containers won't start:**

```bash
docker compose logs -f nightscout
docker compose logs -f mongo
```

**Cannot connect:**

- Check if port is in use: `netstat -tlnp | grep 1337`
- Verify `.env` file exists and has `API_SECRET` set
- Check MongoDB is healthy: `docker compose ps`

**Port already in use:**
Change `NS_PORT` in `.env` to use a different port.

## Updating

To update to a new version:

1. Download new release zip
2. Extract and replace files
3. Run: `docker compose down && docker load < cgm-remote-monitor.tar && docker compose up -d`

## Security

- Never share your `API_SECRET`
- Use HTTPS in production (via reverse proxy)
- Keep `.env` file secure (not committed to git)

## Documentation

- `ENVIRONMENT.md` - Complete environment variable reference
- `.env.example` - Configuration template with all options

## Support

- Nightscout documentation: <https://nightscout.github.io/>
- Upstream repository: <https://github.com/nightscout/cgm-remote-monitor>
