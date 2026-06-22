#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: hkdata-info.sh <dataset-id>"
    echo "Example: hkdata-info.sh hk-td-tis_21-etakmb"
    exit 1
fi

DATASET_ID="$1"
API_URL="https://data.gov.hk/en-data/api/3/action/package_show?id=${DATASET_ID}"

echo "Fetching dataset info for: $DATASET_ID"
curl -s "$API_URL"
