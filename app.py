import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# API Keys dari Environment Variables
WATI_API_KEY = os.getenv("WATI_API_KEY")  # Pastikan API Key benar
WATI_ENDPOINT = "https://live-mt-server.wati.io/411177"  # Endpoint WATI yang benar

# Fungsi untuk mengirim pesan ke WhatsApp melalui WATI
def send_message(phone_number, message_text):
    url = f"{WATI_ENDPOINT}/api/v1/sendSessionMessage"
    headers = {
        "Authorization": f"Bearer {WATI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "chatId": f"{phone_number}@c.us",
        "message": message_text
    }

    print("📤 Mengirim pesan ke:", phone_number)
    print("📨 Isi pesan:", message_text)

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ Pesan berhasil dikirim:", response.json())
    else:
        print("❌ ERROR saat mengirim pesan:", response.status_code, response.text)

# Webhook WhatsApp untuk menerima pesan dari Wati.io
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📥 Pesan diterima dari WATI:", data)

    if "waId" in data and "text" in data:
        phone_number = data["waId"]
        message_text = data["text"]

        # Kirim balasan ke pengirim
        send_message(phone_number, f"Bot WATI: Kamu berkata '{message_text}'")

    return jsonify({"status": "Processed"}), 200

# Webhook untuk pengecekan manual di browser
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Webhook is active"}), 200

# Route utama untuk memastikan server berjalan
@app.route('/')
def home():
    return "✅ Server WATI Bot Berjalan!"

# Jalankan server di Railway
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
