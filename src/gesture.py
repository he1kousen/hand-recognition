"""
Gesture → Volume mapping & fist detection logic.
"""

import math
from collections import deque

import numpy as np

# Kalibrasi jarak (pixel) — sesuaikan sesuai resolusi kamera
MIN_DISTANCE = 20   # px → 0% volume
MAX_DISTANCE = 200  # px → 100% volume

# Smoothing window
SMOOTH_WINDOW = 5

# Landmark IDs ujung jari & pangkal jari (untuk fist detection)
FINGER_TIPS = [8, 12, 16, 20]       # telunjuk, tengah, manis, kelingking
FINGER_MCPS = [5, 9, 13, 17]        # pangkal jari masing-masing


class VolumeMapper:
    """Map jarak jari ke volume 0-100% dengan smoothing."""

    def __init__(self, min_dist=MIN_DISTANCE, max_dist=MAX_DISTANCE, window=SMOOTH_WINDOW):
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.history = deque(maxlen=window)

    def update(self, distance: float) -> float:
        """Terima jarak (px), return volume 0-100% (smoothed)."""
        vol = np.interp(distance, [self.min_dist, self.max_dist], [0, 100])
        vol = float(np.clip(vol, 0, 100))
        self.history.append(vol)
        return sum(self.history) / len(self.history)

    def get_distance(self, thumb_tip, index_tip, frame_w: int, frame_h: int) -> float:
        """Hitung Euclidean distance antara dua landmark dalam pixel."""
        tx, ty = int(thumb_tip.x * frame_w), int(thumb_tip.y * frame_h)
        ix, iy = int(index_tip.x * frame_w), int(index_tip.y * frame_h)
        return math.hypot(ix - tx, iy - ty)


def is_fist(hand_landmarks, frame_w: int, frame_h: int) -> bool:
    """Deteksi kepalan tangan: semua ujung jari lebih dekat ke telapak daripada pangkalnya."""
    wrist = hand_landmarks[0]

    for tip_id, mcp_id in zip(FINGER_TIPS, FINGER_MCPS):
        tip = hand_landmarks[tip_id]
        mcp = hand_landmarks[mcp_id]

        tip_dist = math.hypot(
            (tip.x - wrist.x) * frame_w,
            (tip.y - wrist.y) * frame_h,
        )
        mcp_dist = math.hypot(
            (mcp.x - wrist.x) * frame_w,
            (mcp.y - wrist.y) * frame_h,
        )

        # Jika ujung jari lebih jauh dari pangkal = jari terbuka → bukan fist
        if tip_dist > mcp_dist * 0.9:
            return False

    return True
