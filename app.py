import asyncio
import os
import threading
import datetime
from flask import Flask
from pybedrock_net.bot import BedrockBot

app = Flask(__name__)

SERVER_HOST = "Killanimal.aternos.me"
SERVER_PORT = 19132
BOT_USERNAME = "AFK_Bot"

bot_logs = []

def add_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)
    bot_logs.append(log_msg)
    if len(bot_logs) > 50:
        bot_logs.pop(0)

async def run_bot():
    add_log("বট কানেক্ট করার চেষ্টা করছে...")
    
    try:
        # সরাসরি BedrockBot ব্যবহার করুন, অফলাইন মোডের জন্য উপযুক্ত
        bot = BedrockBot(SERVER_HOST, SERVER_PORT, BOT_USERNAME)
        
        # অফলাইন মোডে লগইন করুন (প্রোটোকল নম্বর সার্ভার সংস্করণ অনুযায়ী সামঞ্জস্য করুন, 776 প্রায় 1.21.60)
        bot.login(protocol=776)
        
        add_log("✅ সফলভাবে সার্ভারে লগইন হয়েছে!")
        
        # এখানে bot.chat() দিয়ে মেসেজ পাঠাতে পারেন
        # bot.chat("Hello!")
        
        # সংযোগ ধরে রাখুন, মাঝে মাঝে হার্টবিট পাঠান
        while True:
            await asyncio.sleep(30)
            # এখানে bot-এর কিছু মেথড কল করে হার্টবিট পাঠাতে পারেন
            
    except Exception as e:
        add_log(f"🚫 কানেক্ট করতে সমস্যা: {e}")
        add_log("১০ সেকেন্ড পর আবার চেষ্টা করবে...")
        await asyncio.sleep(10)
        asyncio.create_task(run_bot())

@app.route('/')
def home():
    html = "<h2>🤖 Minecraft Bot Status</h2>"
    html += "<h3>Recent Logs:</h3>"
    html += "<div style='background:#f4f4f4; padding:10px; border-radius:5px; font-family:monospace; max-height:400px; overflow-y:scroll;'>"
    if not bot_logs:
        html += "এখনো কোনো লগ নেই।"
    else:
        for log in reversed(bot_logs):
            html += f"{log}<br>"
    html += "</div>"
    return html

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)