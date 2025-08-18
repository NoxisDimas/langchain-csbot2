-- Initialize RAG Database
-- This script runs when the PostgreSQL container starts

-- Create vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create default database if it doesn't exist
-- (This is handled by POSTGRES_DB environment variable)

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE rag_database TO rag_user;

-- Connect to the database
\c rag_database;

-- Create vector extension in the database
CREATE EXTENSION IF NOT EXISTS vector;

-- Create default schema
CREATE SCHEMA IF NOT EXISTS public;

-- Set search path
SET search_path TO public;

-- Create initial tables (these will be created by SQLAlchemy, but we can add indexes here)
-- The actual table creation is handled by the application

-- Create indexes for better performance
-- (These will be created after the tables are created by the application)

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'RAG Database initialized successfully';
    RAISE NOTICE 'Vector extension: %', (SELECT extversion FROM pg_extension WHERE extname = 'vector');
END $$;