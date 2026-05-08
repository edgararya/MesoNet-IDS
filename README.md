# MesoNet IDS: Deepfake Intrusion Detection System 🛡️

A real-time Deepfake Intrusion Detection System (IDS) designed for **Blue Team operations**. This project extends the original MesoNet architecture into a live scanning dashboard with target tracking and real-time AI analysis of video feeds or screen regions.

Sangat cocok digunakan untuk presentasi akademik, simulasi Cybersecurity, dan demonstrasi keamanan (*Live Scanning*).

## 🚀 Fitur Utama

- **Live Screen Scanner**: Kunci (lock) area mana saja di layar komputer Anda (contoh: video Zoom, YouTube, atau MP4 player) untuk dipantau secara *real-time*.
- **IDS Dashboard**: Interface pemantauan bergaya radar/Blue Team yang dilengkapi log sistem otomatis dan indikator intrusi.
- **Target Lock System**: Terintegrasi dengan fitur "Snipping Tool" mandiri untuk menangkap area layar secara dinamis tanpa bug rekursif (layar masuk ke dalam layar).
- **MesoNet AI Engine**: Ditenagai arsitektur Meso4 untuk mendeteksi artefak mesoscopic pada gambar wajah.
- **Hybrid ELA Analysis**: Mengkombinasikan Deep Learning dengan perhitungan **Error Level Analysis (ELA)**.
- **Automated Face Tracking**: Menggunakan Haar Cascades dengan *CLAHE Equalization* agar tetap bisa mendeteksi wajah meski video redup.

## 🛠️ Persyaratan Lingkungan (Environment Setup)

Sangat disarankan untuk menggunakan **Anaconda** / **Miniconda** untuk menghindari konflik dependensi (*terutama untuk TensorFlow di Windows*).

### 1. Install Anaconda / Miniconda
Pastikan Anda sudah menginstal [Miniconda](https://docs.conda.io/en/latest/miniconda.html) atau Anaconda.

### 2. Buat Environment Baru
Buka **Anaconda Prompt**, lalu jalankan perintah berikut secara berurutan:

```bash
# Buat environment dengan Python 3.9 (paling stabil untuk TensorFlow versi ini)
conda create -n ids_modern python=3.9 -y

# Aktifkan environment
conda activate ids_modern
```

### 3. Install Dependensi Inti
```bash
# Install library untuk AI dan gambar
pip install tensorflow opencv-python numpy pillow mss
```
*Catatan:* Jika Anda menggunakan Windows dan muncul *warning* TensorFlow GPU tidak tersedia, sistem akan otomatis beralih ke mode CPU (aman digunakan).

## 📦 Menjalankan Program

1. Clone atau unduh repositori ini.
2. Buka Anaconda Prompt, pindah ke folder proyek, dan pastikan environment aktif:
   ```bash
   cd path/ke/folder/MesoNet-master
   conda activate ids_modern
   ```
3. Jalankan Dashboard IDS:
   ```bash
   python live_scanner.py
   ```

## 🎭 Panduan Presentasi / Demo (Skenario Blue Team)

Aplikasi ini didesain agar terlihat profesional saat demonstrasi di depan audiens atau dosen:

1. **Siapkan Barang Bukti:** Buka sebuah video di sebelahnya (bisa video YouTube orang asli, dan tab lain berisi video Deepfake Tom Cruise).
2. **Jalankan Dashboard:** Buka `live_scanner.py`.
3. **Mulai Lock:** Klik tombol **"🎯 LOCK TARGET REGION"**.
4. **Sorot Area:** Layar akan redup seperti *Snipping Tool*. Seleksi/kotaki area wajah yang ada di video. Pastikan mengotaki area wajah saja (jangan terlalu besar/terlalu kecil).
5. **Analisis Berjalan:** 
   - Jika video manusia asli: Status akan berwarna Hijau **"✅ REAL HUMAN"**.
   - Jika diganti ke video Deepfake: AI akan mendeteksi keanehan. Bar Log akan menampilkan warna Merah dan teks **"🚨 DEEPFAKE DETECTED!"**. Log di bagian bawah akan otomatis mencatat status invasi/intrusi (*INTRUSION ALERT*).

### 💡 Tips Resolusi Masalah (Troubleshooting)
- **Status Stuck di "NO FACE":** Artinya AI gagal mendeteksi wajah di kotak yang Anda pilih. Coba klik "LOCK TARGET" lagi, lalu pilih kotak yang lebih presisi (jangan kepotong dagu atau keningnya).
- **Video redup/gelap:** Program sudah dilengkapi *auto-contrast (CLAHE)*, namun usahakan video yang dideteksi cukup terang.

## 🧠 Pretrained Models
Proyek ini membutuhkan *pretrained weights* yang sudah disediakan di folder `weights`:
- `Meso4_DF.h5`: Optimal untuk mendeteksi *Deepfake*.
- `Meso4_F2F.h5`: Optimal untuk mendeteksi manipulasi *Face2Face*.

## 📜 Referensi & Pengakuan
Proyek ini adalah ekstensi (GUI & Live Capabilities) dari riset awal MesoNet:
- **Darius Afchar, Vincent Nozick, Junichi Yamagishi, Isao Echizen.** "MesoNet: a Compact Facial Video Forgery Detection Network". WIFS 2018.

---
*Dikembangkan untuk riset akademik dan simulasi Cybersecurity Blue Team.*
