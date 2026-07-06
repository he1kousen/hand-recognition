# Prompt Claude Code CLI — Hand Gesture Volume Control

Cara pakai: jalanin `claude` di folder project baru, terus copy-paste tiap fase satu-satu (tunggu fase sebelumnya kelar dan ditest dulu sebelum lanjut). Jangan langsung tempel semua sekaligus biar Claude Code nggak overengineer di awal.

---

## FASE 0 — Setup Project & Environment

```
Saya mau bikin project Python "Hand Gesture Volume Control" yang jalan di Windows.
Fungsinya: kamera mendeteksi tangan, jarak antara ujung jempol dan ujung telunjuk
dipetakan jadi level volume sistem (semakin lebar jarak = semakin besar volume).
Nantinya juga akan ada audio feedback (bunyi saat volume naik/turun) dan visual
overlay (progress bar volume + hand landmark) di jendela OpenCV.

Tolong setup dulu:
1. Struktur folder project yang rapi (misal: src/, assets/sounds/, main.py, requirements.txt, README.md)
2. requirements.txt berisi: opencv-python, mediapipe, numpy, pycaw, comtypes, dan library
   untuk play sound ringan (misal simpleaudio atau playsound — pilih yang paling stabil di Windows)
3. Virtual environment (venv) dan instruksi instalasi di README
4. File main.py kosong dengan skeleton awal: buka webcam pakai OpenCV, tampilkan jendela,
   keluar saat tombol 'q' ditekan

Setelah itu jalankan dan pastikan kamera bisa kebuka tanpa error sebelum lanjut ke fase berikutnya.
```

---

## FASE 1 — Deteksi Tangan dengan MediaPipe

```
Lanjutkan project ini. Sekarang integrasikan MediaPipe Hands ke main.py:

1. Deteksi 1 tangan (max_num_hands=1 dulu biar simpel dan stabil)
2. Gambar landmark tangan di frame video (pakai mp_drawing bawaan MediaPipe dulu, tidak usah custom)
3. Ambil koordinat landmark ujung jempol (id 4) dan ujung telunjuk (id 8)
4. Tampilkan titik merah di kedua ujung jari itu, dan garis penghubung antara keduanya
5. Print jarak (dalam pixel) antara kedua titik itu ke console tiap frame, buat sanity check

Pastikan tetap smooth di ~30fps dan tidak crash kalau tangan keluar dari frame.
```

---

## FASE 2 — Mapping Jarak ke Level Volume

```
Lanjutkan project ini. Sekarang buat logic untuk convert jarak jempol-telunjuk jadi
persentase volume 0-100%:

1. Buat konstanta MIN_DISTANCE dan MAX_DISTANCE (kira-kira dari kalibrasi manual,
   misal 20px = 0%, 200px = 100% — buat gampang diubah nanti)
2. Gunakan numpy.interp untuk mapping jarak ke rentang 0-100
3. Clamp hasilnya biar tidak keluar dari 0-100
4. Tambahkan smoothing sederhana (misal moving average 5 frame terakhir) supaya
   angka volume tidak jitter/lompat-lompat
5. Tampilkan angka persentase volume di pojok kiri atas frame (teks putih, font tebal)

Pisahkan logic ini ke file terpisah (misal src/gesture.py) biar main.py tetap bersih.
```

---

## FASE 3 — Kontrol Volume Sistem Beneran (pycaw)

```
Lanjutkan project ini. Sekarang hubungkan persentase volume dari gesture ke
volume sistem Windows beneran pakai pycaw:

1. Buat module src/audio_control.py yang wrap pycaw (get_volume_interface,
   set_volume_scalar, get_current_volume)
2. Tiap frame, set volume sistem sesuai persentase dari deteksi tangan
3. Tambahkan threshold kecil (misal hanya update kalau selisih >2%) supaya
   tidak spam-update volume dan bikin lag
4. Tampilkan volume sistem aktual (bukan cuma dari gesture) juga di layar
   sebagai pembanding/debug

Test dengan real volume laptop — pastikan naik turun beneran ngefek ke sistem.
```

