import math
import time
from collections import deque
from enum import Enum
import numpy as np

class AlertLevel(Enum):
    NORMAL = 0
    WARNING = 1
    CRITICAL = 2

class DistanceAnalyzer:
    def __init__(self, warning_threshold=40, critical_threshold=20, min_duration=1.0, max_duration=5.0):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.min_duration = min_duration
        self.max_duration = max_duration
        
        self.distance_history = deque(maxlen=30)
        self.proximity_start_time = None
        self.current_alert_level = AlertLevel.NORMAL
        self.last_alert_time = 0
        self.alert_cooldown = 3.0
        self.alert_history = []
        
        self.face_region_weights = {
            "eyes": 1.5,
            "mouth": 1.2,
            "nose": 1.0,
            "forehead": 0.8,
            "eyebrow": 1.3,
            "cheek": 0.7,
            "chin": 0.8,
        }
    
    def euclidean(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    
    def min_hand_face_distance(self, hand_points, face_regions, region_sensitivity_func=None):
        if not hand_points or not face_regions:
            return float('inf'), None, None
        
        min_dist = float('inf')
        closest_region = None
        closest_points = None
        
        for hx, hy in hand_points:
            for region, (fx, fy) in face_regions.items():
                d = self.euclidean((hx, hy), (fx, fy))
                
                if region_sensitivity_func:
                    sensitivity = region_sensitivity_func(region)
                    weighted_d = d / sensitivity
                else:
                    base_name = region.split('_')[0] if '_' in region else region
                    weight = self.face_region_weights.get(base_name, 1.0)
                    weighted_d = d / weight
                
                if weighted_d < min_dist:
                    min_dist = weighted_d
                    closest_region = region
                    closest_points = ((hx, hy), (fx, fy))
        
        return min_dist, closest_region, closest_points
    
    def calculate_min_distance(self, hand_points, face_regions, region_sensitivity_func=None):
        return self.min_hand_face_distance(hand_points, face_regions, region_sensitivity_func)
    
    def analyze_temporal_pattern(self, current_distance):
        self.distance_history.append(current_distance)
        
        current_time = time.time()
        
        if current_distance < self.critical_threshold:
            new_alert_level = AlertLevel.CRITICAL
        elif current_distance < self.warning_threshold:
            new_alert_level = AlertLevel.WARNING
        else:
            new_alert_level = AlertLevel.NORMAL
        
        if new_alert_level == AlertLevel.NORMAL:
            if self.proximity_start_time is not None:
                duration = current_time - self.proximity_start_time
                self.proximity_start_time = None
                self.current_alert_level = AlertLevel.NORMAL
                
                if duration > 0.5:
                    self.alert_history.append({
                        'timestamp': current_time,
                        'duration': duration,
                        'max_distance': min(self.distance_history) if self.distance_history else 0,
                        'level': self.current_alert_level.name
                    })
                
                return AlertLevel.NORMAL, 0, False
            return AlertLevel.NORMAL, 0, False
        
        if self.proximity_start_time is None:
            self.proximity_start_time = current_time
            self.current_alert_level = new_alert_level
            return new_alert_level, 0, False
        
        duration = current_time - self.proximity_start_time
        
        if duration < self.min_duration:
            return new_alert_level, duration, False
        
        time_since_last_alert = current_time - self.last_alert_time
        if time_since_last_alert < self.alert_cooldown:
            return new_alert_level, duration, False
        
        should_alert = False
        
        if new_alert_level == AlertLevel.WARNING and duration >= self.min_duration:
            should_alert = True
        elif new_alert_level == AlertLevel.CRITICAL:
            should_alert = True
        
        if (new_alert_level == AlertLevel.WARNING and 
            duration >= self.max_duration):
            new_alert_level = AlertLevel.CRITICAL
            should_alert = True
        
        if new_alert_level.value > self.current_alert_level.value:
            self.current_alert_level = new_alert_level
        
        return self.current_alert_level, duration, should_alert
    
    def trigger_alert(self, alert_level, duration, closest_region):
        current_time = time.time()
        
        alert_record = {
            'timestamp': current_time,
            'level': alert_level.name,
            'duration': duration,
            'region': closest_region,
            'distance': self.distance_history[-1] if self.distance_history else 0
        }
        self.alert_history.append(alert_record)
        
        self.last_alert_time = current_time
        
        return alert_record
    
    def _analyze_pattern_from_history(self):
        if len(self.distance_history) < 10:
            return "insufficient_data"
        
        recent = list(self.distance_history)[-10:]
        avg_distance = sum(recent) / len(recent)
        
        if avg_distance < self.critical_threshold * 1.2:
            return "persistent_proximity"
        elif any(d < self.warning_threshold for d in recent[-5:]):
            return "frequent_nearness"
        else:
            return "normal"
    
    def get_statistics(self):
        recent_alerts = [a for a in self.alert_history 
                        if time.time() - a['timestamp'] < 300]
        
        if recent_alerts:
            avg_duration = np.mean([a['duration'] for a in recent_alerts])
            warning_count = sum(1 for a in recent_alerts if a['level'] == 'WARNING')
            critical_count = sum(1 for a in recent_alerts if a['level'] == 'CRITICAL')
        else:
            avg_duration = 0
            warning_count = 0
            critical_count = 0
        
        return {
            'current_level': self.current_alert_level.name,
            'is_in_proximity': self.proximity_start_time is not None,
            'proximity_duration': time.time() - self.proximity_start_time 
                                 if self.proximity_start_time else 0,
            'recent_alerts': len(recent_alerts),
            'warning_alerts': warning_count,
            'critical_alerts': critical_count,
            'avg_alert_duration': avg_duration,
            'cooldown_active': time.time() - self.last_alert_time < self.alert_cooldown,
            'distance_history_size': len(self.distance_history)
        }
    
    def update_thresholds(self, warning=None, critical=None, min_duration=None, max_duration=None):
        if warning is not None:
            self.warning_threshold = max(10, warning)
        if critical is not None:
            self.critical_threshold = max(5, critical)
        if min_duration is not None:
            self.min_duration = max(0.1, min_duration)
        if max_duration is not None:
            self.max_duration = max(self.min_duration + 0.5, max_duration)
    
    def reset(self):
        self.proximity_start_time = None
        self.current_alert_level = AlertLevel.NORMAL
        self.distance_history.clear()
        self.alert_history.clear()
        self.last_alert_time = 0
    
    def get_alert_stats(self):
        return {
            "alert_level": self.current_alert_level,
            "alert_count": len(self.alert_history),
            "current_threshold": self.warning_threshold,
            "history_size": len(self.distance_history)
        }
    
    def increment_alert_count(self):
        pass
    
    def reset_alert_count(self):
        old_count = len(self.alert_history)
        self.alert_history.clear()
        return old_count