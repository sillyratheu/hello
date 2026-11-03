import socket
import sqlite3

# Hello Corporation Custom DNS Root Server
DNS_PORT = 5353  # Standard DNS uses 53 (requires root/sudo), using 5353 for local/custom testing
DB_PATH = 'hellocorp.db'

def get_dns_record_from_db(domain_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Query A record or CNAME target from database
    cursor.execute("SELECT value FROM dns_records WHERE domain_name = ? AND record_type IN ('A', 'CNAME')", (domain_name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0] # Returns IP or Target Host
    return None

def start_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', DNS_PORT))
    print(f"[*] Hello Corporation Global Root DNS Server running on port {DNS_PORT}...")

    while True:
        data, addr = sock.recvfrom(512) # DNS packets are typically under 512 bytes
        try:
            # Simple query extraction (Looking for domain name in query packet)
            # In a full production DNS server, we parse the DNS header and question section.
            # Here we match incoming requests against our database domains.
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT domain_name FROM domains")
            registered_domains = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Check which domain is being queried in the raw packet bytes
            matched_domain = None
            for dom in registered_domains:
                if dom.encode() in data:
                    matched_domain = dom
                    break
            
            if matched_domain:
                target_value = get_dns_record_from_db(matched_domain)
                print(f"[DNS QUERY] Resolved '{matched_domain}' -> Target: {target_value}")
                
                # Construct a basic dummy DNS response packet pointing to our proxy/IP
                # (For full implementation, standard DNS response structures are packed here)
                response = data[:2] + b'\x81\x80' + data[4:6] + data[4:6] + b'\x00\x00\x00\x00' + data[12:]
                sock.sendto(response, addr)
            else:
                # Domain not found in Hello Corp Root
                pass
        except Exception as e:
            print(f"[DNS Error] {e}")

if __name__ == '__main__':
    start_dns_server()
