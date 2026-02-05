-- Migration: Change event type from enum to string
-- Date: 2026-02-05
-- Description: Changes the type column from enum to varchar to avoid SQLAlchemy enum conversion issues

-- Step 1: Add new column as string
ALTER TABLE school_events
ADD COLUMN type_new VARCHAR(50);

-- Step 2: Copy data from old enum column to new string column
UPDATE school_events
SET type_new = type::text;

-- Step 3: Drop the old enum column
ALTER TABLE school_events
DROP COLUMN type;

-- Step 4: Rename new column to type
ALTER TABLE school_events
RENAME COLUMN type_new TO type;

-- Step 5: Add NOT NULL constraint
ALTER TABLE school_events
ALTER COLUMN type SET NOT NULL;

-- Step 6: Add check constraint to ensure valid values
ALTER TABLE school_events
ADD CONSTRAINT check_event_type CHECK (type IN ('Festivo', 'Lectivo', 'Vacaciones'));

-- Optional: Drop the enum type if no other tables use it
-- DROP TYPE IF EXISTS event_type;

COMMENT ON COLUMN school_events.type IS 'Event type: Festivo, Lectivo, or Vacaciones';
