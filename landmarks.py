import cv2
import mediapipe as mp

class LandmarkDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.face = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.FACE_REGIONS = {
            "mouth": [13, 14, 61, 291],
            "nose": [1, 168],
            "left_eye": [33, 133, 159, 145],
            "right_eye": [362, 263, 386, 374],
            "left_eyebrow": [70, 63, 105],
            "right_eyebrow": [336, 296, 334],
            "forehead": [10, 338]
        }

    def _center(self, landmarks, ids, w, h):
        xs, ys = [], []
        for i in ids:
            lm = landmarks.landmark[i]
            xs.append(lm.x * w)
            ys.append(lm.y * h)
        return (int(sum(xs) / len(xs)), int(sum(ys) / len(ys)))

    def detect(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_results = self.hands.process(rgb)
        face_results = self.face.process(rgb)

        hand_points = []
        face_regions = {}

        if hand_results.multi_hand_landmarks:
            hand = hand_results.multi_hand_landmarks[0]
            for lm in hand.landmark:
                hand_points.append((int(lm.x * w), int(lm.y * h)))

        if face_results.multi_face_landmarks:
            face = face_results.multi_face_landmarks[0]
            for region, ids in self.FACE_REGIONS.items():
                face_regions[region] = self._center(face, ids, w, h)

        return hand_points, face_regions
