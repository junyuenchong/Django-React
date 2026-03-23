# React + Django + PostgreSQL + Redis (CRUD Demo)

Single-page React frontend + Django REST API backend with PostgreSQL and Redis caching. Includes cursor-based pagination, Redis list caching + invalidation, unit/integration tests, Docker, and CI.

## Tech Stack

- Frontend: React (Vite), Tailwind CSS
- Frontend data layer: React Query (`@tanstack/react-query`)
- Backend: Django, Django REST Framework, django-filter
- Database: PostgreSQL
- Cache: Redis (via `django-redis`)
- DevOps: Docker Compose, GitHub Actions CI
- Testing: pytest + pytest-django

## Services

- `backend` (Django REST API on `http://localhost:8000`)
- `db` (PostgreSQL on `localhost:5432`)
- `redis` (Redis on `localhost:6379`)
- `adminer` (DB UI on `http://localhost:8080`)
- (Optional) Frontend (Vite on `http://localhost:5173`)

## Backend Structure

```text
my_project/
├── backend/                         # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── config/                      # Main project settings & config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── settings_test.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── exceptions.py
│   ├── core/                        # Shared backend utilities
│   │   └── pagination.py
│   └── apps/                        # All Django apps
│       └── items/
│           ├── migrations/
│           │   └── 0001_initial.py
│           ├── management/
│           │   └── commands/
│           │       └── seed_items.py
│           ├── seeder/
│           │   └── items.py
│           ├── tests/
│           │   ├── test_item_api.py
│           │   ├── test_services_cache.py
│           │   └── test_error_handling_cache.py
│           ├── models.py            # Model layer
│           ├── views.py             # API controller (DRF)
│           ├── urls.py
│           ├── serializers.py       # API schema/validation
│           ├── repositories.py      # Repository layer
│           └── services.py          # Service layer
```

Backend request flow: `views.py` -> `services.py` -> `repositories.py` -> `models.py`

## Frontend Structure

```text
my_project/
└── frontend/                        # React + Vite frontend
    ├── package.json
    ├── package-lock.json
    ├── index.html
    ├── .env.example
    ├── vite.config.ts
    ├── tsconfig.json
    ├── jest.config.cjs
    ├── prettier.config.cjs
    ├── postcss.config.cjs
    ├── tailwind.config.cjs
    ├── public/                      # Global static assets
    │   ├── robots.txt
    │   ├── sitemap.xml
    │   └── favicon.svg
    └── src/
        ├── api/
        │   └── itemsApi.ts
        ├── components/
        │   ├── ItemForm.tsx
        │   ├── ItemTable.tsx
        │   └── PaginationControls.tsx
        ├── types/
        │   └── item.ts
        ├── test/
        │   └── setupTests.ts
        ├── App.tsx
        ├── App.test.tsx
        ├── main.tsx
        └── styles.css
```

Frontend entry points: `frontend/src/main.tsx`, `frontend/src/App.tsx`

Frontend performance notes:
- `main.tsx` lazy-loads `App` with `React.lazy` + `Suspense` (entry-level code splitting)
- `App.tsx` lazy-loads heavy UI blocks (`ItemForm`, `ItemTable`, `PaginationControls`)
- Data fetching/mutations are handled by React Query for cache + invalidation control

## Environment Variables

1. Backend env (Django):
   - `cd backend`
   - `cp .env.example .env` (or create `.env` by copying)
   - The backend container reads `.env` values used by `backend/docker-compose.yml`.
2. Frontend env (Vite):
   - `cd frontend`
   - `cp .env.example .env` (or create `.env` by copying)
   - Frontend uses `VITE_API_URL` to call the Django API.

Key variables (backend, from `backend/.env.example`):

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `REDIS_PORT`, `ADMINER_PORT`
- `REDIS_DB`, `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`
- `REDIS_MAX_CONNECTIONS`, `REDIS_RETRY_ON_TIMEOUT`, `REDIS_KEY_PREFIX`
- `BACKEND_PORT`
- `DJANGO_DEBUG`, `DJANGO_SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`
- `ITEMS_LIST_CACHE_TTL_SECONDS`

## How to Run Everything (Local)

