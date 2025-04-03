import vosk
import os

model_path = "model/en"
if os.path.exists(model_path):
    model = vosk.Model(model_path)
    print("✅ Vosk Model Loaded Successfully!")
else:
    print("❌ Model path is incorrect. Please check.")