-- Migration: Add Zimmer integration tables
-- Description: Creates tables for user isolation, token management, and usage tracking

-- Create automation_users table
CREATE TABLE IF NOT EXISTS automation_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    automation_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    user_name VARCHAR(255),
    tokens_remaining BIGINT DEFAULT 0 NOT NULL,
    demo_tokens BIGINT DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for automation_users
CREATE INDEX IF NOT EXISTS ix_automation_users_user_id ON automation_users(user_id);
CREATE INDEX IF NOT EXISTS ix_automation_users_automation_id ON automation_users(automation_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_automation_users_user_automation ON automation_users(user_id, automation_id);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    automation_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for user_sessions
CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_automation_id ON user_sessions(automation_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_session_id ON user_sessions(session_id);

-- Create usage_ledger table
CREATE TABLE IF NOT EXISTS usage_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    automation_id VARCHAR(255) NOT NULL,
    delta BIGINT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    meta TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for usage_ledger
CREATE INDEX IF NOT EXISTS ix_usage_ledger_user_id ON usage_ledger(user_id);
CREATE INDEX IF NOT EXISTS ix_usage_ledger_automation_id ON usage_ledger(automation_id);
CREATE INDEX IF NOT EXISTS ix_usage_ledger_created_at ON usage_ledger(created_at);

