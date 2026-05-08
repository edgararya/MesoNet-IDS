import ctypes
try:
    # Aktifkan DPI awareness agar koordinat akurat di Windows scaling
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    pass
import tkinter as tk
from tkinter import scrolledtext
import cv2
import numpy as np
import tensorflow as tf
from mss import MSS
from PIL import Image, ImageTk
import threading
import time
from collections import deque
import datetime
from classifiers import Meso4
import os

# Matikan log TensorFlow yang terlalu berisik
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("Memuat AI MesoNet... Mohon tunggu.")
classifier = Meso4()
classifier.load('weights/Meso4_DF.h5')

score_history = deque(maxlen=5)  # 5 frame = respons lebih cepat

class SnippingTool:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback
        self.snip_window = tk.Toplevel(master)
        self.snip_window.attributes("-fullscreen", True)
        self.snip_window.attributes("-alpha", 0.3)
        self.snip_window.attributes("-topmost", True)
        self.snip_window.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.snip_window, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        self.rect = None
        self.start_x = None
        self.start_y = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.snip_window.bind("<Escape>", lambda e: self.snip_window.destroy())
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=3)
        
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        
    def on_release(self, event):
        end_x = event.x
        end_y = event.y
        self.snip_window.destroy()
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        self.callback(x1, y1, x2 - x1, y2 - y1)

class LiveScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDS Dashboard - Deepfake Scanner")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1e1e1e")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- UI LAYOUT ---
        # Top Header
        self.header = tk.Frame(self.root, bg="#0d47a1", height=50)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        tk.Label(self.header, text="🛡️ BLUE TEAM - DEEPFAKE INTRUSION DETECTION SYSTEM", fg="white", bg="#0d47a1", font=("Consolas", 14, "bold")).pack(pady=10)
        
        # Main Body
        self.body = tk.Frame(self.root, bg="#1e1e1e")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Panel (Video Feed & Selection)
        self.left_panel = tk.Frame(self.body, bg="#2d2d2d")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        # Fixed-size canvas untuk menampilkan video feed
        FEED_W, FEED_H = 480, 360
        self.feed_canvas = tk.Canvas(self.left_panel, bg="black", width=FEED_W, height=FEED_H,
                                     highlightthickness=1, highlightbackground="#3d3d3d")
        self.feed_canvas.pack(padx=10, pady=(10, 5))
        
        # Placeholder text di tengah canvas
        self.feed_canvas_text = self.feed_canvas.create_text(
            FEED_W // 2, FEED_H // 2,
            text="[ NO TARGET LOCKED ]\nKlik tombol di bawah\nuntuk memilih area",
            fill="#7f8c8d", font=("Consolas", 12), justify="center"
        )
        self._feed_image_id = None
        self.FEED_W = FEED_W
        self.FEED_H = FEED_H
        
        self.btn_select = tk.Button(self.left_panel, text="🎯 LOCK TARGET REGION", bg="#c0392b", fg="white",
                                    font=("Consolas", 12, "bold"), command=self.start_selection, relief="flat")
        self.btn_select.pack(pady=5, fill="x", padx=10)
        
        # Right Panel (Status & Log)
        self.right_panel = tk.Frame(self.body, bg="#2d2d2d", width=400)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.lbl_status = tk.Label(self.right_panel, text="STATUS: STANDBY", bg="#2d2d2d", fg="#bdc3c7", font=("Consolas", 16, "bold"))
        self.lbl_status.pack(pady=20)
        
        self.lbl_score = tk.Label(self.right_panel, text="AI Confidence: N/A", bg="#2d2d2d", fg="white", font=("Consolas", 12))
        self.lbl_score.pack(pady=5)
        
        tk.Label(self.right_panel, text="[ SYSTEM LOGS ]", bg="#2d2d2d", fg="#2ecc71", font=("Consolas", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.log_box = scrolledtext.ScrolledText(self.right_panel, bg="#000000", fg="#00ff00", font=("Consolas", 9), height=15)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.log("System Initialized. MesoNet AI Loaded.")
        self.log("MediaPipe Face Tracker Ready.")
        
        # --- LOGIC ---
        self.sct = MSS()
        self.target_coords = None # (x, y, w, h) physical
        self.is_running = True
        
        self.thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.thread.start()

    def log(self, message):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{now}] {message}\n")
        self.log_box.see(tk.END)
        
    def start_selection(self):
        self.log("Menunggu pemilihan target area...")
        # Sembunyikan window IDS agar tidak ikut ter-capture saat user menyeleksi area
        self.root.withdraw()
        # Tunggu sebentar agar window benar-benar hilang dari layar sebelum snipping tool muncul
        self.root.after(300, lambda: SnippingTool(self.root, self.on_target_selected))

    def on_target_selected(self, x, y, w, h):
        # Tampilkan kembali window IDS setelah seleksi selesai
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
        if w < 50 or h < 50:
            self.log("[ERROR] Area target terlalu kecil. Batal.")
            return
            
        # Menghitung ratio monitor (logical vs physical pixels)
        logical_width = self.root.winfo_screenwidth()
        physical_width = self.sct.monitors[1]["width"]
        ratio = physical_width / logical_width if logical_width > 0 else 1.0
        
        x_phy = int(x * ratio)
        y_phy = int(y * ratio)
        w_phy = int(w * ratio)
        h_phy = int(h * ratio)
        
        self.target_coords = (x_phy, y_phy, w_phy, h_phy)
        self.log(f"✅ Target Locked: ({x_phy}, {y_phy}) ukuran {w_phy}x{h_phy}px")
        score_history.clear()

    def scan_loop(self):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        while self.is_running:
            if self.target_coords:
                x, y, w, h = self.target_coords
                try:
                    monitor = {"top": y, "left": x, "width": w, "height": h}
                    sct_img = self.sct.grab(monitor)
                    img_bgra = np.array(sct_img)
                    frame = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
                    
                    self.process_frame(frame, face_cascade)
                except Exception as e:
                    import traceback
                    print("Error di scan_loop:", traceback.format_exc())
            else:
                time.sleep(0.1)

    def process_frame(self, frame, face_cascade):
        ih, iw, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Equalisasi kontras agar wajah gelap/video streaming tetap terdeteksi
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_eq = clahe.apply(gray)
        
        # --- Deteksi wajah dengan Haar Cascade ---
        faces = face_cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.03,
            minNeighbors=1,   # Lebih sensitif
            minSize=(15, 15),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        status_text = "SCANNING..."
        status_color = "#3498db"
        score_text = "AI Confidence: N/A"
        log_msg = None
        
        if len(faces) == 0:
            status_text = "NO FACE — Perluas atau geser area lock"
            status_color = "#f39c12"
            self.root.after(0, self.update_gui, frame, status_text, status_color, score_text, log_msg)
            time.sleep(0.08)
            return
        
        # --- Ambil wajah terbesar ---
        best_face = max(faces, key=lambda r: r[2] * r[3])
        fx, fy, fw, fh = best_face
        center_x = fx + fw // 2
        center_y = fy + fh // 2
        side = max(fw, fh)
        half_side = int((side // 2) * 1.35)  # Margin 35%
        
        top    = max(0, center_y - half_side)
        bottom = min(ih, center_y + half_side)
        left   = max(0, center_x - half_side)
        right  = min(iw, center_x + half_side)
        
        face_crop = frame[top:bottom, left:right]
        
        if face_crop.shape[0] < 20 or face_crop.shape[1] < 20:
            status_text = "WAJAH TERLALU KECIL — perluas area lock"
            status_color = "#f39c12"
            self.root.after(0, self.update_gui, frame, status_text, status_color, score_text, log_msg)
            time.sleep(0.08)
            return
        
        try:
            face_std = cv2.resize(face_crop, (256, 256))
            
            # ELA Analysis (Error Level Analysis)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, encimg = cv2.imencode('.jpg', face_std, encode_param)
            decimg = cv2.imdecode(encimg, 1)
            ela_score = float(np.mean(cv2.absdiff(face_std, decimg)))
            
            # MesoNet AI Prediction
            img_ai = face_std.astype(np.float32) / 255.0
            img_ai = np.expand_dims(img_ai, axis=0)
            
            result = classifier.predict(img_ai)
            if result is None or len(result) == 0:
                status_text = "AI Error — model tidak merespons"
                status_color = "#e74c3c"
                self.root.after(0, self.update_gui, frame, status_text, status_color, score_text, log_msg)
                time.sleep(0.08)
                return
            
            raw_score = float(result[0][0])  # Nilai mentah per frame (0=fake, 1=real)
            score_history.append(raw_score)
            avg_score = sum(score_history) / len(score_history)
            
            # avg_score mendekati 0 = FAKE, mendekati 1 = REAL
            fake_prob = (1.0 - avg_score) * 100
            raw_fake  = (1.0 - raw_score) * 100   # untuk ditampilkan tanpa smoothing
            
            if fake_prob > 45:  # Threshold 45% lebih sensitif
                status_text = "🚨 DEEPFAKE DETECTED!"
                status_color = "#e74c3c"
                box_color = (0, 0, 255)   # Merah BGR
                if fake_prob > 65:
                    log_msg = f"[INTRUSION ALERT] Deepfake terdeteksi! Prob: {fake_prob:.1f}%"
            else:
                status_text = "✅ REAL HUMAN"
                status_color = "#2ecc71"
                box_color = (0, 255, 0)   # Hijau BGR
            
            score_text = f"Deepfake Score: {fake_prob:.0f}%"
            
            # Gambar bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            label_y = top - 10 if top > 20 else bottom + 20
            cv2.putText(frame, f"FAKE:{fake_prob:.0f}%",
                        (left, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
            
        except Exception as e:
            import traceback
            print("Error AI prediction:", traceback.format_exc())
            status_text = "ERROR: AI prediction gagal"
            status_color = "#e74c3c"
        
        # Update UI
        self.root.after(0, self.update_gui, frame, status_text, status_color, score_text, log_msg)
        time.sleep(0.05)  # ~20 fps

    def update_gui(self, frame, status_text, status_color, score_text, log_msg):
        self.lbl_status.config(text=status_text, fg=status_color)
        self.lbl_score.config(text=score_text)
        
        if log_msg:
            # Cegah spam log, catat 1 log per 3 detik untuk alert
            current_time = time.time()
            if not hasattr(self, 'last_log_time') or current_time - self.last_log_time > 3.0:
                self.log(log_msg)
                self.last_log_time = current_time
            
        # Tampilkan feed ke fixed Canvas
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        fh, fw = frame_rgb.shape[:2]
        if fw > 0 and fh > 0:
            scale = min(self.FEED_W / fw, self.FEED_H / fh)
            new_w = max(1, int(fw * scale))
            new_h = max(1, int(fh * scale))
            
            frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
            img_pil = Image.fromarray(frame_resized)
            img_tk = ImageTk.PhotoImage(img_pil)
            
            # Hapus gambar lama, gambar baru di tengah canvas
            if self._feed_image_id:
                self.feed_canvas.delete(self._feed_image_id)
            self.feed_canvas.delete(self.feed_canvas_text)
            self._feed_image_id = self.feed_canvas.create_image(
                self.FEED_W // 2, self.FEED_H // 2, anchor="center", image=img_tk
            )
            self.feed_canvas.image = img_tk  # Cegah garbage collection
            
    def on_close(self):
        self.is_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveScannerApp(root)
    root.mainloop()