1. Start backend + dependencies (Docker):
   ```powershell
   cd "C:\Users\LEGION\Desktop\MyInterviewProject\React-Django\backend"
   docker compose up -d --build --force-recreate
   ```
2. (Recommended) Seed demo data:
   ```powershell
   docker compose run --rm backend sh -c "cd /app && python manage.py seed_items --count 20 --clear"
   ```
3. Verify backend:
   - `GET http://localhost:8000/healthz` (should return `{"status":"ok"}`)
4. Start the frontend (Vite, local):
   ```powershell
   cd "C:\Users\LEGION\Desktop\MyInterviewProject\React-Django\frontend"
   npm install
   cp .env.example .env
   npm run dev
   ```
5. Open:
   - `http://localhost:5173`

## API Endpoints (CRUD)

- `GET    /api/items/?q=&page_size=&cursor=` (cursor-based pagination)
- `POST   /api/items/`
- `PATCH  /api/items/{id}/`
- `DELETE /api/items/{id}/`
- `GET    /healthz`

## Caching & Performance

- Cursor pagination: stable ordering using `-id`
- Redis caching: `GET list` caches the whole paginated response
- Cache invalidation: `POST/PATCH/DELETE` bumps a version key so cached lists are naturally invalidated
- DB indexes: model indexes on `title` and a composite index for ordering
- Production-oriented Redis settings: configurable TTL, socket connect/read timeout, max connections, retry-on-timeout, and key prefix

## Error Handling

- Global DRF exception handler returns a consistent JSON shape:
  `{"error": {"type": "...", "message": "..."}}`
- Redis/cache failures are handled gracefully (service falls back to no-cache mode so CRUD still works)

## Testing

### Unit Tests

```powershell
cd backend
docker compose run --rm backend sh -c "cd /app && pip install -r requirements-dev.txt && pytest -m unit"
```

### Integration Tests

```powershell
cd backend
docker compose run --rm backend sh -c "cd /app && pip install -r requirements-dev.txt && pytest -m integration"
```

## CI (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

- Installs `backend/requirements.txt` and `backend/requirements-dev.txt`
- Runs:
  - `pytest -m unit`
  - `pytest -m integration`

## Code Quality Gates (Pre-commit / Hooks)

This repo runs checks locally before you commit/push, so issues are caught early.

### Pre-commit (Python)

Config: `.pre-commit-config.yaml`

- `isort` (import order check)
- `black` (format check)
- `mypy` (typecheck)

Setup (once):

```powershell
pip install -r backend/requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

### Git Hooks (Frontend)

On `git commit` and `git push` we run:

- `npm run typecheck`
- `npm run format:check`
- `npm test -- --watchAll=false`

Commit message style is enforced by `commitlint` (conventional commits).
Config: `commitlint.config.cjs`

Windows note: in this environment the git repository root is `C:\` (so `.git` lives at `C:\.git`), so hooks live under `C:\.git\hooks\`.

### Conventional Commit Types (commitlint)

Allowed `type` values:

| Type       | Meaning                                                                               |
| ---------- | ------------------------------------------------------------------------------------- |
| `feat`     | New feature                                                                           |
| `fix`      | Bug fix                                                                               |
| `test`     | Add/update tests                                                                      |
| `refactor` | Code change (no new feature/fix)                                                      |
| `chore`    | Setup/config/deps changes                                                             |
| `docs`     | Documentation changes                                                                 |
| `style`    | Formatting-only changes                                                               |
| `perf`     | Performance improvements (e.g., faster queries, caching, indexing, better pagination) |

Examples:

- `feat: add cursor pagination for items`
- `fix: handle cache failure gracefully when listing items`
- `test: add integration test for CRUD + pagination`
- `refactor: reorganize items service/repository layers`
- `chore: add ruff/black/isort/mypy checks`
- `style: reformat frontend files with prettier`
- `docs: update README with backend structure`
- `perf: add database indexes for faster item ordering`

## Notes for Interview Demo

1. Run `docker compose up ...` from `backend/` (backend-only docker)
2. Run seeder command to populate data quickly
3. Start React and demonstrate:
   - Create/Edit/Delete
   - Cursor pagination (Next/Previous)
   - Search by `title`
