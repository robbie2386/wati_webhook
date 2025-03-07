import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# API Keys (Ganti dengan API Key milikmu)
WATI_API_KEY = "YOUR_WATI_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Fungsi untuk menganalisis gambar dengan GPT-4 Vision
def analyze_image(image_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {"role": "system", "content": "Analyze the image and describe it."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

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

    requests.post("https://api.wati.io/v1/messages", json=payload, headers=headers)

# Webhook untuk menerima pesan dari Wati.io
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    phone_number = data['waId']

    # Jika pesan berisi gambar
    if "message" in data and "image" in data["message"]:
        image_url = data["message"]["image"]["url"]
        result = analyze_image(image_url)
        send_message(phone_number, result)

    return jsonify({"status": "Processed"}), 200

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)




