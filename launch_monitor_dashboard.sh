#!/bin/bash
# Launch opencode Monitor Dashboard with tmux
# Creates a split-screen view: Monitor + Work Terminal

SESSION_NAME="opencode-monitor"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux is not installed!"
    echo "Install with: sudo apt install tmux"
    exit 1
fi

# Kill existing session if it exists
tmux kill-session -t $SESSION_NAME 2>/dev/null || true

echo "🚀 Launching opencode Monitor Dashboard..."
sleep 1

# Create new tmux session
tmux new-session -d -s $SESSION_NAME

# Rename first window
tmux rename-window -t $SESSION_NAME:0 'Monitor'

# Split window horizontally (top: monitor, bottom: work terminal)
tmux split-window -v -t $SESSION_NAME:0

# Adjust split sizes (70% monitor, 30% work terminal)
tmux resize-pane -t $SESSION_NAME:0.0 -y 70%

# Run monitor in top pane
tmux send-keys -t $SESSION_NAME:0.0 "cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker && ./opencode_monitor.sh" C-m

# Set up work terminal in bottom pane
tmux send-keys -t $SESSION_NAME:0.1 "cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo '🎯 Work Terminal - Run opencode commands here:'" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo '   Example: opencode \"Implement Producer Worker\"'" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo '📊 Monitor is running above ☝️'" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo ''" C-m

# Create second window for logs
tmux new-window -t $SESSION_NAME:1 -n 'Logs'
tmux send-keys -t $SESSION_NAME:1 "cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker/MultiAgentDokumentation/logs" C-m
tmux send-keys -t $SESSION_NAME:1 "tail -f implementation.log" C-m

# Attach to session
tmux attach-session -t $SESSION_NAME

# Cleanup message (shown after detach/exit)
echo ""
echo "✅ Monitor session closed"
echo "📊 Session logs saved to: MultiAgentDokumentation/reports/opencode-sessions/"
echo ""
echo "To reattach: tmux attach -t $SESSION_NAME"
echo "To kill:     tmux kill-session -t $SESSION_NAME"
