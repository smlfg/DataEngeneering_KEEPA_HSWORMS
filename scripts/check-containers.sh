#!/bin/bash

# ============================================================================
# check-containers.sh - Container health check with OOM detection
# ============================================================================
# Purpose: Check Docker containers status, health, and OOM conditions
#
# Required Containers:
#   - arbitrage-elasticsearch, arbitrage-kibana, arbitrage-zookeeper
#   - arbitrage-kafka, arbitrage-airflow, arbitrage-fastapi, arbitrage-streamlit
#
# Exit Codes: 0=OK, 1=Warning, 2=Critical
#
# Output: Valid JSON with containers, missing, oomkilled, and summary
#
# Usage Examples:
#   # Check all containers and pretty-print
#   ./check-containers.sh | jq .
#
#   # Find unhealthy containers
#   ./check-containers.sh | jq '.containers[] | select(.health != "healthy")'
#
#   # Check for missing required containers
#   ./check-containers.sh | jq '.missing'
#
#   # Check for OOMKilled containers
#   ./check-containers.sh | jq '.oomkilled'
#
#   # Get overall status only
#   ./check-containers.sh | jq -r '.status'
#
#   # Check if critical (exit code 2)
#   ./check-containers.sh | jq '.exit_code'
#
#   # List all container names and their health
#   ./check-containers.sh | jq -r '.containers[].name, .containers[].health'
#
#   # Filter for running containers only
#   ./check-containers.sh | jq '.containers[] | select(.state == "running")'
#
# ============================================================================

REQUIRED_CONTAINERS=(
    "arbitrage-elasticsearch"
    "arbitrage-kibana"
    "arbitrage-zookeeper"
    "arbitrage-kafka"
    "arbitrage-airflow"
    "arbitrage-fastapi"
    "arbitrage-streamlit"
)

if ! command -v docker &> /dev/null; then
    echo "{\"error\":\"Docker not found\",\"exit_code\":2}"
    exit 2
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EXIT_CODE=0
RUNNING=0
STOPPED=0
OOMKILLED_COUNT=0

declare -a CONTAINERS_JSON
declare -a MISSING_CONTAINERS
declare -a OOMKILLED_CONTAINERS

for CONTAINER in $(docker ps -a --format "{{.Names}}" 2>/dev/null || true); do
    CONTAINER_FOUND[$CONTAINER]=1
done

for CONTAINER in "${REQUIRED_CONTAINERS[@]}"; do
    INSPECT_DATA=$(docker inspect "$CONTAINER" 2>/dev/null || true)

    if [ -z "$INSPECT_DATA" ]; then
        MISSING_CONTAINERS+=("$CONTAINER")
        EXIT_CODE=2
        continue
    fi

    STATE=$(echo "$INSPECT_DATA" | jq -r '.[0].State.Status' 2>/dev/null || echo "unknown")
    OOMKILLED=$(echo "$INSPECT_DATA" | jq -r '.[0].State.OOMKilled' 2>/dev/null || echo "false")

    if [ "$OOMKILLED" = "true" ]; then
        OOMKILLED_CONTAINERS+=("$CONTAINER")
        EXIT_CODE=2
        OOMKILLED_COUNT=$((OOMKILLED_COUNT + 1))
        HEALTH="oomkilled"
    elif [ "$STATE" = "running" ]; then
        RUNNING=$((RUNNING + 1))
        HEALTH=$(echo "$INSPECT_DATA" | jq -r '.[0].State.Health.Status // "running"' 2>/dev/null || echo "running")
        if [ "$HEALTH" = "unhealthy" ]; then
            EXIT_CODE=1
        fi
    else
        STOPPED=$((STOPPED + 1))
        HEALTH="stopped"
        EXIT_CODE=2
    fi

    STATUS=$(docker ps -a --filter "name=^${CONTAINER}$" --format "{{.Status}}" 2>/dev/null || echo "unknown")

    CONTAINER_JSON=$(cat <<EOF
    {
      "name": "$CONTAINER",
      "state": "$STATE",
      "health": "$HEALTH",
      "status": "$STATUS"
    }
EOF
)
    CONTAINERS_JSON+=("$CONTAINER_JSON")
done

for CONTAINER in "${REQUIRED_CONTAINERS[@]}"; do
    if [ "${CONTAINER_FOUND[$CONTAINER]}" != "1" ]; then
        MISSING_CONTAINERS+=("$CONTAINER")
        EXIT_CODE=2
    fi
done

MISSING_JSON=$(printf '%s\n' "${MISSING_CONTAINERS[@]}" 2>/dev/null | grep -v '^$' | jq -R . | jq -s . || echo "[]")
OOMKILLED_JSON=$(printf '%s\n' "${OOMKILLED_CONTAINERS[@]}" 2>/dev/null | grep -v '^$' | jq -R . | jq -s . || echo "[]")

echo "{"
echo "  \"timestamp\": \"$TIMESTAMP\","
echo "  \"containers\": ["

FIRST=true
for JSON in "${CONTAINERS_JSON[@]}"; do
    [ "$FIRST" = true ] || echo ","
    echo "$JSON"
    FIRST=false
done

echo ""
echo "  ],"
echo "  \"missing\": $MISSING_JSON,"
echo "  \"oomkilled\": $OOMKILLED_JSON,"
echo "  \"summary\": {\"total\": ${#REQUIRED_CONTAINERS[@]}, \"running\": $RUNNING, \"stopped\": $STOPPED, \"oomkilled\": $OOMKILLED_COUNT, \"missing\": ${#MISSING_CONTAINERS[@]}},"

if [ $EXIT_CODE -eq 0 ]; then
    STATUS="ok"
elif [ $EXIT_CODE -eq 1 ]; then
    STATUS="warning"
else
    STATUS="critical"
fi

echo "  \"status\": \"$STATUS\","
echo "  \"exit_code\": $EXIT_CODE"
echo "}"

exit $EXIT_CODE
