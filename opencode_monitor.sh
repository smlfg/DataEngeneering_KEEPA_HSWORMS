#!/bin/bash
# opencode Live Monitor Dashboard
# Permanent live monitoring of opencode multi-agent activity
# Usage: ./opencode_monitor.sh

set -e

MONITOR_DIR="$HOME/Dokumente/WS2025/DataEnge/arbitrage-tracker/MultiAgentDokumentation"
LOG_DIR="$MONITOR_DIR/logs"
SESSION_DIR="$MONITOR_DIR/reports/opencode-sessions"
LIVE_STATS="$MONITOR_DIR/dashboards/live-stats.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p "$SESSION_DIR"
mkdir -p "$LOG_DIR"

# Session info
SESSION_ID="session-$(date +%Y%m%d-%H%M%S)"
SESSION_LOG="$SESSION_DIR/${SESSION_ID}.log"
SESSION_REPORT="$SESSION_DIR/${SESSION_ID}-report.md"

# Initialize session log
cat > "$SESSION_LOG" <<EOF
# opencode Monitor Session
# Started: $(date)
# Session ID: $SESSION_ID

EOF

# Function to detect opencode process
detect_opencode() {
    pgrep -f "opencode" | head -1
}

# Function to count active subagents
count_subagents() {
    # Try to detect based on common patterns
    local count=0

    # Check for python processes (often used by agents)
    count=$(pgrep -f "python.*agent\|python.*worker" 2>/dev/null | wc -l)

    # Check for aider/minimax processes
    local aider_count=$(pgrep -f "aider\|minimax" 2>/dev/null | wc -l)
    count=$((count + aider_count))

    echo "$count"
}

# Function to parse recent activity
parse_activity() {
    local activity_log="$LOG_DIR/implementation.log"

    if [ -f "$activity_log" ]; then
        tail -n 5 "$activity_log" 2>/dev/null || echo "No recent activity"
    else
        echo "No activity log found"
    fi
}

# Function to detect file changes
detect_file_changes() {
    local project_dir="$HOME/Dokumente/WS2025/DataEnge/arbitrage-tracker"

    # Find files modified in last 2 minutes
    find "$project_dir/src" -type f -name "*.py" -mmin -2 2>/dev/null | while read file; do
        echo "$(basename "$file")"
    done | head -5
}

# Function to render dashboard
render_dashboard() {
    clear

    local opencode_pid=$(detect_opencode)
    local subagent_count=$(count_subagents)
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    # Header
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}          🤖 opencode Multi-Agent Live Monitor 🤖              ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Session:${NC} $SESSION_ID"
    echo -e "${BLUE}Time:${NC}    $timestamp"
    echo ""

    # Status Section
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│${WHITE} STATUS                                                          ${YELLOW}│${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"

    if [ -n "$opencode_pid" ]; then
        echo -e "${GREEN}● opencode Status:${NC} ${GREEN}RUNNING${NC} (PID: $opencode_pid)"
    else
        echo -e "${RED}○ opencode Status:${NC} ${RED}IDLE${NC}"
    fi

    echo -e "${MAGENTA}⚡ Active Subagents:${NC} $subagent_count"
    echo ""

    # Activity Section
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│${WHITE} RECENT ACTIVITY (Last 5 entries)                               ${YELLOW}│${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"

    parse_activity | while IFS= read -r line; do
        if [[ "$line" =~ ERROR|error|Error ]]; then
            echo -e "${RED}  $line${NC}"
        elif [[ "$line" =~ INFO|info|Complete|complete|✅ ]]; then
            echo -e "${GREEN}  $line${NC}"
        elif [[ "$line" =~ WARNING|warning|⚠️ ]]; then
            echo -e "${YELLOW}  $line${NC}"
        else
            echo -e "${WHITE}  $line${NC}"
        fi
    done
    echo ""

    # File Changes Section
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│${WHITE} FILE CHANGES (Last 2 minutes)                                  ${YELLOW}│${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"

    local changed_files=$(detect_file_changes)
    if [ -n "$changed_files" ]; then
        echo "$changed_files" | while read -r file; do
            echo -e "${CYAN}  📝 $file${NC}"
        done
    else
        echo -e "${WHITE}  No recent changes${NC}"
    fi
    echo ""

    # Agent Activity Visualization
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│${WHITE} AGENT ACTIVITY GRAPH                                           ${YELLOW}│${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"

    # Simple bar chart based on subagent count
    local bar=""
    for i in $(seq 1 $subagent_count); do
        bar="${bar}█"
    done

    echo -e "  Agents: ${GREEN}$bar${NC} ($subagent_count active)"
    echo ""

    # System Resources
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│${WHITE} SYSTEM RESOURCES                                               ${YELLOW}│${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"

    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)"%"}')

    echo -e "  CPU Usage:  ${CYAN}$cpu_usage${NC}"
    echo -e "  Memory:     ${CYAN}$mem_usage${NC}"
    echo ""

    # Footer
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}Press ${RED}Ctrl+C${WHITE} to stop monitoring${NC}"
    echo -e "${WHITE}Logs: ${BLUE}$SESSION_LOG${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"

    # Save stats to file
    cat > "$LIVE_STATS" <<STATS
opencode_running: $([ -n "$opencode_pid" ] && echo "yes" || echo "no")
opencode_pid: ${opencode_pid:-none}
subagents_active: $subagent_count
timestamp: $timestamp
session_id: $SESSION_ID
STATS
}

# Function to log activity
log_activity() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$SESSION_LOG"
}

# Main monitoring loop
echo -e "${GREEN}Starting opencode Monitor...${NC}"
echo -e "${BLUE}Session ID: $SESSION_ID${NC}"
echo ""
sleep 2

# Track previous state
PREV_OPENCODE_STATE="idle"
PREV_SUBAGENT_COUNT=0

while true; do
    # Render the dashboard
    render_dashboard

    # Detect state changes and log them
    CURRENT_OPENCODE_PID=$(detect_opencode)
    CURRENT_SUBAGENT_COUNT=$(count_subagents)

    if [ -n "$CURRENT_OPENCODE_PID" ] && [ "$PREV_OPENCODE_STATE" = "idle" ]; then
        log_activity "opencode started (PID: $CURRENT_OPENCODE_PID)"
        PREV_OPENCODE_STATE="running"
    elif [ -z "$CURRENT_OPENCODE_PID" ] && [ "$PREV_OPENCODE_STATE" = "running" ]; then
        log_activity "opencode stopped"
        PREV_OPENCODE_STATE="idle"
    fi

    if [ "$CURRENT_SUBAGENT_COUNT" -gt "$PREV_SUBAGENT_COUNT" ]; then
        log_activity "Subagent count increased: $PREV_SUBAGENT_COUNT → $CURRENT_SUBAGENT_COUNT"
    elif [ "$CURRENT_SUBAGENT_COUNT" -lt "$PREV_SUBAGENT_COUNT" ]; then
        log_activity "Subagent count decreased: $PREV_SUBAGENT_COUNT → $CURRENT_SUBAGENT_COUNT"
    fi

    PREV_SUBAGENT_COUNT=$CURRENT_SUBAGENT_COUNT

    # Refresh every 2 seconds
    sleep 2
done

# Cleanup on exit
trap "echo 'Monitor stopped. Session saved to: $SESSION_LOG' && exit 0" INT TERM