---

## FASE 4 — Audio Feedback (Bunyi saat Volume Naik/Turun)

```
Lanjutkan project ini. Sekarang tambahkan audio feedback:

1. Siapkan 2 file suara pendek (bisa generate tone sederhana pakai numpy+scipy
   kalau tidak ada file siap pakai — misal beep naik nada untuk volume up,
   beep turun nada untuk volume down) simpan di assets/sounds/
2. Buat module src/sound_feedback.py yang:
   - Play sound "volume_up" ketika volume naik melewati threshold tertentu
   - Play sound "volume_down" ketika volume turun melewati threshold tertentu
   - Punya cooldown (misal 300ms) supaya suara tidak spam terus-menerus tiap frame
   - Berjalan di thread terpisah / non-blocking supaya tidak bikin video freeze
3. Integrasikan ke main loop: setiap kali ada perubahan volume signifikan, trigger sound yang sesuai

Pastikan suara playback tidak nge-lag video feed sama sekali.
```

---

## FASE 5 — Visual Overlay yang Lebih Niat

```
Lanjutkan project ini. Sekarang percantik visual overlay-nya jadi lebih niat,
bukan cuma teks polos:

1. Volume bar vertikal di sisi kanan layar (kayak equalizer), terisi sesuai
   persentase volume, warna gradasi (hijau di bawah, kuning tengah, merah di atas)
2. Landmark tangan digambar custom (bukan default MediaPipe yang biru-item):
   titik jempol dan telunjuk warna cyan, garis penghubung warna putih tipis,
   lingkaran di titik tengah garis yang membesar/mengecil sesuai jarak
3. Teks persentase volume besar dan jelas, dengan efek shadow/outline biar
   kebaca di background apapun
4. Indikator kecil (ikon panah atau teks "▲ UP" / "▼ DOWN") yang muncul sesaat
   tiap kali audio feedback ke-trigger, lalu fade out
5. FPS counter kecil di pojok buat monitoring performa

Simpan semua fungsi drawing ini di src/overlay.py biar main.py tetap ringkas.
```

---

## FASE 6 — Polish, Stabilitas, dan UX

```
Lanjutkan project ini. Sekarang fase finishing:

1. Tambahkan gesture khusus untuk mute/unmute (misal kepalan tangan/fist terdeteksi
   dari semua ujung jari menekuk ke arah telapak — pakai perbandingan jarak landmark)
2. Tambahkan on-screen instruction singkat saat aplikasi baru start (overlay teks
   yang hilang setelah beberapa detik atau saat tangan pertama kali terdeteksi)
3. Tambahkan try-except di seluruh main loop supaya kalau ada error (kamera kedisconnect,
   dsb) aplikasi keluar dengan pesan jelas, bukan crash mentah
4. Tambahkan opsi command-line argument (pakai argparse) untuk pilih index kamera
   (--camera 0/1) dan toggle sound on/off (--mute-feedback)
5. Update README.md dengan: cara install, cara run, screenshot/gif kalau ada,
   penjelasan singkat gesture yang didukung, dan troubleshooting umum (kamera
   tidak kebuka, pycaw error di non-Windows, dll)

Terakhir, review keseluruhan kode untuk clean-up: hapus print debug yang tidak perlu,
rapikan struktur file, dan pastikan tidak ada hardcoded path yang bikin project
tidak portable.
```

---

### Catatan tambahan
- pycaw itu Windows-only. Kalau nanti pengen cross-platform, bagian audio_control.py itu yang paling perlu di-swap (misal pakai `osascript` di Mac atau `amixer` di Linux).
- Kalau webcam laptop kurang responsif buat testing gesture cepat, gunain kamera eksternal atau turunin resolusi capture (misal 640x480) biar MediaPipe lebih cepat proses tiap frame.
- Kalibrasi MIN_DISTANCE/MAX_DISTANCE di Fase 2 itu bakal beda-beda tergantung jarak tangan ke kamera — kalau mau lebih robust, bisa nanti ditambah auto-kalibrasi pakai ukuran telapak tangan sebagai referensi jarak.