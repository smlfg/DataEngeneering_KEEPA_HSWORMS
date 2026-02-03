#!/bin/bash
# Quick Status Viewer for Amazon Arbitrage Tracker
# Usage: ./VIEW_STATUS.sh [overview|daily|dashboard|logs|all]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Amazon Arbitrage Tracker"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    ${PROJECT_NAME} - Status Viewer       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

view_overview() {
    echo -e "${GREEN}📊 PROJECT OVERVIEW${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "$SCRIPT_DIR/OVERVIEW.md" ]; then
        cat "$SCRIPT_DIR/OVERVIEW.md"
    else
        echo -e "${RED}OVERVIEW.md not found${NC}"
    fi
    echo ""
}

view_dashboard() {
    echo -e "${GREEN}📈 PROGRESS DASHBOARD${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "$SCRIPT_DIR/dashboards/progress-dashboard.md" ]; then
        cat "$SCRIPT_DIR/dashboards/progress-dashboard.md"
    else
        echo -e "${RED}progress-dashboard.md not found${NC}"
    fi
    echo ""
}

view_daily() {
    echo -e "${GREEN}📅 DAILY REPORT (Latest)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    LATEST_REPORT=$(ls -t "$SCRIPT_DIR/reports/daily/" 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        cat "$SCRIPT_DIR/reports/daily/$LATEST_REPORT"
    else
        echo -e "${YELLOW}No daily reports found yet${NC}"
    fi
    echo ""
}

view_logs() {
    echo -e "${GREEN}📝 RECENT IMPLEMENTATION ACTIVITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "$SCRIPT_DIR/logs/implementation.log" ]; then
        tail -20 "$SCRIPT_DIR/logs/implementation.log"
    else
        echo -e "${YELLOW}No implementation log found${NC}"
    fi
    echo ""

    echo -e "${RED}🐛 RECENT ERRORS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "$SCRIPT_DIR/logs/errors.log" ]; then
        ERROR_COUNT=$(grep -v "^#" "$SCRIPT_DIR/logs/errors.log" | grep -v "^$" | wc -l)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            tail -10 "$SCRIPT_DIR/logs/errors.log"
        else
            echo -e "${GREEN}✅ No errors logged!${NC}"
        fi
    else
        echo -e "${YELLOW}No error log found${NC}"
    fi
    echo ""
}

view_metrics() {
    echo -e "${GREEN}📊 PROJECT METRICS (JSON)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "$SCRIPT_DIR/dashboards/metrics.json" ]; then
        if command -v jq &> /dev/null; then
            jq '.' "$SCRIPT_DIR/dashboards/metrics.json"
        else
            cat "$SCRIPT_DIR/dashboards/metrics.json"
            echo -e "${YELLOW}Tip: Install 'jq' for pretty JSON formatting${NC}"
        fi
    else
        echo -e "${RED}metrics.json not found${NC}"
    fi
    echo ""
}

view_worker_status() {
    echo -e "${GREEN}👥 WORKER STATUS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    WORKERS=("producer" "enrichment" "arbitrage" "api" "dashboard")

    for worker in "${WORKERS[@]}"; do
        LATEST_REPORT=$(ls -t "$SCRIPT_DIR/reports/worker-progress/${worker}-"* 2>/dev/null | head -1)
        if [ -n "$LATEST_REPORT" ]; then
            echo -e "${BLUE}Worker: ${worker}${NC}"
            head -30 "$LATEST_REPORT"
            echo ""
        fi
    done

    if [ -z "$(ls -A $SCRIPT_DIR/reports/worker-progress/ 2>/dev/null)" ]; then
        echo -e "${YELLOW}No worker reports found yet${NC}"
    fi
    echo ""
}

# Main logic
case "${1:-overview}" in
    overview)
        view_overview
        ;;
    daily)
        view_daily
        ;;
    dashboard)
        view_dashboard
        ;;
    logs)
        view_logs
        ;;
    metrics)
        view_metrics
        ;;
    workers)
        view_worker_status
        ;;
    all)
        view_overview
        view_dashboard
        view_daily
        view_logs
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 [overview|daily|dashboard|logs|metrics|workers|all]${NC}"
        echo ""
        echo "Options:"
        echo "  overview   - Show main project overview (default)"
        echo "  daily      - Show latest daily report"
        echo "  dashboard  - Show visual progress dashboard"
        echo "  logs       - Show recent activity and errors"
        echo "  metrics    - Show project metrics (JSON)"
        echo "  workers    - Show worker-specific reports"
        echo "  all        - Show everything"
        echo ""
        exit 1
        ;;
esac

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}For real-time updates, use: watch -n 60 ./VIEW_STATUS.sh${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
