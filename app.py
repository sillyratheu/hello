from flask import Flask, request, Response, render_template_string, redirect, url_for
import sqlite3
import os
import requests

app = Flask(__name__)
DB_PATH = 'hellocorp.db'

def init_db():
    """ডাটাবেস টেবিল ইনিশিয়ালাইজ করে"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dns_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT UNIQUE,
            target_host TEXT
        )
    ''')
    # ডিফল্ট একটি টেস্ট এন্ট্রি
    cursor.execute("INSERT OR IGNORE INTO dns_records (domain_name, target_host) VALUES (?, ?)", 
                   ("corporation.hello", "example.com"))
    conn.commit()
    conn.close()

@app.before_request
def reverse_proxy_middleware():
    """কাস্টম ডোমেইন রিকোয়েস্ট ধরে প্রক্সি করবে"""
    host = request.host.split(':')[0]
    
    # রেন্ডার নিজস্ব ইউআরএল বা লোকালহোস্ট হলে অ্যাডমিন বা হোমপেজ দেখাবে, প্রক্সি করবে না
    if "onrender.com" in host or "localhost" in host or "127.0.0.1" in host:
        return None
        
    # ডাটাবেس থেকে টার্গেট হোস্টিং খোঁজা
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT target_host FROM dns_records WHERE domain_name = ?", (host,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            target_backend = row[0]
            target_url = f"https://{target_backend}{request.path}"
            if request.query_string:
                target_url += f"?{request.query_string.decode('utf-8')}"
                
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers={key: value for (key, value) in request.headers if key != 'Host'},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=10
            )
            
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
            
            return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Hello Corporation Gateway Error: {str(e)}", 502

@app.route('/')
def home():
    """মেইন ড্যাশবোর্ড যেখান থেকে ডোমেইন ম্যানেজ করা যাবে"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, domain_name, target_host FROM dns_records")
    records = cursor.fetchall()
    conn.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hello Corporation - Autonomous Gateway</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
            .container { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
            h1 { color: #38bdf8; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: left; }
            th { background: #0f172a; color: #38bdf8; }
            input, button { padding: 10px; margin: 5px 0; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; width: calc(100% - 22px); }
            button { background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; border: none; }
            button:hover { background: #7dd3fc; }
            .form-box { margin-top: 30px; background: #0f172a; padding: 20px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello Corporation Gateway</h1>
            <p style="text-align: center; color: #94a3b8;">Decentralized Autonomous TLD & Proxy Management</p>
            
            <table>
                <tr>
                    <th>ID</th>
                    <th>Custom Domain (.hello / .shahajjo)</th>
                    <th>Target Host / Backend</th>
                </tr>
                {% for row in records %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td><b>{{ row[1] }}</b></td>
                    <td>{{ row[2] }}</td>
                </tr>
                {% endfor %}
            </table>

            <div class="form-box">
                <h3>Add New Custom Domain Mapping</h3>
                <form method="POST" action="/add">
                    <label>Domain Name (e.g. mysite.hello):</label>
                    <input type="text" name="domain" required placeholder="mysite.hello">
                    <label>Target Host (e.g. myproject.onrender.com or example.com):</label>
                    <input type="text" name="target" required placeholder="target-site.com">
                    <button type="submit">Save & Register Domain</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, records=records)

@app.route('/add', methods=['POST'])
def add_domain():
    """নতুন ডোমেইন ডাটাবেসে সেভ করার রুট"""
    domain = request.form.get('domain').strip()
    target = request.form.get('target').strip()
    
    if domain and target:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO dns_records (domain_name, target_host) VALUES (?, ?)", (domain, target))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error:", e)
            
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
