# BigAnalysis: Keepa DataEngineering Project

> Deep Technical Analysis — February 2026
> Generated from OpenCode 4-Agent Parallel Analysis + Manual Code Review

---

## 1. Executive Summary

This Keepa API monitoring project is a **multi-agent Amazon arbitrage detection system** with significant architectural ambition but critical integration gaps. The codebase has grown organically through branch merges, resulting in duplicated layers and dead code paths.

**Key Metrics:**

| Metric | Value |
|--------|-------|
| Total Project Size | ~19 MB (incl. .venv) |
| Python Files (excl. venv) | 52 |
| Source Code (src/) | 3,246 lines |
| Test Code (tests/) | 44 lines |
| Test Coverage (estimated) | ~2-5% |
| Completion Level | 6/10 |

**Critical Finding:** The LangGraph Orchestrator (`src/agents/orchestrator.py`) is **dead code** — it is never imported or referenced by any other module in the project. The system bypasses the entire LangGraph workflow layer in practice.

**Architecture Decision Required:** Should LangGraph be fully integrated as the single orchestration layer, or should it be removed entirely in favor of the simpler direct-agent approach?

---

## 2. Architecture & Data Flow

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL CLIENTS                         │
│              (Browser / curl / Monitoring Tools)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI API LAYER                          │
│                   src/api/main.py (409 lines)                   │
│                                                                 │
│  Endpoints:                                                     │
│  GET  /health              GET  /api/v1/status                  │
│  GET  /api/v1/watches      POST /api/v1/watches                 │
│  DEL  /api/v1/watches/:id  POST /api/v1/price/check             │
│  POST /api/v1/price/check-all                                   │
│  POST /api/v1/deals/search                                      │
│  GET  /api/v1/tokens       GET  /api/v1/rate-limit              │
└───────┬──────────────────────┬──────────────────────┬───────────┘
        │                      │                      │
        ▼                      ▼                      ▼
 ┌─────────────┐      ┌──────────────┐      ┌──────────────────┐
 │  SERVICES   │      │  SCHEDULERS  │      │  AGENTS (unused) │
 │  (async)    │      │  (2 impls!)  │      │  + LangGraph     │
 │             │      │              │      │  (dead code)     │
 │ keepa_api   │      │ scheduler.py │      │                  │
 │ database    │      │ scheduler/   │      │ orchestrator.py  │
 │ notification│      │   jobs.py    │      │ graph/nodes.py   │
 └──────┬──────┘      └──────┬───────┘      │ graph/states.py  │
        │                    │              └──────────────────┘
        └────────┬───────────┘
                 │
                 ▼
 ┌───────────────────────────────────────────────────────────────┐
 │                    KEEPA API (External)                       │
 │               keepa.com — Products & Deals Data               │
 │            Token-bucket rate limited (async client)            │
 └───────────────────────────────────────────────────────────────┘
                 │
                 ▼
 ┌───────────────────────────────────────────────────────────────┐
 │                     DATA LAYER                                │
 │                                                               │
 │  ┌─────────────────────┐    ┌─────────────────────────────┐   │
 │  │ PostgreSQL 15       │    │ Redis 7 (configured but     │   │
 │  │ Dual Schema Problem │    │ NOT actively used)          │   │
 │  │ (see Section 6)     │    │                             │   │
 │  └─────────────────────┘    └─────────────────────────────┘   │
 └───────────────────────────────────────────────────────────────┘
```

### Active Data Flows (What Actually Works)

1. **Watch Creation:** `POST /api/v1/watches` → `KeepaAPIClient.query_product()` → `services/database.create_watch()` (async, UUID PKs)
2. **Scheduled Price Check:** `scheduler.py` → `KeepaAPIClient.query_product()` → `AlertDispatcherAgent.dispatch_alert()` (direct call, bypasses LangGraph)
3. **Deal Search:** `POST /api/v1/deals/search` → `KeepaAPIClient.search_deals()` → inline filtering/scoring in `main.py`
4. **Manual Price Check:** `POST /api/v1/price/check` → `KeepaAPIClient.query_product()` → direct response

### Dead Data Flow (LangGraph Path — Never Executed)

```
OrchestratorAgent.run_workflow()
  → create_workflow_graph()
    → price_monitor_node → alert_dispatcher_node
    → deal_finder_node → alert_dispatcher_node
    → error_handler_node (retry logic)
