#!/bin/sh
# Render the Prometheus config from the template, then exec Prometheus.
#
# Why sed and not envsubst: the prom/prometheus base image is busybox-based and
# ships sed but NOT gettext's envsubst, so sed keeps the image dependency-free.
# Why render at start-up instead of baking a static config: the same image must
# run in local, on-prem and cloud, where only the backend address/scheme differ.
# Passing those as env vars means one image and no per-environment rebuild.
set -eu

: "${BACKEND_TARGET:?BACKEND_TARGET must be set (e.g. backend:8000 local/on-prem, <fqdn>:443 cloud)}"
SCRAPE_SCHEME="${SCRAPE_SCHEME:-http}"
RETENTION="${PROMETHEUS_RETENTION:-15d}"

TEMPLATE=/etc/prometheus/prometheus.tmpl.yml
RENDERED=/etc/prometheus/prometheus.yml

# Substitute the two placeholders. '|' delimiter avoids clashing with the
# '/' and ':' that appear in hostnames and schemes.
sed -e "s|__BACKEND_TARGET__|${BACKEND_TARGET}|g" \
    -e "s|__SCRAPE_SCHEME__|${SCRAPE_SCHEME}|g" \
    "${TEMPLATE}" > "${RENDERED}"

echo "Rendered Prometheus config (target=${BACKEND_TARGET}, scheme=${SCRAPE_SCHEME}):"
# Substitute the scrape credential, or remove the authorization lines
# entirely. Leaving an unsubstituted placeholder would make Prometheus send
# "Bearer __METRICS_TOKEN__" and every scrape would 401.
if [ -n "${METRICS_TOKEN:-}" ]; then
	sed -i "s|__METRICS_TOKEN__|${METRICS_TOKEN}|" "${RENDERED}"
	echo "Prometheus: scraping /metrics with a bearer token."
else
	sed -i -e '/authorization:/d' -e '/type: Bearer/d' -e '/credentials: "__METRICS_TOKEN__"/d' "${RENDERED}"
	echo "Prometheus: METRICS_TOKEN unset, scraping without credentials."
fi

cat "${RENDERED}"

# --web.enable-lifecycle is deliberately NOT set. It enables POST /-/reload,
# which nothing here uses, but it also enables POST /-/quit -- unauthenticated
# remote shutdown of the monitoring stack on whatever port this is published
# on. The config is rendered at start-up above, so a reload means restarting
# the container, which is the same operation for our purposes.
exec /bin/prometheus \
  --config.file="${RENDERED}" \
  --storage.tsdb.path=/prometheus \
  --storage.tsdb.retention.time="${RETENTION}" \
  --web.listen-address=0.0.0.0:9090
