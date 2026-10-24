CREATE TABLE accounts (
  account_id TEXT PRIMARY KEY,
  balance BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE processed_events (
  handler_scope TEXT NOT NULL,
  event_id TEXT NOT NULL,
  PRIMARY KEY (handler_scope, event_id)
);
