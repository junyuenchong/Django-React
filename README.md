# React + Django + PostgreSQL + Redis (CRUD Demo)

Single-page React frontend + Django REST API backend with PostgreSQL and Redis caching. Includes cursor-based pagination, Redis list caching + invalidation, unit/integration tests, Docker, and CI.

## Tech Stack

- Frontend: React (Vite), Tailwind CSS
- Frontend data layer: React Query (`@tanstack/react-query`)
- Backend: Django, Django REST Framework, django-filter
- Database: PostgreSQL
- Cache: Redis (via `django-redis`)
- DevOps: Docker Compose, GitHub Actions CI/CD, AWS EC2
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
│           ├── http_cache.py        # ETag/Last-Modified helpers
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
        ├── hooks/
        │   └── useItemsCrud.ts
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
        └── globals.css
```

Frontend entry points: `frontend/src/main.tsx`, `frontend/src/App.tsx`

Frontend performance notes:

- `main.tsx` lazy-loads `App` with `React.lazy` + `Suspense` (entry-level code splitting)
- `App.tsx` lazy-loads heavy UI blocks (`ItemForm`, `ItemTable`, `PaginationControls`)
- CRUD/query state is extracted into `hooks/useItemsCrud.ts` for cleaner UI components
- The item table renders rows in ascending `id` order for a predictable 1,2,3-style view
- React Query keeps previous page data during pagination to avoid UI flicker
- React Query prefetches the next page for faster page navigation
- React Query retries only server-side failures (5xx), and skips retry for 4xx errors
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
- `ITEMS_LIST_CACHE_TTL_SEARCH_SECONDS`, `ITEMS_LIST_CACHE_TTL_LARGE_PAGE_SECONDS`

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
- Tiered TTL strategy for list cache:
  - Search query (`q`) uses `ITEMS_LIST_CACHE_TTL_SEARCH_SECONDS`
  - Larger page sizes use `ITEMS_LIST_CACHE_TTL_LARGE_PAGE_SECONDS`
  - Default list uses `ITEMS_LIST_CACHE_TTL_SECONDS`
- Conditional response caching:
  - List endpoint returns `ETag` and `Last-Modified`
  - Supports `If-None-Match` / `If-Modified-Since` with `304 Not Modified`
- DB indexes: model indexes on `title` and a composite index for ordering
- Queryset optimization entry point:
  - `ItemRepository.base_queryset()` includes `select_related/prefetch_related` hooks for future relation-heavy models
- Production-oriented Redis settings: configurable TTL, socket connect/read timeout, max connections, retry-on-timeout, and key prefix

### N+1 Query Problem and Solution

- What is N+1:
  - The API runs 1 query to load a list, then runs 1 extra query per row for related data (`N` more queries).
  - Total becomes `1 + N` queries, which gets slower as list size grows.
- Why it matters:
  - More DB round-trips increase latency and DB load.
  - It becomes a bottleneck under higher traffic.
- Current prevention in this project:
  - `ItemRepository.base_queryset()` is the single place that builds list querysets.
  - It already provides hooks for relation optimization:
    - `select_related_fields`
    - `prefetch_related_fields`
  - The list API always goes through repository -> service -> view flow, so optimization is centralized.
- How to apply when relations are added:
  - Use `select_related(...)` for foreign key / one-to-one fields.
  - Use `prefetch_related(...)` for many-to-many or reverse relations.
  - Keep these optimizations in repository methods (not in views) for maintainability.

## Error Handling

- Global DRF exception handler returns a consistent JSON shape:
  `{"error": {"type": "...", "message": "..."}}`
- Redis/cache failures are handled gracefully (service falls back to no-cache mode so CRUD still works)
- Backend service layer uses explicit typing (avoids `Any`) and defensive cache helpers to keep runtime behavior predictable

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

## CD (Auto Deploy to EC2)

Workflow: `.github/workflows/cd.yml`

When code is pushed to `main`, GitHub Actions connects to your EC2 host over SSH and deploys backend changes automatically:

- `cd ~/Django-React`
- `git fetch --all && git checkout main && git pull origin main`
- `cd backend`
- `docker compose up -d --build backend`
- print container status and recent backend logs

### Required GitHub Secrets

Add these in `GitHub repo -> Settings -> Secrets and variables -> Actions`:

- `EC2_HOST`: your EC2 public IPv4 (example: `47.131.86.17`)
- `EC2_USER`: SSH user (usually `ubuntu`)
- `EC2_SSH_KEY`: private key content (`.pem` file text)
- `EC2_PORT`: SSH port (usually `22`)

### AWS EC2 Ubuntu Setup (Step-by-Step)

1. Connect to Ubuntu EC2:

   ```bash
   chmod 400 ~/.ssh/SSH.pem
   ssh -i ~/.ssh/SSH.pem ubuntu@47.131.86.17
   ```

2. Update packages and install Docker:

   ```bash
   sudo apt update
   sudo apt install -y ca-certificates curl gnupg lsb-release
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo usermod -aG docker $USER
   ```

3. Reconnect SSH (required after group change), then verify Docker:

   ```bash
   exit
   ssh -i ~/.ssh/SSH.pem ubuntu@47.131.86.17
   docker --version
   docker compose version
   ```

4. Clone repository on EC2:

   ```bash
   git clone https://github.com/junyuenchong/Django-React.git ~/Django-React
   cd ~/Django-React/backend
   ```

5. Create backend env and set minimum values:

   ```bash
   cp .env.example .env
   ```

   Update `backend/.env`:
   - `DJANGO_ALLOWED_HOSTS=47.131.86.17,localhost,127.0.0.1`
   - `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://192.168.1.3:5173,http://26.248.135.138:5173`

6. Deploy backend stack:

   ```bash
   cd ~/Django-React/backend
   docker compose up -d --build
   docker compose ps
   ```

7. Verify health:

   ```bash
   curl -i http://127.0.0.1:8000/healthz
   ```

   Expected: `HTTP 200` and `{"status":"ok"}`.

8. AWS Security Group (EC2 inbound rules):
   - `22` (SSH)
   - `8000` (API access for this demo)

### Repository Variables Fallback (Optional)

The CD workflow supports both `secrets.*` and `vars.*` values:

- Primary source: `Repository secrets`
- Fallback source: `Repository variables`

Supported keys:

- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `EC2_PORT`

### Notes

- This CD flow is backend-focused and uses `backend/docker-compose.yml`.
- Ensure your EC2 instance already has Docker + Docker Compose installed.
- Ensure repository path on EC2 is `~/Django-React` (or update `cd.yml` script path).
- If deployment fails with `EC2_HOST is empty`, set `EC2_HOST` in repository secrets or variables and rerun the workflow.

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
