import os
import cv2
from deepface import DeepFace

# Rasmlar joylashgan papka
faces_dir = "faces"


def analyze_faces():
    """Yuklab olingan rasmlarni DeepFace bilan tahlil qilish"""

    if not os.path.exists(faces_dir):
        print("❌ 'faces/' papkasi mavjud emas. Avval rasmlarni yuklab oling.")
        return

    image_files = [f for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

    if not image_files:
        print("❌ 'faces/' papkasida rasm topilmadi.")
        return

    for image_name in image_files:
        image_path = os.path.join(faces_dir, image_name)

        try:
            # OpenCV yordamida rasmni yuklash
            img = cv2.imread(image_path)
            if img is None:
                print(f"❌ {image_name} yuklab bo‘lmadi.")
                continue

            # Yuzni aniqlash
            analysis = DeepFace.analyze(img_path=image_path, actions=['age', 'gender'], enforce_detection=False)

            # Agar inson aniqlansa
            if analysis:
                print(f"✅ {image_name}: Inson mavjud.")
            else:
                print(f"❌ {image_name}: Inson topilmadi.")

        except Exception as e:
            print(f"⚠️ {image_name}: Xatolik yuz berdi -> {e}")


# ✅ Rasmlarni tahlil qilish
analyze_faces()
