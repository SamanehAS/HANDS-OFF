import cv2
import mediapipe as mp
import numpy as np

class LandmarkDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.face = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.FACE_REGIONS = {
            "mouth": [13, 14, 78, 308, 0, 17, 61, 291, 62, 292],
            "nose": [1, 2, 98, 327, 4, 5, 195, 197],
            "left_eye": [33, 133, 157, 158, 159, 160, 161, 246, 173, 155],
            "right_eye": [362, 263, 386, 387, 388, 389, 390, 466, 397, 384],
            "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52],
            "right_eyebrow": [336, 296, 334, 293, 300, 285, 295, 282],
            "forehead": [10, 338, 297, 332, 151, 9, 107, 336, 8, 6],
            "chin": [152, 148, 176, 149, 150, 136, 377, 400, 378, 379],
            "left_cheek": [50, 123, 116, 117, 118, 119, 120, 100, 126],
            "right_cheek": [280, 352, 345, 346, 347, 348, 349, 329, 355],
        }
        
        self.REGION_SENSITIVITY = {
            "eye": 1.8,
            "eyebrow": 1.3,
            "mouth": 1.5,
            "nose": 1.2,
            "cheek": 0.7,
            "forehead": 0.6,
            "chin": 0.8,
        }
        
        self.FINGERTIP_INDICES = [4, 8, 12, 16, 20]
    
    def get_region_sensitivity(self, region_name):
        base_name = region_name
        for prefix in ['left_', 'right_']:
            if region_name.startswith(prefix):
                base_name = region_name[len(prefix):]
                break
        
        for key, sensitivity in self.REGION_SENSITIVITY.items():
            if key in base_name:
                return sensitivity
        
        return 1.0
    
    def _calculate_region_center(self, landmarks, region_name, region_points, w, h):
        if not landmarks or not region_points:
            return None
        
        points_x = []
        points_y = []
        weights = []
        
        for point_idx in region_points:
            if point_idx < len(landmarks.landmark):
                lm = landmarks.landmark[point_idx]
                
                weight = 1.0
                if region_name in ["forehead", "chin"]:
                    if point_idx in [10, 151, 152]:
                        weight = 2.0
                
                points_x.append(lm.x * w * weight)
                points_y.append(lm.y * h * weight)
                weights.append(weight)
        
        if not points_x:
            return None
        
        total_weight = sum(weights)
        center_x = sum(points_x) / total_weight
        center_y = sum(points_y) / total_weight
        
        return (int(center_x), int(center_y))
    
    def _get_fingertips(self, hand_landmarks, w, h):
        fingertips = []
        for idx in self.FINGERTIP_INDICES:
            if idx < len(hand_landmarks.landmark):
                lm = hand_landmarks.landmark[idx]
                fingertips.append((int(lm.x * w), int(lm.y * h)))
        return fingertips
    
    def detect(self, frame):
        if frame is None:
            return [], {}, [], []
        
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        
        hand_results = self.hands.process(rgb)
        face_results = self.face.process(rgb)
        
        rgb.flags.writeable = True
        
        hand_points = []
        face_regions = {}
        all_fingertips = []
        face_points_raw = []
        
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for lm in hand_landmarks.landmark:
                    hand_points.append((int(lm.x * w), int(lm.y * h)))
                
                fingertips = self._get_fingertips(hand_landmarks, w, h)
                all_fingertips.extend(fingertips)
        
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            
            for lm in face_landmarks.landmark:
                face_points_raw.append((int(lm.x * w), int(lm.y * h)))
            
            for region_name, region_points in self.FACE_REGIONS.items():
                center = self._calculate_region_center(
                    face_landmarks, region_name, region_points, w, h
                )
                if center:
                    face_regions[region_name] = center
        
        return hand_points, face_regions, all_fingertips, face_points_raw
    
    def draw_detection(self, frame, hand_points, face_regions, all_fingertips=None):
        display_frame = frame.copy()
        
        for (x, y) in hand_points:
            cv2.circle(display_frame, (x, y), 3, (0, 255, 0), -1)
        
        if all_fingertips:
            for (x, y) in all_fingertips:
                cv2.circle(display_frame, (x, y), 6, (255, 0, 0), -1)
        
        region_colors = {
            "forehead": (255, 200, 0),
            "chin": (0, 255, 255),
            "eye": (0, 255, 0),
            "mouth": (255, 0, 0),
            "nose": (255, 0, 255),
            "eyebrow": (255, 165, 0),
            "cheek": (255, 192, 203),
        }
        
        for region_name, (x, y) in face_regions.items():
            base_name = region_name.replace("left_", "").replace("right_", "")
            color = region_colors.get(base_name, (255, 255, 255))
            
            cv2.circle(display_frame, (x, y), 8, color, -1)
            cv2.putText(display_frame, region_name, (x + 10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return display_frame
    
    def release(self):
        try:
            self.hands.close()
            self.face.close()
        except:
            pass