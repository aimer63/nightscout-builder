# Environment Variables Reference

This document describes all environment variables available for CGM-Remote-Monitor configuration.

## Quick Start

Minimum required variables:
- `API_SECRET` (12+ characters)
- `MONGO_CONNECTION` (defaults to internal mongo container)

## Required Variables

| Variable | Description | Example |
| -------- | ----------- | ------- |
| `API_SECRET` | Admin passphrase (min 12 chars) | `my-secret-passphrase` |

## Database

Uses MongoDB 7.0 (container image `mongo:7.0`).

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `MONGO_CONNECTION` | `mongodb://mongo:27017/nightscout` | MongoDB connection URI |
| `NS_MONGO_DATA_DIR` | `./mongo-data` | Host path for MongoDB data |

## Server

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NS_PORT` | `1337` | Host port to expose Nightscout |
| `NS_TZ` | `Etc/UTC` | Timezone for display |
| `INSECURE_USE_HTTP` | `true` | Allow HTTP (nginx handles HTTPS) |

## Features

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NS_ENABLE` | `careportal rawbg iob` | Space-separated plugin list |
| `NS_DISABLE` | (none) | Plugins to disable |
| `NS_AUTH_DEFAULT_ROLES` | `denied` | Default access: readable, denied, status-only |
| `NS_DISPLAY_UNITS` | `mg/dl` | mg/dl or mmol/L |

## Alarms

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NS_BG_HIGH` | `260` | Urgent high threshold |
| `NS_BG_TARGET_TOP` | `180` | Target range upper limit |
| `NS_BG_TARGET_BOTTOM` | `80` | Target range lower limit |
| `NS_BG_LOW` | `55` | Urgent low threshold |
| `NS_ALARM_*` | `on` | Toggle specific alarms |

## Display

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NS_TIME_FORMAT` | `24` | 12 or 24 hour format |
| `NS_LANGUAGE` | `en` | Language code |
| `NS_CUSTOM_TITLE` | `Nightscout` | Site title |
| `NS_THEME` | `colors` | colors, default, colorblindfriendly |

## Plugin-Specific Variables

### Bridge (Dexcom Share)

| Variable | Description |
| -------- | ----------- |
| `BRIDGE_USER_NAME` | Dexcom username |
| `BRIDGE_PASSWORD` | Dexcom password |
| `BRIDGE_SERVER` | Blank for US, 'EU' for Europe |

### Pushover

| Variable | Description |
| -------- | ----------- |
| `PUSHOVER_API_TOKEN` | Pushover API token |
| `PUSHOVER_USER_KEY` | Pushover user key |

### Basal

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `BASAL_RENDER` | `none` | none, default, icicle |

## Full Reference

For complete documentation of all environment variables, see:
https://github.com/nightscout/cgm-remote-monitor/blob/master/README.md
