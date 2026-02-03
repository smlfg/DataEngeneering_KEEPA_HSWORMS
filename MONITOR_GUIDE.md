# 🤖 opencode Live Monitor - Benutzerhandbuch

**Live-Monitoring für opencode Multi-Agent Aktivität**

---

## 🚀 Quick Start

### **Option 1: Mit tmux (Empfohlen!)** ⭐

```bash
cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker

# Dashboard starten
./launch_monitor_dashboard.sh
```

**Was passiert:**
- ✅ Öffnet tmux Session mit 3 Panels
- ✅ Panel 1 (oben): **Live Monitor Dashboard** 📊
- ✅ Panel 2 (unten): **Work Terminal** - Hier opencode commands ausführen
- ✅ Panel 3 (Tab 2): **Live Logs** - Real-time log tail

### **Option 2: Standalone Monitor**

```bash
cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker

# Monitor starten
./opencode_monitor.sh
```

**Dann in einem anderen Terminal:**
```bash
# opencode commands ausführen
opencode "dein command"
```

---

## 📺 Was du siehst

```
╔════════════════════════════════════════════════════════════════════╗
║          🤖 opencode Multi-Agent Live Monitor 🤖              ║
╚════════════════════════════════════════════════════════════════════╝

Session: session-20260108-180000
Time:    2026-01-08 18:00:00

┌─────────────────────────────────────────────────────────────────┐
│ STATUS                                                          │
└─────────────────────────────────────────────────────────────────┘
● opencode Status: RUNNING (PID: 12345)
⚡ Active Subagents: 3

┌─────────────────────────────────────────────────────────────────┐
│ RECENT ACTIVITY (Last 5 entries)                               │
└─────────────────────────────────────────────────────────────────┘
  [18:00:15] [INFO] [PRODUCER] Started implementation
  [18:00:18] [INFO] [PRODUCER] Writing keepa_client.py
  [18:00:22] [INFO] [PRODUCER] Writing kafka_producer.py
  [18:00:25] [INFO] [PRODUCER] Tests passing
  [18:00:28] [INFO] [PRODUCER] Task complete ✅

┌─────────────────────────────────────────────────────────────────┐
│ FILE CHANGES (Last 2 minutes)                                  │
└─────────────────────────────────────────────────────────────────┘
  📝 keepa_client.py
  📝 kafka_producer.py
  📝 main.py

┌─────────────────────────────────────────────────────────────────┐
│ AGENT ACTIVITY GRAPH                                           │
└─────────────────────────────────────────────────────────────────┘
  Agents: ███ (3 active)

┌─────────────────────────────────────────────────────────────────┐
│ SYSTEM RESOURCES                                               │
└─────────────────────────────────────────────────────────────────┘
  CPU Usage:  45.3%
  Memory:     62%

════════════════════════════════════════════════════════════════════
Press Ctrl+C to stop monitoring
Logs: /path/to/session-20260108-180000.log
════════════════════════════════════════════════════════════════════
```

---

## 🎮 tmux Steuerung

### **Wichtige Keyboard Shortcuts:**

| Aktion | Shortcut | Beschreibung |
|--------|----------|--------------|
| **Zwischen Panels wechseln** | `Ctrl+b` dann `↑↓` | Hoch/Runter navigieren |
| **Panel vergrößern** | `Ctrl+b` dann `z` | Toggle Fullscreen |
| **Zwischen Tabs wechseln** | `Ctrl+b` dann `n` | Nächster Tab |
| **Session detachen** | `Ctrl+b` dann `d` | Läuft im Hintergrund weiter |
| **Monitor beenden** | `Ctrl+C` (im Monitor-Panel) | Stoppt nur Monitor |
| **Alles beenden** | `Ctrl+b` dann `:kill-session` | Komplette Session killen |

### **Nützliche Befehle:**

```bash
# Zu laufender Session zurück
tmux attach -t opencode-monitor

# Session im Hintergrund laufen lassen (detach)
Ctrl+b dann d

# Alle Sessions anzeigen
tmux ls

# Session killen
tmux kill-session -t opencode-monitor
```

---

## 📊 Was wird überwacht?

### **1. opencode Status**
- ✅ Läuft opencode gerade?
- ✅ Process ID (PID)
- ✅ Start/Stop Events

### **2. Subagent Activity**
- ✅ Anzahl aktiver Subagents
- ✅ Agent-Starts/-Stops
- ✅ Activity Graph

### **3. Recent Activity**
- ✅ Letzte 5 Log-Einträge
- ✅ Color-coded (Errors rot, Success grün)
- ✅ Real-time Updates

### **4. File Changes**
- ✅ Welche Files wurden in letzten 2min geändert?
- ✅ Nur .py Files im src/ Verzeichnis
- ✅ Zeigt aktive Entwicklung

### **5. System Resources**
- ✅ CPU Usage
- ✅ Memory Usage
- ✅ System Load

---

## 📝 Logs & Reports

### **Session Logs**

Jeder Monitor-Lauf erstellt:

```
MultiAgentDokumentation/reports/opencode-sessions/
├── session-20260108-180000.log          # Detaillierter Log
└── session-20260108-180000-report.md   # Zusammenfassung (geplant)
```

**Log-Format:**
```
# opencode Monitor Session
# Started: 2026-01-08 18:00:00
# Session ID: session-20260108-180000

[2026-01-08 18:00:05] opencode started (PID: 12345)
[2026-01-08 18:00:15] Subagent count increased: 0 → 1
[2026-01-08 18:00:25] Subagent count increased: 1 → 2
[2026-01-08 18:15:30] opencode stopped
```

