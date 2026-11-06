import asyncio
import os
import threading
import datetime
from flask import Flask, jsonify
from pybedrock_net import BedrockClient

app = Flask(__name__)

# আপনার Aternos সার্ভার তথ্য
SERVER_HOST = "Killanimal.aternos.me"
SERVER_PORT = 19132
BOT_USERNAME = "AFK_Bot"

# বটের লগ সেভ করার জন্য একটি লিস্ট (সর্বশেষ ৫০টি লগ রাখবে)
bot_logs = []

def add_log(message):
    # টার্মিনালে প্রিন্ট করবে
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)
    
    # ওয়েবসাইটে দেখানোর জন্য লিস্টে সেভ করবে
    bot_logs.append(log_msg)
    if len(bot_logs) > 50:
        bot_logs.pop(0)

# বট সংযোগ ফাংশন
async def run_bot():
    add_log("বট কানেক্ট করার চেষ্টা করছে...")
    bot = BedrockClient(
        host=SERVER_HOST,
        port=SERVER_PORT,
        username=BOT_USERNAME,
        anti_afk=True 
    )

    @bot.on("spawn")
    async def on_spawn(data):
        add_log(f"✅ সফলভাবে সার্ভারে ঢুকেছে! বটের পজিশন: {data.position}")

    @bot.on("error")
    async def on_error(err):
        add_log(f"❌ বট এরর: {err}")

    @bot.on("end")
    async def on_end(reason):
        add_log(f"⚠️ সার্ভার থেকে কানেকশন কেটে গেছে। কারণ: {reason}")
        add_log("৫ সেকেন্ড পর আবার চেষ্টা করবে...")
        await asyncio.sleep(5)
        asyncio.create_task(run_bot())

    try:
        await bot.connect()
    except Exception as e:
        add_log(f"🚫 কানেক্ট করতে সমস্যা হচ্ছে: {e}")
        add_log("সার্ভার কি Aternos-এ অনলাইন আছে? ১০ সেকেন্ড পর আবার চেষ্টা করবে...")
        await asyncio.sleep(10)
        asyncio.create_task(run_bot())

# Flask রুট
@app.route('/')
def home():
    html = "<h2>🤖 Minecraft Bot Status</h2>"
    html += "<h3>Recent Logs (সর্বশেষ লগ):</h3>"
    html += "<div style='background:#f4f4f4; padding:10px; border-radius:5px; font-family:monospace; max-height:400px; overflow-y:scroll;'>"
    if not bot_logs:
        html += "এখনো কোনো লগ নেই।"
    else:
        for log in reversed(bot_logs): # নতুন লগ আগে দেখাবে
            html += f"{log}<br>"
    html += "</div>"
    return html

# বটকে আলাদা থ্রেডে চালান
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == '__main__':
    # ব্যাকগ্রাউন্ড বট থ্রেড চালু করুন
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)