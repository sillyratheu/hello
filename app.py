from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Mock Database: { "my-site.hello": { "ip": "192.168.1.10", "cname": "@", "txt": "hello-verify=123", "status": "Active" } }
domains_db = {}

def generate_random_ip():
    return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

@app.route('/')
def index():
    return render_template('index.html', domains=domains_db)

@app.route('/create-domain', methods=['POST'])
def create_domain():
    subdomain = request.form.get('subdomain').strip().lower()
    extension = request.form.get('extension', '.hello')
    target_ip = request.form.get('target_ip').strip() or generate_random_ip()
    
    if not subdomain:
        return redirect(url_for('index'))
        
    full_domain = f"{subdomain}{extension}"
    
    # Save to database with default DNS records
    domains_db[full_domain] = {
        'ip': target_ip,
        'cname': 'main.hello.corp',
        'txt': 'ver=hello-corp-secure-99',
        'status': 'Active (Global)'
    }
    
    # Domain create hoar por sora-sori tar DNS management panel e niye jabe
    return redirect(url_for('dns_settings', domain_name=full_domain))

@app.route('/dns/<domain_name>', methods=['GET', 'POST'])
def dns_settings(domain_name):
    domain_info = domains_db.get(domain_name)
    if not domain_info:
        return "Domain not found!", 404
        
    if request.method == 'POST':
        # Update DNS records
        domain_info['ip'] = request.form.get('ip', domain_info['ip'])
        domain_info['cname'] = request.form.get('cname', domain_info['cname'])
        domain_info['txt'] = request.form.get('txt', domain_info['txt'])
        return redirect(url_for('dns_settings', domain_name=domain_name))
        
    return render_template('dns.html', domain=domain_name, info=domain_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
