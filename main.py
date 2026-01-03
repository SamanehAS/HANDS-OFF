import cv2
import time
import json
from datetime import datetime
from camera import Camera
from landmarks import LandmarkDetector
from distance import DistanceAnalyzer
from alerts import AlertSystem, AlertLevel

class HandsOffSystem:
    def __init__(self):
        print("=" * 60)
        print("HANDS OFF - Intelligent Hand Proximity Alert System")
        print("=" * 60)
        
        self.camera = Camera()
        self.detector = LandmarkDetector()
        self.analyzer = DistanceAnalyzer(
            warning_threshold=40,
            critical_threshold=20,
            min_duration=1.0,
            max_duration=5.0
        )
        
        self.alerts = AlertSystem(muted=False)
        
        self.running = True
        self.show_detection = True
        self.show_info = True
        
        self.frame_count = 0
        self.start_time = time.time()
        self.session_stats = {
            "total_frames": 0,
            "total_alerts": 0,
            "warning_alerts": 0,
            "critical_alerts": 0,
            "closest_regions": {},
            "session_start": datetime.now().isoformat()
        }
        
        self.load_settings()
        
        print("\nSystem initialized successfully")
        print(f"Camera: {self.camera.width}x{self.camera.height}")
        print(f"Warning threshold: {self.analyzer.warning_threshold}px")
        print(f"Critical threshold: {self.analyzer.critical_threshold}px")
        print(f"Min duration: {self.analyzer.min_duration}s")
        print(f"Max duration: {self.analyzer.max_duration}s")
        print(f"Alert sound: {'ON' if not self.alerts.muted else 'MUTED'}")
        print("\nControls:")
        print("  [ESC] or [Q] - Exit")
        print("  [M] - Mute/Unmute alerts")
        print("  [D] - Toggle detection display")
        print("  [I] - Toggle info display")
        print("  [S] - Save settings")
        print("  [R] - Reset statistics")
        print("  [+] - Increase sensitivity")
        print("  [-] - Decrease sensitivity")
        print("=" * 60)
    
    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.analyzer.warning_threshold = settings.get("warning_threshold", 40)
                self.analyzer.critical_threshold = settings.get("critical_threshold", 20)
                self.analyzer.min_duration = settings.get("min_duration", 1.0)
                self.analyzer.max_duration = settings.get("max_duration", 5.0)
                self.alerts.muted = settings.get("muted", False)
            print("Settings loaded from settings.json")
        except FileNotFoundError:
            print("No settings file found, using defaults")
    
    def save_settings(self):
        settings = {
            "warning_threshold": self.analyzer.warning_threshold,
            "critical_threshold": self.analyzer.critical_threshold,
            "min_duration": self.analyzer.min_duration,
            "max_duration": self.analyzer.max_duration,
            "muted": self.alerts.muted,
            "last_updated": datetime.now().isoformat()
        }
        
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        
        print("Settings saved to settings.json")
    
    def draw_ui(self, frame, distance, alert_level, closest_region, closest_points, fps):
        h, w = frame.shape[:2]
        
        if self.show_info:
            cv2.rectangle(frame, (0, 0), (w, 120), (40, 40, 40), -1)
            
            cv2.putText(frame, "HANDS OFF - Proximity Alert System", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            
            if distance < float('inf'):
                distance_text = f"Distance: {int(distance)}px"
                region_text = f"Closest: {closest_region}" if closest_region else ""
                
                if alert_level == AlertLevel.CRITICAL:
                    color = (0, 0, 255)
                    status = "CRITICAL"
                elif alert_level == AlertLevel.WARNING:
                    color = (0, 165, 255)
                    status = "WARNING"
                else:
                    color = (0, 255, 0)
                    status = "SAFE"
                
                cv2.putText(frame, distance_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, region_text, (10, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Status: {status}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
            
            if closest_points:
                (hx, hy), (fx, fy) = closest_points
                cv2.line(frame, (hx, hy), (fx, fy), (0, 0, 255), 2)
                cv2.circle(frame, (hx, hy), 8, (0, 255, 0), -1)
                cv2.circle(frame, (fx, fy), 8, (0, 0, 255), -1)
        
        cv2.rectangle(frame, (0, h-60), (w, h), (30, 30, 30), -1)
        
        alert_stats = self.alerts.get_stats()
        stats_text = [
            f"FPS: {fps:.1f}",
            f"Alerts: {alert_stats['total_alerts']}",
            f"Frame: {self.frame_count}",
            f"Sound: {'OFF' if alert_stats['is_muted'] else 'ON'}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(frame, text, (10 + i*150, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)
        
        cv2.rectangle(frame, (w-200, h-120), (w-10, h-70), (60, 60, 60), -1)
        cv2.putText(frame, "[Q] Exit  [M] Mute", (w-190, h-95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)
        cv2.putText(frame, "[D] Detection  [I] Info", (w-190, h-70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)
        
        return frame
    
    def update_statistics(self, alert_level, closest_region):
        self.session_stats["total_frames"] += 1
        
        if alert_level != AlertLevel.NORMAL:
            self.session_stats["total_alerts"] += 1
            
            if alert_level == AlertLevel.WARNING:
                self.session_stats["warning_alerts"] += 1
            elif alert_level == AlertLevel.CRITICAL:
                self.session_stats["critical_alerts"] += 1
            
            if closest_region:
                self.session_stats["closest_regions"][closest_region] = \
                    self.session_stats["closest_regions"].get(closest_region, 0) + 1
    
    def handle_keyboard(self, key):
        if key in [27, ord('q'), ord('Q')]:
            self.running = False
            print("\nExiting...")
            
        elif key in [ord('m'), ord('M')]:
            self.alerts.toggle_mute()
            
        elif key in [ord('d'), ord('D')]:
            self.show_detection = not self.show_detection
            status = "HIDDEN" if not self.show_detection else "SHOWN"
            print(f"Landmarks {status}")
            
        elif key in [ord('i'), ord('I')]:
            self.show_info = not self.show_info
            status = "HIDDEN" if not self.show_info else "SHOWN"
            print(f"Info {status}")
            
        elif key in [ord('s'), ord('S')]:
            self.save_settings()
            
        elif key in [ord('r'), ord('R')]:
            old_alerts = self.alerts.reset_stats()
            
            old_stats = self.session_stats.copy()
            self.session_stats = {
                "total_frames": 0,
                "total_alerts": 0,
                "warning_alerts": 0,
                "critical_alerts": 0,
                "closest_regions": {},
                "session_start": datetime.now().isoformat()
            }
            
            self.analyzer.reset()
            
            print(f"Statistics reset (previous: {old_alerts} alerts)")
            
        elif key in [ord('+')]:
            self.analyzer.update_thresholds(
                warning=max(10, self.analyzer.warning_threshold - 5),
                critical=max(5, self.analyzer.critical_threshold - 3)
            )
            print(f"Sensitivity increased: Warning={self.analyzer.warning_threshold}px, Critical={self.analyzer.critical_threshold}px")
            
        elif key in [ord('-')]:
            self.analyzer.update_thresholds(
                warning=min(100, self.analyzer.warning_threshold + 5),
                critical=min(50, self.analyzer.critical_threshold + 3)
            )
            print(f"Sensitivity decreased: Warning={self.analyzer.warning_threshold}px, Critical={self.analyzer.critical_threshold}px")
    
    def run(self):
        print("\nStarting monitoring...")
        print("Looking for face and hands...")
        
        try:
            while self.running:
                frame = self.camera.read()
                if frame is None:
                    print("Failed to read frame from camera")
                    break
                
                self.frame_count += 1
                display_frame = frame.copy()
                
                hand_points, face_regions, fingertips_data, face_points = self.detector.detect(frame)
                
                distance = float('inf')
                closest_region = None
                closest_points = None
                alert_level = AlertLevel.NORMAL
                proximity_duration = 0
                
                if hand_points and face_regions:
                    distance, closest_region, closest_points = self.analyzer.calculate_min_distance(
                        hand_points, 
                        face_regions,
                        self.detector.get_region_sensitivity
                    )
                    
                    alert_level, proximity_duration, should_alert = \
                        self.analyzer.analyze_temporal_pattern(distance)
                    
                    if should_alert:
                        alert_result = self.alerts.trigger_alert(
                            alert_level, 
                            proximity_duration, 
                            closest_region,
                            display_frame
                        )
                        
                        self.update_statistics(alert_level, closest_region)
                        
                        self.analyzer.trigger_alert(alert_level, proximity_duration, closest_region)
                
                if self.show_detection and hand_points and face_regions:
                    display_frame = self.detector.draw_detection(
                        display_frame, hand_points, face_regions, fingertips_data
                    )
                
                fps = self.camera.get_info()["fps"]
                display_frame = self.draw_ui(
                    display_frame, distance, alert_level, closest_region, closest_points, fps
                )
                
                cv2.imshow("Hands Off - Intelligent Alert System", display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key != 255:
                    self.handle_keyboard(key)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        print("\nCleaning up...")
        
        self.save_settings()
        
        self.camera.release()
        self.detector.release()
        cv2.destroyAllWindows()
        
        self.show_final_statistics()
        
        print("=" * 60)
        print("Thank you for using Hands Off! Stay healthy!")
        print("=" * 60)
    
    def show_final_statistics(self):
        elapsed = time.time() - self.start_time
        
        alert_stats = self.alerts.get_stats()
        
        print("\nFINAL STATISTICS:")
        print(f"   Session duration: {elapsed:.1f} seconds")
        print(f"   Total frames: {self.frame_count}")
        print(f"   Average FPS: {self.frame_count/elapsed:.1f}" if elapsed > 0 else "")
        print(f"   Total alerts: {alert_stats['total_alerts']}")
        print(f"   - Warning alerts: {self.session_stats['warning_alerts']}")
        print(f"   - Critical alerts: {self.session_stats['critical_alerts']}")
        
        if self.session_stats['closest_regions']:
            print(f"   Most frequent close regions:")
            for region, count in sorted(
                self.session_stats['closest_regions'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]:
                print(f"     {region}: {count} times")

if __name__ == "__main__":
    try:
        import mediapipe
        print(f"MediaPipe {mediapipe.__version__} is available")
    except ImportError:
        print("MediaPipe is not installed!")
        print("Please install: pip install mediapipe")
        exit()
    
    app = HandsOffSystem()
    app.run()