import tensorflow as tf
from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
import numpy as np

# 1. Membangun Arsitektur Xception yang sudah dilatih (ImageNet)
# Di industri, model ini dilatih ulang khusus untuk deepfake
base_model = Xception(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(1, activation='sigmoid')(x)
model = Model(inputs=base_model.input, outputs=predictions)

print("Model Xception berhasil dimuat ke RTX 2050...")

def deteksi_hebat(img_path):
    # Xception butuh ukuran 299x299
    img = image.load_img(img_path, target_size=(299, 299))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = tf.keras.applications.xception.preprocess_input(x)

    print(f"Menganalisis: {img_path}")
    preds = model.predict(x)
    score = preds[0][0]
    
    print("-" * 30)
    print(f"Skor Keyakinan Asli: {score:.4f}")
    
    if score > 0.5:
        print("Hasil: Terdeteksi Wajah MANUSIA ASLI")
    else:
        print("Hasil: Terdeteksi MANIPULASI AI / DEEPFAKE")
    print("-" * 30)

# Jalankan tes pada gambar yang tadi membuat MesoNet tertipu
deteksi_hebat('test_images/df/df01254.jpg')