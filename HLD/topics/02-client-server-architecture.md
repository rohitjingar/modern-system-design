# 02. Client-Server Architecture

Client-Server is like ordering pizza: you make a request, they fulfill it. The difference? The server doesn’t judge your 3 AM double-cheese POST requests. 🌙🍕

[← Back to Main](../README.md) | [Previous: What is System Design](01-what-is-system-design.md) | [Next: IP, DNS, and HTTP Basics →](03-ip-dns-http-basics.md)

---

## 🎯 Quick Summary

**Client-Server Architecture** is the foundation of almost every app you use. One side makes requests (client), the other handles them (server). It's simple, proven, and has been the backbone of the internet for 30 years.

Think of it as: **Request → Process → Response** (repeat forever).

---

## 🌟 Beginner Explanation

### What Are Clients and Servers?

Imagine a coffee shop:

```
☕ COFFEE SHOP ANALOGY

Client = You (customer)
Server = Barista

Interaction:
1. You walk in (connection established)
2. You order coffee (request sent)
3. Barista makes it (processing)
4. You get your coffee (response received)
5. You leave (connection closed)

Next day:
You come back, barista doesn't remember you
(stateless - each interaction is independent)
```

### In Technology Terms

```
CLIENT (Your Device)
├─ Web Browser (Chrome, Safari, Firefox)
├─ Mobile App (Instagram, Twitter)
├─ Desktop App (Slack, Discord)
└─ Smart Device (Alexa, Google Home)

        ↓↑ (HTTP Request/Response)

SERVER (Company's Computer)
├─ Handles the request
├─ Processes the data
├─ Sends response back
└─ Handles 1000s of clients simultaneously
```

### Real-World Example

**When you visit Google:**

```
WHAT YOU SEE:
1. You type "how to fix my code" in browser
2. Hit Enter
3. Google shows results in 0.5 seconds

WHAT ACTUALLY HAPPENS:

Your Browser (Client):
  ↓ "Give me search results for 'how to fix my code'"
  ↓ (HTTPS request over internet)
  ↓

Google's Servers:
  ↓ "Received request from this IP"
  ↓ "Search for 'how to fix my code' in our database"
  ↓ "Found 2 billion results"
  ↓ "Get top 10, rank them, format as HTML"
  ↓ "Add CSS for styling, JavaScript for interactivity"
  ↓ (Send back ~100 KB of data)

Your Browser:
  ↓ "Got HTML, CSS, JavaScript"
  ↓ Render the page
  ↓ Load images, ads, tracking scripts
  ↓ Show results to user

Total time: ~0.5 seconds ⚡
```

### Key Point: Stateless

A critical property of client-server: **the server doesn't remember you.**

```
Request 1: "What's my account balance?"
Server: "Balance is $1000" + stores nothing about you

Request 2: (5 minutes later) "What's my account balance?"
Server: "Who are you?" 🤔

Solution: You send ID/session token with every request
Request 2: "I'm user123, what's my balance?"
Server: "OK user123, balance is $1000"
```

This is why **sessions and cookies exist** — to make it feel like the server remembers you, when it actually doesn't.

---

## 🔬 Advanced Explanation

### Architecture Layers

Client-Server has clear separation of concerns:

```
┌─────────────────────────────────────────┐
│          CLIENT (Presentation)          │
│  - User Interface                       │
│  - Business Logic (limited)             │
│  - Display Data                         │
└────────────────────────────────────────┘
            ↓↑ (Network Call)
┌─────────────────────────────────────────┐
│         SERVER (Application Logic)      │
│  - Process Requests                     │
│  - Business Logic (main)                │
│  - Authentication/Authorization         │
│  - API Endpoints                        │
└────────────────────────────────────────┘
            ↓↑ (Database Query)
┌─────────────────────────────────────────┐
│         DATABASE (Data Storage)         │
│  - Persistent Storage                   │
│  - Query Processing                     │
│  - Data Integrity                       │
└─────────────────────────────────────────┘
```

### The Problems With Single Server

```
❌ PROBLEM 1: Single Point of Failure

[100,000 Clients]
        ↓
    [1 Server]
        ↓
    Server crashes
        ↓
[ALL 100,000 clients get error]
        ↓
[Company loses money]
        ↓
[You get fired 😢]
```