```

This entire path exists in code but is **never triggered** because `orchestrator.py` is never imported.

---

## 3. Code Quality Assessment

### Working Components

| Component | File | Lines | Status | Notes |
|-----------|------|-------|--------|-------|
| **KeepaAPIClient** | `services/keepa_api.py` | 657 | Working | Token bucket rate limiting, async wrapper, deal search |
| **PriceMonitorAgent** | `agents/price_monitor.py` | 93 | Working | Volatility-based scheduling, batch processing (50) |
| **DealFinderAgent** | `agents/deal_finder.py` | 120 | Working | Scoring formula, dropshipper filtering |
| **AlertDispatcherAgent** | `agents/alert_dispatcher.py` | 179 | Working | Rate limiting (10/hr), duplicate detection, retry logic |
| **NotificationService** | `services/notification.py` | 175 | Working | Email via aiosmtplib, HTML formatting |
| **FastAPI Endpoints** | `api/main.py` | 409 | Working | 11 endpoints, Pydantic validation |
| **Async DB Layer** | `services/database.py` | 356 | Working | Full CRUD, async SQLAlchemy 2.0 |

### Broken / Dead Components

| Component | File | Lines | Issue | Impact |
|-----------|------|-------|-------|--------|
| **OrchestratorAgent** | `agents/orchestrator.py` | 77 | Never imported anywhere | Entire LangGraph layer is dead code |
| **LangGraph Nodes** | `graph/nodes.py` | 184 | Only reachable via dead Orchestrator | Workflow logic never executes |
| **LangGraph States** | `graph/states.py` | 79 | Only used by dead nodes | State management unused |
| **Sync DB Layer** | `core/database.py` | 146 | Conflicts with async layer | Dual schema problem |
| **Repository Layer** | `repositories/watch_repository.py` | 214 | Imports non-existent model fields | Runtime ImportError |

### Import Path Chaos

Different modules use incompatible import styles:

```python
# agents/orchestrator.py — relative imports (no src. prefix)
from graph.nodes import create_workflow_graph
from services.keepa_api import keepa_client

# scheduler/jobs.py — absolute imports (src. prefix)
from src.core.database import get_db_session
from src.models import Watch, Alert

# api/main.py — relative imports (no src. prefix)
from services.database import init_db, create_watch
from scheduler import run_immediate_check
```

This causes different behavior depending on whether the app runs from the project root, from inside `src/`, or inside Docker.

---

## 4. Agent System & LangGraph Status

### The Four Agents

| Agent | File | Lines | Status | How It's Used |
|-------|------|-------|--------|---------------|
| **PriceMonitorAgent** | `agents/price_monitor.py` | 93 | Active | Called directly by `scheduler.py` |
| **DealFinderAgent** | `agents/deal_finder.py` | 120 | Active | Standalone usage, not in workflows |
| **AlertDispatcherAgent** | `agents/alert_dispatcher.py` | 179 | Active | Called directly by `scheduler.py` |
| **OrchestratorAgent** | `agents/orchestrator.py` | 77 | DEAD | Never imported, never instantiated |

### LangGraph Workflow Analysis

The LangGraph workflow graph is defined in `graph/nodes.py:165-184`:

```
┌─────────────────┐
│  ENTRY POINT    │
│ price_monitor   │─────────────────────────┐
│     node        │                         │
└────────┬────────┘                         │
         │                                  │
         ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│  deal_finder    │              │ error_handler   │
│     node        │              │     node        │
└────────┬────────┘              │ (retry logic)   │
         │                       └─────────────────┘
         │
         ▼
