#!/bin/bash

# ============================================================================
# monitor-resources.sh - Resource monitoring for Arbitrage Tracker
# ============================================================================
# Purpose: Monitor Docker container resource usage (CPU, Memory, Disk I/O)
#          and output structured JSON for integration with monitoring systems.
#
# Exit Codes:
#   0 = OK (all containers within thresholds)
#   1 = Warning (one or more containers near or exceeding thresholds)
#   2 = Critical (one or more containers exceeding critical thresholds)
#
# Dependencies: docker, jq (optional, for parsing JSON)
#
# Usage Examples:
#   # Run and view full output
#   ./monitor-resources.sh
#
#   # Check overall status only
#   ./monitor-resources.sh | jq '.status'
#
#   # List all container names
#   ./monitor-resources.sh | jq '.containers[].name'
#
#   # Check for critical alerts
#   ./monitor-resources.sh | jq '.summary.critical'
#
#   # Get memory usage for all containers
#   ./monitor-resources.sh | jq '.containers[] | {name, memory_mb, memory_percent}'
#
#   # Check exit code in script
#   ./monitor-resources.sh > /dev/null && echo "OK" || echo "Alert"
#
# ============================================================================

set -o pipefail

# Configuration
MEMORY_WARNING_THRESHOLD=85
MEMORY_CRITICAL_THRESHOLD=95
CPU_WARNING_THRESHOLD=75

# Initialize counters
EXIT_STATUS=0
CRITICAL_COUNT=0
WARNING_COUNT=0

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "{\"error\": \"Docker not found\", \"exit_code\": 2}" >&2
    exit 2
fi

# Verify Docker daemon is running
if ! docker info &> /dev/null; then
    echo "{\"error\": \"Docker daemon not running or not accessible\", \"exit_code\": 2}" >&2
    exit 2
fi

# Get timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Extract numeric part from string (handles empty input)
parse_number() {
    local input="${1:-}"
    if [ -z "$input" ]; then
        echo "0"
        return
    fi
    echo "$input" | grep -oE '[0-9]+\.?[0-9]*' | head -1 || echo "0"
}

# Convert memory string to MB
parse_memory() {
    local str="${1:-0}"
    local num=$(parse_number "$str")

    if [ -z "$num" ] || [ "$num" = "0" ]; then
        echo "0"
        return
    fi

    # Remove decimal part for arithmetic
    local int_part="${num%.*}"

    if echo "$str" | grep -qi "GiB\|GB"; then
        echo "$((int_part * 1024))"
    elif echo "$str" | grep -qi "MiB\|MB"; then
        echo "$int_part"
    elif echo "$str" | grep -qi "KiB\|KB"; then
        echo "$((int_part / 1024))"
    else
        echo "$int_part"
    fi
}

# Convert Block I/O to MB
parse_blockio() {
    local str="${1:-0 B}"
    local num=$(parse_number "$str")

    if [ -z "$num" ] || [ "$num" = "0" ]; then
        echo "0"
        return
    fi

    local int_part="${num%.*}"

    if echo "$str" | grep -qi "KiB\|KB"; then
        echo "scale=3; $int_part / 1024" | bc 2>/dev/null || echo "0"
    elif echo "$str" | grep -qi "GiB\|GB"; then
        echo "$((int_part * 1024))"
    elif echo "$str" | grep -qi "TiB\|TB"; then
        echo "$((int_part * 1024 * 1024))"
    else
        echo "$int_part"
    fi
}

# Get all running containers
CONTAINERS=$(docker ps --format "{{.Names}}" 2>/dev/null || true)

if [ -z "$CONTAINERS" ]; then
    cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "containers": [],
  "summary": {"total_containers": 0, "critical": 0, "warnings": 0},
  "status": "ok",
  "exit_code": 0
}
EOF
    exit 0
fi

# Start JSON output
echo "{"
echo "  \"timestamp\": \"$TIMESTAMP\","
echo "  \"containers\": ["

FIRST=true

