CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS roi_detections (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    VARCHAR(64)  NOT NULL,
    frame_number  INTEGER      NOT NULL CHECK (frame_number >= 0),
    timestamp     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    bbox_x        FLOAT        NOT NULL,
    bbox_y        FLOAT        NOT NULL,
    bbox_width    FLOAT        NOT NULL,
    bbox_height   FLOAT        NOT NULL,
    confidence    FLOAT        NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    frame_width   INTEGER      NOT NULL,
    frame_height  INTEGER      NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_roi_session_ts ON roi_detections (session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_roi_frame      ON roi_detections (session_id, frame_number);

-- Stamp Alembic so it does not re-run migrations already applied via this script
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version (version_num) VALUES ('0001') ON CONFLICT DO NOTHING;
