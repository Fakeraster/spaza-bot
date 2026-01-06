from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Your credentials
VERIFY_TOKEN = "SpazaToken123"
WHATSAPP_TOKEN = "EAATr7dGXzn0BQWq54D1920cSiyUze4Aa1zLVrFZCcEHawfQKJF7wHC2PMOs6dPZCdVdNfZAXkUVbBShELZBZCdDeLDwBpFY0j9NV2NU2XvTfBprZBixZC2d9WXhaIUvPKplhqZB0bSV4GXuK7rKbihIZC9OpZCFaaZBkPZAlaUxcNsrBPtPXxSMKMNRFaMveYAYMfpxJpvUoW8bg3LoxKulMxACySp9mL2wftIubissH5Rl5"
PHONE_NUMBER_ID = "940433765813183"

# Webhook verification
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return challenge, 200
    return 'Forbidden', 403

# Handle incoming messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📨 Received:", data)
    
    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' in value:
            message = value['messages'][0]
            sender = message['from']
            
            if message['type'] == 'text':
                text = message['text']['body'].lower().strip()
                print(f"📱 Message from {sender}: {text}")
                
                # Send reply
                send_message(sender, f"👋 Hello! You said: {text}\n\nWelcome to Spaza II Spaza!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return 'OK', 200

# Send message function
def send_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Message sent: {response.status_code} - {response.text}")
    return response

# Home page
@app.route('/')
def home():
    return '🏪 Spaza II Spaza Bot is Running!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
