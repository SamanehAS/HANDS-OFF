CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

CREATE INDEX idx_habits_user_id ON habits(user_id);
CREATE INDEX idx_habits_user_active ON habits(user_id, is_active);

CREATE INDEX idx_behavior_events_habit ON behavior_events(habit_id);
CREATE INDEX idx_behavior_events_detected ON behavior_events(detected_at);
CREATE INDEX idx_behavior_events_habit_detected ON behavior_events(habit_id, detected_at);
CREATE INDEX idx_behavior_events_confidence ON behavior_events(confidence_score);
CREATE INDEX idx_behavior_events_false_positive ON behavior_events(is_false_positive);
CREATE INDEX idx_behavior_events_date ON behavior_events(DATE(detected_at));

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_for) 
    WHERE status = 'Pending';
CREATE INDEX idx_notifications_created ON notifications(created_at);
CREATE INDEX idx_notifications_type ON notifications(notification_type);

CREATE INDEX idx_rate_limits_user ON notification_rate_limits(user_id);
CREATE INDEX idx_rate_limits_window ON notification_rate_limits(window_start, window_end);
CREATE INDEX idx_rate_limits_user_window ON notification_rate_limits(user_id, window_start, window_end);
CREATE INDEX idx_rate_limits_active ON notification_rate_limits(is_active);

CREATE INDEX idx_rules_enabled ON rate_limit_rules(is_enabled);
CREATE INDEX idx_rules_priority ON rate_limit_rules(priority);

CREATE INDEX idx_violations_user ON rate_limit_violations(user_id);
CREATE INDEX idx_violations_time ON rate_limit_violations(attempted_at);

CREATE INDEX idx_daily_reports_user ON daily_reports(user_id);
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
CREATE INDEX idx_daily_reports_user_date ON daily_reports(user_id, report_date);

CREATE INDEX idx_monthly_reports_user ON monthly_reports(user_id);
CREATE INDEX idx_monthly_reports_year_month ON monthly_reports(year_month);
CREATE INDEX idx_monthly_reports_viewed ON monthly_reports(is_viewed);

CREATE INDEX idx_activity_logs_user ON user_activity_logs(user_id);
CREATE INDEX idx_activity_logs_type ON user_activity_logs(activity_type);
CREATE INDEX idx_activity_logs_created ON user_activity_logs(created_at);