import requests
import datetime

# Supabase ma'lumotlari
SUPABASE_URL = "https://rdqutzknswfuondczfrt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkcXV0emtuc3dmdW9uZGN6ZnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5NDIxNDAsImV4cCI6MjA1NjUxODE0MH0.Cf1RggQ4e8L34Ged3RKvrNdkYtMUU0u9NSEeVbCa3qg"
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "apikey": SUPABASE_KEY
}


def send_attendance(id, name, entry_time, exit_time, late):
    """ Ma'lumotlarni attendance jadvaliga yuborish """

    # Hozirgi sanani olish
    today_date = datetime.date.today().isoformat()

    # To'g'ri timestamp formatiga o'tkazish
    entry_timestamp = f"{today_date} {entry_time}"
    exit_timestamp = f"{today_date} {exit_time}"

    data = {
        "id": id,
        "name": name,
        "image_path": "",  # Bo‘sh string qo‘shildi
        "entry_time": entry_timestamp,
        "exit_time": exit_timestamp,
        "date": today_date,
        "late": late
    }

    url = f"{SUPABASE_URL}/rest/v1/attendance"
    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        print("✅ Data successfully sent to the database.")
    else:
        print("❌ Error:", response.text)


# Test ma'lumotlar
send_attendance(
    id=7,
    name="butest",
    entry_time="08:30:00",  # Vaqt endi to'g'ri formatga o'tadi
    exit_time="17:30:00",
    late=False




)



