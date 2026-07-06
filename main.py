"""
Hand Gesture Volume Control
Kontrol volume sistem Windows menggunakan gestur tangan via webcam.
"""

import math

import cv2
import mediapipe as mp

# MediaPipe Tasks API
vision = mp.tasks.vision
BaseOptions = mp.tasks.BaseOptions
DrawingUtils = vision.drawing_utils
HandConnections = vision.HandLandmarksConnections.HAND_CONNECTIONS

# Landmark IDs
THUMB_TIP = 4
INDEX_TIP = 8

MODEL_PATH = "assets/hand_landmarker.task"


def create_detector():
    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak bisa membuka webcam.")
        return

    detector = create_detector()
    print("Webcam berhasil dibuka. Tekan 'q' untuk keluar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Gagal membaca frame.")
            break

        # Flip horizontal supaya mirror-like
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Konversi ke MediaPipe Image (RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Deteksi tangan
        result = detector.detect_for_video(mp_image, int(cv2.getTickCount() / cv2.getTickFrequency() * 1000))

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                # Gambar landmark bawaan MediaPipe
                DrawingUtils.draw_landmarks(
                    image=frame,
                    landmark_list=hand_landmarks,
                    connections=HandConnections,
                )

                # Ambil koordinat ujung jempol & telunjuk
                thumb = hand_landmarks[THUMB_TIP]
                index = hand_landmarks[INDEX_TIP]

                tx, ty = int(thumb.x * w), int(thumb.y * h)
                ix, iy = int(index.x * w), int(index.y * h)

                # Titik merah di ujung jari
                cv2.circle(frame, (tx, ty), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(frame, (ix, iy), 8, (0, 0, 255), cv2.FILLED)

                # Garis penghubung
                cv2.line(frame, (tx, ty), (ix, iy), (0, 0, 255), 2)

                # Jarak Euclidean dalam pixel
                dist = math.hypot(ix - tx, iy - ty)
                print(f"Thumb-Index distance: {dist:.1f} px")

        cv2.imshow("Hand Gesture Volume Control", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    detector.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
