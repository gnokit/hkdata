"""Shared constants for hkdata."""

API_BASE_URL = "https://data.gov.hk/en-data/api/3/action/"

# Browser-like User-Agent to avoid 403s from endpoints such as Censtatd, LandsD
# and the map APIs that reject requests without a recognizable agent string.
# Every fetch path (info, test, catalog crawl, embeddings) must use this — some
# endpoints 403 the bare Python urllib agent even though curl works.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
