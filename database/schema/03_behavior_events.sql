-- Behavior Events Table
CREATE TABLE behavior_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id UUID NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confidence_score DECIMAL(3,2) 
        CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    severity VARCHAR(10) 
        CHECK (severity IN ('Low', 'Medium', 'High')),
    
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_type_sent VARCHAR(20),
    
    is_false_positive BOOLEAN DEFAULT FALSE,
    user_feedback VARCHAR(20) 
        CHECK (user_feedback IN ('Correct', 'Incorrect', 'Unsure')),
    
    camera_position VARCHAR(20),
    detection_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);