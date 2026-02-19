# Keeper System Deep-Dive (Feb 5, 2026)

## Overview & Purpose
- Amazon price monitoring and deal-finding platform built on FastAPI, LangGraph, and Keepa API.
- Three agents (Price Monitor, Deal Finder, Alert Dispatcher) coordinated by an Orchestrator; persistence in PostgreSQL; notifications via email/Telegram/Discord.
- Goals: trigger alerts when prices drop below targets, deliver daily deal reports, respect Keepa rate limits and user channel preferences.

## Architecture & Data Flow
- **Ingress:** FastAPI app (`src/api/main.py`) exposes REST endpoints for health, watches CRUD, price checks, deal search, and rate-limit status.
- **Core Logic:** Agents in `src/agents/` and LangGraph nodes in `src/graph/` orchestrate workflows (price_check, deal_report). Agents call services for Keepa data and notifications.
- **Persistence:** Two parallel schema stacks exist (async in `src/services/database.py`, sync in `src/core/database.py` + `src/repositories/`). Both target PostgreSQL; duplication is a major risk.
- **Scheduling:** APScheduler jobs (`src/scheduler/jobs.py`) for 30-min price checks, 06:00 UTC deal reports, Monday cleanup; separate simple scheduler (`src/scheduler.py`) for 6-hour loops/manual triggers.
- **Egress:** Notifications formatted in `src/services/notification.py`; currently only email send implemented, with placeholders for Telegram/Discord.

## Components (by responsibility)
- `src/api/main.py` – FastAPI app, Pydantic request/response models, endpoints. Uses Keepa client and scheduler helpers.
- `src/agents/orchestrator.py` – Creates LangGraph workflow and dispatches price_check/deal_report runs.
- `src/agents/price_monitor.py` – Batch price queries, simple alert condition (≤ target * 1.01), volatility-based next-interval calculation.
- `src/agents/deal_finder.py` – Keepa deals query, deal scoring, spam filtering, HTML report generation.
- `src/agents/alert_dispatcher.py` – Input validation, duplicate suppression (1h window), per-user rate limit (10/hour), retries; only email channel wired.
- `src/graph/states.py` & `src/graph/nodes.py` – Workflow state dataclasses; nodes for price monitor, deal finder, alert dispatcher, error handler; graph edges join price/deal nodes to alert dispatcher.
- `src/services/keepa_api.py` – Async Keepa wrapper with token bucket, status refresh, product query, deals search, price history; exposes legacy async facade `keepa_client`.
- `src/services/database.py` – Async SQLAlchemy models (User, WatchedProduct, PriceHistory, PriceAlert, DealFilter, DealReport) and CRUD helpers.
- `src/services/notification.py` – Email send via aiosmtplib, templated alert and deal report formatting.
- `src/core/database.py` & `src/repositories/watch_repository.py` – Sync SQLAlchemy models and repositories used by APScheduler jobs; schema diverges from async models (different table names/types).
- `src/scheduler/jobs.py` – APScheduler-based background jobs; uses sync repo stack.
- `src/scheduler.py` – Async price-check loop using async services stack.
- `prompts/*.md` – System prompts for Orchestrator, Price Monitor, Deal Finder, Alert Dispatcher (German/English); define operational constraints and fallback logic.

## Database Schema & Data Lifecycle
- Async stack (`services/database.py`):
  - `users`, `watched_products`, `price_history`, `price_alerts`, `deal_filters`, `deal_reports`.
  - UUID primary keys; status enums; history rows recorded per check; alerts created when price crosses target.
- Sync stack (`core/database.py` + `repositories/`):
  - `users`, `watches`, `price_history`, `alerts` with integer PKs and different column names; volatility score stored on watch; alert channel flags.
- Lifecycle (intended async path): create_watch → optional current price fetch → periodic `run_price_check`/scheduler updates price and history → create_price_alert when under target → alert dispatcher sends and marks sent.
- Divergence risk: two schemas are incompatible; code paths mix async and sync stacks (see Risks).

## External Services & Config
- Keepa API via `keepa` library; token bucket defaults 20 tokens/min with async wait and status refresh.
- Notifications: email via SMTP credentials (`SMTP_*` env vars); Telegram/Discord placeholders in alerts and settings but not fully wired.
- Environment (`src/config.py`, `.env.example`): requires `KEEPA_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL`; optional SMTP/Telegram/Discord. Defaults point to local Postgres/Redis.
- Docker: `docker-compose.yml` runs app, db, redis, scheduler; `Dockerfile` builds uvicorn app image on python:3.11-slim.

