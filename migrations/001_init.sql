CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS notes (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS investments (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(10),
    symbol VARCHAR(20),
    price NUMERIC,
    quantity NUMERIC,
    note TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_config (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(50),
    model_name VARCHAR(100),
    active BOOLEAN DEFAULT FALSE
);

INSERT INTO model_config (provider, model_name, active)
SELECT 'ollama', 'llama3.2', TRUE
WHERE NOT EXISTS (SELECT 1 FROM model_config WHERE active = TRUE);
