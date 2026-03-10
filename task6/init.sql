
CREATE TABLE IF NOT EXISTS sentiment_logs(
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    from_cache BOOLEAN NOT NULL,
    timestamp FLOAT NOT NULL
);