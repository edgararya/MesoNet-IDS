import streamlit as st
import cv2
import tensorflow as tf
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Deepfake IDS Scanner", layout="wide")
st.title("🛡️ IDS Live Face Scanner")
st.sidebar.header("Control Panel")

# --- LOAD MODEL (Cache agar tidak berat) ---
@st.cache_resource
def load_pro_model():
    base = tf.keras.applications.InceptionResNetV2(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
    predictions = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    return tf.keras.models.Model(inputs=base.input, outputs=predictions)

model = load_pro_model()

# --- WIDGET DI SIDEBAR ---
threshold = st.sidebar.slider("Sensitivitas Deteksi", 0.0, 1.0, 0.5)
run_cam = st.sidebar.checkbox("Nyalakan Kamera")

# --- AREA UTAMA ---
frame_placeholder = st.empty()
status_placeholder = st.sidebar.empty()

# --- LOGIKA LIVE CAMERA ---
if run_cam:
    vid = cv2.VideoCapture(0) # 0 adalah ID webcam laptop
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break

        # Olah gambar untuk AI (299x299)
        img_ai = cv2.resize(frame, (299, 299))
        img_ai = np.expand_dims(img_ai, axis=0)
        img_ai = preprocess_input(img_ai)

        # Prediksi
        prediction = model.predict(img_ai)[0][0]

        # Tentukan Status
        if prediction > threshold:
            label = "ASLI (AUTHENTIC)"
            color = (0, 255, 0) # Hijau
        else:
            label = "PALSU (DEEPFAKE!)"
            color = (0, 0, 255) # Merah

        # Tambahkan Widget Text & Kotak di Video
        cv2.putText(frame, f"{label}: {prediction:.2f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Tampilkan di Streamlit
        frame_placeholder.image(frame, channels="BGR")
        status_placeholder.metric("Confidence Score", f"{prediction:.4f}")

    vid.release()
else:
    st.info("Klik 'Nyalakan Kamera' di sidebar untuk memulai pemindaian.")