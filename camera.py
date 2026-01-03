import cv2
import time

class Camera:
    def __init__(self, camera_id=0, width=640, height=480, fps=30):
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        self.width = width
        self.height = height
        self.fps = fps
        self.last_frame_time = time.time()
        
        print(f" Camera initialized: {width}x{height} @ {fps}FPS")

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        
        current_time = time.time()
        self.current_fps = 1.0 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time
        
        return frame

    def get_info(self):
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.current_fps if hasattr(self, 'current_fps') else 0
        }

    def release(self):
        self.cap.release()
        print("📷 Camera released")

    def __del__(self):
        self.release()