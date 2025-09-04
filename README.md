# Gardena Smart by RK

Home Assistant custom integration (API v2 auth, WebSocket updates) for Gardena Smart System devices.

## Features
- OAuth2 (Husqvarna Group Authentication API v2)
- Live updates over WebSocket
- Device Tracker for mower GPS (`device_tracker.sileno`)
- Route sensor with GeoJSON (`sensor.sileno_route`) for track rendering
- Switches for mower control: start / park / stop
- Works with standard **Map** card (history track) or `custom:map-track-card` (gradient route)

## Setup
1. Create an app at Husqvarna Developer Portal and enable **Authentication API** and **GARDENA smart system API**.
2. Use the following redirect_uri
   If "my" component is enabled: `https://my.home-assistant.io/redirect/oauth`
   With HA cloud configured: `https://<cloud-remote-url>/auth/external/callback`
   Without HA cloud configured: `http://<local-ip>:<port>/auth/external/callback`
3. In Home Assistant → Settings → Integrations → *Add Integration* → **Gardena Smart by RK** → enter your **Client ID** and **Client Secret**.

## Lovelace (gradient track example)
```yaml
type: custom:map-track-card
entities:
  - device_tracker.sileno
hours_to_show: 12
title: "Sileno Route"
gradient:
  enabled: true
  colors:
    - color: "#ff0000"
      value: 0
    - color: "#ffff00"
      value: 0.5
    - color: "#00ff00"
      value: 1
```

## Notes
- API base: `{'API_BASE': 'https://api.smart.gardena.dev/v1', 'WS_URL': 'wss://ws.smart.gardena.dev/v1/stream'}`
- If the endpoints change, edit `const.py` (AUTH/WS/REST).
- This package was generated 2025-09-04T17:46:49.713001Z.
