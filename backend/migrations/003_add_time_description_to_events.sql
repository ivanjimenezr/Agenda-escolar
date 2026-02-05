-- Migration: Add time and description fields to school_events table
-- Date: 2026-02-05
-- Description: Adds optional time and description columns to events

-- Add time column (optional)
ALTER TABLE school_events
ADD COLUMN IF NOT EXISTS time TIME;

-- Add description column (optional)
ALTER TABLE school_events
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add comment for documentation
COMMENT ON COLUMN school_events.time IS 'Optional event time in HH:MM:SS format';
COMMENT ON COLUMN school_events.description IS 'Optional detailed description of the event';
