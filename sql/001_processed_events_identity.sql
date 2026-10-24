-- Additive M3 migration. Existing rows retain NULL content and are therefore
-- explicitly rejected on a later duplicate rather than silently trusted.
ALTER TABLE processed_events ADD COLUMN IF NOT EXISTS account_id TEXT;
ALTER TABLE processed_events ADD COLUMN IF NOT EXISTS amount BIGINT;