┌─────────────────┐
│ alert_dispatcher│
│     node        │
│  (FINISH POINT) │
└─────────────────┘
```

**Problems with this graph:**
1. `deal_finder_node` is not reachable from the entry point — there's no edge from `price_monitor` to `deal_finder`
2. The conditional edge from `price_monitor` conflicts with the unconditional edge (both exist, line 174 vs 177-179)
3. The error handler has no outgoing edges — once an error occurs, the workflow terminates

### Evidence: Orchestrator is Dead Code

```bash
$ grep -r "orchestrator" src/ --include="*.py"
# Only matches within orchestrator.py itself — zero external imports
```

The `api/main.py` imports directly from `services/` and `scheduler`:
```python
# api/main.py:15-24 — NO orchestrator import
from services.database import init_db, create_watch, ...
from services.keepa_api import KeepaAPIClient, ...
from scheduler import run_immediate_check, check_single_asin
```

### Dual Scheduler Problem

Two independent scheduler implementations exist:

| Scheduler | File | Interval | Uses |
|-----------|------|----------|------|
| **PriceMonitorScheduler** | `scheduler.py` (231 lines) | 6 hours default | Direct agent calls |
| **KeeperScheduler** | `scheduler/jobs.py` (269 lines) | 30 min price, daily deals | APScheduler + sync DB |

Both could run simultaneously in Docker (the `docker-compose.yml` defines a separate `scheduler` service), potentially causing duplicate price checks and alerts.

---

## 5. Integration Gaps

### Priority Matrix

| # | Gap | Severity | Components Affected | Fix Effort |
|---|-----|----------|---------------------|------------|
| 1 | OrchestratorAgent never imported | CRITICAL | LangGraph layer dead | Low (import) or High (redesign) |
| 2 | Dual database schemas | CRITICAL | All DB operations | High |
| 3 | Import path inconsistency | HIGH | Cross-module imports | Medium |
| 4 | `keepa` not in requirements.txt | HIGH | Docker build fails | Low |
| 5 | Dual schedulers | HIGH | Background jobs | Medium |
| 6 | Repository imports wrong models | HIGH | Data access layer | Low |
| 7 | Deal reports generated but not sent | MEDIUM | User value | Medium |
| 8 | Telegram/Discord not implemented | MEDIUM | Notifications | Medium |
| 9 | Hardcoded email in nodes.py | LOW | Alert delivery | Low |
| 10 | Redis configured but unused | LOW | Caching/performance | Low |

### Missing Connections

```
API Layer ──── uses ──── services/database.py (ASYNC, UUID PKs)
                              ↕ CONFLICT
Scheduler ──── uses ──── core/database.py (SYNC, Integer PKs)
                              ↕ CONFLICT
Repository ──── tries to import ──── models that don't exist
                              ↕ BROKEN
