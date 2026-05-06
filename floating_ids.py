import tkinter as tk
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input
from mss import mss
import mss.tools

# --- KONFIGURASI AI ---
print("Memuat AI... Mohon tunggu sebentar.")
# Menggunakan InceptionResNetV2 yang lebih kuat
base = tf.keras.applications.InceptionResNetV2(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
predictions = tf.keras.layers.Dense(1, activation='sigmoid')(x)
model = tf.keras.models.Model(inputs=base.input, outputs=predictions)

def scan_sekarang():
    # Menggunakan mss.mss() sesuai saran warning atau MSS()
    with mss.mss() as sct:
        print("\n[MENGAMBIL TANGKAPAN LAYAR...]")
        # 1. Ambil screenshot seluruh layar utama
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Konversi ke format yang dimengerti OpenCV
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # 2. Pre-processing sesuai kebutuhan model (299x299)
        img_ai = cv2.resize(frame, (299, 299))
        img_ai = np.expand_dims(img_ai, axis=0)
        img_ai = preprocess_input(img_ai.astype(np.float32))

        # 3. Prediksi Deepfake
        prediction = model.predict(img_ai)[0][0]
        
        # Logika skor: Skor tinggi (>0.5) dianggap asli oleh model ini
        if prediction > 0.5:
            status = "MANUSIA ASLI"
            warna_teks = "green"
        else:
            status = "TERDETEKSI AI / DEEPFAKE"
            warna_teks = "red"

        print(f"HASIL: {status} | Skor: {prediction:.4f}")
        tampilkan_hasil(status, prediction, warna_teks)

def tampilkan_hasil(status, skor, warna):
    res_win = tk.Toplevel()
    res_win.title("Hasil Analisis IDS")
    res_win.geometry("350x180")
    res_win.attributes("-topmost", True) # Biar tetap di depan
    
    tk.Label(res_win, text="HASIL SCAN LAYAR:", font=("Arial", 10)).pack(pady=5)
    tk.Label(res_win, text=status, font=("Arial", 14, "bold"), fg=warna).pack(pady=10)
    tk.Label(res_win, text=f"Confidence Score: {skor:.4f}", font=("Courier", 10)).pack()
    
    tk.Button(res_win, text="TUTUP", command=res_win.destroy, bg="#ecf0f1").pack(pady=10)

# --- MEMBUAT TOMBOL MENGAMBANG (WIDGET) ---
root = tk.Tk()
root.title("IDS Widget")
# Posisi awal tombol (x=100, y=100)
root.geometry("120x60+100+100")
root.attributes("-topmost", True) 
root.overrideredirect(True) # Menghilangkan judul window agar terlihat seperti widget

# Warna background tombol yang solid agar tidak error
root.config(bg='#2c3e50') 
root.attributes("-alpha", 0.9) # Transparansi seluruh jendela (0.0 - 1.0)

# Tombol interaktif
btn = tk.Button(root, text="🛡️ SCAN AI", command=scan_sekarang, 
                bg="#34495e", fg="white", font=("Arial", 10, "bold"),
                activebackground="#1abc9c", relief="flat")
btn.pack(fill="both", expand=True, padx=2, pady=2)

# Fitur Drag & Drop (Geser tombol kemana saja di layar)
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

btn.bind("<Button-1>", start_move)
btn.bind("<ButtonRelease-1>", stop_move)
btn.bind("<B1-Motion>", on_move)

print("Widget IDS Aktif. Geser tombol dan klik untuk scan apa pun di layar OS.")
root.mainloop()