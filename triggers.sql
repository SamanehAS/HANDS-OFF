CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_habits_updated_at 
    BEFORE UPDATE ON habits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER update_notifications_updated_at 
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();



CREATE OR REPLACE FUNCTION check_notification_rate_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.notification_type = 'Behavior_Alert' THEN
        IF (
            SELECT COUNT(*) 
            FROM notifications 
            WHERE user_id = NEW.user_id
              AND notification_type = 'Behavior_Alert'
              AND sent_at > (NOW() - INTERVAL '5 minutes')
        ) >= 10 THEN
            RAISE EXCEPTION 'محدودیت Rate Limit برای اعلان‌های رفتار';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_notification_type VARCHAR,
    p_max_per_minute INTEGER DEFAULT 10,
    p_max_per_hour INTEGER DEFAULT 60
)
RETURNS BOOLEAN AS $$
DECLARE
    v_count_minute INTEGER;
    v_count_hour INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count_minute
    FROM notifications
    WHERE user_id = p_user_id
      AND notification_type = p_notification_type
      AND sent_at > (NOW() - INTERVAL '1 minute');
    
    SELECT COUNT(*) INTO v_count_hour
    FROM notifications
    WHERE user_id = p_user_id
      AND notification_type = p_notification_type
      AND sent_at > (NOW() - INTERVAL '1 hour');
    
    IF v_count_minute >= p_max_per_minute OR v_count_hour >= p_max_per_hour THEN
        INSERT INTO rate_limit_violations (user_id, notification_type, error_message)
        VALUES (p_user_id, p_notification_type, 
                FORMAT('Rate limit exceeded: %s/min, %s/hour', 
                       v_count_minute, v_count_hour));
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION update_rate_limit_counter()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Sent' THEN
        INSERT INTO notification_rate_limits 
            (user_id, window_type, window_start, window_end, 
             notification_type, notification_count, max_allowed)
        VALUES (
            NEW.user_id,
            'Minute',
            DATE_TRUNC('minute', NEW.sent_at),
            DATE_TRUNC('minute', NEW.sent_at) + INTERVAL '1 minute',
            NEW.notification_type,
            1,
            10  
        )
        ON CONFLICT (user_id, window_type, window_start, notification_type) 
        DO UPDATE SET 
            notification_count = notification_rate_limits.notification_count + 1,
            updated_at = CURRENT_TIMESTAMP;
        
        INSERT INTO notification_rate_limits 
            (user_id, window_type, window_start, window_end, 
             notification_type, notification_count, max_allowed)
        VALUES (
            NEW.user_id,
            'Hour',
            DATE_TRUNC('hour', NEW.sent_at),
            DATE_TRUNC('hour', NEW.sent_at) + INTERVAL '1 hour',
            NEW.notification_type,
            1,
            60  
        )
        ON CONFLICT (user_id, window_type, window_start, notification_type) 
        DO UPDATE SET 
            notification_count = notification_rate_limits.notification_count + 1,
            updated_at = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER trg_update_rate_limit
    AFTER UPDATE ON notifications
    FOR EACH ROW
    WHEN (NEW.status = 'Sent')
    EXECUTE FUNCTION update_rate_limit_counter();



CREATE TRIGGER update_rate_limits_updated_at 
    BEFORE UPDATE ON notification_rate_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();



CREATE TRIGGER update_rate_rules_updated_at 
    BEFORE UPDATE ON rate_limit_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


INSERT INTO rate_limit_rules 
    (rule_name, description, window_seconds, max_requests, applies_to, priority)
VALUES
    ('Behavior_Alerts_Per_Minute', 
     'محدودیت ارسال هشدارهای رفتار در دقیقه', 
     60, 10, 'Behavior_Alert', 1),
     
    ('Behavior_Alerts_Per_Hour', 
     'محدودیت ارسال هشدارهای رفتار در ساعت', 
     3600, 60, 'Behavior_Alert', 2),
     
    ('Daily_Reminders_Per_Day', 
     'محدودیت ارسال یادآوری روزانه', 
     86400, 3, 'Daily_Reminder', 1),
     
    ('All_Notifications_Per_Day', 
     'محدودیت کلی اعلان‌ها در روز', 
     86400, 100, 'All', 3);



CREATE OR REPLACE FUNCTION cleanup_old_rate_limits()
RETURNS VOID AS $$
BEGIN
    DELETE FROM notification_rate_limits 
    WHERE window_end < (NOW() - INTERVAL '7 days');
    
    DELETE FROM rate_limit_violations 
    WHERE attempted_at < (NOW() - INTERVAL '30 days');
    
    RAISE NOTICE '✅ داده‌های قدیمی Rate Limits پاکسازی شد';
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_daily_reports_updated_at 
    BEFORE UPDATE ON daily_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();