### The Solution: Multiple Servers

```
✅ SOLUTION: Load Balancer + Multiple Servers

[100,000 Clients]
        ↓
[Load Balancer]
(distributes traffic)
    ↙  ↓  ↘
[S1][S2][S3]
(each handles 33K requests)
    ↓  ↓  ↓
[Shared Database]
(single source of truth)
```

### Key Design Principle: Stateless Servers

**Why stateless matters:**

```
❌ STATEFUL SERVER (Bad)
Server 1 stores: User123 logged in
Request 1: Client → Server1 (says "logout")
Result: User logged out

Request 2: Same client → Server2 
Result: Server2 says "Who is this? They're not logged in on me!"
Problem: Session lost 💥

✅ STATELESS SERVER (Good)
Server stores nothing about users
Request 1: Client → Server1 + session_token
Request 2: Same client → Server2 + session_token
Result: Server2 looks up session_token in database, recognizes user
Problem: Solved! ✅
```

This means **any server can handle any request**:

```
LOAD BALANCING OPTIONS:

Round Robin:
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1
(repeats cyclically)

Least Connections:
Always route to server with fewest active connections
Server 1: 100 connections
Server 2: 50 connections ← Route here
Server 3: 75 connections

Weighted:
Server 1: 2x more powerful (gets 50% traffic)
Server 2: 1x power (gets 25% traffic)
Server 3: 1x power (gets 25% traffic)

IP Hash:
Route based on client IP
Same client always goes to same server
(useful for session persistence if needed)
```

### Communication Protocol: HTTP/HTTPS

```
HTTP = HyperText Transfer Protocol (unencrypted)
HTTPS = HTTP + Security (encrypted with SSL/TLS)

HTTP REQUEST FORMAT:
┌─────────────────────┐
│ GET /api/users/123  │ ← Method & Path
│ Host: api.example.com
│ Authorization: Bearer token123
│ Content-Type: application/json
│ [empty line]
│ (optional body for POST/PUT)
└─────────────────────┘

HTTP RESPONSE FORMAT:
┌─────────────────────┐
│ 200 OK              │ ← Status Code
│ Content-Type: application/json
│ Content-Length: 256
│ [empty line]
│ {                   │
│   "id": 123,        │ ← Response Body
│   "name": "Alice"   │
│ }                   │
└─────────────────────┘
```

**Common HTTP Status Codes:**

```
2xx = Success
  200 OK (request succeeded)
  201 Created (resource created)
  204 No Content (success, no response body)

3xx = Redirect
  301 Moved Permanently (use new URL)
  302 Found (temporary redirect)

4xx = Client Error (client's fault)
  400 Bad Request (malformed request)
  401 Unauthorized (need to login)
  403 Forbidden (not allowed even if logged in)
  404 Not Found (resource doesn't exist)
  429 Too Many Requests (rate limited)

5xx = Server Error (server's fault)
  500 Internal Server Error (something broke)
  502 Bad Gateway (server unreachable)
  503 Service Unavailable (server overloaded)
```

### Real-World Architecture

```
MODERN CLIENT-SERVER SETUP:

[Client 1 - Browser]
[Client 2 - Mobile App]
[Client 3 - Desktop App]
[Client 4 - IoT Device]
        ↓ (HTTPS)
[CDN - Cloudflare]
(caches static content: JS, CSS, images)
        ↓
[API Gateway - Kong/AWS API Gateway]
(rate limiting, authentication, routing)
        ↓
[Load Balancer - Nginx/HAProxy]
(distributes traffic, health checks)
    ↙  ↓  ↘
[App Server 1] [App Server 2] [App Server 3]
(Node.js, Python, Java, Go)
    ↓  ↓  ↓
[Cache - Redis]
(session storage, hot data)
    ↓
[Database - PostgreSQL/MongoDB]
(persistent data)
    ↓
[Backup Database]
(replication for disaster recovery)
```

---

## 🐍 Python Code Example

### ❌ Simple Client-Server (Single Server)

