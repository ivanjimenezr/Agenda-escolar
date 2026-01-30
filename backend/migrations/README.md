# Database Migrations

This directory contains Alembic database migrations for Agenda Escolar Pro.

## Setup

Ensure you have set up your `.env` file with the correct `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/agenda_escolar
```

## Migration Commands

### Apply all pending migrations

```bash
# From the backend directory
cd backend
alembic upgrade head
```

### Rollback the last migration

```bash
alembic downgrade -1
```

### Rollback to a specific revision

```bash
alembic downgrade <revision_id>
```

### View migration history

```bash
alembic history
```

### View current database revision

```bash
alembic current
```

### Create a new migration (auto-generate)

```bash
alembic revision --autogenerate -m "description of changes"
```

### Create a new migration (manual)

```bash
alembic revision -m "description of changes"
```

## Migration Files

### Current Migrations

1. **001_create_initial_schema** - Creates all database tables with proper constraints, indexes, and relationships
   - Users and authentication
   - Student profiles and active modules
   - Subjects, exams, dinners
   - Menu items and school events
   - Centers and contacts
   - User preferences

2. **002_create_triggers_and_functions** - Creates PostgreSQL functions and triggers
   - Auto-update `updated_at` timestamp on all tables
   - Auto-create `active_modules` for new student profiles
   - Auto-create `user_preferences` for new users

## Database Schema

### Key Features

- **Multi-tenancy**: All data is scoped by `user_id` for security
- **Soft deletes**: `deleted_at` column allows data recovery
- **Audit trails**: `created_at` and `updated_at` timestamps on all tables
- **Type safety**: PostgreSQL ENUMs for subject types, weekdays, event types, themes
- **Constraints**: Foreign keys, unique constraints, check constraints
- **Performance**: Optimized indexes including partial and GIN indexes
- **Triggers**: Automatic timestamp updates and default record creation

### Entity Relationships

```
users (1) ──────────< (N) student_profiles
  │                         │
  │                         ├─< subjects
  │                         ├─< exams
  │                         ├─< dinners
  │                         └─> (1) active_modules
  │
  ├─< menu_items
  ├─< school_events
  ├─< centers ──────< contacts
  └─> (1) user_preferences ──> student_profiles (active)
```

## Development Workflow

### Initial Setup (First Time)

1. Create the database:
   ```bash
   createdb agenda_escolar
   ```

2. Run all migrations:
   ```bash
   alembic upgrade head
   ```

### Making Schema Changes

1. Modify the SQLAlchemy models in `src/domain/models.py`

2. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "add new column to users"
   ```

3. Review the generated migration in `migrations/versions/`

4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### Production Deployment

1. **Always** back up the database before running migrations in production

2. Test migrations in a staging environment first

3. Run migrations during a maintenance window if making breaking changes

4. Use transactions (Alembic does this by default)

## Troubleshooting

### "Target database is not up to date"

Run: `alembic upgrade head`

### "Can't locate revision identified by 'xxx'"

The migrations table may be out of sync. Check:
```bash
alembic current
alembic history
```

### Reset database (DESTRUCTIVE - Development Only)

```bash
# Drop all tables
alembic downgrade base

# Reapply all migrations
alembic upgrade head
```

### Manual SQL execution

If you need to run raw SQL:

```bash
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"
```

## Best Practices

1. **Never edit applied migrations** - Create a new migration instead
2. **Always review auto-generated migrations** - Alembic may not catch everything
3. **Test migrations in both directions** - Ensure upgrade and downgrade work
4. **Use meaningful names** - Migration names should describe what they do
5. **Keep migrations atomic** - One logical change per migration
6. **Document complex migrations** - Add comments for non-obvious changes

## File Naming Convention

Migrations use the following naming pattern:
```
YYYYMMDD_HHMM_NNN_description.py
```

Example: `20260130_1400_001_create_initial_schema.py`

- `YYYYMMDD` - Date
- `HHMM` - Time (24-hour format)
- `NNN` - Sequential number
- `description` - Brief description of changes
