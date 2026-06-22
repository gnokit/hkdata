"""Shared constants for hkdata."""

API_BASE_URL = "https://data.gov.hk/en-data/api/3/action/"

# Browser-like User-Agent to avoid 403s from endpoints such as Censtatd
# that reject requests without a recognizable agent string.
USER_AGENT = "curl/8.0"
