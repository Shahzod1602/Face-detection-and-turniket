import cv2
from deepface import DeepFace
import os
import numpy as np
from datetime import datetime
from supabase import create_client, Client

# ✅ 1. Supabase bilan bog‘lanish
SUPABASE_URL = "https://rdqutzknswfuondczfrt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkcXV0emtuc3dmdW9uZGN6ZnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5NDIxNDAsImV4cCI6MjA1NjUxODE0MH0.Cf1RggQ4e8L34Ged3RKvrNdkYtMUU0u9NSEeVbCa3qg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 2. Webcam ochish
cap = cv2.VideoCapture(0)

# ✅ 3. Rasmlar katalogi
faces_dir = "faces"
if not os.path.exists(faces_dir):
    print("❌ 'faces' papkasi topilmadi!")
    exit()

# ✅ 4. Kechikkanlarni yozish uchun video katalog
video_dir = "late_arrivals"
if not os.path.exists(video_dir):
    os.makedirs(video_dir)

# ✅ 5. Ma'lumotlarni saqlash
detected_persons = {}
work_status = {}
video_writers = {}

# ✅ 6. Kechikish vaqtlari
late_threshold_time = datetime.strptime("09:30:00", "%H:%M:%S").time()
record_threshold_time = datetime.strptime("11:00:00", "%H:%M:%S").time()

# ✅ 7. Video sozlamalari
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 20.0

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    try:
        temp_image_path = "temp_frame.jpg"
        cv2.imwrite(temp_image_path, frame)

        result = DeepFace.find(
            img_path=temp_image_path,
            db_path=faces_dir,
            enforce_detection=False
        )

        if len(result[0]) > 0:
            best_match = result[0].iloc[0]
            name = best_match['identity'].split('/')[-1].split('.')[0]
            confidence = 1 - best_match['distance']

            if confidence > 0.6:
                if name not in detected_persons:
                    detected_persons[name] = {'count': 0, 'start_time': None}
                    work_status[name] = False

                detected_persons[name]['count'] += 1

                if detected_persons[name]['count'] == 1:
                    work_status[name] = True
                    detected_persons[name]['start_time'] = datetime.now()

                    current_time = datetime.now().time()
                    if current_time > late_threshold_time:
                        cv2.putText(frame, "Kechikdi", (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                        if current_time > record_threshold_time:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            video_filename = os.path.join(video_dir, f"{name}_{timestamp}.avi")
                            video_writers[name] = cv2.VideoWriter(video_filename, fourcc, fps, (frame.shape[1], frame.shape[0]))

                            print(f"📹 {name} uchun kechikkan video yozilmoqda: {video_filename}")

                    else:
                        cv2.putText(frame, "Ishga keldi", (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    print(f"✅ {name} - Ishga keldi")

                    # 📌 **Supabase-ga yozish**
                    supabase.table("attendance").insert({
                        "name": name,
                        "arrival_time": str(datetime.now()),
                        "status": "Keldi" if current_time <= late_threshold_time else "Kechikdi"
                    }).execute()

                    cv2.imshow("Test", frame)
                    cv2.waitKey(10000)
                    continue

                elif detected_persons[name]['count'] == 2:
                    work_status[name] = False
                    end_time = datetime.now()
                    work_duration = end_time - detected_persons[name]['start_time']
                    hours, remainder = divmod(work_duration.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    print(f"⏳ {name} - Ishdan ketdi")
                    print(f"🕒 Ish vaqti: {hours:02d}:{minutes:02d}:{seconds:02d}")

                    cv2.putText(frame, "Ishdan ketdi", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, f"Vaqt: {hours:02d}:{minutes:02d}:{seconds:02d}",
                                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # 📌 **Supabase-ga chiqish vaqtini yozish**
                    supabase.table("attendance").update({
                        "departure_time": str(datetime.now()),
                        "work_duration": f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    }).eq("name", name).execute()

                    if name in video_writers:
                        video_writers[name].release()
                        del video_writers[name]
                        print(f"🛑 {name} uchun video yozish to‘xtatildi")

                    cv2.imshow("Test", frame)
                    cv2.waitKey(5000)
                    detected_persons[name]['count'] = 0
                    continue

                if work_status[name]:
                    current_duration = datetime.now() - detected_persons[name]['start_time']
                    hours, remainder = divmod(current_duration.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    status_text = f"{name} | Ish vaqti: {hours:02d}:{minutes:02d}:{seconds:02d}"
                    cv2.putText(frame, status_text, (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            cv2.putText(frame, "Noma'lum", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for name, writer in video_writers.items():
            writer.write(frame)

    except Exception as e:
        print(f"⚠️ Xatolik yuz berdi: {e}")

    cv2.imshow("Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
for writer in video_writers.values():
    writer.release()
cv2.destroyAllWindows()
