# 03. IP, DNS, and HTTP Basics

DNS: the magical service that translates names to IPs… until it doesn’t, and every engineer in the room says, “Yup, definitely DNS.” (It’s always DNS.) 🧙‍♂️🌍

[← Back to Main](../README.md) | [Previous: Client-Server Architecture](02-client-server-architecture.md) | [Next: APIs (REST, GraphQL, gRPC) →](04-apis-rest-graphql-grpc.md)

---

## 🎯 Quick Summary

**IP, DNS, and HTTP** are the fundamental technologies that make the internet work. IP addresses identify computers, DNS translates domain names to addresses, and HTTP is the protocol that lets clients and servers actually communicate. Together, they're the internet's plumbing system.

Think of it as: **IP = Address, DNS = Phone Book, HTTP = Conversation Protocol**

---

## 🌟 Beginner Explanation

### IP Address: Your Internet Home Address

Imagine the postal system:

```
POSTAL SYSTEM ANALOGY

Physical Address:
"123 Main Street, New York, NY 10001"
↓
Person's House (unique identifier)

IP Address:
"192.168.1.100" or "2600:1700::68"
↓
Your Device on Internet (unique identifier)
```

**What is an IP Address?**

An IP address is a unique number that identifies your device on the internet. Just like your home address lets mail carriers deliver letters to you, your IP address lets internet packets reach your computer.

**Types of IP Addresses:**

```
IPv4 (Old, still dominant):
- Format: 192.168.1.1
- Four numbers (octets) from 0-255
- Total: 4.3 billion addresses
- Problem: We're running out! (need IPv6)

IPv6 (New, future):
- Format: 2600:1700::68
- 128-bit address
- Total: 340 trillion trillion trillion addresses
- Problem: Still not widely adopted
```

### DNS: The Internet's Phone Book

Imagine you want to call your friend Alice:

```
WITHOUT PHONE BOOK:
"I want to call Alice... but what's her number?"
❌ You have to remember thousands of phone numbers

WITH PHONE BOOK:
"I want to call Alice"
↓
Look up "Alice" in phone book
↓
Find phone number: 555-1234
↓
Call 555-1234
✅ Problem solved!
```

**DNS works exactly the same way:**

```
WITHOUT DNS (Old internet):
User: "I want to visit google.com"
User must know: "That's 142.250.185.46"
❌ Impossible to remember 1000s of IPs

WITH DNS:
User: "I want to visit google.com"
↓
Query DNS Server: "What IP is google.com?"
↓
DNS replies: "142.250.185.46"
↓
Browser connects to 142.250.185.46
✅ Much easier!
```

**How DNS Resolution Works:**

```
1. YOU: "What's the IP for google.com?"
   ↓
2. RECURSIVE RESOLVER (your ISP's DNS):
   "I don't know, let me ask Root Nameserver"
   ↓
3. ROOT NAMESERVER: 
   "I don't know google.com, but try Top-Level Domain server for .com"
   ↓
4. TLD SERVER (.com authority):
   "I don't know google.com specifically, but try google.com's nameserver"
   ↓
5. AUTHORITATIVE NAMESERVER (google.com's own server):
   "google.com is 142.250.185.46"
   ↓
6. RESPONSE CHAIN (reverse):
   ← TLD ← Root ← Resolver ← YOU
   ↓
7. YOU GET: "142.250.185.46" ✅
   (and your computer caches it for next time)

TOTAL TIME: Usually < 100ms ⚡
```

### HTTP: The Conversation Protocol

Imagine you're at a restaurant:

```
RESTAURANT CONVERSATION

You (Client): "I'd like to order a pizza"
Waiter (Server): "Sure! What kind?"
You: "Pepperoni"
Waiter: "Coming right up!"
[Waiter goes to kitchen]
Waiter: "Here's your pizza"
You: "Thank you!"
[Conversation ends]

HTTP WORKS THE SAME WAY

You (Browser): "GET /index.html"
Server: "I found it! Here's the HTML"
You: "Now give me style.css"
Server: "Here it is"
You: "Now give me script.js"
Server: "Here it is"
[Page loads completely]
```

**The Key Insight:** HTTP is **stateless and request-response**

- You send request → Server responds → Connection closes
- Next request: Server doesn't remember previous ones
- Each request is completely independent

