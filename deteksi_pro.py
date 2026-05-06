import tkinter as tk
import cv2
import numpy as np
import tensorflow as tf
from mss import MSS
from PIL import Image, ImageTk
from classifiers import Meso4, MesoInception4

# --- KONFIGURASI AI ---
print("Memuat AI MesoNet... Mohon tunggu.")
# Menggunakan Meso4 yang lebih stabil untuk mendeteksi DeepFaceLive/FaceSwap
classifier = Meso4()
classifier.load('weights/Meso4_DF.h5')

def proses_gambar(face_crop):
    print("\n[STEP 1] Memproses gambar hasil crop...")
    
    # Konversi OpenCV BGR ke RGB
    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    
    # ---------------------------------------------------------
    # [PENTING] Deteksi letak wajah dengan HaarCascade
    # ---------------------------------------------------------
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=4)
    
    if len(faces) > 0:
        print("[INFO] Wajah terdeteksi di dalam crop. Merapikan crop ke bentuk presisi...")
        x, y, w, h_face = faces[0]
        
        # [PENTING] Memaksa crop menjadi persegi (square) agar model AI tidak "melihat" gambar yang distorsi/gepeng
        center_x = x + w // 2
        center_y = y + h_face // 2
        side = max(w, h_face)
        half_side = (side // 2) + int(side * 0.3)  # 30% margin
        
        top = max(0, center_y - half_side)
        bottom = min(face_rgb.shape[0], center_y + half_side)
        left = max(0, center_x - half_side)
        right = min(face_rgb.shape[1], center_x + half_side)
        
        img_ai_ready = face_rgb[top:bottom, left:right]
        img_bgr_ready = face_crop[top:bottom, left:right]
    else:
        print("[WARNING] Tidak ada wajah jelas yang terdeteksi, mencoba scan seluruh kotak manual...")
        img_ai_ready = face_rgb
        img_bgr_ready = face_crop

    # --- ANALISIS TAMBAHAN (TANPA PERLU RETRAINING) ---
    print("[STEP 2] Melakukan Analisis Artefak OpenCV (Noise & Blur)...")
    
    # [PENTING STABILISASI] Standarisasi ukuran agar nilai selalu konsisten terlepas dari ukuran tarikan mouse
    std_size = (256, 256)
    img_bgr_std = cv2.resize(img_bgr_ready, std_size)
    
    # 1. Laplacian Variance (Deteksi Blur)
    gray_face = cv2.cvtColor(img_bgr_std, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
    print(f"  -> Laplacian Variance (Ketajaman): {laplacian_var:.2f}")
    
    # 2. Error Level Analysis (ELA)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    _, encimg = cv2.imencode('.jpg', img_bgr_std, encode_param)
    decimg = cv2.imdecode(encimg, 1)
    ela_diff = cv2.absdiff(img_bgr_std, decimg)
    ela_score = np.mean(ela_diff)
    print(f"  -> ELA Score (Tingkat Artefak): {ela_score:.2f}")

    # --- ANALISIS MESONET ---
    print("[STEP 3] Menganalisis gambar dengan AI MesoNet...")
    img_ai = cv2.resize(img_ai_ready, (256, 256))
    img_ai = img_ai.astype(np.float32) / 255.0
    img_ai = np.expand_dims(img_ai, axis=0)

    meso_pred = classifier.predict(img_ai)[0][0]
    print(f"  -> MesoNet Score: {meso_pred:.4f}")
    
    # --- LOGIKA KEPUTUSAN GABUNGAN ---
    # DeepFaceLive cenderung:
    # 1. Memiliki Laplacian Variance rendah (blur/halus, biasanya < 150)
    # 2. ELA Score agak tinggi di batas tempelan (walaupun sulit ditebak, bisa bervariasi)
    # 3. MesoNet sering tertipu
    
    # Kita buat skor gabungan (Heuristic). Semakin tinggi final_score, semakin terdeteksi Manusia.
    # Base dari MesoNet:
    final_score = meso_pred 
    
    # Penalti jika gambar terlalu halus (indikasi kuat filter beautify / DeepFaceLive)
    if laplacian_var < 80:
        final_score -= 0.3  # Penalti besar
        print("  [!] Wajah terlalu halus/blur (Laplacian < 80), kemungkinan DeepFaceLive.")
    elif laplacian_var > 300:
        final_score += 0.2  # Bonus jika sangat tajam (pori-pori natural)
        
    # Penalti jika ada artefak tempelan kompresi yang aneh
    if ela_score > 3.0:
        final_score -= 0.15
        print("  [!] Terdeteksi anomali kompresi ELA (potensi tempelan).")

    # Batasi skor 0 - 1
    final_score = max(0.0, min(1.0, final_score))

    if final_score > 0.45:  # Ambang batas kita turunkan sedikit karena DeepFaceLive canggih
        status = "MANUSIA ASLI"
        warna_teks = "green"
    else:
        status = "TERDETEKSI AI / DEEPFACE"
        warna_teks = "red"

    print(f"✅ ANALISIS SELESAI: {status} (Skor Akhir: {final_score:.4f})")
    tampilkan_hasil(status, final_score, warna_teks)

def tampilkan_hasil(status, skor, warna):
    res_win = tk.Toplevel()
    res_win.title("Hasil Analisis IDS")
    res_win.geometry("350x200")
    res_win.attributes("-topmost", True)
    
    tk.Label(res_win, text="HASIL SCAN WAJAH:", font=("Arial", 10)).pack(pady=5)
    tk.Label(res_win, text=status, font=("Arial", 13, "bold"), fg=warna).pack(pady=10)
    
    tk.Label(res_win, text=f"Confidence Score: {skor:.4f}", font=("Courier", 10)).pack()
    
    # Progress bar sederhana
    canvas = tk.Canvas(res_win, width=200, height=20, bg="white")
    canvas.pack(pady=5)
    canvas.create_rectangle(0, 0, skor*200, 20, fill=warna)
    
    tk.Button(res_win, text="TUTUP", command=res_win.destroy, bg="#ecf0f1").pack(pady=10)

class ScreenSnip(tk.Toplevel):
    def __init__(self, master, bg_image_array):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.config(cursor="cross")
        
        self.bg_image_array = bg_image_array
        
        # Convert BGRA ke RGB untuk PIL (Tkinter)
        img_rgb = cv2.cvtColor(bg_image_array, cv2.COLOR_BGRA2RGB)
        self.bg_image_pil = Image.fromarray(img_rgb)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image_pil)
        
        # Buat Canvas yang menutupi seluruh layar
        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # Bind event mouse untuk cropping
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Escape>", lambda e: self.destroy())
        
        # Petunjuk (DIPERBAIKI: Hapus parameter bg="white" yang menyebabkan error)
        self.canvas.create_text(self.winfo_screenwidth()//2, 50, text="Tahan & Tarik Mouse untuk meng-crop wajah. Tekan ESC untuk batal.", 
                                fill="red", font=("Arial", 16, "bold"))

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=3)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        x1, x2 = sorted([self.start_x, end_x])
        y1, y2 = sorted([self.start_y, end_y])
        
        # Pastikan area crop cukup besar
        if (x2 - x1) > 20 and (y2 - y1) > 20:
            # Crop gambar asli (numpy array BGR)
            crop_img = self.bg_image_array[y1:y2, x1:x2]
            # Hapus alpha channel (BGRA -> BGR) jika diperlukan
            if crop_img.shape[2] == 4:
                crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGRA2BGR)
                
            self.destroy() # Tutup window crop
            
            # Panggil fungsi proses
            self.master.after(100, lambda: proses_gambar(crop_img))
        else:
            self.destroy()

