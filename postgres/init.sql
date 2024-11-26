CREATE TABLE IF NOT EXISTS caption_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    audio_id VARCHAR(255),
    generated_transcript TEXT,
    feedback_received BOOLEAN DEFAULT FALSE,
    rating INT,
    ideal_transcript TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_session ON caption_logs(user_id, session_id);
CREATE INDEX idx_created_at ON caption_logs(created_at);