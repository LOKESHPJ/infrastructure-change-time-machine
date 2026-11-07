CREATE TABLE IF NOT EXISTS infrastructure_snapshots (
    id SERIAL PRIMARY KEY,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) NOT NULL,
    instance_count INTEGER DEFAULT 0,
    snapshot_data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS infrastructure_changes (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resource_id VARCHAR(100) NOT NULL,
    change_type VARCHAR(50),
    attribute VARCHAR(100),
    old_value TEXT,
    new_value TEXT
);

CREATE TABLE IF NOT EXISTS cloudtrail_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(200),
    event_name VARCHAR(200),
    event_source VARCHAR(200),
    username VARCHAR(200),
    event_time TIMESTAMP,
    risk_level VARCHAR(20),
    event_data JSONB
);
CREATE TABLE IF NOT EXISTS incident_reports (
    id SERIAL PRIMARY KEY,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    snapshot_file VARCHAR(255),
    cloudtrail_file VARCHAR(255),
    total_events INTEGER DEFAULT 0,
    report_data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS recovery_plans (
    id SERIAL PRIMARY KEY,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    incident_report_id INTEGER REFERENCES incident_reports(id),
    plan_data JSONB NOT NULL,
    automatic_execution BOOLEAN DEFAULT FALSE
);
