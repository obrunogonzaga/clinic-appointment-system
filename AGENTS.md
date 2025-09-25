# Repository Guidelines

## Project Structure & Module Organization
The repository is split into `backend` (FastAPI) and `frontend` (React/Vite). `backend/src` follows Clean Architecture: `domain` holds entities and exceptions, `application` encapsulates use cases, `infrastructure` manages settings, persistence, and dependency wiring, and `presentation` exposes API routers and response models. Backend tests live in `backend/tests`, while reusable scripts (seeders, maintenance) reside under `backend/scripts`. Frontend code sits in `frontend/src` grouped by feature folders such as `components/users`, `pages`, `services`, and `hooks`; public assets live in `frontend/public`. Deployment helpers and templates are under `docker/` and `render*.env`, with additional reference docs stored in `docs/`.

## Build, Test & Development Commands
Use `make quick-start` for a full-stack boot with health checks, or `docker-compose up --build` for a production-like run. Local iterative work pairs `make dev-backend` and `make dev-frontend` (run `make install` first for dependencies). `make test`, `make test-backend`, and `make test-frontend` execute suites—backend runs `pytest` with an 80% coverage gate. `make lint` invokes Black, isort, flake8, mypy, and frontend ESLint/type-checking; `make format-*` applies auto-formatters. Run `make clean` when containers or caches need a reset.

## Coding Style & Naming Conventions
Python modules use 4-space indentation, snake_case for files/functions, and PascalCase for Pydantic models or services; validate formatting with `make format-backend`. TypeScript components sit in PascalCase files, React hooks start with `use`, and shared helpers live in `frontend/src/utils`. Tailwind utility classes stay inline, while shared styles move to composable components. Before committing, run `npm run lint` and `npx prettier --write .` via `make format-frontend` to align with the ESLint/Prettier baseline.

### Frontend TypeScript & React Query specifics
- The project uses TanStack Query v5. Always pass explicit generics to hooks like `useQuery`/`useMutation` so the compiler knows the data shape.
- To preserve previous data while paginating, use `placeholderData: keepPreviousData` (imported from `@tanstack/react-query`) instead of the deprecated `keepPreviousData` option.
- Keep the config aligned with TypeScript `noImplicitAny`; if a callback parameter needs typing (e.g., `map(tag => …)`), annotate it.
- TypeScript builds run with `noUnusedLocals`. Quando desabilitar interações (ex.: selects in-line), remova ou reutilize handlers ligados a elas e execute `npm run build` antes do deploy para evitar falhas na pipeline.

## Testing Guidelines
Mirror backend module names with `test_<module>.py` files and lean on fixtures in `backend/tests/conftest.py`; add integration tests whenever repositories or external gateways change. Frontend specs belong next to their components with a `.test.tsx` suffix and run through `npm test`. End-to-end flows live in the top-level `tests/` package—seed sample data via `make db-seed` and execute `npm run e2e` from that directory.

## Commit & Pull Request Guidelines
Commits follow the conventional scheme observed in history (`feat:`, `fix:`, `chore:`) with imperative, ≤72-character subjects and optional scopes (`feat(frontend):`). Bundle related changes per layer and reference tickets in the body when relevant. Pull requests should summarize the change, list affected services (`backend`, `frontend`, `tests`), link issues, and attach screenshots or screen recordings for UI updates. Document manual/automated test results, call out schema or environment changes, and request review from the owning maintainer before merging.
