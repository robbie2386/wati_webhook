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
    headers = {
        "Authorization": f"Bearer {WATI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": phone_number,
        "type": "text",
        "text": {"body": message_text}
    }

    response = requests.post(
        "https://api.wati.io/v1/messages",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        print("Error sending message:", response.json())

# Webhook WhatsApp untuk menerima pesan dari Wati.io
@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    phone_number = data.get("waId", "")

    # Logging untuk debug
    print("Received WhatsApp Data:", data)

    # Jika pesan berisi gambar
    if "message" in data and "image" in data["message"]:
        image_url = data["message"]["image"]["url"]
        result = analyze_image(image_url)
        send_message(phone_number, result)

    return jsonify({"status": "Processed"}), 200

# Webhook untuk pengujian manual
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return jsonify({"message": "Webhook is active"}), 200  # Debugging response
        
    data = request.json
    print("Received data from API Test:", data)
    return jsonify({"message": "Webhook received"}), 200

# Route utama untuk memastikan server berjalan
@app.route('/')
def home():
    return "Server is running!"

# Jalankan server di Railway
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