for CONTAINER in $CONTAINERS; do
    # Get resource usage with all metrics including Block I/O
    STATS=$(docker stats --no-stream "$CONTAINER" --format '{{.MemUsage}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.BlockIO}}' 2>/dev/null || true)

    if [ -z "$STATS" ]; then
        [ "$FIRST" != true ] && echo "," || true
        FIRST=false
        echo "    {\"name\": \"$CONTAINER\", \"status\": \"error\", \"error\": \"Could not get stats\"}"
        continue
    fi

    # Output container JSON with comma handling
    [ "$FIRST" != true ] && echo "," || true
    FIRST=false

    # Parse fields
    MEM_USAGE_RAW=$(echo "$STATS" | cut -f1)
    CPU=$(echo "$STATS" | cut -f2)
    MEMPERCENT=$(echo "$STATS" | cut -f3)
    BLOCKIO=$(echo "$STATS" | cut -f4)

    # Extract memory usage part (before /) and limit part (after /)
    MEM_USAGE_PART=$(echo "$MEM_USAGE_RAW" | cut -d'/' -f1)
    MEM_LIMIT_PART=$(echo "$MEM_USAGE_RAW" | cut -d'/' -f2)

    # Parse Block I/O (format: "X B / Y B" or "X / Y")
    DISK_READ_RAW=$(echo "$BLOCKIO" | cut -d'/' -f1)
    DISK_WRITE_RAW=$(echo "$BLOCKIO" | cut -d'/' -f2)

    MEM_MB=$(parse_memory "$MEM_USAGE_PART")
    LIMIT_MB=$(parse_memory "$MEM_LIMIT_PART")
    CPU_PCT=$(parse_number "$CPU")
    MEM_PCT=$(parse_number "$MEMPERCENT")
    DISK_READ_MB=$(parse_blockio "$DISK_READ_RAW")
    DISK_WRITE_MB=$(parse_blockio "$DISK_WRITE_RAW")

    # Determine status
    CONTAINER_STATUS="ok"
    MEM_PCT_INT="${MEM_PCT%.*}"

    if [ -n "$MEM_PCT_INT" ] && [ "$MEM_PCT_INT" -ge "$MEMORY_CRITICAL_THRESHOLD" ] 2>/dev/null; then
        CONTAINER_STATUS="critical"
        ((CRITICAL_COUNT++)) || true
        EXIT_STATUS=2
    elif [ -n "$MEM_PCT_INT" ] && [ "$MEM_PCT_INT" -ge "$MEMORY_WARNING_THRESHOLD" ] 2>/dev/null; then
        CONTAINER_STATUS="warning"
        ((WARNING_COUNT++)) || true
        if [ "$EXIT_STATUS" -lt 1 ]; then
            EXIT_STATUS=1
        fi
    fi

    CPU_INT="${CPU_PCT%.*}"
    if [ -n "$CPU_INT" ] && [ "$CPU_INT" -ge "$CPU_WARNING_THRESHOLD" ] 2>/dev/null; then
        if [ "$CONTAINER_STATUS" = "ok" ]; then
            CONTAINER_STATUS="warning"
            ((WARNING_COUNT++)) || true
            if [ "$EXIT_STATUS" -lt 1 ]; then
                EXIT_STATUS=1
            fi
        fi
    fi

    # Output container
    cat <<EOF_CONTAINER
    {
      "name": "$CONTAINER",
      "status": "$CONTAINER_STATUS",
      "memory_mb": $MEM_MB,
      "memory_limit_mb": $LIMIT_MB,
      "memory_percent": ${MEM_PCT_INT:-0},
      "cpu_percent": ${CPU_INT:-0},
      "disk_read_mb": ${DISK_READ_MB:-0},
      "disk_write_mb": ${DISK_WRITE_MB:-0}
    }
EOF_CONTAINER
done

echo ""
echo "  ],"

TOTAL=$(echo "$CONTAINERS" | wc -w)

echo "  \"summary\": {"
echo "    \"total_containers\": $TOTAL,"
echo "    \"critical\": ${CRITICAL_COUNT:-0},"
echo "    \"warnings\": ${WARNING_COUNT:-0}"
echo "  },"

if [ "$EXIT_STATUS" -eq 2 ]; then
    STATUS="critical"
elif [ "$EXIT_STATUS" -eq 1 ]; then
    STATUS="warning"
else
    STATUS="ok"
fi

echo "  \"status\": \"$STATUS\","
echo "  \"exit_code\": ${EXIT_STATUS:-0}"
echo "}"

exit ${EXIT_STATUS:-0}
