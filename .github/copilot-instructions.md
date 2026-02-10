# Copilot Instructions for Agenda Escolar

This file provides guidance for Copilot when working on this repository.

## Quick Reference

**Monorepo Structure**: Frontend (React + TypeScript) and Backend (FastAPI + Python)
- Frontend: `/frontend/` - All npm commands run from here
- Backend: `/backend/` - All Python commands run from here

## Build, Test, and Lint Commands

### Frontend

Run all commands from `frontend/` directory:

```bash
# Development
npm run dev              # Start dev server (http://localhost:3000)
npm run build            # Build for production
npm run preview          # Preview production build

# Testing (Vitest configured)
npm run test             # Run all tests once
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate coverage report

# Run a single test file
npm run test -- src/path/to/test.test.ts
```

### Backend

Run all commands from `backend/` directory:

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Development
uvicorn src.infrastructure.api.main:app --reload

# Testing (pytest configured)
pytest                           # Run all tests
pytest tests/unit                # Run unit tests only
pytest tests/integration         # Run integration tests only
pytest tests/ -k "test_name"     # Run specific test
pytest --cov=src                 # Run with coverage

# Code Quality
black src/ tests/                # Format code
isort src/ tests/                # Sort imports
flake8 src/ tests/               # Lint
mypy src/                        # Type check
```

## High-Level Architecture

### Project Overview

**Agenda Escolar Pro** is a school agenda application for managing children's school activities, meals, exams, and schedules. It features AI-powered dinner suggestions via Google Gemini.

### Frontend Architecture (React 19 + TypeScript)

**Core Pattern**: Centralized state management in `App.tsx` with view-based routing

- **State Flow**: App manages all state → passes filtered data (by active student) to page components → pages use setter functions that merge changes back
- **Multi-profile Support**: All data scoped by `studentId`. When switching students, pages re-filter data for the active profile
- **Pages**: HomePage, ManagePage, ProfilePage, DinnersPage
- **Components**: Modular UI components in `/src/components/` (BottomNav, ItemFormModal, icons)
- **Services**: 
  - `aiService.ts` - Gemini AI integration (suggestDinner, generateDinnerPlan, generateShoppingList)
  - Respects profile allergies and excluded foods
- **Persistence**: localStorage with `school-agenda-*` prefix via `useLocalStorage` hook

**Key Convention**: When updating student-scoped data, filter by `studentId`, modify, then merge back into global state:
```typescript
setAllDinners(prev => {
  const current = prev.filter(d => d.studentId === activeProfileId);
  const others = prev.filter(d => d.studentId !== activeProfileId);
  const updated = /* modification */;
  return [...others, ...updated.map(d => ({...d, studentId: activeProfileId}))];
});
```

### Backend Architecture (FastAPI + Python)

**Pattern**: Clean Architecture (Hexagonal)

- **Domain**: Pure business logic and models (`src/domain/models.py`)
- **Application**: Use cases and orchestration (`src/application/use_cases/`)
  - Schemas for input/output validation (`src/application/schemas/`)
  - Exception handling (`src/application/exceptions.py`)
- **Infrastructure**: 
  - FastAPI routes (`src/infrastructure/api/`)
  - PostgreSQL repositories (`src/infrastructure/repositories/`)
  - Services for external integrations (`src/infrastructure/services/`)
  - Security utilities (`src/infrastructure/security/`)
  - Database config via Alembic migrations
- **Tests**: Organized by `tests/unit/` and `tests/integration/`

**Note**: Backend is scaffolded but not fully implemented. Use this structure when adding features.

## Key Conventions

### Frontend

1. **Component Naming**: PascalCase for components, files match component name
2. **Types**: All TypeScript interfaces in `src/types.ts` (StudentProfile, Subject, Exam, MenuItem, DinnerItem, SchoolEvent, Center, Contact)
3. **Features Toggle**: Each profile has `activeModules` array to enable/disable features (subjects, exams, menu, events, dinner, contacts)
4. **Dark Mode**: Theme state in ProfilePage, persisted to localStorage, applied via `document.documentElement` in App.tsx
5. **Environment**: GEMINI_API_KEY in `.env.local` (see frontend/README.md for setup)

### Backend

1. **Project Structure**: All code under `src/`, tests under `tests/` with unit/integration subdirs
2. **Pydantic Models**: Use for validation in use cases, return in DTOs
3. **Database**: Alembic migrations in `backend/migrations/` - run migrations before tests
4. **Async**: pytest configured with `asyncio_mode = auto` for async endpoint testing
5. **Markers**: Use `@pytest.mark.unit` and `@pytest.mark.integration` for test organization
6. **Environment**: `.env.example` provided - copy to `.env` before running

### Monorepo

1. **Separate Dependencies**: Frontend uses npm, backend uses pip - manage separately
2. **Directory Discipline**: Run commands from appropriate directory (frontend/ or backend/)
3. **Git Workflow**: Repository already initialized

## Data Models Reference

Key TypeScript interfaces in `frontend/src/types.ts` all include `studentId` for multi-profile support:
- `StudentProfile` - Child profile with school info, allergies, excluded foods, activeModules
- `Subject` - Classes (days, time, teacher)
- `Exam` - Upcoming exams (subject, date, topic)
- `MenuItem` - School lunch menu by date
- `DinnerItem` - Planned dinners with ingredients
- `SchoolEvent` - Calendar events
- `Center` - Educational centers
- `Contact` - Contact info per center

## Common Patterns

### Running a Single Test

**Frontend**:
```bash
cd frontend
npm run test -- src/components/BottomNav.test.ts
```

**Backend**:
```bash
cd backend
pytest tests/unit/application/test_use_cases.py::TestProfileUseCases::test_create_profile -v
```

### Switching Frontend Between Dev and Prod

```bash
cd frontend
npm run build    # Compile to dist/
npm run preview  # Test production build locally
```

### Database Migrations (Backend)

```bash
cd backend
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback
```

## Environment Setup

### Frontend
```bash
cd frontend
npm install
# Create .env.local with GEMINI_API_KEY
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env from .env.example
uvicorn src.infrastructure.api.main:app --reload
```

## Notes

- Backend is scaffolded but not fully implemented - use provided structure for new endpoints
- Frontend testing framework exists but not yet configured - when adding tests, use Vitest + React Testing Library
- All AI calls use Google Gemini API (frontend only currently)