```python
# ===== SERVER SIDE =====
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory database (lost on restart!)
users_db = {
    1: {"name": "Alice", "email": "alice@example.com", "balance": 1000},
    2: {"name": "Bob", "email": "bob@example.com", "balance": 500},
}

# Single endpoint to get user
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

# Single endpoint to create user
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.json
    new_id = max(users_db.keys()) + 1
    users_db[new_id] = {
        "name": data['name'],
        "email": data['email'],
        "balance": 0
    }
    return jsonify({"id": new_id}), 201

# Single endpoint to transfer money
@app.route('/api/transfer', methods=['POST'])
def transfer_money():
    """Transfer money between users"""
    data = request.json
    from_user = data['from']
    to_user = data['to']
    amount = data['amount']
    
    if users_db[from_user]['balance'] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    users_db[from_user]['balance'] -= amount
    users_db[to_user]['balance'] += amount
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)


# ===== CLIENT SIDE =====
import requests

class BankClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_user(self, user_id):
        """Get user info"""
        response = requests.get(f"{self.base_url}/api/users/{user_id}")
        return response.json()
    
    def create_user(self, name, email):
        """Create new user"""
        response = requests.post(
            f"{self.base_url}/api/users",
            json={"name": name, "email": email}
        )
        return response.json()
    
    def transfer(self, from_user, to_user, amount):
        """Transfer money"""
        response = requests.post(
            f"{self.base_url}/api/transfer",
            json={
                "from": from_user,
                "to": to_user,
                "amount": amount
            }
        )
        return response.json()

# Usage
client = BankClient()

# Get user
user = client.get_user(1)
print(user)  # {'name': 'Alice', 'email': 'alice@example.com', 'balance': 1000}

# Create user
new_user = client.create_user("Charlie", "charlie@example.com")
print(new_user)  # {'id': 3}

# Transfer money
result = client.transfer(1, 2, 100)
print(result)  # {'status': 'success'}

# Problems with this approach:
# ❌ Single server (crashes = app down)
# ❌ In-memory storage (data lost on restart)
# ❌ No authentication (anyone can transfer money!)
# ❌ No error handling (network failures, timeouts)
# ❌ No scaling (1000 concurrent users = crash)
```

### ✅ Scalable Client-Server (Multiple Servers + Database)

```python
# ===== SERVER SIDE (Multiple Instances) =====
from flask import Flask, request, jsonify, session
import psycopg2
from functools import wraps
import json
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Database connection (shared across all server instances)
def get_db():
    return psycopg2.connect(
        host="db.example.com",
        database="bank",
        user="postgres",
        password="secret"
    )

# Middleware: Check authentication
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# API Endpoint: Login (creates session)
@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email = data['email']
    password = data['password']
    
    db = get_db()
    cur = db.cursor()
    
    # Query user
    cur.execute(
        "SELECT id, password FROM users WHERE email = %s",
        (email,)
    )
    result = cur.fetchone()
    
    if not result or result[1] != password:  # In real app, hash password!
        return jsonify({"error": "Invalid credentials"}), 401
    
    user_id = result[0]
    
    # Store in session (session ID sent to client as cookie)
    session['user_id'] = user_id
    session.permanent = True
    
    return jsonify({"status": "logged_in", "user_id": user_id}), 200

# API Endpoint: Get user (requires auth)
@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get user info (authenticated)"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute(
        "SELECT id, name, email, balance FROM users WHERE id = %s",
        (user_id,)
    )
    result = cur.fetchone()
    
    if not result:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": result[0],
        "name": result[1],
        "email": result[2],
        "balance": result[3]
    }), 200

# API Endpoint: Transfer money (requires auth, with transaction)
@app.route('/api/transfer', methods=['POST'])
@require_auth
def transfer_money():
    """Transfer money with database transaction"""
    data = request.json
    from_user = data['from']
    to_user = data['to']
    amount = data['amount']
    
    # Verify: requester is from_user (security check)
    if session['user_id'] != from_user:
        return jsonify({"error": "Can only transfer from your account"}), 403
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Start transaction
        db.set_isolation_level(None)  # Autocommit off
        
        # Check balance
        cur.execute("SELECT balance FROM users WHERE id = %s FOR UPDATE", (from_user,))
        result = cur.fetchone()
        
        if not result or result[0] < amount:
            db.rollback()
            return jsonify({"error": "Insufficient balance"}), 400
        
        # Deduct from source
        cur.execute(
            "UPDATE users SET balance = balance - %s WHERE id = %s",
            (amount, from_user)
        )
        
        # Add to destination
        cur.execute(
            "UPDATE users SET balance = balance + %s WHERE id = %s",
            (amount, to_user)
        )
        
        # Log transaction
        cur.execute(
            "INSERT INTO transactions (from_user, to_user, amount) VALUES (%s, %s, %s)",
            (from_user, to_user, amount)
        )
        
        # Commit transaction (all-or-nothing)
        db.commit()
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run multiple instances on different ports
    # Instance 1: python app.py → port 5000
    # Instance 2: python app.py → port 5001
    # Instance 3: python app.py → port 5002
    # Then put load balancer in front
    app.run(port=5000, debug=False)

# ===== LOAD BALANCER CONFIGURATION (Nginx) =====
"""
upstream backend {
    # Define 3 backend servers
    server localhost:5000 weight=1;
    server localhost:5001 weight=1;
    server localhost:5002 weight=1;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

# ===== CLIENT SIDE (Same as Before) =====
import requests
from requests.auth import HTTPBasicAuth

class ScalableBankClient:
    def __init__(self, base_url="http://api.example.com"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, email, password):
        """Login and establish session"""
        response = self.session.post(
            f"{self.base_url}/api/login",
            json={"email": email, "password": password}
        )
        return response.json()
    
    def get_user(self, user_id):
        """Get user info (requires authentication)"""
        response = self.session.get(f"{self.base_url}/api/users/{user_id}")
        return response.json()
    
    def transfer(self, from_user, to_user, amount):
        """Transfer money securely"""
        response = self.session.post(
            f"{self.base_url}/api/transfer",
            json={
                "from": from_user,
                "to": to_user,
                "amount": amount
            }
        )
        return response.json()

# Usage
client = ScalableBankClient()

# Login
client.login("alice@example.com", "password123")

# Get user (now authenticated)
user = client.get_user(1)
print(user)

# Transfer (securely with authentication & transactions)
result = client.transfer(1, 2, 100)
print(result)

# Benefits of scalable approach:
# ✅ Multiple servers (one fails, others handle traffic)
# ✅ Persistent database (data survives restarts)
# ✅ Authentication (secure, only authorized users can transfer)
# ✅ Transaction support (money transfer all-or-nothing)
# ✅ Scaling (can handle 1000s of concurrent users)
# ✅ Any server can handle any request (stateless)
```

