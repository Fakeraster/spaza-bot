from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your credentials (we'll update these later)
VERIFY_TOKEN = "SpazaToken123"
WHATSAPP_TOKEN = "YOUR_WHATSAPP_TOKEN"
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"

# Product catalog
PRODUCTS = {
    "bread": {"name": "🍞 Bread", "price": 25},
    "milk": {"name": "🥛 Milk", "price": 30},
    "sugar": {"name": "🍬 Sugar", "price": 40},
    "rice": {"name": "🍚 Rice", "price": 45},
    "eggs": {"name": "🥚 Eggs", "price": 28},
    "maize": {"name": "🌽 Maize Meal", "price": 55},
    "oil": {"name": "🛢️ Cooking Oil", "price": 35}
}

# Store orders (simple in-memory storage)
orders = {}

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
                handle_message(sender, text)
            
            elif message['type'] == 'interactive':
                handle_interactive(sender, message['interactive'])
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return 'OK', 200

# Handle text messages
def handle_message(sender, text):
    if text in ['hi', 'hello', 'menu', 'order']:
        send_menu(sender)
    elif text == 'help':
        send_help(sender)
    elif text == 'status':
        send_status(sender)
    else:
        send_welcome(sender)

# Send welcome message
def send_welcome(sender):
    message = """👋 Welcome to *Spaza II Spaza*!

🛒 Your neighborhood shop on WhatsApp!

Type *menu* to see our products
Type *help* for assistance"""
    
    send_message(sender, message)

# Send help
def send_help(sender):
    message = """🆘 *Spaza II Spaza Help*

Commands:
• *menu* - View products
• *order* - Start ordering
• *status* - Check order status
• *help* - Show this message

Need help? Just reply!"""
    
    send_message(sender, message)

# Send product menu with buttons
def send_menu(sender):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Build product list
    product_text = "🛒 *Spaza II Spaza Menu*\n\n"
    for key, item in PRODUCTS.items():
        product_text += f"{item['name']} - R{item['price']}\n"
    product_text += "\n👇 Select a product below:"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": sender,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🏪 Spaza II Spaza"
            },
            "body": {
                "text": product_text
            },
            "footer": {
                "text": "Free delivery over R100!"
            },
            "action": {
                "button": "View Products",
                "sections": [
                    {
                        "title": "Products",
                        "rows": [
                            {"id": "bread", "title": "🍞 Bread", "description": "R25"},
                            {"id": "milk", "title": "🥛 Milk", "description": "R30"},
                            {"id": "sugar", "title": "🍬 Sugar", "description": "R40"},
                            {"id": "rice", "title": "🍚 Rice", "description": "R45"},
                            {"id": "eggs", "title": "🥚 Eggs", "description": "R28"},
                            {"id": "maize", "title": "🌽 Maize Meal", "description": "R55"},
                            {"id": "oil", "title": "🛢️ Cooking Oil", "description": "R35"}
                        ]
                    }
                ]
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Menu sent: {response.status_code}")

# Handle button/list selections
def handle_interactive(sender, interactive):
    if interactive['type'] == 'list_reply':
        selected = interactive['list_reply']['id']
        product = PRODUCTS.get(selected)
        
        if product:
            send_quantity_options(sender, selected, product)

# Ask for quantity
def send_quantity_options(sender, product_id, product):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": sender,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"You selected: {product['name']}\nPrice: R{product['price']} each\n\nHow many do you want?"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"{product_id}_1", "title": "1"}},
                    {"type": "reply", "reply": {"id": f"{product_id}_2", "title": "2"}},
                    {"type": "reply", "reply": {"id": f"{product_id}_3", "title": "3"}}
                ]
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Quantity options sent: {response.status_code}")

# Send order status
def send_status(sender):
    if sender in orders:
        order = orders[sender]
        message = f"""📦 *Your Order Status*

🧾 Order ID: {order['id']}
📊 Status: {order['status']}
💰 Total: R{order['total']}"""
    else:
        message = "❌ No orders found.\n\nType *menu* to place an order!"
    
    send_message(sender, message)

# Send simple text message
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
    print(f"📤 Message sent: {response.status_code}")

# Home page
@app.route('/')
def home():
    return '🏪 Spaza II Spaza Bot is Running!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)