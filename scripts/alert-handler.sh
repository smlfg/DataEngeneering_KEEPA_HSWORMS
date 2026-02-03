#!/bin/bash
# Alert Handler for Arbitrage Tracker
# Purpose: Handle resource warnings and critical alerts
# Usage: ./alert-handler.sh <severity> <metric> <value> [duration_seconds]
# Examples:
#   ./alert-handler.sh warning ram 87
#   ./alert-handler.sh critical ram 94 180
#   ./alert-handler.sh warning cpu 82 600

set -o pipefail

# Script directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/alert-thresholds.json"
CACHE_DIR="${XDG_CACHE_HOME:=$HOME/.cache}/arbitrage-tracker"
ALERT_LOG="/var/log/arbitrage-alerts.log"

# Create cache directory
mkdir -p "$CACHE_DIR" 2>/dev/null || CACHE_DIR="/tmp/arbitrage-alerts-cache"
mkdir -p "$CACHE_DIR"

# Color codes for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Validate arguments
if [[ $# -lt 3 ]]; then
    echo -e "${RED}Usage: $(basename "$0") <severity> <metric> <value> [duration_seconds]${NC}" >&2
    echo "Examples:" >&2
    echo "  ./alert-handler.sh warning ram 87" >&2
    echo "  ./alert-handler.sh critical cpu 92 300" >&2
    exit 1
fi

SEVERITY="$1"
METRIC="$2"
VALUE="$3"
DURATION="${4:-0}"

# Validate severity
if [[ ! "$SEVERITY" =~ ^(warning|critical)$ ]]; then
    echo -e "${RED}Invalid severity: $SEVERITY (must be 'warning' or 'critical')${NC}" >&2
    exit 1
fi

# Validate metric
if [[ ! "$METRIC" =~ ^(ram|cpu|disk|container)$ ]]; then
    echo -e "${RED}Invalid metric: $METRIC${NC}" >&2
    exit 1
fi

# Function to read JSON config
read_config() {
    local key="$1"
    local default="$2"

    if [[ -f "$CONFIG_FILE" ]]; then
        # Use grep + sed to extract JSON values (minimal dependencies)
        local value=$(grep "\"$key\"" "$CONFIG_FILE" | head -1 | sed 's/.*: \([0-9]*\).*/\1/')
        [[ -n "$value" ]] && echo "$value" || echo "$default"
    else
        echo "$default"
    fi
}

# Function to check rate limiting
check_rate_limit() {
    local metric_severity="${METRIC}_${SEVERITY}"
    local rate_limit_file="$CACHE_DIR/.last_alert_${metric_severity}"
    local current_time=$(date +%s)

    # Determine rate limit interval
    local interval=600  # default 10 minutes
    if [[ "$SEVERITY" == "warning" ]]; then
        interval=$(read_config "warning_interval_seconds" 600)
    else
        interval=$(read_config "critical_interval_seconds" 300)
    fi

    # Check if rate limit file exists and is within interval
    if [[ -f "$rate_limit_file" ]]; then
        local last_alert=$(cat "$rate_limit_file")
        local time_diff=$((current_time - last_alert))

        if [[ $time_diff -lt $interval ]]; then
            # Within rate limit window, skip alert
            return 1
        fi
    fi

    # Update rate limit timestamp
    echo "$current_time" > "$rate_limit_file"
    return 0
}

# Function to get ISO timestamp
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Function to get system urgency level for notify-send
get_urgency() {
    if [[ "$SEVERITY" == "critical" ]]; then
        echo "critical"
    else
        echo "normal"
    fi
}

# Function to format alert message
format_alert_message() {
    local metric_upper=$(echo "$METRIC" | tr '[:lower:]' '[:upper:]')
    local duration_min=0

    if [[ $DURATION -gt 0 ]]; then
        duration_min=$((DURATION / 60))
    fi

    echo "[$(get_timestamp)] [$SEVERITY] [${metric_upper}] VALUE=${VALUE} DURATION=${duration_min}min"
}

# Function to format notification message
format_notification() {
    local metric_upper=$(echo "$METRIC" | tr '[:lower:]' '[:upper:]')
    local severity_upper=$(echo "$SEVERITY" | tr '[:lower:]' '[:upper:]')
    local duration_str=""

    if [[ $DURATION -gt 0 ]]; then
        local duration_min=$((DURATION / 60))
        duration_str=" (sustained for ${duration_min}m)"
    fi

    echo "Arbitrage Tracker: $severity_upper - $metric_upper at ${VALUE}%${duration_str}"
}

# Function to send desktop notification
send_notification() {
    local message="$1"
    local urgency=$(get_urgency)

    # Check if notify-send is available
    if command -v notify-send &>/dev/null; then
        notify-send \
            -u "$urgency" \
            -a "arbitrage-tracker" \
            "Arbitrage Tracker Alert" \
            "$message" 2>/dev/null || true
    fi
}

# Function to log alert
log_alert() {
    local message="$1"

    # Try to write to /var/log (requires permissions)
    if [[ -w /var/log ]]; then
        echo "$message" >> "$ALERT_LOG"
    fi

    # Always write to cache directory as fallback
    local cache_log="$CACHE_DIR/alerts.log"
    echo "$message" >> "$cache_log"

    # Also output to stderr for immediate visibility
    echo -e "${YELLOW}[ALERT]${NC} $message" >&2
}

# Main logic
main() {
    # Check rate limiting
    if ! check_rate_limit; then
        return 0  # Alert suppressed by rate limiting
    fi

    # Format messages
    local alert_message=$(format_alert_message)
    local notification_message=$(format_notification)

    # Log the alert
    log_alert "$alert_message"

    # Send desktop notification
    send_notification "$notification_message"

    # Exit with appropriate code
    if [[ "$SEVERITY" == "critical" ]]; then
        exit 2
    else
        exit 1
    fi
}

# Execute main logic
main
