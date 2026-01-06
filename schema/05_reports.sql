-- Reports Tables
CREATE TABLE daily_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    
    total_events INTEGER DEFAULT 0 CHECK (total_events >= 0),
    correct_detections INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    avg_confidence_score DECIMAL(3,2),

    manual_notes TEXT,
    mood VARCHAR(20) CHECK (mood IN (
        'Very_Happy', 'Happy', 'Neutral', 'Sad', 'Very_Sad', 'Stressed'
    )),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),

    daily_summary TEXT,
    improvement_tip TEXT,
    success_score INTEGER CHECK (success_score BETWEEN 0 AND 100),

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, report_date)
);



CREATE TABLE monthly_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year_month CHAR(7) NOT NULL CHECK (year_month ~ '^\d{4}-\d{2}$'),
    
    total_events INTEGER DEFAULT 0 CHECK (total_events >= 0),
    average_events_per_day DECIMAL(5,2) CHECK (average_events_per_day >= 0),
    improvement_percentage DECIMAL(5,2) 
        CHECK (improvement_percentage BETWEEN -100 AND 100),
    
    most_active_day VARCHAR(10) CHECK (most_active_day IN (
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
        'Friday', 'Saturday', 'Sunday'
    )),
    peak_hour INTEGER CHECK (peak_hour >= 0 AND peak_hour <= 23),
    most_common_behavior VARCHAR(50),
    
    trends_analysis JSONB DEFAULT '{}',
    recommendations TEXT[] DEFAULT '{}',
    achievements TEXT[] DEFAULT '{}',
    
    previous_month_comparison JSONB DEFAULT '{}',
    
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMP,
    is_viewed BOOLEAN DEFAULT FALSE,
    
    UNIQUE(user_id, year_month)
);



CREATE TABLE user_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'Login', 'Logout', 'Profile_Update', 'Password_Change',
        'Habit_Created', 'Habit_Updated', 'Habit_Deleted',
        'Report_Viewed', 'Settings_Changed', 'Notification_Read'
    )),

    ip_address INET,
    user_agent TEXT,

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

