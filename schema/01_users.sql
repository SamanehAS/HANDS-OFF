-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_image_url TEXT,
    sensitivity_level VARCHAR(10) DEFAULT 'Medium' 
        CHECK (sensitivity_level IN ('Low', 'Medium', 'High')),
    notification_preference VARCHAR(20) DEFAULT 'Popup' 
        CHECK (notification_preference IN ('Popup', 'Sound', 'Vibration', 'Popup+Sound')),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    verification_token_expires_at TIMESTAMP,
    reset_password_token VARCHAR(100),
    reset_token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
