# Hand Gesture Volume Control

Kontrol volume sistem Windows menggunakan gestur tangan via webcam.
Jarak antara ujung jempol dan telunjuk dipetakan ke level volume sistem.

## Fitur

- Deteksi tangan real-time pakai MediaPipe
- Mapping jarak jempol-telunjuk → volume sistem (via pycaw)
- Audio feedback (bunyi saat volume naik/turun)
- Visual overlay: progress bar volume + hand landmark

## Struktur Project

```
handrecognition/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── README.md
├── src/                 # Modul-modul
│   └── __init__.py
└── assets/
    ├── hand_landmarker.task  # MediaPipe hand landmarker model
    └── sounds/               # File WAV untuk audio feedback
```

## Instalasi

### 1. Clone / masuk ke folder project

```powershell
cd c:\Project\python\handrecognition
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

Model hand landmarker sudah ada di `assets/hand_landmarker.task`.
Jika perlu download ulang:

```powershell
curl -L -o assets/hand_landmarker.task "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
```

### 6. Jalankan

```powershell
python main.py
```

Tekan `q` untuk keluar.

## Persyaratan

- Python 3.9+
- Windows 10/11
- Webcam