---

## 🔬 Advanced Explanation

### IP Addressing Deep Dive

**How IP Routing Actually Works:**

```
YOUR COMPUTER:
IP: 192.168.1.100
Wants to send packet to: 8.8.8.8 (Google DNS)

NETWORK LAYER DECISION:
1. Is 8.8.8.8 on my local network (192.168.1.0)?
   Check: 8.8.8.8 vs 192.168.1.0/24
   Answer: NO ❌

2. Send to default gateway (router): 192.168.1.1

3. ROUTER DECISION:
   Is 8.8.8.8 on my network? NO
   Check routing table...
   Send to ISP gateway

4. ISP DECISION:
   Is 8.8.8.8 on my network? NO
   Check routing table...
   Send to next router closer to destination

5. [Packet hops through many routers]

6. GOOGLE'S NETWORK:
   Is 8.8.8.8 on my network? YES ✅
   Send to server 8.8.8.8

RESULT: Packet arrived at Google!
```

**Subnetting (Breaking Networks Into Pieces):**

```
Network: 192.168.0.0/24 (256 addresses)

Subnet Mask: 255.255.255.0
This means: "First 3 parts are network, last part is host"

Example breakdown:
192.168.0.0   = Network address
192.168.0.1   = Gateway/Router
192.168.0.2   = Host 1
...
192.168.0.254 = Host 253
192.168.0.255 = Broadcast address

/24 means "24 bits for network, 8 bits for hosts"
/25 means "25 bits for network, 7 bits for hosts" (128 addresses)
/30 means "30 bits for network, 2 bits for hosts" (4 addresses)

Bigger number = smaller network = fewer addresses
```

### DNS Deep Dive

**DNS Record Types:**

```
A Record:
Domain → IPv4 Address
google.com → 142.250.185.46

AAAA Record:
Domain → IPv6 Address
google.com → 2607:f8b0:4004:80a::200e

CNAME Record (Alias):
www.google.com → google.com
(CNAME points to another domain)

MX Record (Mail):
gmail.com → mx.google.com
(Route emails here)

TXT Record (Text):
Any text data (often for verification)

NS Record (Nameserver):
Points to the authoritative nameserver

SOA Record (Start of Authority):
Contains zone information
```

