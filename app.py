import asyncio
import os
import threading
from flask import Flask
from pybedrock_net import BedrockClient

app = Flask(__name__)

# আপনার Aternos সার্ভার তথ্য
SERVER_HOST = "Killanimal.aternos.me"
SERVER_PORT = 19132
BOT_USERNAME = "AFK_Bot"

# বট সংযোগ ফাংশন
async def run_bot():
    bot = BedrockClient(
        host=SERVER_HOST,
        port=SERVER_PORT,
        username=BOT_USERNAME,
        anti_afk=True  # স্বয়ংক্রিয়ভাবে নড়াচড়া করে, idle kick প্রতিরোধ করে
    )

    @bot.on("spawn")
    async def on_spawn(data):
        print(f"বট সফলভাবে প্রবেশ করেছে, অবস্থান: {data.position}")

    @bot.on("error")
    async def on_error(err):
        print(f"বট ত্রুটি: {err}")

    await bot.connect()

# Flask রুট, UptimeRobot এখানে ping করে Render-কে জাগিয়ে রাখবে
@app.route('/')
def health():
    return "Bot is running", 200

# বটকে আলাদা থ্রেডে চালান (Flask ব্লক এড়াতে)
def start_bot():
    asyncio.run(run_bot())

if __name__ == '__main__':
    # ব্যাকগ্রাউন্ড বট থ্রেড চালু করুন
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Render স্বয়ংক্রিয়ভাবে PORT এনভায়রনমেন্ট ভেরিয়েবল প্রদান করে
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)