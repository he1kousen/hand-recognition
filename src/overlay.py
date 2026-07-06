"""
Visual overlay functions untuk Hand Gesture Volume Control.
"""

import time

import cv2


def draw_volume_bar(frame, volume: float, x: int = None, bar_w: int = 30, margin: int = 30):
    """Gambar volume bar vertikal di sisi kanan layar dengan gradien hijau→kuning→merah."""
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

    if fill_h > 0:
        for i in range(fill_h):
            ratio = i / bar_h
            y_pos = y_bot - i
            if ratio < 0.5:
                g, r, b = 255, int(255 * (ratio / 0.5)), 0
            else:
                r, g, b = 255, int(255 * (1 - (ratio - 0.5) / 0.5)), 0
            cv2.line(frame, (x + 2, y_pos), (x + bar_w - 2, y_pos), (b, g, r), 1)

    # Border
    cv2.rectangle(frame, (x, y_top), (x + bar_w, y_bot), (200, 200, 200), 2)

    # Persentase di atas bar
    text = f"{volume:.0f}%"
    cv2.putText(
        frame, text, (x + bar_w // 2 - 15, y_top - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
    )


class StartupInstructions:
    """Overlay instruksi saat pertama kali start, hilang setelah deteksi tangan."""

    def __init__(self):
        self.visible = True

    def dismiss(self):
        """Sembunyikan instruksi (dipanggil saat tangan pertama kali terdeteksi)."""
        self.visible = False

    def draw(self, frame):
        """Gambar instruksi di tengah layar."""
        if not self.visible:
            return

        h, w, _ = frame.shape
        overlay = frame.copy()

        # Semi-transparent background
        box_y1 = h // 2 - 100
        box_y2 = h // 2 + 100
        cv2.rectangle(overlay, (40, box_y1), (w - 40, box_y2), (0, 0, 0), cv2.FILLED)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Teks instruksi
        lines = [
            "Hand Gesture Volume Control",
            "",
            "Jempol + Telunjuk = Atur Volume",
            "Kepalan Tangan  = Mute/Unmute",
            "",
            "Tekan 'q' untuk keluar",
        ]

        font = cv2.FONT_HERSHEY_SIMPLEX
        y_start = box_y1 + 30
        for i, line in enumerate(lines):
            scale = 0.7 if i == 0 else 0.55
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            thickness = 2 if i == 0 else 1
            text_size = cv2.getTextSize(line, font, scale, thickness)[0]
            tx = (w - text_size[0]) // 2
            ty = y_start + i * 28
            cv2.putText(frame, line, (tx, ty), font, scale, color, thickness)
