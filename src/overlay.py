"""
Visual overlay functions untuk Hand Gesture Volume Control.
Semua fungsi drawing dipisah di sini supaya main.py tetap ringkas.
"""

import time

import cv2
import numpy as np


# ──────────────────────────────────────────────
# 1. Volume Bar Vertikal (gradien hijau→kuning→merah)
# ──────────────────────────────────────────────

def draw_volume_bar(frame, volume: float, x: int = None, bar_w: int = 30, margin: int = 30):
    """Gambar volume bar vertikal di sisi kanan layar."""
    h, w, _ = frame.shape
    if x is None:
        x = w - margin - bar_w

    y_top = margin
    y_bot = h - margin
    bar_h = y_bot - y_top

    # Background bar (semi-transparent dark)
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y_top), (x + bar_w, y_bot), (40, 40, 40), cv2.FILLED)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Fill level
    fill_h = int(bar_h * volume / 100)
    y_fill = y_bot - fill_h

    if fill_h > 0:
        # Gradien hijau→kuning→merah dari bawah ke atas
        for i in range(fill_h):
            ratio = i / bar_h  # 0=bawah, 1=atas
            y_pos = y_bot - i
            if ratio < 0.5:
                # Hijau → Kuning
                g = 255
                r = int(255 * (ratio / 0.5))
                b = 0
            else:
                # Kuning → Merah
                r = 255
                g = int(255 * (1 - (ratio - 0.5) / 0.5))
                b = 0
            cv2.line(frame, (x + 2, y_pos), (x + bar_w - 2, y_pos), (b, g, r), 1)

    # Border
    cv2.rectangle(frame, (x, y_top), (x + bar_w, y_bot), (200, 200, 200), 2)

    # Persentase di atas bar
    text = f"{volume:.0f}%"
    cv2.putText(
        frame, text, (x + bar_w // 2 - 15, y_top - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
    )


# ──────────────────────────────────────────────
# 2. Custom Hand Landmarks
# ──────────────────────────────────────────────

def draw_custom_hand(frame, thumb_tip, index_tip, w: int, h: int, distance: float):
    """Gambar landmark custom: cyan dots, white line, scaling midpoint circle."""
    tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
    ix, iy = int(index_tip.x * w), int(index_tip.y * h)

    # Titik cyan di ujung jari
    cv2.circle(frame, (tx, ty), 10, (255, 255, 0), cv2.FILLED)
    cv2.circle(frame, (ix, iy), 10, (255, 255, 0), cv2.FILLED)

    # Outline gelap di sekitar titik biar kontras
    cv2.circle(frame, (tx, ty), 10, (0, 0, 0), 2)
    cv2.circle(frame, (ix, iy), 10, (0, 0, 0), 2)

    # Garis penghubung putih tipis
    cv2.line(frame, (tx, ty), (ix, iy), (255, 255, 255), 1)

    # Lingkaran di titik tengah, radius sesuai jarak
    mx, my = (tx + ix) // 2, (ty + iy) // 2
    radius = int(np.clip(distance / 4, 5, 60))

    # Lingkaran luar (glow effect)
    cv2.circle(frame, (mx, my), radius + 3, (255, 255, 0), 1)
    cv2.circle(frame, (mx, my), radius, (255, 255, 0), 2)

    return tx, ty, ix, iy


# ──────────────────────────────────────────────
# 3. Volume Text dengan Shadow/Outline
# ──────────────────────────────────────────────

def draw_volume_text(frame, text: str, x: int, y: int, scale: float = 1.2):
    """Gambar teks dengan outline hitam tebal supaya kebaca di background apapun."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 3

    # Shadow/outline hitam
    cv2.putText(frame, text, (x + 2, y + 2), font, scale, (0, 0, 0), thickness + 2)
    # Teks utama merah terang
    cv2.putText(frame, text, (x, y), font, scale, (0, 0, 255), thickness)


# ──────────────────────────────────────────────
# 4. Direction Indicator (▲ UP / ▼ DOWN) dengan fade-out
# ──────────────────────────────────────────────

class DirectionIndicator:
    """Indikator arah volume yang muncul sesaat lalu fade out."""

    def __init__(self, display_duration: float = 1.0, fade_duration: float = 0.5):
        self.direction = None      # "up" atau "down"
        self.trigger_time = 0.0
        self.display_duration = display_duration
        self.fade_duration = fade_duration

    def trigger(self, direction: str):
        """Trigger indikator baru ('up' atau 'down')."""
        self.direction = direction
        self.trigger_time = time.time()

    def draw(self, frame, x: int = 10, y: int = 140):
        """Gambar indikator jika masih aktif."""
        if self.direction is None:
            return

        elapsed = time.time() - self.trigger_time
        if elapsed > self.display_duration + self.fade_duration:
            self.direction = None
            return

        # Hitung alpha (fade out)
        if elapsed < self.display_duration:
            alpha = 1.0
        else:
            alpha = 1.0 - (elapsed - self.display_duration) / self.fade_duration

        if self.direction == "up":
            text = "UP"
            color = (0, 255, 0)  # hijau
        else:
            text = "DOWN"
            color = (0, 0, 255)  # merah

        # Overlay semi-transparan
        overlay = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overlay, text, (x, y), font, 0.9, (0, 0, 0), 4)  # outline
        cv2.putText(overlay, text, (x, y), font, 0.9, color, 2)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


# ──────────────────────────────────────────────
# 5. FPS Counter
# ──────────────────────────────────────────────

class FPSCounter:
    """Hitung dan tampilkan FPS."""

    def __init__(self):
        self.prev_time = time.time()
        self.fps = 0.0

    def update(self):
        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)  # smoothed
        return self.fps

    def draw(self, frame, x: int = None, y: int = None):
        """Gambar FPS counter di pojok kanan bawah."""
        h, w, _ = frame.shape
        if x is None:
            x = w - 100
        if y is None:
            y = h - 15

        text = f"FPS: {self.fps:.0f}"
        cv2.putText(
            frame, text, (x, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1,
        )
