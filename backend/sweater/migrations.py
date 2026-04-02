import asyncpg

_MIGRATIONS = [
    'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',

    """CREATE TABLE IF NOT EXISTS users (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email           VARCHAR(255) NOT NULL UNIQUE,
        password_hash   TEXT         NOT NULL,
        is_confirmed    BOOLEAN      NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS email_confirmations (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token      VARCHAR(64) NOT NULL UNIQUE,
        expires_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS password_resets (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token      VARCHAR(64) NOT NULL UNIQUE,
        expires_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS chats (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title      VARCHAR(255) NOT NULL DEFAULT 'New Chat',
        created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
    );""",

    # backfill user_id on chats if it was created without it
    """DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'chats' AND column_name = 'user_id'
        ) THEN
            ALTER TABLE chats
                ADD COLUMN user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE;
        END IF;
    END $$;""",

    """CREATE TABLE IF NOT EXISTS messages (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        chat_id    UUID         NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        role       VARCHAR(20)  NOT NULL CHECK (role IN ('user', 'assistant')),
        content    TEXT         NOT NULL,
        created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
    );""",

    "CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);",
    "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(chat_id, created_at);",

    """CREATE TABLE IF NOT EXISTS processing_statuses (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        message_id  UUID        NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
        status      VARCHAR(50) NOT NULL,
        label       TEXT        NOT NULL,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    );""",

    "CREATE INDEX IF NOT EXISTS idx_processing_statuses_message_id ON processing_statuses(message_id);",

    """CREATE TABLE IF NOT EXISTS pictures_set_a (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        url        TEXT         NOT NULL,
        verified   BOOLEAN      NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS pictures_set_b (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        url        TEXT         NOT NULL,
        verified   BOOLEAN      NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS roles (
        id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name       TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );""",

    """CREATE TABLE IF NOT EXISTS user_roles (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role_id     UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
        assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE(user_id, role_id)
    );""",

    "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);",

    """INSERT INTO roles (name) VALUES ('admin') ON CONFLICT (name) DO NOTHING;""",
    """INSERT INTO roles (name) VALUES ('analyst') ON CONFLICT (name) DO NOTHING;""",
    """INSERT INTO roles (name) VALUES ('marketing_specialist') ON CONFLICT (name) DO NOTHING;""",
]


async def run_migrations(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        for stmt in _MIGRATIONS:
            await conn.execute(stmt)
