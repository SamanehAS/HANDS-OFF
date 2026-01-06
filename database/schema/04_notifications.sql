-- Notifications Table

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    habit_id UUID REFERENCES habits(id) ON DELETE SET NULL,
    
    notification_type VARCHAR(20) NOT NULL 
        CHECK (notification_type IN (
            'Behavior_Alert',    
            'Daily_Reminder',    
            'Progress_Update',   
            'Motivational',      
            'System'            
        )),
    
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    delivery_method VARCHAR(20) NOT NULL 
        CHECK (delivery_method IN (
            'Popup', 
            'Sound', 
            'Vibration', 
            'Popup+Sound'
        )),
    
    status VARCHAR(20) DEFAULT 'Pending' 
        CHECK (status IN (
            'Pending',      
            'Sent',         
            'Delivered',    
            'Read',         
            'Failed',       
            'Cancelled'     
        )),
    
    priority INTEGER DEFAULT 1 
    
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    metadata JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Rate Limiting Tables
CREATE TABLE notification_rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    window_type VARCHAR(20) NOT NULL CHECK (window_type IN (
        'Minute',      
        'Hour',        
        'Day',         
        'Custom'       
    )),
    
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    
    notification_type VARCHAR(20) CHECK (notification_type IN (
        'Behavior_Alert',
        'Daily_Reminder',
        'Progress_Update',
        'Motivational',
        'System'
    )),
    
    notification_count INTEGER DEFAULT 0 CHECK (notification_count >= 0),
    max_allowed INTEGER NOT NULL CHECK (max_allowed > 0),
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, window_type, window_start, notification_type)
);

CREATE TABLE rate_limit_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    
    window_seconds INTEGER NOT NULL CHECK (window_seconds > 0),
    max_requests INTEGER NOT NULL CHECK (max_requests > 0),
    
    applies_to VARCHAR(20) DEFAULT 'All' CHECK (applies_to IN (
        'All',
        'Behavior_Alert',
        'Daily_Reminder',
        'Progress_Update'
    )),
    
    priority INTEGER DEFAULT 1 CHECK (priority >= 1),
    
    is_enabled BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rate_limit_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    rule_id UUID REFERENCES rate_limit_rules(id),
    attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    notification_type VARCHAR(20),
    ip_address INET,
    user_agent TEXT,
    
    action_taken VARCHAR(20) DEFAULT 'Blocked' CHECK (action_taken IN (
        'Blocked',      
        'Delayed',      
        'Allowed',      
        'Queued'        
    )),
    
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
