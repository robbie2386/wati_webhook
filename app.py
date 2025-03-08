import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# API Keys dari Environment Variables
WATI_API_KEY = os.getenv("WATI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fungsi untuk analisis gambar dengan GPT-4 Vision
def analyze_image(image_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {"role": "system", "content": "Analyze the image and describe it."},
            {"role": "user", "content": [
                {"type": "text", "text": "What do you see in this image?"},
                {"type": "image_url", "image_url": image_url}
            ]}
        ],
        "max_tokens": 500
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=data,
        headers=headers
    )

    if response.status_code != 200:
        print("Error:", response.json())
        return "Error processing image"

    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

# Fungsi untuk mengirim pesan ke WhatsApp melalui Wati.io
def send_message(phone_number, message_text):
    url = "https://live-mt-server.wati.io/411177/api/v1/sendSessionMessage"  # Ganti dengan endpoint WATI kamu
    headers = {
        "Authorization": f"Bearer {WATI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "chatId": f"{phone_number}@c.us",
        "message": message_text
    }

    print(f"🚀 Mengirim pesan ke: {phone_number}")
    print(f"📩 Isi pesan: {message_text}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("✅ Respons dari WATI:", response.text)  # Debugging untuk melihat hasil API call

        if response.status_code != 200:
            print("❌ ERROR: Gagal mengirim pesan. Response:", response.text)
        else:
            try:
                response_json = response.json()
                print("✅ Pesan berhasil dikirim:", response_json)
            except ValueError:
                print("⚠️ ERROR: API WATI mengembalikan response kosong atau tidak valid")

    except requests.exceptions.RequestException as e:
        print("⚠️ ERROR: Koneksi ke API WATI gagal:", str(e))

# Webhook WhatsApp untuk menerima pesan dari Wati.io
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return jsonify({"message": "Webhook is active"}), 200

    data = request.json
    print("Pesan diterima:", data)

    # Validasi apakah data memiliki "waId" dan "text"
    if data and "waId" in data and "text" in data:
        phone_number = data["waId"]
        message_text = data["text"]

        # Kirim balasan ke pengirim
        send_message(phone_number, f"Halo! Kamu berkata: {message_text}")
    
    # Jika pesan berisi gambar
    if data and "message" in data and "image" in data["message"]:
        image_url = data["message"]["image"]["url"]
        phone_number = data["message"]["from"]  # Nomor pengirim
        result = analyze_image(image_url)
        send_message(phone_number, result)

    return jsonify({"status": "Processed"}), 200

# Webhook untuk pengecekan manual
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Webhook is active"}), 200

# Route utama untuk memastikan server berjalan
@app.route('/')
def home():
    return "Server is running!"

# Jalankan server di Railway
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
