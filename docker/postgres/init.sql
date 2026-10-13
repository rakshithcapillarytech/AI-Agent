-- Fuzzy matching for error strings and API names in keyword search (PLAN.md §5.4 stage B)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- Available for stage C semantic search; unused until evals show the need
CREATE EXTENSION IF NOT EXISTS vector;
