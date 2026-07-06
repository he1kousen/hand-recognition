"""
Gesture → Volume mapping logic.
Convert jarak jempol-telunjuk ke persentase volume 0-100%.
"""

import math
from collections import deque

import numpy as np

# Kalibrasi jarak (pixel) — sesuaikan sesuai resolusi kamera
MIN_DISTANCE = 20   # px → 0% volume
MAX_DISTANCE = 200  # px → 100% volume

# Smoothing window
SMOOTH_WINDOW = 5


class VolumeMapper:
    """Map jarak jari ke volume 0-100% dengan smoothing."""

    def __init__(self, min_dist=MIN_DISTANCE, max_dist=MAX_DISTANCE, window=SMOOTH_WINDOW):
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.history = deque(maxlen=window)

    def update(self, distance: float) -> float:
        """Terima jarak (px), return volume 0-100% (smoothed)."""
        # Map ke 0-100
        vol = np.interp(distance, [self.min_dist, self.max_dist], [0, 100])
        # Clamp
        vol = float(np.clip(vol, 0, 100))
        # Smoothing
        self.history.append(vol)
        return sum(self.history) / len(self.history)

    def get_distance(self, thumb_tip, index_tip, frame_w: int, frame_h: int) -> float:
        """Hitung Euclidean distance antara dua landmark dalam pixel."""
        tx, ty = int(thumb_tip.x * frame_w), int(thumb_tip.y * frame_h)
        ix, iy = int(index_tip.x * frame_w), int(index_tip.y * frame_h)
        return math.hypot(ix - tx, iy - ty)
