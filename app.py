from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Mock Database for domains
domains_db = {}

def generate_random_ip():
    return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

# Landing Page Route (Website-e prothom dhuklei eta ashbe)
@app.route('/')
def landing():
    return render_template('landing.html')

# Dashboard & Domain Creator Route
@app.route('/dashboard')
def dashboard():
    return render_template('index.html', domains=domains_db)

@app.route('/create-domain', methods=['POST'])
def create_domain():
    subdomain = request.form.get('subdomain').strip().lower()
    extension = request.form.get('extension', '.hello')
    target_ip = request.form.get('target_ip').strip() or generate_random_ip()
    
    if not subdomain:
        return redirect(url_for('dashboard'))
        
    full_domain = f"{subdomain}{extension}"
    
    domains_db[full_domain] = {
        'ip': target_ip,
        'cname': 'main.hello.corp',
        'txt': 'ver=hello-corp-secure-99',
        'status': 'Active (Global)'
    }
    
    return redirect(url_for('dns_settings', domain_name=full_domain))

@app.route('/dns/<domain_name>', methods=['GET', 'POST'])
def dns_settings(domain_name):
    domain_info = domains_db.get(domain_name)
    if not domain_info:
        return "Domain not found!", 404
        
    if request.method == 'POST':
        domain_info['ip'] = request.form.get('ip', domain_info['ip'])
        domain_info['cname'] = request.form.get('cname', domain_info['cname'])
        domain_info['txt'] = request.form.get('txt', domain_info['txt'])
        return redirect(url_for('dns_settings', domain_name=domain_name))
        
    return render_template('dns.html', domain=domain_name, info=domain_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)