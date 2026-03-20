-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -- ── Users & Auth ────────────────────────────────────────────────────

-- CREATE TABLE IF NOT EXISTS users (
--     id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     email           VARCHAR(255) NOT NULL UNIQUE,
--     password_hash   TEXT         NOT NULL,
--     is_confirmed    BOOLEAN      NOT NULL DEFAULT FALSE,
--     created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
-- );

-- CREATE TABLE IF NOT EXISTS email_confirmations (
--     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     token      VARCHAR(64) NOT NULL UNIQUE,
--     expires_at TIMESTAMPTZ NOT NULL,
--     created_at TIMESTAMPTZ NOT NULL DEFAULT now()
-- );

-- CREATE TABLE IF NOT EXISTS password_resets (
--     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     token      VARCHAR(64) NOT NULL UNIQUE,
--     expires_at TIMESTAMPTZ NOT NULL,
--     created_at TIMESTAMPTZ NOT NULL DEFAULT now()
-- );

-- -- ── Chats ───────────────────────────────────────────────────────────

-- CREATE TABLE IF NOT EXISTS chats (
--     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     title      VARCHAR(255) NOT NULL DEFAULT 'New Chat',
--     created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
-- );

-- CREATE TABLE IF NOT EXISTS messages (
--     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     chat_id    UUID         NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
--     role       VARCHAR(20)  NOT NULL CHECK (role IN ('user', 'assistant')),
--     content    TEXT         NOT NULL,
--     created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
-- );

-- CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
-- CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
-- CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(chat_id, created_at);

-- -- Processing statuses: tracks each step of query processing for a user message
-- CREATE TABLE IF NOT EXISTS processing_statuses (
--     id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     message_id  UUID        NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
--     status      VARCHAR(50) NOT NULL,
--     label       TEXT        NOT NULL,
--     created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
-- );

-- CREATE INDEX IF NOT EXISTS idx_processing_statuses_message_id ON processing_statuses(message_id);

-- -- ── Picture screening ───────────────────────────────────────────────
