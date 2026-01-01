import cv2
from camera import Camera
from landmarks import LandmarkDetector
from distance import min_hand_face_distance

def main():
    camera = Camera()
    detector = LandmarkDetector()

    while True:
        frame = camera.read()
        if frame is None:
            break

        hand_points, face_regions = detector.detect(frame)

        for (x, y) in hand_points:
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        for region, (x, y) in face_regions.items():
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            # cv2.putText(
            #     frame,
            #     region,
            #     (x + 5, y),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     0.4,
            #     (255, 255, 255),
            #     1
            # )

        if hand_points and face_regions:
            dist, closest = min_hand_face_distance(hand_points, face_regions)

            cv2.putText(
                frame,
                f"Min Dist: {int(dist)} ({closest})",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2
            )

            if dist < 40:
                cv2.putText(
                    frame,
                    "WARNING",
                    (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

        cv2.imshow("Hands Off MVP", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()

if __name__ == "__main__":
    main()
