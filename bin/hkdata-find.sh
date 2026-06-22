#!/bin/bash
set -e

# Parse arguments
PAGE=1
KEYWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --page|-p)
            PAGE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: hkdata-find.sh <keyword> [--page N]"
            echo ""
            echo "Options:"
            echo "  --page, -p N    Show page N of results (default: 1, 50 results per page)"
            echo ""
            echo "Examples:"
            echo "  hkdata-find.sh transport"
            echo "  hkdata-find.sh transport --page 2"
            exit 0
            ;;
        *)
            if [ -z "$KEYWORD" ]; then
                KEYWORD="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$KEYWORD" ]; then
    echo "Usage: hkdata-find.sh <keyword> [--page N]"
    echo "Example: hkdata-find.sh transport"
    exit 1
fi

# Calculate offset based on page number
ROWS=50
OFFSET=$(( (PAGE - 1) * ROWS ))

API_URL="https://data.gov.hk/en-data/api/3/action/package_search?q=${KEYWORD}&rows=${ROWS}&start=${OFFSET}"

echo "Searching data.gov.hk for: $KEYWORD (page $PAGE)"
curl -s "$API_URL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('result', {})
datasets = results.get('results', [])
total_count = results.get('count', 0)

if not datasets:
    print('No matching datasets found.')
    sys.exit(0)

for ds in datasets:
    ds_id = ds.get('name', 'N/A')
    title = ds.get('title', 'N/A')
    notes = ds.get('notes', 'N/A')
    print(f\"{ds_id} | {title} | {notes}\")

# Show pagination info
total_pages = (total_count + 49) // 50  # Ceiling division
start_result = $OFFSET + 1
end_result = $OFFSET + len(datasets)

if total_count > 0:
    print(f\"\\nShowing results {start_result}-{end_result} of {total_count} (page $PAGE of {total_pages})\")
    if total_pages > 1:
        if $PAGE < total_pages:
            print(f\"Use --page {int($PAGE) + 1} to see more results\")
        if $PAGE > 1:
            print(f\"Use --page {int($PAGE) - 1} to see previous results\")
"
