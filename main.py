"""
Hand Gesture Volume Control
Kontrol volume sistem Windows menggunakan gestur tangan via webcam.
"""

import cv2
import mediapipe as mp

from src.audio_control import get_current_volume, set_volume_scalar
from src.gesture import VolumeMapper

# MediaPipe Tasks API
vision = mp.tasks.vision
BaseOptions = mp.tasks.BaseOptions
DrawingUtils = vision.drawing_utils
HandConnections = vision.HandLandmarksConnections.HAND_CONNECTIONS
LipsIndices = set()
for conn in vision.FaceLandmarksConnections.FACE_LANDMARKS_LIPS:
    LipsIndices.add(conn.start)
    LipsIndices.add(conn.end)

# Landmark IDs
THUMB_TIP = 4
INDEX_TIP = 8

MODEL_PATH = "assets/hand_landmarker.task"
FACE_MODEL_PATH = "assets/face_landmarker.task"

# Threshold: hanya update volume kalau selisih > 2%
VOLUME_THRESHOLD = 2.0


def create_hand_detector():
    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def create_face_detector():
    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=FACE_MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.FaceLandmarker.create_from_options(options)


def blur_mouth(frame, face_landmarks, h, w):
    """Blur area sekitar mulut dari face landmarks."""
    xs, ys = [], []
    for idx in LipsIndices:
        lm = face_landmarks[idx]
        xs.append(int(lm.x * w))
        ys.append(int(lm.y * h))

    if not xs:
        return

    # Bounding box dengan padding
    pad = 20
    x1 = max(min(xs) - pad, 0)
    y1 = max(min(ys) - pad, 0)
    x2 = min(max(xs) + pad, w)
    y2 = min(max(ys) + pad, h)

    # Gaussian blur pada area mulut
    roi = frame[y1:y2, x1:x2]
    if roi.size > 0:
        blurred = cv2.GaussianBlur(roi, (51, 51), 0)
        frame[y1:y2, x1:x2] = blurred


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak bisa membuka webcam.")
        return

    hand_detector = create_hand_detector()
    face_detector = create_face_detector()
    mapper = VolumeMapper()

    # Volume awal dari sistem
    last_set_volume = get_current_volume()
    print(f"Volume awal sistem: {last_set_volume:.0f}%")
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
        timestamp = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        # Deteksi wajah → blur mulut
        face_result = face_detector.detect_for_video(mp_image, timestamp)
        if face_result.face_landmarks:
            for face_lm in face_result.face_landmarks:
                blur_mouth(frame, face_lm, h, w)

        # Deteksi tangan
        hand_result = hand_detector.detect_for_video(mp_image, timestamp)

        if hand_result.hand_landmarks:
            # Status text hijau di pojok kanan atas
            cv2.putText(
                frame, "Hand Detected", (w - 200, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
            )

            for hand_landmarks in hand_result.hand_landmarks:
                # Gambar landmark bawaan MediaPipe
                DrawingUtils.draw_landmarks(
                    image=frame,
                    landmark_list=hand_landmarks,
                    connections=HandConnections,
                )

                # Hitung jarak & volume dari gesture
                thumb = hand_landmarks[THUMB_TIP]
                index = hand_landmarks[INDEX_TIP]
                dist = mapper.get_distance(thumb, index, w, h)
                gesture_volume = mapper.update(dist)

                # Update volume sistem hanya jika selisih > threshold
                if abs(gesture_volume - last_set_volume) > VOLUME_THRESHOLD:
                    set_volume_scalar(gesture_volume / 100.0)
                    last_set_volume = gesture_volume

                # Titik merah di ujung jari
                tx, ty = int(thumb.x * w), int(thumb.y * h)
                ix, iy = int(index.x * w), int(index.y * h)
                cv2.circle(frame, (tx, ty), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(frame, (ix, iy), 8, (0, 0, 255), cv2.FILLED)

                # Garis penghubung
                cv2.line(frame, (tx, ty), (ix, iy), (0, 0, 255), 2)

                # Volume aktual dari sistem (untuk debug)
                sys_volume = get_current_volume()

                # Tampilkan di pojok kiri atas (merah)
                cv2.putText(
                    frame, f"Gesture: {gesture_volume:.0f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,
                )
                cv2.putText(
                    frame, f"System:  {sys_volume:.0f}%", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,
                )
                cv2.putText(
                    frame, f"Distance: {dist:.0f}px", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,
                )

                print(f"Distance: {dist:.1f} px | Gesture: {gesture_volume:.0f}% | System: {sys_volume:.0f}%")

        cv2.imshow("Hand Gesture Volume Control", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    hand_detector.close()
    face_detector.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
