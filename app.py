from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect('hellocorp.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT UNIQUE,
            mail_zone TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dns_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT,
            record_type TEXT,
            host TEXT,
            value TEXT,
            priority TEXT,
            ttl TEXT,
            FOREIGN KEY (domain_name) REFERENCES domains (domain_name)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Smart Domain Interceptor (Proxy/Routing Middleware)
@app.before_request
def proxy_handler():
    host = request.host.split(':')[0].lower() # Get domain name without port
    
    # If request is coming for a registered custom .hello or .shahajjo domain (and not main platform)
    if (host.endswith('.hello') or host.endswith('.shahajjo')) and host != 'hellocorp.local':
        conn = sqlite3.connect('hellocorp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT domain_name FROM domains WHERE domain_name = ?", (host,))
        domain_row = cursor.fetchone()
        conn.close()
        
        if domain_row:
            # Real custom domain hit! Serve custom response or target site contents
            return render_template('site_live.html', domain=host)
        else:
            return f"Error: The custom domain '{host}' is not registered with Hello Corporation.", 404

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('hellocorp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT domain_name FROM domains")
    domains = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', domains=domains)

@app.route('/create-domain', methods=['POST'])
def create_domain():
    subdomain = request.form.get('subdomain').strip().lower()
    extension = request.form.get('extension', '.hello')
    
    if not subdomain:
        return redirect(url_for('dashboard'))
        
    full_domain = f"{subdomain}{extension}"
    
    conn = sqlite3.connect('hellocorp.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO domains (domain_name, mail_zone) VALUES (?, ?)", (full_domain, full_domain))
        
        default_records = [
            ('A', '@', '192.168.1.10', '', '30 min'),
            ('CNAME', 'www', 'main.hello.corp', '', '30 min'),
            ('TXT', 'ver', 'hello-corp-secure-99', '', '60 min'),
            ('MX', 'mail', 'mail.' + full_domain, '10', '30 min')
        ]
        
        for r_type, host, val, prio, ttl in default_records:
            cursor.execute("""
                INSERT INTO dns_records (domain_name, record_type, host, value, priority, ttl)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_domain, r_type, host, val, prio, ttl))
            
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    
    return redirect(url_for('dns_settings', domain_name=full_domain))

@app.route('/dns/<domain_name>')
def dns_settings(domain_name):
    conn = sqlite3.connect('hellocorp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dns_records WHERE domain_name = ?", (domain_name,))
    records = cursor.fetchall()
    conn.close()
    
    info = {
        'mail_zone': domain_name,
        'a_records': [],
        'cname_records': [],
        'txt_records': [],
        'mx_records': []
    }
    
    for r in records:
        rec_id, _, r_type, host, val, prio, ttl = r
        if r_type == 'A':
            info['a_records'].append({'id': rec_id, 'host': host, 'ip': val, 'ttl': ttl})
        elif r_type == 'CNAME':
            info['cname_records'].append({'id': rec_id, 'alias': host, 'target': val, 'ttl': ttl})
        elif r_type == 'TXT':
            info['txt_records'].append({'id': rec_id, 'name': host, 'value': val, 'ttl': ttl})
        elif r_type == 'MX':
            info['mx_records'].append({'id': rec_id, 'mail_server': val, 'priority': prio, 'ttl': ttl})
            
    return render_template('dns.html', domain=domain_name, info=info)

# Add Record Route
@app.route('/dns/<domain_name>/add-record', methods=['POST'])
def add_record(domain_name):
    r_type = request.form.get('record_type')
    host = request.form.get('host', '').strip()
    value = request.form.get('value', '').strip()
    priority = request.form.get('priority', '10').strip()
    ttl = request.form.get('ttl', '30 min')
    
    if host and value:
        conn = sqlite3.connect('hellocorp.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dns_records (domain_name, record_type, host, value, priority, ttl)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (domain_name, r_type, host, value, priority, ttl))
        conn.commit()
        conn.close()
        
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Delete Record Route
@app.route('/dns/<domain_name>/delete/<int:rec_id>', methods=['POST'])
def delete_record(domain_name, rec_id):
    conn = sqlite3.connect('hellocorp.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dns_records WHERE id = ? AND domain_name = ?", (rec_id, domain_name))
    conn.commit()
    conn.close()
    return redirect(url_for('dns_settings', domain_name=domain_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