LangGraph ──── not connected to ──── anything (dead code)
```

---

## 6. Database Layer Problems (Dual Schema)

### The Core Problem

Two completely separate database model definitions exist with **incompatible schemas**:

#### Location A: `src/services/database.py` (Async — used by API)

| Model | PK Type | Table Name | Key Differences |
|-------|---------|------------|-----------------|
| `User` | UUID | `users` | Has `relationship()` to watches |
| `WatchedProduct` | UUID | `watched_products` | Has `status` enum, `updated_at` |
| `PriceHistory` | UUID | `price_history` | Has `buy_box_seller` |
| `PriceAlert` | UUID | `price_alerts` | Has `notification_channel` |
| `DealFilter` | UUID | `deal_filters` | JSON categories |
| `DealReport` | UUID | `deal_reports` | JSON deals_data |

#### Location B: `src/core/database.py` (Sync — used by Scheduler)

| Model | PK Type | Table Name | Key Differences |
|-------|---------|------------|-----------------|
| `User` | String(36) | `users` | No relationships |
| `Watch` | Integer | `watches` | Has `product_name`, `volatility_score` |
| `PriceHistory` | Integer | `price_history` | No `buy_box_seller` |
| `Alert` | Integer | `alerts` | Has `old_price`, `new_price`, `discount_percent` |

### Schema Conflicts in Detail

| Field | Async Model (`services/`) | Sync Model (`core/`) | Conflict |
|-------|---------------------------|----------------------|----------|
| Primary Key | `UUID(as_uuid=True)` | `Integer` / `String(36)` | Type mismatch |
| `user_id` FK | `UUID(as_uuid=True)` | `String(36)` | FK type mismatch |
| `watch_id` FK | `UUID` → `watched_products.id` | `Integer` → implicit | Relationship broken |
| `product_name` | Missing | `String(255)` | Repository fails |
| `old_price` | Missing | `Float` | Alert creation fails |
| `new_price` | Missing | `Float` | Alert creation fails |
| `volatility_score` | Missing | `Float` | Scheduling may break |
| `discount_percent` | Missing | `Integer` | Reporting fails |
| Table: watches | `watched_products` | `watches` | Different names |
| Table: alerts | `price_alerts` | `alerts` | Different names |

### What Breaks

```python
# src/repositories/watch_repository.py — tries to create Alert with fields
# that ONLY exist in the sync model (core/database.py):
alert = Alert(
    product_name=watch.product_name,  # Missing in async model
    old_price=old_price,              # Missing in async model
    new_price=new_price,              # Missing in async model
    discount_percent=discount_percent # Missing in async model
)
# → RuntimeError: these columns don't exist on PriceAlert
```

### Root Cause

This happened because three Git branches were merged without reconciling their database models:
- One branch built the async layer (`services/database.py`)
- Another branch built the sync layer (`core/database.py`)
- The merge combined both without choosing one

---

## 7. Test Coverage Gaps

### Current State: CRITICAL (~2-5% Coverage)

| Component | Test File | Tests | Coverage |
|-----------|-----------|-------|----------|
| PriceMonitorAgent | `test_agents/test_price_monitor.py` | 2 | ~10% |
| DealFinderAgent | — | 0 | 0% |
| AlertDispatcherAgent | — | 0 | 0% |
| OrchestratorAgent | — | 0 | 0% |
| KeepaAPIClient | — | 0 | 0% |
| API Endpoints (11) | — | 0 | 0% |
| Database Operations | — | 0 | 0% |
| LangGraph Nodes | — | 0 | 0% |
| Notification Service | — | 0 | 0% |
| Schedulers | — | 0 | 0% |

### What IS Tested (27 lines)

```python
# tests/test_agents/test_price_monitor.py
def test_calculate_volatility()      # Tests edge cases (0 price, equal prices)
def test_determine_check_interval()  # Tests 3 interval tiers (2h, 4h, 6h)
```

### Critical Test Gaps

| Priority | Component | Risk Without Tests |
|----------|-----------|-------------------|
| CRITICAL | API Endpoints (11 endpoints) | Unknown behavior, crashes, data corruption |
| CRITICAL | KeepaAPIClient (657 lines) | Rate limit violations, API key exposure |
| HIGH | AlertDispatcher (retry/duplicate logic) | Infinite loops, notification spam |
| HIGH | Database CRUD operations | Silent data loss, constraint violations |
| MEDIUM | NotificationService | Failed deliveries, malformed emails |
| MEDIUM | Scheduler timing logic | Duplicate alerts, missed checks |

### Existing Test Infrastructure

```python
# tests/conftest.py (17 lines)
# - Imports pytest, datetime
# - Defines basic fixtures
# - No database fixtures, no API test client, no mocking
```

The test infrastructure would need:
- `httpx.AsyncClient` for API endpoint testing
- SQLite in-memory for database tests
- `unittest.mock` / `pytest-mock` for Keepa API mocking
- `pytest-asyncio` (already referenced in tests)

---

## 8. Docker Setup Assessment

### Dockerfile (19 lines)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY .env.example .env         # Uses example, not real .env!
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Assessment: Development Scaffolding Only**

| Aspect | Status | Issue |
|--------|--------|-------|
| Base image | Acceptable | python:3.11-slim is reasonable |
| Multi-stage build | Missing | Image larger than necessary |
| Non-root user | Missing | Security vulnerability |
| Health check | Missing | Container orchestration blind |
| Signal handling | Missing | Graceful shutdown not ensured |
| Workers | Single uvicorn | No Gunicorn for production |
| Env handling | Broken | Copies `.env.example` as `.env` |

### docker-compose.yml (62 lines)

```yaml
services:
  app:        # FastAPI on port 8000
  db:         # PostgreSQL 15 (postgres/postgres credentials)
  redis:      # Redis 7 (configured but unused)
  scheduler:  # python -m src.scheduler