---

## 💡 Mini Project: "Design a Chat Server"

### Phase 1: Basic (Direct Messaging) ⭐

**Requirements:**
- 2 users can send messages
- Messages stored
- Can retrieve chat history

**Architecture:**
```
[User A Browser] → [1 Server] → [Database]
                ↗ ↗ ↖ ↖
[User B Browser]
```

**Code:**
```python
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('chat.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            sender_id INTEGER,
            receiver_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/messages/<int:receiver_id>', methods=['POST'])
def send_message(receiver_id):
    """Send message"""
    data = request.json
    sender_id = data['sender_id']
    content = data['content']
    
    conn = sqlite3.connect('chat.db')
    conn.execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
        (sender_id, receiver_id, content)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "sent"}), 201

@app.route('/api/messages/<int:user_id>/<int:other_id>', methods=['GET'])
def get_messages(user_id, other_id):
    """Get chat history"""
    conn = sqlite3.connect('chat.db')
    cur = conn.cursor()
    
    cur.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) 
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp
    ''', (user_id, other_id, other_id, user_id))
    
    messages = cur.fetchall()
    conn.close()
    
    return jsonify({
        "messages": [
            {
                "sender_id": m[1],
                "receiver_id": m[2],
                "content": m[3],
                "timestamp": m[4]
            }
            for m in messages
        ]
    }), 200

if __name__ == '__main__':
    init_db()
    app.run()
```

**Limitations:**
- ❌ No real-time updates (must refresh to see new messages)
- ❌ Single server (crashes = lose messages)
- ❌ No authentication
- ❌ Can't scale to 1000s of users

---

### Phase 2: Multi-User (Chat Rooms) ⭐⭐

**Requirements:**
- Group chats (many users)
- Real-time notifications
- User online status

**Architecture:**
```
[User 1] ──┐
[User 2] ──┼→ [Load Balancer] → [App 1, 2, 3] → [PostgreSQL]
[User 3] ──┤                   → [Redis Cache]
[User 4] ──┘                   → [Kafka (events)]
```