## API Surface (FastAPI)
- `GET /health` – token status summary (watches_count hardcoded 0).
- `GET /api/v1/status` – token bucket + Keepa rate-limit info.
- `GET /api/v1/watches?user_id=` – list user watches (async DB).
- `POST /api/v1/watches` – create watch after Keepa price fetch; validates ASIN length and target > 0.
- `DELETE /api/v1/watches/{id}` – placeholder returns success without DB mutation.
- `POST /api/v1/price/check` – manual price lookup via Keepa.
- `POST /api/v1/price/check-all` – runs async scheduler `run_immediate_check`.
- `POST /api/v1/deals/search` – filters deals; **bug:** calls async `client.search_deals` without `await`, so coroutine is returned instead of data; filter fields partly unused.
- `GET /api/v1/tokens`, `GET /api/v1/rate-limit` – expose token bucket and Keepa status.

## Workflows & Scheduling
- LangGraph workflow: entry `price_monitor` → `alert_dispatcher`; `deal_finder` can feed `alert_dispatcher`; `error_handler` on failure with retry up to `max_retries`.
- Price monitor node triggers alerts when current_price ≤ target * 1.01; uses Keepa legacy client.
- Deal finder node pulls Keepa deals with category/discount filters, scores, keeps top 15.
- Alert dispatcher node formats and sends email for unsent alerts.
- APScheduler jobs: 30-min price checks, 06:00 UTC daily deals, Monday cleanup of 90+ day data; use sync repository stack and synchronous Keepa client calls.
- Standalone scheduler (`src/scheduler.py`): 6-hour loop, uses async services stack.

## Prompts & Behavioral Rules (high level)
- Orchestrator: prioritize latency <2s, rate-limit awareness, retry/backoff, seller-tier preference, GDPR logging hygiene.
- Price Monitor: batch size 50, adaptive intervals (2h/4h/6h by volatility), double-check to avoid false alerts, prevent duplicate alerts within 1h.
- Deal Finder: score by discount/rating/sales rank; drop spam (ratings <3.5, price <10, drop-ship keywords, >80% discount).
- Alert Dispatcher: rate limit 10 alerts/hour/user, duplicate window 1h, retries with delays [0, 30s, 120s]; fallback channels noted in prompt though code only emails.

## Risks & Gaps (prioritized)
- **High — Dual DB schemas**: async (`services/database.py`) vs sync (`core/database.py`/`repositories`) cause diverging tables and model types; schedulers and API use different stacks. Consolidate to one schema and session type.
- **High — Async bug in deals endpoint**: `client.search_deals` not awaited; endpoint returns coroutine and likely 500. Await call and adjust filters to Keepa wrapper signature.
- **High — Keepa client initialization**: `Keepa` object created at import; failures set `_is_initialized=False` and later calls raise, but API endpoints don’t handle initialization failure gracefully.
- **Medium — Notification channels**: Telegram/Discord referenced in prompts and alert logic but not implemented in `notification_service` or `alert_dispatcher.send_alert`.
- **Medium — Scheduler parity**: APScheduler jobs use sync repo stack; async scheduler uses async stack; risk of duplicate checks and inconsistent data if both run.
- **Medium — Delete watch endpoint**: returns success without DB change; can mislead clients.
- **Low — Health count**: watches_count hardcoded 0; should query DB.
- **Low — Tests**: only price monitor interval/volatility tests; no coverage for API, Keepa client, schedulers, or alert logic.
- **Low — Logging/observability**: minimal structured logging; prompts prescribe audit logs but code largely silent aside from scheduler logs.

## Testing Status & Recommendations
- Current automated tests: `tests/test_agents/test_price_monitor.py` only; pytest not installed in env (command failed).
- Recommended additions:
  - API endpoint tests with async client (happy/validation/error paths).
  - Keepa client token bucket unit tests (wait/consume/refill).
  - Alert dispatcher duplicate/rate-limit and retry behavior.
  - Scheduler job integration test with in-memory DB.
  - Deal scoring and spam filter tests with edge cases.

## Next Steps (suggested)
1) Unify database schema (choose async or sync), migrate repositories/schedulers to it, and remove the duplicate stack.
2) Fix async bug in `/api/v1/deals/search`; add proper filter plumbing to Keepa wrapper.
3) Implement missing notification channels or strip from prompts until supported.
4) Make delete watch endpoint perform soft delete/inactivation.
5) Add pytest dependency and expand test suite as outlined; wire CI.
6) Enhance health/status endpoints with real counts and error surfacing.

## Glossary
- **ASIN**: Amazon Standard Identification Number (10-char).
- **Keepa tokens**: Credits consumed per API call; refilled per minute.
- **Watch**: User-defined product with target price to monitor.
- **Deal Filter**: User criteria for daily deal reports.
- **Alert**: Notification triggered when price crosses target.
