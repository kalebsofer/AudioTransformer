CREATE TABLE IF NOT EXISTS transcription_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    audio_id VARCHAR(255) NOT NULL,
    generated_transcription TEXT NOT NULL,
    feedback_received BOOLEAN DEFAULT FALSE,
    rating INT,
    ideal_transcription TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_session ON transcription_logs(user_id, session_id);
CREATE INDEX idx_created_at ON transcription_logs(created_at);