**Key Changes:**
```python
# Real-time updates with WebSocket
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('join_room')
def on_join(data):
    """User joins chat room"""
    room = data['room_id']
    user_id = data['user_id']
    join_room(room)
    
    # Notify others
    emit('user_joined', {
        'user_id': user_id,
        'message': f'User {user_id} joined'
    }, room=room)

@socketio.on('send_message')
def on_message(data):
    """User sends message in real-time"""
    room = data['room_id']
    message = {
        'user_id': data['user_id'],
        'content': data['content'],
        'timestamp': datetime.now()
    }
    
    # Save to database
    db.save_message(message)
    
    # Broadcast to all users in room (real-time)
    emit('new_message', message, room=room)
```

**Improvements:**
- ✅ Real-time updates (messages appear instantly)
- ✅ Group chats (1-to-many)
- ✅ Online status tracking
- ✅ Multiple servers (redundancy)
- ✅ Scales to 10K+ concurrent users

---

### Phase 3: Enterprise (Global, Reliable) ⭐⭐⭐

**Requirements:**
- Global deployment (US, EU, Asia)
- 1M+ concurrent users
- 99.9% uptime
- Message encryption

**Architecture:**
```
US REGION:
[CDN] → [Load Balancer] → [App Servers 1-20]
                       → [Redis Cluster]
                       → [PostgreSQL Master]

EU REGION:
[CDN] → [Load Balancer] → [App Servers 21-40]
                       → [Redis Cluster]
                       → [PostgreSQL Replica] → Replicates to US

ASIA REGION:
[CDN] → [Load Balancer] → [App Servers 41-60]
                       → [Redis Cluster]
                       → [PostgreSQL Replica] → Replicates to US

MESSAGE QUEUE (Kafka):
All events (messages, typing indicators, online status)
flow through Kafka for reliability & scalability
```

**Features:**
```python
# End-to-end encryption
from cryptography.fernet import Fernet

def encrypt_message(message, key):
    cipher = Fernet(key)
    return cipher.encrypt(message.encode())

def decrypt_message(encrypted, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted).decode()

# Geographic routing
def get_nearest_server(user_location):
    if user_location in ['US-East', 'US-West', 'US-Central']:
        return 'US_REGION'
    elif user_location in ['EU-North', 'EU-South']:
        return 'EU_REGION'
    else:
        return 'ASIA_REGION'

# Automatic failover
def send_message_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            server = get_healthy_server()
            server.send(message)
            return True
        except ServerDown:
            if attempt == max_retries - 1:
                # Save to queue for later
                save_to_outbox(message)
                return False
            continue
```

**Capabilities:**
- ✅ 1M+ concurrent users
- ✅ Multi-region (low latency globally)
- ✅ End-to-end encryption
- ✅ 99.9% uptime (automatic failover)
- ✅ Scales infinitely (add more regions)

---

## ⚖️ Single Server vs Multiple Servers

| Aspect | Single Server | Multiple Servers |
|--------|---------------|------------------|
| **Simplicity** | ✅ Easy to setup | ❌ Complex setup |
| **Cost** | ✅ Cheap ($10/month) | ❌ Expensive ($1000+/month) |
| **Reliability** | ❌ One crash = down | ✅ One down, others run |
| **Scalability** | ❌ Limited to machine specs | ✅ Unlimited (add more) |
| **Speed** | ❌ Slow at scale | ✅ Fast (distributed) |
| **Development** | ✅ Quick to build | ❌ Takes time |
| **When to use** | Startup MVP | Production scale |

---

## 🔐 Security in Client-Server

### Authentication (Proving Who You Are)

```
Method 1: Session Cookies (Traditional)
Client logs in → Server creates session → Stores in database
Client makes requests → Sends session cookie with each request
Server verifies cookie → Knows it's you

Method 2: JWT Tokens (Modern)
Client logs in → Server creates signed JWT token
Client makes requests → Sends JWT in Authorization header
Server verifies JWT signature → Doesn't need database lookup (stateless!)

Method 3: OAuth (Third-party)
"Login with Google"
Redirect to Google → Google authenticates → Redirect back with token
Your app trusts Google → User authenticated
```

### HTTPS (Encrypted Communication)

