# Hand Gesture Volume Control

Kontrol volume sistem Windows menggunakan gestur tangan via webcam.
Jarak antara ujung jempol dan telunjuk dipetakan ke level volume sistem.

## Gesture yang Didukung

| Gesture | Aksi |
|---------|------|
| **Jempol + Telunjuk terbuka** | Atur volume (jarak = level volume) |
| **Kepalan tangan (fist)** | Mute / Unmute |
| **Tekan `q`** | Keluar |

## Fitur

- Deteksi tangan real-time pakai MediaPipe
- Mapping jarak jempol-telunjuk → volume sistem (via pycaw)
- Mute/unmute via kepalan tangan
- Visual overlay: volume bar gradien + hand landmark
- Blur area mulut (face detection)
- Startup instructions overlay
- Error handling robust

## Struktur Project

```
handrecognition/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md
├── src/
│   ├── __init__.py
│   ├── gesture.py           # Volume mapping & fist detection
│   ├── audio_control.py     # pycaw wrapper
│   └── overlay.py           # Visual overlay functions
└── assets/
    ├── hand_landmarker.task  # MediaPipe hand model
    └── face_landmarker.task  # MediaPipe face model
```

## Instalasi

### 1. Clone repository

```powershell
git clone https://github.com/he1kousen/hand-recognition.git
cd hand-recognition
```

### 2. Buat virtual environment

```powershell
python -m venv venv
```

### 3. Aktifkan virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

> Jika error execution policy, jalankan dulu:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Download model MediaPipe

Model sudah ada di folder `assets/`. Jika perlu download ulang:

```powershell
curl -L -o assets/hand_landmarker.task "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
curl -L -o assets/face_landmarker.task "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
```

### 6. Jalankan

```powershell
# Default (webcam 0)
python main.py

# Pilih webcam tertentu
python main.py --camera 1

# Bantuan
python main.py --help
```

Tekan `q` untuk keluar.

## Command-Line Arguments

| Argumen | Keterangan |
|---------|------------|
| `--camera N` / `-c N` | Pilih index webcam (default: 0) |
| `--mute-feedback` | Matikan audio feedback |

## Persyaratan

- Python 3.9+
- Windows 10/11
- Webcam

## Troubleshooting

### Webcam tidak terbuka
- Pastikan webcam tidak dipakai aplikasi lain
- Coba ganti index: `python main.py --camera 1`
- Cek Device Manager → Cameras untuk memastikan webcam terdeteksi

### pycaw error / volume tidak berubah
- pycaw hanya jalan di Windows. Project ini tidak support macOS/Linux
- Pastikan audio output device aktif (speaker/headphone tersambung)
- Coba restart Windows Audio Service di Services.msc

### MediaPipe error / landmark tidak terdeteksi
- Pastikan pencahayaan cukup
- Tangan harus menghadap kamera (telapak terlihat)
- Cek file model ada di `assets/`: `hand_landmarker.task` dan `face_landmarker.task`

### Frame drop / lag
- Tutup aplikasi lain yang pakai kamera/GPU
- Turunkan resolusi webcam di webcam settings
- Pastikan tidak ada proses berat di background

### Import error
- Pastikan virtual environment aktif: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`
