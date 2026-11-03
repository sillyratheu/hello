from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

domains_db = {}

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html', domains=domains_db)

@app.route('/create-domain', methods=['POST'])
def create_domain():
    subdomain = request.form.get('subdomain').strip().lower()
    extension = request.form.get('extension', '.hello')
    
    if not subdomain:
        return redirect(url_for('dashboard'))
        
    full_domain = f"{subdomain}{extension}"
    
    if full_domain not in domains_db:
        domains_db[full_domain] = {
            'a_records': [{'host': '@', 'ip': '192.168.1.10', 'ttl': '00:02'}],
            'cname_records': [{'alias': 'www', 'target': 'main.hello.corp', 'ttl': '00:02'}],
            'txt_records': [{'name': 'ver', 'value': 'hello-corp-secure-99', 'ttl': '00:02'}]
        }
    
    return redirect(url_for('dns_settings', domain_name=full_domain))

@app.route('/dns/<domain_name>')
def dns_settings(domain_name):
    domain_info = domains_db.get(domain_name)
    if not domain_info:
        return "Domain not found!", 404
    return render_template('dns.html', domain=domain_name, info=domain_info)

# Add A Record
@app.route('/dns/<domain_name>/add-a', methods=['POST'])
def add_a_record(domain_name):
    domain_info = domains_db.get(domain_name)
    if domain_info:
        host = request.form.get('host', '@').strip()
        ip = request.form.get('ip', '').strip()
        if ip:
            domain_info['a_records'].append({'host': host, 'ip': ip, 'ttl': '00:02'})
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Delete A Record
@app.route('/dns/<domain_name>/delete-a/<int:index>', methods=['POST'])
def delete_a_record(domain_name, index):
    domain_info = domains_db.get(domain_name)
    if domain_info and 0 <= index < len(domain_info['a_records']):
        domain_info['a_records'].pop(index)
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Edit A Record
@app.route('/dns/<domain_name>/edit-a/<int:index>', methods=['POST'])
def edit_a_record(domain_name, index):
    domain_info = domains_db.get(domain_name)
    if domain_info and 0 <= index < len(domain_info['a_records']):
        domain_info['a_records'][index]['host'] = request.form.get('host', '@')
        domain_info['a_records'][index]['ip'] = request.form.get('ip', '')
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Add CNAME Record
@app.route('/dns/<domain_name>/add-cname', methods=['POST'])
def add_cname_record(domain_name):
    domain_info = domains_db.get(domain_name)
    if domain_info:
        alias = request.form.get('alias', '').strip()
        target = request.form.get('target', '').strip()
        if alias and target:
            domain_info['cname_records'].append({'alias': alias, 'target': target, 'ttl': '00:02'})
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Delete CNAME Record
@app.route('/dns/<domain_name>/delete-cname/<int:index>', methods=['POST'])
def delete_cname_record(domain_name, index):
    domain_info = domains_db.get(domain_name)
    if domain_info and 0 <= index < len(domain_info['cname_records']):
        domain_info['cname_records'].pop(index)
    return redirect(url_for('dns_settings', domain_name=domain_name))

# Edit CNAME Record
@app.route('/dns/<domain_name>/edit-cname/<int:index>', methods=['POST'])
def edit_cname_record(domain_name, index):
    domain_info = domains_db.get(domain_name)
    if domain_info and 0 <= index < len(domain_info['cname_records']):
        domain_info['cname_records'][index]['alias'] = request.form.get('alias', '')
        domain_info['cname_records'][index]['target'] = request.form.get('target', '')
    return redirect(url_for('dns_settings', domain_name=domain_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
