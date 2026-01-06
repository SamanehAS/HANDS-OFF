-- Habits Table
CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    behavior_type VARCHAR(50) NOT NULL CHECK (behavior_type IN (
        'Nail_Biting', 'Skin_Picking', 'Face_Touching', 
        'Hair_Pulling', 'Lip_Biting', 'Custom'
    )),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    reminder_schedule JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);