import numpy as np
from classifiers import MesoInception4

print("Loading model...")
model = MesoInception4()
model.load('weights/MesoInception_DF.h5')

# Test with pure white
img_white = np.ones((1, 256, 256, 3), dtype=np.float32)
pred_white = model.predict(img_white)[0][0]
print(f"White image prediction: {pred_white}")

# Test with pure black
img_black = np.zeros((1, 256, 256, 3), dtype=np.float32)
pred_black = model.predict(img_black)[0][0]
print(f"Black image prediction: {pred_black}")

# Test with random noise
np.random.seed(42)
img_rand = np.random.rand(1, 256, 256, 3).astype(np.float32)
pred_rand = model.predict(img_rand)[0][0]
print(f"Random noise prediction: {pred_rand}")
