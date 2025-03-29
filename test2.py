import os
import requests
from supabase import create_client, Client

# Supabase ma'lumotlari
SUPABASE_URL = "https://rdqutzknswfuondczfrt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkcXV0emtuc3dmdW9uZGN6ZnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5NDIxNDAsImV4cCI6MjA1NjUxODE0MH0.Cf1RggQ4e8L34Ged3RKvrNdkYtMUU0u9NSEeVbCa3qg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def download_known_faces():
    """Supabase-dan barcha rasmlarni yuklab olish va `faces/` papkasiga saqlash"""
    faces_dir = "faces"
    os.makedirs(faces_dir, exist_ok=True)

    # `users` bucket-dan fayllar ro'yxatini olish
    files = supabase.storage.from_("users").list()

    if not files:
        print("❌ Bucket bo'sh yoki mavjud emas.")
        return

    for file in files:
        file_name = file['name']
        local_path = os.path.join(faces_dir, file_name)

        # Agar fayl allaqachon yuklangan bo'lsa, o'tkazib yuboramiz
        if os.path.exists(local_path):
            print(f"🔹 {file_name} allaqachon mavjud.")
            continue

        # Faylni yuklab olish
        try:
            res = supabase.storage.from_("users").download(file_name)
            with open(local_path, 'wb') as f:
                f.write(res)
            print(f"✅ {file_name} yuklandi.")
        except Exception as e:
            print(f"❌ {file_name} yuklanmadi: {e}")

    print("📂 Barcha rasmlar yuklandi.")


# ✅ Rasmlarni yuklab olish
download_known_faces()