```
HTTP (Bad ❌):
Your password sent over internet in plain text
Anyone with network access can read it

HTTPS (Good ✅):
Your password encrypted with SSL/TLS
Even if someone intercepts, they see gibberish
```

---

## 🎓 Key Takeaways

✅ **Client-Server** = Request/Response pattern  
✅ **Stateless** = Server doesn't remember you (use sessions/tokens)  
✅ **Scalable** = Multiple servers behind load balancer  
✅ **HTTP/HTTPS** = Protocol for communication  
✅ **Authentication** = Prove who you are (cookies, JWT, OAuth)  
✅ **Database** = Persistent storage shared by all servers  
✅ **Load Balancer** = Distributes traffic fairly  

---

## 🚀 When Client-Server Is NOT Enough

**Client-Server doesn't work well for:**

1. **Real-time Gaming** → Need Peer-to-Peer + Server
2. **Offline-first Apps** → Need client-side database + sync
3. **IoT Networks** → Need edge computing + cloud hybrid
4. **Blockchain** → Need distributed consensus (not just client-server)

**But for:** Social media, banking, email, messaging, shopping — client-server is perfect.

---

## ❌ Common Mistakes

### Mistake 1: Putting Business Logic on Client

```python
# ❌ Bad: Client calculates discount
total = 100
discount = 20  # Client decides discount
final = total - discount  # 80

# User modifies JavaScript: discount = 100
# They pay $0 😱

# ✅ Good: Server calculates discount
# Client just displays it
Server: "User gets 20% discount"
Server: total = 100 - 20 = 80
```

### Mistake 2: Trusting Client Input

```python
# ❌ Bad: Trust client
quantity = request.json['quantity']  # Client says "100"
price = request.json['price']  # Client says "$1"
total = quantity * price  # 100

# ✅ Good: Verify on server
quantity = int(request.json['quantity'])
if quantity < 1 or quantity > MAX_PER_ORDER:
    return error
price = lookup_price_from_database(product_id)  # Don't trust client
total = quantity * price
```

### Mistake 3: Assuming Network Won't Fail

```python
# ❌ Bad: Assume request succeeds
response = requests.post(url, data)
user_account.balance -= amount  # If request fails, balance wrong!

# ✅ Good: Handle failures
try:
    response = requests.post(url, data, timeout=5)
    if response.status_code == 200:
        user_account.balance -= amount
    else:
        save_for_retry()
except Timeout:
    save_for_retry()
except Exception:
    log_error()
    return error_to_user()
```

---

## 📚 Additional Resources

**To understand client-server better:**

- **HTTP Basics:** [MDN HTTP Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- **REST API Design:** [REST API Tutorial](https://restfulapi.net/)
- **Load Balancing:** [NGINX Load Balancing](https://nginx.org/en/docs/http/load_balancing.html)
- **WebSockets:** [Socket.io Documentation](https://socket.io/)

**Videos:**
- "How the Web Works" (2 minutes explanation)
- "REST API Crash Course" (learn HTTP methods)
- "Understanding DNS" (how clients find servers)

---

## 🎯 Before You Leave

**Can you answer these?**

1. **Why is "stateless" important?**
   - Answer: So any server can handle any request

2. **What's the difference between HTTP and HTTPS?**
   - Answer: HTTPS encrypts communication with SSL/TLS

3. **If you have 3 servers, can they all store user sessions locally?**
   - Answer: No! Use centralized session store (Redis/DB)

4. **Why use load balancer instead of just adding one big server?**
   - Answer: Load balancer scales infinitely; big servers have limits

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Developer 1:** "I'll just put everything on one server."
>
> **Developer 2:** "Bold strategy. Your users on 6 continents will love that 5-second latency."
>
> **Developer 1:** *adds more servers* 😅

---

[← Back to Main](../README.md) | [Previous: What is System Design](01-what-is-system-design.md) | [Next: IP, DNS, and HTTP Basics →](03-ip-dns-http-basics.md)

---

**Last Updated:** November 9, 2025  
**Difficulty:** ⭐⭐ Beginner-Intermediate (basic networking knowledge helpful)  
**Time to Read:** 20 minutes  
**Time to Build Chat Server:** 2-3 hours per phase  

---

*Built to make client-server architecture crystal clear, from your first HTTP request to handling millions.* 🚀