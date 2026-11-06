import asyncio
import os
import threading
import datetime
from flask import Flask
from pybedrock_net import BedrockClient

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
        # বট ক্লায়েন্ট তৈরি
        bot = BedrockClient(
            host=SERVER_HOST,
            port=SERVER_PORT,
            username=BOT_USERNAME,
            anti_afk=True
        )

        # ইভেন্ট হ্যান্ডলার সেট
        @bot.on("connect")
        async def on_connect():
            add_log("✅ সার্ভারের সাথে সংযোগ স্থাপন হয়েছে!")

        @bot.on("login")
        async def on_login():
            add_log("✅ সফলভাবে সার্ভারে লগইন হয়েছে!")

        @bot.on("error")
        async def on_error(err):
            add_log(f"❌ বট এরর: {err}")

        # কানেক্ট করার সঠিক উপায় (লাইব্রেরি ডকুমেন্টেশন অনুযায়ী)
        # বট শুরু করুন
        if hasattr(bot, 'start'):
            await bot.start()
        else:
            add_log("⚠️ লাইব্রেরিতে start() মেথড নেই, অন্য উপায় চেষ্টা করছি...")
            # ফলব্যাক: connect মেথড থাকলে সেটা কল করুন
            if hasattr(bot, 'connect'):
                await bot.connect()
            else:
                add_log("❌ কোনো উপযুক্ত মেথড পাওয়া যায়নি। লাইব্রেরি আপডেট করুন।")

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