**DNS Caching (Why it's so fast):**

```
FIRST TIME:
User → Recursive Resolver → Root → TLD → Authoritative
Response: 8.8.8.8 → Stored in cache with TTL: 3600 seconds
Time: 200ms 🐢

SECOND TIME (within 1 hour):
User → Recursive Resolver (cache hit!)
Response: Returns cached result
Time: 2ms ⚡ (100x faster!)

TTL = Time To Live (how long cache is valid)
- Short TTL (5 min): Updates quickly, but more queries
- Long TTL (24 hours): Fewer queries, but updates slowly
```

**DNS Security Problem: DNS Spoofing**

```
ATTACK SCENARIO:

Hacker intercepts your DNS query:
You: "What's the IP for bank.com?"

Hacker responds before real DNS:
Hacker: "bank.com is 192.168.1.1 (my server)"

Result: You connect to hacker's fake bank website! 💀

SOLUTION: DNSSEC
- Digitally sign DNS responses
- Can verify responses are authentic
- Prevents spoofing
```

### HTTP Protocol Deep Dive

**HTTP Request Structure:**

```
GET /api/users/123 HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0 (Chrome)
Accept: application/json
Authorization: Bearer token123xyz
Content-Length: 0

[Empty body for GET]
```

**HTTP Response Structure:**

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 256
Cache-Control: max-age=3600
Set-Cookie: session=abc123; Path=/

{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com"
}
```

**HTTP Methods (Verbs):**

```
GET:     Retrieve data (safe, idempotent)
POST:    Create new data (not idempotent)
PUT:     Replace entire resource (idempotent)
PATCH:   Partial update (sometimes idempotent)
DELETE:  Remove data (idempotent)
HEAD:    Like GET but no body (check if resource exists)
OPTIONS: Describe communication options

Idempotent = Can call multiple times, same result
GET /users/1     → Always returns same user
GET /users/1     → Always returns same user
POST /users      → Creates new user each time!
```

**HTTP Status Codes:**

```
1xx: Information
100 Continue: "Send request body"
101 Switching Protocols: "Upgrading to WebSocket"

2xx: Success
200 OK: Request successful
201 Created: Resource created
204 No Content: Success but no body
206 Partial Content: Partial download

3xx: Redirection
300 Multiple Choices: Multiple options available
301 Moved Permanently: Use new URL permanently
302 Found: Temporary redirect
304 Not Modified: Use cached version
307 Temporary Redirect: Use this URL temporarily

4xx: Client Error
400 Bad Request: Malformed request
401 Unauthorized: Not authenticated
403 Forbidden: Authenticated but not allowed
404 Not Found: Resource doesn't exist
409 Conflict: Request conflicts with state
429 Too Many Requests: Rate limited

5xx: Server Error
500 Internal Server Error: Generic error
502 Bad Gateway: Upstream server unreachable
503 Service Unavailable: Server overloaded
504 Gateway Timeout: Upstream timed out
```

**HTTP Versions:**

```
HTTP/1.0 (1996):
- Simple but inefficient
- New connection for each request
- No keep-alive

HTTP/1.1 (1997):
- Keep-alive (reuse connections)
- Pipelining (multiple requests at once)
- Still widely used today

HTTP/2 (2015):
- Binary protocol (faster parsing)
- Server push (push resources proactively)
- Multiplexing (multiple streams on one connection)
- 20-30% faster than HTTP/1.1

HTTP/3 (2022):
- Uses QUIC instead of TCP
- Faster connection setup
- Better for mobile/unreliable networks
- Still being adopted

COMPARISON:
HTTP/1.1: Many sequential requests
HTTP/2:   Many parallel requests on same connection
HTTP/3:   Faster connection, better resilience
```

### How They Work Together

**Real-World Request Journey:**

```
1. YOU TYPE IN BROWSER:
   "google.com"

2. BROWSER CHECKS:
   "Do I have google.com cached?"
   "Is it still valid (TTL not expired)?"
   If yes → Skip to step 5
   If no → Continue to step 3

3. DNS RESOLUTION:
   Recursive Resolver → Root → TLD → Authoritative
   Result: 142.250.185.46

4. TCP CONNECTION:
   Your computer → 142.250.185.46:80 (HTTP)
   Three-way handshake (SYN, SYN-ACK, ACK)
   Connection established

5. HTTPS NEGOTIATION (if HTTPS):
   TLS handshake (establish encryption)
   Exchange certificates
   Agreement on encryption method

6. HTTP REQUEST:
   GET / HTTP/1.1
   Host: google.com
   [Other headers]

7. HTTP RESPONSE:
   200 OK
   [HTML content]

8. BROWSER PROCESSING:
   Parse HTML
   Find CSS → New HTTP request → CSS received
   Find JS → New HTTP request → JS received
   Find images → New HTTP requests → Images received
   Render page

9. KEEP-ALIVE:
   Connection stays open for potential requests
   Times out after idle period

10. PAGE DISPLAYS:
    User sees Google homepage
    Total time: ~0.5-2 seconds ⚡
```

---

## 🐍 Python Code Example

### ❌ Simple DNS & HTTP (Manual)

```python
# ===== DNS LOOKUP =====
import socket

def simple_dns_lookup(hostname):
    """Manually resolve hostname to IP"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✓ {hostname} → {ip}")
        return ip
    except socket.gaierror:
        print(f"✗ Could not resolve {hostname}")
        return None

# Usage
ip = simple_dns_lookup("google.com")
# Output: ✓ google.com → 142.250.185.46


# ===== HTTP REQUEST (Manual) =====
import socket

def simple_http_request(hostname, path="/"):
    """Manual HTTP request"""
    # 1. DNS lookup
    ip = socket.gethostbyname(hostname)
    
    # 2. Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 3. Connect to server
    sock.connect((ip, 80))
    
    # 4. Send HTTP request (raw bytes)
    request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\n\r\n"
    sock.send(request.encode())
    
    # 5. Receive response
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    
    # 6. Close socket
    sock.close()
    
    return response.decode(errors='ignore')

# Usage
response = simple_http_request("example.com", "/")
print(response[:500])
# Output: HTTP/1.1 200 OK\r\nDate: ...\r\n\r\n<!doctype html>...

# Problems with manual approach:
# ❌ No HTTPS support (unencrypted)
# ❌ No automatic redirects (301, 302)
# ❌ No connection pooling (creates new socket each time)
# ❌ No retries on failure
# ❌ Hard to handle errors
# ❌ No cookies/session support
```

### ✅ Professional DNS & HTTP (Using Libraries)

```python
# ===== DNS RESOLUTION (Advanced) =====
import dns.resolver
import dns.rdatatype
from datetime import datetime

class DNSResolver:
    def __init__(self):
        self.cache = {}  # Simple cache
        self.ttl_cache = {}
    
    def resolve(self, domain):
        """Resolve domain to IP with caching"""
        # Check cache
        if domain in self.cache:
            cached_result = self.cache[domain]
            ttl_time = self.ttl_cache[domain]
            
            # Check if TTL expired
            if datetime.now().timestamp() < ttl_time:
                print(f"✓ {domain} → {cached_result} (from cache)")
                return cached_result
        
        try:
            # Query DNS servers
            answers = dns.resolver.resolve(domain, 'A')
            ip = str(answers[0])
            ttl = answers.rrset.ttl
            
            # Store in cache with TTL
            self.cache[domain] = ip
            self.ttl_cache[domain] = datetime.now().timestamp() + ttl
            
            print(f"✓ {domain} → {ip} (TTL: {ttl}s)")
            return ip
        except Exception as e:
            print(f"✗ Failed to resolve {domain}: {e}")
            return None
    
    def get_all_records(self, domain):
        """Get all DNS records for domain"""
        records = {}
        
        for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [str(rdata) for rdata in answers]
            except:
                pass
        
        return records

# Usage
resolver = DNSResolver()
ip = resolver.resolve("google.com")

records = resolver.get_all_records("google.com")
for record_type, values in records.items():
    print(f"{record_type}: {values}")


# ===== HTTP REQUESTS (Professional) =====
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class HTTPClient:
    def __init__(self, max_retries=3, timeout=10):
        self.session = requests.Session()
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s delays
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, url, headers=None):
        """Make GET request with retries"""
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()  # Raise exception on 4xx/5xx
            return response
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return None
    
    def post(self, url, data=None, json=None, headers=None):
        """Make POST request with retries"""
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return None
    
    def download_file(self, url, filepath, chunk_size=8192):
        """Download file with progress"""
        try:
            response = self.session.get(
                url,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            print(f"Download: {percent:.1f}%")
            
            print(f"✓ Downloaded to {filepath}")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False

# Usage
client = HTTPClient()

# Simple GET
response = client.get("https://api.github.com/users/github")
if response:
    print(response.json())

# POST with JSON
response = client.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "Hello", "body": "World", "userId": 1}
)
if response:
    print(response.json())

# Download file
client.download_file(
    "https://www.python.org/ftp/python/3.11.0/python-3.11.0.tgz",
    "python.tgz"
)


# ===== HTTP STATUS CODE HANDLER =====
def handle_response(response):
    """Handle different HTTP status codes"""
    if response.status_code == 200:
        print("✓ Success!")
        return response.json()
    
    elif response.status_code == 301 or response.status_code == 302:
        print(f"! Redirect to {response.headers['Location']}")
        # Requests library follows redirects by default
        return response.json()
    
    elif response.status_code == 401:
        print("✗ Unauthorized - need to login")
        return None
    
    elif response.status_code == 403:
        print("✗ Forbidden - don't have permission")
        return None
    
    elif response.status_code == 404:
        print("✗ Not found - resource doesn't exist")
        return None
    
    elif response.status_code == 429:
        print("✗ Rate limited - wait before retrying")
        wait_time = int(response.headers.get('Retry-After', 60))
        print(f"Wait {wait_time} seconds")
        return None
    
    elif response.status_code >= 500:
        print("✗ Server error - try again later")
        return None


# ===== COMPLETE WORKFLOW =====
def fetch_user_data(username):
    """Real-world example: Fetch GitHub user data"""
    print(f"\n=== Fetching GitHub user: {username} ===\n")
    
    # 1. Resolve DNS
    resolver = DNSResolver()
    ip = resolver.resolve("api.github.com")
    
    # 2. Make HTTP request
    client = HTTPClient()
    url = f"https://api.github.com/users/{username}"
    response = client.get(url)
    
    # 3. Handle response
    if response and response.status_code == 200:
        user_data = response.json()
        
        print(f"\n✓ User: {user_data['name']}")
        print(f"  Location: {user_data['location']}")
        print(f"  Public Repos: {user_data['public_repos']}")
        print(f"  Followers: {user_data['followers']}")
        
        return user_data
    else:
        print(f"✗ Failed to fetch user")
        return None

# Usage
fetch_user_data("torvalds")

# Benefits of professional approach:
# ✅ Automatic retries on failure
# ✅ HTTPS support (encrypted)
# ✅ Automatic redirect following (301, 302)
# ✅ Connection pooling (reuse connections)
# ✅ Timeout handling
# ✅ Proper error handling
# ✅ Cookie/session support
# ✅ DNS caching
# ✅ Rate limiting awareness
```

---

## 💡 Mini Project: "Build a Website Status Checker"

### Phase 1: Simple (Check One Website) ⭐

**Requirements:**
- Check if website is up
- Show response time
- Show status code

**Code:**
```python
import requests
import time

def check_website(url):
    """Check if website is up"""
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            print(f"✓ {url} is UP ({duration:.2f}s)")
        else:
            print(f"! {url} returned {response.status_code}")
        
        return True
    except requests.exceptions.Timeout:
        print(f"✗ {url} timed out")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {url} is DOWN (connection refused)")
        return False

# Usage
check_website("https://google.com")
check_website("https://github.com")
```

**Limitations:**
- ❌ Can't run continuously
- ❌ No history tracking
- ❌ No notifications
- ❌ No analytics

---

### Phase 2: Intermediate (Multiple Sites + Scheduling) ⭐⭐

**Requirements:**
- Check 10+ websites
- Check every 5 minutes
- Track uptime percentage
- Store history

**Code:**
```python
import requests
import time
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

class WebsiteMonitor:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.init_database()
    
    def init_database(self):
        """Create database"""
        conn = sqlite3.connect('monitor.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY,
                website TEXT,
                status_code INTEGER,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def check_website(self, url):
        """Check website and store result"""
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            duration = time.time() - start
            status_code = response.status_code
        except:
            status_code = 0
            duration = 0
        
        # Store in database
        conn = sqlite3.connect('monitor.db')
        conn.execute(
            "INSERT INTO checks (website, status_code, response_time) VALUES (?, ?, ?)",
            (url, status_code, duration)
        )
        conn.commit()
        conn.close()
        
        return status_code
    
    def check_all_websites(self):
        """Check multiple websites"""
        websites = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://amazon.com",
            "https://netflix.com",
        ]
        
        print(f"\n[{datetime.now()}] Checking {len(websites)} websites...")
        
        for website in websites:
            status = self.check_website(website)
            emoji = "✓" if status == 200 else "✗"
            print(f"{emoji} {website} → {status}")
    
    def get_uptime(self, url, hours=24):
        """Calculate uptime percentage"""
        conn = sqlite3.connect('monitor.db')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT COUNT(*) FROM checks 
            WHERE website = ? AND status_code = 200
            AND timestamp > datetime('now', '-' || ? || ' hours')
        ''', (url, hours))
        
        success_count = cur.fetchone()[0]
        
        cur.execute('''
            SELECT COUNT(*) FROM checks 
            WHERE website = ? 
            AND timestamp > datetime('now', '-' || ? || ' hours')
        ''', (url, hours))
        
        total_count = cur.fetchone()[0]
        conn.close()
        
        if total_count == 0:
            return 100
        
        uptime = (success_count / total_count) * 100
        return uptime
    
    def start(self):
        """Start background monitoring"""
        self.scheduler.add_job(
            self.check_all_websites,
            'interval',
            minutes=5
        )
        self.scheduler.start()
        print("Monitor started. Checking every 5 minutes...")
    
    def get_stats(self):
        """Get uptime statistics"""
        websites = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
        ]
        
        print("\n=== Uptime Report (Last 24 hours) ===")
        for website in websites:
            uptime = self.get_uptime(website, 24)
            print(f"{website}: {uptime:.2f}%")

# Usage
monitor = WebsiteMonitor()
monitor.start()
# Run in background...
monitor.get_stats()
```

**Improvements:**
- ✅ Monitors multiple sites
- ✅ Continuous monitoring
- ✅ Database storage
- ✅ Uptime statistics
- ✅ Runs in background

---

### Phase 3: Enterprise (Global Monitoring + Alerts) ⭐⭐⭐

**Requirements:**
- Check from multiple locations (geo-distributed)
- 1000+ websites
- Alert on issues
- Dashboard visualization
- Latency from each region

**Architecture:**
```
MONITORING NODES (Multiple regions):
├─ US Node → Check all websites
├─ EU Node → Check all websites
├─ Asia Node → Check all websites

Database:
├─ Store all check results
├─ Latency analytics
├─ Uptime trends

Alert System:
├─ Email on failure
├─ Slack notifications
├─ PagerDuty on-call

Dashboard:
├─ Real-time status
├─ Historical graphs
├─ Alert history
```

**Features:**
```python
import smtplib
from slack_sdk import WebClient

class EnterpriseMonitor:
    def __init__(self):
        self.slack = WebClient(token="xoxb-your-token")
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "port": 587,
            "sender": "monitor@company.com",
            "password": "app_password"
        }
    
    def alert_on_failure(self, website, status_code):
        """Send alerts when site goes down"""
        
        # Slack notification
        self.slack.chat_postMessage(
            channel="#alerts",
            text=f"🚨 {website} is DOWN (Status: {status_code})"
        )
        
        # Email notification
        self.send_email(
            to="ops@company.com",
            subject=f"ALERT: {website} is down",
            body=f"{website} returned status code {status_code}"
        )
    
    def send_email(self, to, subject, body):
        """Send email alert"""
        try:
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["port"])
            server.starttls()
            server.login(self.email_config["sender"], self.email_config["password"])
            
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_config["sender"], to, message)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    def geo_distributed_check(self, url):
        """Check website from multiple locations"""
        regions = {
            "US-East": "18.206.1.1",
            "EU-West": "52.17.3.1",
            "Asia-SE": "54.169.0.1"
        }
        
        results = {}
        for region, proxy_ip in regions.items():
            try:
                start = time.time()
                response = requests.get(
                    url,
                    proxies={"http": f"http://{proxy_ip}:8080", "https": f"http://{proxy_ip}:8080"},
                    timeout=5
                )
                latency = time.time() - start
                
                results[region] = {
                    "status": response.status_code,
                    "latency": latency
                }
            except:
                results[region] = {
                    "status": 0,
                    "latency": 0
                }
        
        return results

# Usage
monitor = EnterpriseMonitor()
results = monitor.geo_distributed_check("https://example.com")
for region, data in results.items():
    print(f"{region}: {data['status']} ({data['latency']:.2f}s)")
```

**Capabilities:**
- ✅ Geo-distributed monitoring
- ✅ 1000s of websites
- ✅ Real-time alerts (Slack, Email)
- ✅ Multi-region latency tracking
- ✅ Historical analytics
- ✅ Dashboard visualization

---

## ⚖️ DNS vs HTTP vs IP

| Aspect | IP | DNS | HTTP |
|--------|----|----- |------|
| **What** | Network address | Domain name resolver | Communication protocol |
| **Example** | 142.250.185.46 | google.com | GET /search |
| **Resolves** | N/A | google.com → IP | HTTP request → Response |
| **Layer** | Network (Layer 3) | Application (Layer 7) | Application (Layer 7) |
| **Speed** | Instant | 10-100ms | 50-500ms |
| **Caching** | N/A | Yes (TTL) | Yes (Cache-Control) |
| **When Used** | Always (foundation) | Before HTTP | For communication |

---

## 🔐 Security Concerns

### DNS Security Issues

```
DNSSEC (DNS Security Extensions):
- Cryptographically sign DNS responses
- Prevents DNS spoofing
- Prevents DNS hijacking
- Adds latency but much more secure

DNS Privacy Issues:
- ISP can see all your DNS queries
- DOH (DNS over HTTPS): Encrypt DNS queries
- DOT (DNS over TLS): Encrypt DNS with TLS
```

### HTTP vs HTTPS

```
HTTP (Insecure ❌):
- Data sent in plain text
- Anyone can read it
- No server verification
- Use only for testing

HTTPS (Secure ✅):
- Data encrypted with TLS
- Server verified with certificate
- Man-in-the-middle attacks prevented
- Always use in production
```

---

## ❌ Common Mistakes

### Mistake 1: Assuming DNS is Instant

```python
# ❌ Bad: No DNS caching
for i in range(1000):
    response = requests.get("https://api.example.com/data")
    # Each request might do DNS lookup = slow!

# ✅ Good: Reuse session (automatic DNS caching)
session = requests.Session()
for i in range(1000):
    response = session.get("https://api.example.com/data")
    # Session reuses connections, caches DNS
```

### Mistake 2: Hardcoding IPs

```python
# ❌ Bad: Hardcoded IP (breaks if IP changes)
requests.get("http://142.250.185.46/search")

# What if Google changes servers?
# Your code breaks!

# ✅ Good: Use domain name
requests.get("https://google.com/search")
# DNS automatically finds new IP
```

### Mistake 3: Ignoring DNS TTL

```python
# ❌ Bad: DNS query every request (slow)
for i in range(10000):
    response = requests.get("https://example.com")
    # 10,000 DNS queries!

# ✅ Good: Let library handle DNS caching
session = requests.Session()
for i in range(10000):
    response = session.get("https://example.com")
    # DNS cached after first query
```

### Mistake 4: Not Handling HTTP Redirects

```python
import requests

# ❌ Bad: Forcing redirects OFF
response = requests.get("http://bit.ly/3abc123", allow_redirects=False)
print(response.status_code)  # 301 (redirect)
print(response.headers["Location"])  # 'https://real-url.com/...'

# ✅ Good: Let requests follow redirects automatically
response = requests.get("http://bit.ly/3abc123")  # allow_redirects=True by default
print(response.status_code)  # 200 (OK)
print(response.url)          # 'https://real-url.com/...'

```

---

## 📚 Additional Resources

**To understand IP/DNS/HTTP better:**

- **IP Addressing:** [Subnetting Tutorial](https://www.youtube.com/watch?v=BWZ-MHIhqjM)
- **DNS:** ["It's Always DNS" TED Talk](https://www.youtube.com/watch?v=44BGV3v6EEY)
- **HTTP:** [HTTP Methods Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- **HTTPS/TLS:** [TLS Handshake Visualization](https://tls.ulfheim.net/)

**Tools:**
- `nslookup` - DNS lookup from command line
- `dig` - Advanced DNS query tool
- `curl` - HTTP testing tool
- `Wireshark` - Network packet sniffer

**Commands:**
```bash
# Look up IP for domain
nslookup google.com
dig google.com

# Trace all DNS queries
dig +trace google.com

# Make HTTP request
curl https://api.github.com/users/github

# See HTTP headers only
curl -i https://google.com

# See full request/response
curl -v https://google.com

# Test latency
ping google.com
```


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's the difference between IP and DNS?**
   - Answer: IP is the address, DNS translates domain names to IPs

2. **Why use HTTPS instead of HTTP?**
   - Answer: HTTPS encrypts data with TLS; HTTP sends plain text

3. **What does DNS caching do?**
   - Answer: Stores DNS results locally (TTL); faster next time

4. **What HTTP status code means "not found"?**
   - Answer: 404

5. **Why is the request/response pattern important?**
   - Answer: It makes HTTP stateless; server doesn't remember clients

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **System Admin 1:** "The network is down!"
>
> **System Admin 2:** "Have you tried checking DNS?"
>
> **System Admin 1:** "How would I check DNS if the network is down?"
>
> **Both:** "It's always DNS." 🤷

---

[← Back to Main](../README.md) | [Previous: Client-Server Architecture](02-client-server-architecture.md) | [Next: APIs (REST, GraphQL, gRPC) →](04-apis-rest-graphql-grpc.md)

---

**Last Updated:** November 9, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (basic networking knowledge)  
**Time to Read:** 22 minutes  
**Time to Build Status Checker:** 2-4 hours per phase  

---

*Making the internet's plumbing crystal clear: IP, DNS, and HTTP explained for humans.* 🚀