def mulai_snip():
    # Sembunyikan window utama sebentar supaya tidak ikut terscreenshot
    root.withdraw()
    root.update()
    
    with MSS() as sct:
        # Ambil layar utama
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        bg_image_array = np.array(sct_img)
        
        # Tampilkan lagi window utama, lalu buka window snipping
        root.deiconify()
        snip_win = ScreenSnip(root, bg_image_array)

# --- MEMBUAT WIDGET MENGAMBANG ---
root = tk.Tk()
root.title("IDS Widget")
root.geometry("140x70+100+100")
root.attributes("-topmost", True) 
root.overrideredirect(True)
root.config(bg='#2c3e50') 
root.attributes("-alpha", 0.9)

btn = tk.Button(root, text="📷 CROP & SCAN", command=mulai_snip, 
                bg="#34495e", fg="white", font=("Arial", 10, "bold"),
                activebackground="#1abc9c", relief="flat")
btn.pack(fill="both", expand=True, padx=3, pady=3)

# Logika geser jendela
def start_move(event): 
    root.x = event.x
    root.y = event.y

def stop_move(event): 
    root.x = None
    root.y = None

def on_move(event):
    x = root.winfo_x() + (event.x - root.x)
    y = root.winfo_y() + (event.y - root.y)
    root.geometry(f"+{x}+{y}")

btn.bind("<Button-3>", start_move) 
btn.bind("<ButtonRelease-3>", stop_move)
btn.bind("<B3-Motion>", on_move)

print("Widget IDS Aktif.")
print("👉 KLIK KIRI untuk Crop & Scan layar.")
print("👉 TAHAN & GESER KLIK KANAN untuk memindah widget.")

root.mainloop()