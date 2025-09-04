DOMAIN = "gardena_smart_by_rk"
PLATFORMS = ["sensor", "device_tracker", "switch"]
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_REDIRECT_URI = "redirect_uri"
CONF_DEVICE_NAME = "device_name"
CONF_ROUTE_WINDOW_HOURS = "route_window_hours"

# OAuth2 (Husqvarna Group Authentication API v2)
AUTH_BASE = "https://api.authentication.husqvarnagroup.dev/v2/oauth2"
AUTH_AUTHORIZE_URL = f"{AUTH_BASE}/authorize"
AUTH_TOKEN_URL = f"{AUTH_BASE}/token"

# Smart System API (HTTP) + WebSocket
API_BASE = "https://api.smart.gardena.dev/v1"
WS_URL = "wss://ws.smart.gardena.dev/v1/stream"

# Scopes
SCOPES = ["iam:read", "smart:read", "smart:write"]

ATTRIBUTION = "Data provided by Husqvarna Group / Gardena"
