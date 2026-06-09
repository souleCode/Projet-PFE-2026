# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EPI Detection is a full-stack PPE (Personal Protective Equipment) compliance monitoring system using YOLO AI for real-time detection. The backend is Django REST Framework with JWT auth; the frontend is React + TypeScript + Vite. Deployed on AWS via CodeBuild/CodeDeploy.

## Development Commands

### Backend (from `backend/api/`)

```powershell
# First-time setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python manage.py migrate

# Run dev server (http://localhost:8000)
python manage.py runserver

# Run a single test
python manage.py test Apps.Users.tests
```

### Frontend (from `frontend/`)

```powershell
npm install
npm run dev      # Vite dev server at http://localhost:8080
npm run build    # Production build
npm run lint     # ESLint
npm test         # Vitest unit tests
```

## Architecture

### Backend (`backend/api/`)

Django project with modular apps under `Apps/`:

- **Users** — JWT auth via HttpOnly cookies, role-based access. Custom `CookieJWTAuthentication` reads tokens from cookies (not Authorization header). Access token: 8h, refresh: 7 days.
- **Cameras** — Camera CRUD and status management (`active`/`inactive`/`error`)
- **detection** — YOLO inference endpoint (`POST /api/detection/detect/`). Model at `models/best.pt` (path set via `YOLO_MODEL_PATH` in settings).
- **alertes** — Alert creation, listing, bulk update. Alert statuses use unaccented values (`resolu`, not `résolu`).
- **audits** — Audit sessions with captures, PDF report generation via ReportLab, CSV export.
- **RegleSHE** — HSE rules per camera. Has both legacy `epi_type` field and newer `epi_criticites` field (migration in progress — use `epi_criticites`).

Settings hierarchy: all config in `api/settings.py`. AWS S3 storage activates only when `USE_S3=True` and all AWS env vars are present. Gemini AI rate-limited to 5 queries/day.

### Frontend (`frontend/src/`)

- **App.tsx** — Root with React Router v6 routes and `AuthProvider` wrapping all protected routes.
- **context/AuthContext.tsx** — Global auth state; login/logout, current user, role checks.
- **lib/api.ts** — Central API client (`apiFetch`). Base URL resolves via `VITE_API_BASE_URL` → `VITE_API_URL` → hardcoded production URL. All cookie credentials included by default.
- **lib/epiDetectionApi.ts** — Detection-specific API helpers.
- **pages/** — One file per route: `Dashboard`, `Cameras`, `Alerts`, `HSERules`, `Reporting`, `AuditDetail`, `Admin`, `GeminiAnalyses`.
- **components/WebcamFeed.tsx** — Core camera feed component driving live detection.

Path alias `@` maps to `src/` (configured in `tsconfig.json` and `vite.config.ts`).

### API Endpoints Summary

| Prefix | App |
|---|---|
| `/api/users/` | Auth, user CRUD |
| `/api/cameras/` | Camera management |
| `/api/detection/` | YOLO detect, logs, stats |
| `/api/alerts/` | Alerts, bulk update |
| `/api/rules/hse-rules/` | HSE rule configuration |
| `/api/audits/` | Audits, captures, PDF/CSV export |

### Deployment

CI/CD: AWS CodeBuild (`buildspec.yml`) → CodeDeploy (`appspec.yml`). Deployment scripts in `backend/api/scripts/` manage Gunicorn startup and Nginx reverse proxy setup. Python runtime is 3.11.

## Key Configuration

- **CORS**: `localhost:5173`, `localhost:8080`, `localhost:3000` plus production URLs. `CORS_ALLOW_CREDENTIALS = True` required for cookie auth.
- **Vite port**: `8080` in `vite.config.ts` (CORS also allows `5173` as fallback).
- **Database**: SQLite for local dev (`db.sqlite3`), PostgreSQL in production.
- **Frontend env vars**: Create `frontend/.env.local` with `VITE_API_BASE_URL=http://localhost:8000` for local development.

## Known Inconsistencies

- `VITE_API_BASE_URL` and `VITE_API_URL` are both used in the frontend — they both resolve to the same value, but should be harmonized.
- Camera status: backend uses `active`/`inactive`/`error`; some frontend code uses `online`/`offline` — map on the frontend side.
- Alert status accented chars: always use `resolu`/`en_cours`/`nouveau` (no accents) when sending to the backend.