### **Live Stats File**

```
MultiAgentDokumentation/dashboards/live-stats.txt
```

Enthält immer den aktuellen Status (für andere Scripts):
```
opencode_running: yes
opencode_pid: 12345
subagents_active: 3
timestamp: 2026-01-08 18:00:30
session_id: session-20260108-180000
```

---

## 🎯 Typische Workflows

### **Workflow 1: Normales Arbeiten mit Live-Monitor**

```bash
# 1. Dashboard starten
./launch_monitor_dashboard.sh

# 2. Im unteren Panel (Work Terminal):
opencode "Implement Producer Worker"

# 3. Zuschauen wie Monitor sich updated! 🍿

# 4. Fertig? Ctrl+b dann d (detach)
#    Monitor läuft weiter im Hintergrund
```

### **Workflow 2: Parallel Development**

```bash
# Terminal 1: Monitor
./opencode_monitor.sh

# Terminal 2: Work
cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker
opencode "Add Airflow support"

# Terminal 3: Logs
tail -f MultiAgentDokumentation/logs/implementation.log
```

### **Workflow 3: Post-Session Analysis**

```bash
# Nach opencode Lauf:
cd MultiAgentDokumentation/reports/opencode-sessions/

# Letzten Session-Log anschauen
cat session-$(date +%Y%m%d)-*.log | tail -50

# Oder mit less:
less session-$(date +%Y%m%d)-*.log
```

---

## 🔧 Troubleshooting

### **Problem: Monitor zeigt keine Subagents**

**Ursache:** Detection basiert auf Process-Namen

**Lösung:**
```bash
# Prüfe manuell:
ps aux | grep -E "aider|minimax|agent|worker"

# Falls andere Namen: Script anpassen (Zeile 48-58)
```

### **Problem: tmux nicht installiert**

```bash
# Installieren:
sudo apt install tmux

# Oder ohne tmux:
./opencode_monitor.sh
```

### **Problem: "Permission denied"**

```bash
# Scripts ausführbar machen:
chmod +x opencode_monitor.sh
chmod +x launch_monitor_dashboard.sh
```

### **Problem: Monitor Update zu langsam/schnell**

**Script bearbeiten:**
```bash
nano opencode_monitor.sh

# Zeile 196: sleep 2
# Ändern zu: sleep 1 (schneller) oder sleep 5 (langsamer)
```

---

## 🎨 Customization

### **Farben ändern**

Im Script (Zeile 13-20):
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
# ... anpassen nach Geschmack
```

### **Refresh-Rate ändern**

Zeile 196:
```bash
sleep 2  # Alle 2 Sekunden aktualisieren
```

### **Mehr/Weniger Activity-Zeilen**

Zeile 91:
```bash
tail -n 5 "$activity_log"  # Ändern zu -n 10 für mehr
```

---

## 📚 Erweiterte Features (Coming Soon)

- [ ] **Agent-spezifische Panels** (Producer, Consumer, etc.)
- [ ] **Graphische Activity Timeline**
- [ ] **Notification bei Agent-Starts**
- [ ] **Export zu AFTERVIEW.md**
- [ ] **Integration mit Git commits**
- [ ] **Performance Metrics per Agent**

---

## 🎬 Demo Session

```bash
# 1. Dashboard starten
./launch_monitor_dashboard.sh

# 2. Im Work Panel (unten):
opencode "Write a hello world function"

# 3. Du siehst LIVE:
#    - opencode Status: IDLE → RUNNING
#    - Subagents: 0 → 1
#    - Activity: "Started agent", "Writing code..."
#    - File Changes: hello.py appears!

# 4. Wenn fertig:
#    - opencode Status: RUNNING → IDLE
#    - Session-Log gespeichert ✅
```

---

## 💡 Pro-Tips

1. **Dual-Monitor Setup:**
   - Monitor 1: opencode_monitor.sh fullscreen
   - Monitor 2: Dein Editor + opencode commands

2. **Background Monitoring:**
   ```bash
   ./launch_monitor_dashboard.sh
   Ctrl+b dann d  # Detach
   # Arbeite normal weiter
   tmux attach -t opencode-monitor  # Zurück schauen
   ```

3. **Session History:**
   ```bash
   # Alle Sessions heute:
   ls -lth MultiAgentDokumentation/reports/opencode-sessions/session-$(date +%Y%m%d)*
   ```

4. **Monitor als Screensaver:**
   ```bash
   # Cool aussehen lassen 😎
   ./opencode_monitor.sh
   # Läuft einfach und zeigt Activity
   ```

---

## 🆘 Support

**Fragen? Probleme?**

1. Check Session-Logs: `MultiAgentDokumentation/reports/opencode-sessions/`
2. Check Error-Logs: `MultiAgentDokumentation/logs/errors.log`
3. Script-Source lesen: `opencode_monitor.sh` (gut kommentiert!)

---

## 📄 Files Overview

```
arbitrage-tracker/
├── opencode_monitor.sh              # Core monitor script
├── launch_monitor_dashboard.sh      # tmux launcher
├── MONITOR_GUIDE.md                 # This file
└── MultiAgentDokumentation/
    ├── dashboards/
    │   └── live-stats.txt           # Current stats (auto-updated)
    ├── logs/
    │   └── implementation.log       # Activity log (parsed)
    └── reports/
        └── opencode-sessions/       # Session logs & reports
            ├── session-*.log
            └── session-*-report.md
```

---

**Happy Monitoring! 🍿🤖**

_"Watch your agents work while you grab coffee ☕"_