```

| Aspect | Status | Issue |
|--------|--------|-------|
| Service definitions | Acceptable | 4 services properly defined |
| Health checks | Missing | No readiness/liveness probes |
| Volume mounts | Dev-only | `./src:/app/src` exposes host filesystem |
| Credentials | Hardcoded | `postgres/postgres` in compose file |
| Logging | Missing | No log driver configuration |
| Resource limits | Missing | No CPU/memory constraints |
| Network isolation | Missing | All services on default network |
| Restart policy | Good | `unless-stopped` on all services |

### What's Missing for Production

1. **Health checks** for all services (PostgreSQL, Redis, App, Scheduler)
2. **Non-root user** in Dockerfile
3. **Gunicorn** with multiple workers instead of single uvicorn
4. **Multi-stage build** for smaller image size
5. **Proper .env handling** (not copying .env.example)
6. **CI/CD pipeline** (no GitHub Actions, no tests in build)
7. **Database migrations** (no Alembic setup)
8. **Backup/restore scripts** for PostgreSQL
9. **Prometheus metrics** endpoint
10. **Production credentials management** (secrets, not env vars)

---

## 9. Critical Issues (Sorted by Severity)

| # | Issue | Severity | Category | Fix Effort | Description |
|---|-------|----------|----------|------------|-------------|
| 1 | **Dual database schemas (UUID vs Integer PKs)** | CRITICAL | Data Layer | HIGH | Two incompatible SQLAlchemy model sets create different tables with different types. Running both will cause schema conflicts and data integrity issues. |
| 2 | **LangGraph Orchestrator is dead code** | CRITICAL | Architecture | HIGH | `orchestrator.py` is never imported. The entire LangGraph layer (3 files, 340 lines) serves no purpose. Architecture decision needed. |
| 3 | **Repository imports non-existent fields** | CRITICAL | Data Layer | LOW | `watch_repository.py` tries to use `product_name`, `old_price`, `new_price` which don't exist on the async models. Runtime crash guaranteed. |
| 4 | **`keepa` library missing from requirements.txt** | HIGH | Deploy | LOW | Docker build will fail. Add `keepa>=1.5.0` to requirements.txt. |
| 5 | **Import path inconsistency** | HIGH | Build | MEDIUM | Mix of `from services.x` and `from src.services.x` causes different behavior in different execution contexts. |
| 6 | **Dual scheduler implementations** | HIGH | Architecture | MEDIUM | `scheduler.py` (231 lines) and `scheduler/jobs.py` (269 lines) could run simultaneously, causing duplicate price checks and alerts. |
| 7 | **Deal reports generated but not delivered** | MEDIUM | Feature | MEDIUM | `scheduler/jobs.py:198-202` generates deal reports but only logs them. Users never receive deal notifications. |
| 8 | **Telegram/Discord not implemented** | MEDIUM | Feature | MEDIUM | Config exists for both channels, `AlertDispatcherAgent` has stubs, but actual sending is email-only. |

---

## 10. Architecture Decision: LangGraph — Keep or Remove?

### Option A: Embrace LangGraph (The Vision)

**What this means:**
- Make `OrchestratorAgent` the single entry point for all workflows
- Remove direct agent calls from schedulers
- Fix the workflow graph (connect deal_finder, fix error handling edges)
- Route all API calls through the orchestrator

**Pro:**
- Centralized workflow management
- Built-in state tracking (WorkflowState with status, retries, errors)
- Conditional routing (price check → alert vs. deal search → report)
- Better observability — every workflow has a UUID and timestamps
- Easier to add new workflow types (e.g., competitor monitoring)
- LangGraph is the industry standard for agent orchestration

**Con:**
- Additional dependency (langgraph, langchain, langchain-openai)
- OPENAI_API_KEY required even though no LLM is actually used
- Increased complexity for what is currently a straightforward pipeline
- WorkflowState uses dataclasses, not Pydantic — may conflict with LangGraph expectations
- The graph definition has bugs that need fixing first

**Effort:** ~2-3 weeks to fully integrate and test

### Option B: Remove LangGraph (Simplification)

**What this means:**
- Delete `src/agents/orchestrator.py`
- Delete `src/graph/` directory entirely
- Remove langgraph, langchain, langchain-openai from requirements
- Keep standalone agents with direct scheduler calls

**Pro:**
- Removes 340 lines of dead code and 3 unused dependencies
- Simplifies mental model — agents are plain Python classes
- No OPENAI_API_KEY needed
- Faster Docker builds
- Fewer potential failure points

**Con:**
- Loses the workflow state management
- No built-in retry/error handling framework
- Each scheduler must implement its own error handling
- Harder to add complex multi-step workflows later
- Loses the "architectural vision" of the project

**Effort:** ~2-3 days to clean up

### Recommendation

**For learning/portfolio purposes:** Keep LangGraph (Option A) — it demonstrates understanding of modern agent orchestration patterns.

**For production/shipping fast:** Remove LangGraph (Option B) — the current direct-agent approach works and is simpler.

---

## Appendix: File Reference

### Source Files (3,246 lines total)

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `src/services/keepa_api.py` | 657 | Keepa API client + token bucket rate limiting | Working |
| `src/api/main.py` | 409 | FastAPI REST endpoints (11 endpoints) | Working |
| `src/services/database.py` | 356 | Async SQLAlchemy models + CRUD (UUID PKs) | Working |
| `src/scheduler/jobs.py` | 269 | APScheduler background jobs | Partial |
| `src/scheduler.py` | 231 | Simple scheduler without APScheduler | Working |
| `src/repositories/watch_repository.py` | 214 | Watch/price/alert data access | Broken |
| `src/graph/nodes.py` | 184 | LangGraph workflow nodes | Dead code |
| `src/agents/alert_dispatcher.py` | 179 | Multi-channel alert dispatch (email only) | Working |
| `src/services/notification.py` | 175 | Email formatting and sending | Working |
| `src/core/database.py` | 146 | Sync SQLAlchemy models (Integer PKs) | Conflicts |
| `src/agents/deal_finder.py` | 120 | Deal scoring and filtering | Working |
| `src/agents/price_monitor.py` | 93 | Volatility-based price monitoring | Working |
| `src/graph/states.py` | 79 | Dataclasses for LangGraph state | Dead code |
| `src/agents/orchestrator.py` | 77 | LangGraph orchestrator | Dead code |
| `src/config.py` | 49 | Pydantic-settings config | Working |
| Various `__init__.py` | 8 | Package markers | — |

### Test Files (44 lines total)

| File | Lines | Tests | Coverage |
|------|-------|-------|----------|
| `tests/test_agents/test_price_monitor.py` | 27 | 2 | ~10% of PriceMonitorAgent |
| `tests/conftest.py` | 17 | — | Fixtures only |
| Other `__init__.py` | 0 | — | Empty |

### Infrastructure Files

| File | Lines | Purpose |
|------|-------|---------|
| `Dockerfile` | 19 | Python 3.11-slim container |
| `docker-compose.yml` | 62 | 4-service orchestration |
| `.env.example` | 27 | Environment variable template |
| `requirements.txt` | 40 | Dependencies (missing: keepa) |
| `README.md` | 89 | Bilingual project overview |

---

## Related Documentation

- **Accessible project overview:** [`KeepaProjectsforDataEngeneering3BranchesMerge/FOR_SMLFLG.md`](./KeepaProjectsforDataEngeneering3BranchesMerge/FOR_SMLFLG.md) — Detailed walkthrough of architecture, deployment, and errors in an engaging format.
- **This document (BigAnalysis.md)** — Technically deeper analysis with code-level findings, severity assessments, and architectural decision framework.

---

*Analysis completed: February 2026*
*Source: OpenCode 4-Agent Parallel Analysis (plan agent + 4 SubAgents) + Manual Code Review*
*Project: DataEngeeneeringKEEPA / KeepaProjectsforDataEngeneering3BranchesMerge*
