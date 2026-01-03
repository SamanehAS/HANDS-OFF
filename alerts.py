# alerts.py
import cv2
import time
import winsound
import threading
from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    NORMAL = 0
    WARNING = 1
    CRITICAL = 2

class AlertSystem:
    def __init__(self, muted=False):
        self.muted = muted
        self.alert_count = 0
        self.last_alert_time = 0
        self.alert_cooldown = 3.0
        self.alert_thread = None
        
        print(f"Alert System initialized (Muted: {muted})")
    
    def play_sound_alert(self, alert_level, intensity=1.0):
        if self.muted:
            return
        
        try:
            intensity = max(0.1, min(1.0, intensity))
            
            if alert_level == AlertLevel.CRITICAL:
                frequency = 1200
                duration = int(200 * intensity)
                for i in range(3):
                    winsound.Beep(frequency, duration)
                    time.sleep(0.05)
            
            elif alert_level == AlertLevel.WARNING:
                frequency = 800 + int(400 * intensity)
                duration = int(300 * intensity)
                for i in range(2):
                    winsound.Beep(frequency, duration)
                    time.sleep(0.1)
            
            else:
                winsound.Beep(600, 150)
                
        except Exception as e:
            print(f"Could not play alert sound: {e}")
    
    def add_visual_alert(self, frame, alert_level, duration=0, region=""):
        h, w = frame.shape[:2]
        
        if alert_level == AlertLevel.CRITICAL:
            if int(time.time() * 2) % 2 == 0:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
                frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
            
            cv2.putText(frame, "CRITICAL: HAND TOO CLOSE!", 
                       (w//2 - 250, h//2 - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            info = f"{region} - {duration:.1f}s" if region else f"{duration:.1f}s"
            cv2.putText(frame, info, 
                       (w//2 - 100, h//2 + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        
        elif alert_level == AlertLevel.WARNING:
            cv2.putText(frame, "WARNING: HAND NEAR FACE", 
                       (w//2 - 220, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
            
            if region:
                cv2.putText(frame, f"Region: {region}", 
                           (w//2 - 100, h//2 + 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        
        return frame
    
    def trigger_alert(self, alert_level, duration, closest_region, frame=None):
        current_time = time.time()
        
        if current_time - self.last_alert_time < self.alert_cooldown:
            return None
        
        self.alert_count += 1
        self.last_alert_time = current_time
        
        intensity = min(1.0, duration / 5.0)
        
        if not self.muted:
            self.alert_thread = threading.Thread(
                target=self.play_sound_alert,
                args=(alert_level, intensity),
                daemon=True
            )
            self.alert_thread.start()
        
        result_frame = None
        if frame is not None:
            result_frame = self.add_visual_alert(
                frame.copy(), alert_level, duration, closest_region
            )
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_icon = "CRITICAL" if alert_level == AlertLevel.CRITICAL else "WARNING"
        print(f"[{timestamp}] {level_icon} Alert #{self.alert_count}: "
              f"{alert_level.name} - {duration:.1f}s - {closest_region}")
        
        return {
            'count': self.alert_count,
            'level': alert_level.name,
            'duration': duration,
            'region': closest_region,
            'timestamp': timestamp,
            'frame': result_frame,
            'intensity': intensity
        }
    
    def toggle_mute(self):
        self.muted = not self.muted
        status = "MUTED" if self.muted else "UNMUTED"
        print(f"Alert sound {status}")
        return self.muted
    
    def get_stats(self):
        return {
            'total_alerts': self.alert_count,
            'is_muted': self.muted,
            'seconds_since_last_alert': time.time() - self.last_alert_time,
            'cooldown_active': time.time() - self.last_alert_time < self.alert_cooldown
        }
    
    def reset_stats(self):
        old_count = self.alert_count
        self.alert_count = 0
        self.last_alert_time = 0
        print(f"Alert statistics reset (previous: {old_count} alerts)")
        return old_count

def string_to_alert_level(level_str):
    level_str = level_str.upper()
    if level_str == "CRITICAL":
        return AlertLevel.CRITICAL
    elif level_str == "WARNING":
        return AlertLevel.WARNING
    else:
        return AlertLevel.NORMAL