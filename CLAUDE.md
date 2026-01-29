# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Agenda Escolar Pro** - A school agenda application that helps parents manage their children's school activities, meals, exams, and schedules. The app features AI-powered dinner suggestions based on school menus and dietary restrictions.

## Technology Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with dark mode support
- **AI Integration**: Google Gemini AI (`@google/genai`)
- **State Management**: Custom hooks with localStorage persistence
- **Testing**: Vitest

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Architecture**: Clean Architecture/Hexagonal pattern
  - `domain/` - Domain models and business logic
  - `application/` - Use cases and application services
  - `infrastructure/` - External interfaces (API endpoints, database repositories)
- **Testing**: pytest

**Note**: Backend is currently scaffolded but not implemented yet.

## Architecture

This is a **monorepo** structure:

```
agenda_escolar/
├── frontend/                   # React + TypeScript + Tailwind frontend
│   ├── app/                    # Page components
│   ├── components/             # Reusable UI components
│   ├── hooks/                  # Custom hooks
│   ├── services/               # API and AI services
│   └── src/                    # Test setup
└── backend/                    # FastAPI + PostgreSQL backend
    ├── src/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    │       ├── api/
    │       └── repositories/
    └── tests/
```

### Frontend Architecture

**UI Pattern**: Single-page application with view-based routing (home, dinners, manage, profile)

**Key Architecture Patterns:**
- **Multi-profile support**: All data is scoped by `studentId` - profiles, subjects, exams, and dinners are filtered per active child
- **Modular features**: Each feature (subjects, exams, menu, events, dinner, contacts) can be toggled on/off per profile via `activeModules`
- **Centralized state**: `App.tsx` manages all state and passes filtered data to child pages
- **Data flow**: Pages receive filtered data (for active profile) and setter functions that handle merging changes back into global state

**File Structure:**
- `App.tsx` - Root component, state management, view routing
- `types.ts` - All TypeScript interfaces
- `app/` - Page components (HomePage, ManagePage, ProfilePage, DinnersPage)
- `components/` - Reusable UI components (BottomNav, ItemFormModal, icons)
- `services/aiService.ts` - Gemini AI integration for dinner suggestions
- `hooks/useLocalStorage.ts` - localStorage persistence hook

### Backend Architecture (Planned)

Following **Clean Architecture** principles:
- **Domain Layer**: Pure business logic, entities, value objects
- **Application Layer**: Use cases, orchestration, DTOs
- **Infrastructure Layer**:
  - API endpoints (FastAPI routes)
  - PostgreSQL repositories
  - External service integrations

## Development Commands

### Frontend

All commands must be run from `frontend/`:

```bash
cd frontend

# Development
npm install              # Install dependencies
npm run dev              # Start dev server on http://localhost:3000
npm run build            # Build for production
npm run preview          # Preview production build

# Testing
npm run test             # Run vitest tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
```

### Backend (When Implemented)

Expected commands from `backend/`:

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Development
uvicorn src.infrastructure.api.main:app --reload  # Run FastAPI server

# Testing
pytest                    # Run all tests
pytest tests/unit         # Run unit tests only
pytest tests/integration  # Run integration tests only
pytest -v                 # Verbose output
pytest --cov              # Run with coverage
```

## Environment Variables

### Frontend
Create `.env.local` in `frontend/`:
```
GEMINI_API_KEY=your_api_key_here
```

The Vite config maps this to `process.env.API_KEY` and `process.env.GEMINI_API_KEY` for the app.

### Backend (Planned)
Expected environment variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/agenda_escolar
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

## Key Technical Details

### Data Persistence (Current: Frontend Only)
- All data stored in localStorage with keys prefixed `school-agenda-*`
- Theme, profiles, subjects, exams, menu, events, dinners, centers, contacts, and card order are persisted
- Multi-child support: data filtered by `activeProfileId` when displayed

### AI Service Integration
The `aiService` provides three AI-powered features using Gemini:
1. `suggestDinner()` - Suggests a single dinner based on school lunch
2. `generateDinnerPlan()` - Generates dinner plan (today or weekly)
3. `generateShoppingList()` - Creates categorized shopping list from meals

All AI calls respect `allergies` and `excludedFoods` arrays from the active profile.

### Component State Patterns
When updating data scoped by student:
```typescript
// Example: updating dinners for active child
setAllDinners(prev => {
  const currentChildDinners = prev.filter(d => d.studentId === activeProfileId);
  const otherChildDinners = prev.filter(d => d.studentId !== activeProfileId);
  const updated = updaterFunction(currentChildDinners);
  return [...otherChildDinners, ...updated.map(d => ({...d, studentId: activeProfileId}))];
});
```

This pattern ensures changes only affect the active profile while preserving other profiles' data.

### Dark Mode
Theme toggling is in ProfilePage. Theme state is persisted and applied to `document.documentElement` via a `useEffect` in `App.tsx`.

## Data Models

Key TypeScript interfaces in `types.ts`:
- `StudentProfile` - Child profile with school info, allergies, excluded foods, and active modules
- `Subject` - Classes with days, time, teacher (both school and extracurricular)
- `Exam` - Upcoming exams with subject, date, topic
- `MenuItem` - School lunch menu by date
- `DinnerItem` - Planned dinners with ingredients
- `SchoolEvent` - Calendar events (holidays, school days, vacations)
- `Center` - Educational centers
- `Contact` - Contact information per center

All student-related data includes `studentId` for multi-profile support.

## Testing Strategy

### Frontend (Vitest)
- Test framework not yet configured
- When implementing tests, use Vitest with React Testing Library
- Focus on component behavior, state management, and AI service integration

### Backend (pytest)
- Test framework not yet configured
- When implementing tests, organize by:
  - `tests/unit/` - Domain and application layer tests
  - `tests/integration/` - API and repository tests
  - Use pytest fixtures for database setup/teardown

## Git Workflow

This repository is **not initialized as a git repository** yet. Initialize with `git init` if version control is needed.
