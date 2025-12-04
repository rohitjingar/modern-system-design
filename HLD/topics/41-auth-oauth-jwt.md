# 41. Authentication & Authorization (OAuth, JWT, SSO)

Authentication answers "who are you?" Authorization answers "what can you do?" Everyone confuses them. Then you spend three days debugging why a user can login but can't access anything. They're authenticated but not authorized. Or sometimes the opposite. Or sometimes both. Security is fun! 🔐😅

[← Back to Main](../README.md) | [Previous: Chaos Engineering](40-chaos-engineering.md) |  [Next: Rate Limiting (Security)](42-rate-limiting-security.md)

---

## 🎯 Quick Summary

**Authentication** verifies identity (who are you?). **Authorization** grants permissions (what can you do?). Methods: Basic auth (username/password), OAuth (third-party), JWT (tokens), SSO (single sign-on). OAuth 2.0 industry standard. JWT stateless and scalable. SSO reduces password fatigue. Netflix uses OAuth for partners. Google uses OAuth for everything. Trade-off: security vs complexity, token management, revocation difficulty.

Think of it as: **Authentication = ID Check, Authorization = Permission Check**

---

## 🌟 Beginner Explanation

### Authentication vs Authorization

```
AUTHENTICATION (Who are you?):

User logs in:
├─ Username: alice@example.com
├─ Password: secret123
└─ System verifies:
   ├─ User exists? Yes
   ├─ Password matches? Yes
   └─ ✓ AUTHENTICATED (identity verified)

What it answers:
├─ Are you really Alice?
├─ Can we trust you're who you say?
└─ Yes!


AUTHORIZATION (What can you do?):

Alice logged in, now accessing:
├─ Request: "Get user list"
├─ System checks:
│  ├─ Is Alice authenticated? Yes
│  ├─ Does Alice have permission? Check roles
│  │  ├─ Alice is "user" role
│  │  ├─ "user" can't access user list
│  │  └─ Permission denied!
│  └─ ✗ NOT AUTHORIZED
└─ Access denied

What it answers:
├─ Even though we know who you are
├─ Do you have permission to do this?
└─ No!


CORRECT SCENARIO:

Bob logged in, now accessing:
├─ Request: "Get user list"
├─ System checks:
│  ├─ Is Bob authenticated? Yes
│  ├─ Does Bob have permission?
│  │  ├─ Bob is "admin" role
│  │  ├─ "admin" can access user list
│  │  └─ Permission granted!
│  └─ ✓ AUTHORIZED
└─ Access allowed
```

### Authentication Methods

```
BASIC AUTH (Simplest):

Request: GET /api/users
Headers:
├─ Authorization: Basic base64(username:password)
└─ Authorization: Basic YWxpY2VAZXhhbXBsZS5jb206c2VjcmV0MTIz

Flow:
├─ Decode base64
├─ Extract username and password
├─ Verify credentials
└─ Grant access (if match)

Pros:
✅ Simple

Cons:
❌ Password sent with every request (encoded, not encrypted!)
❌ Password in memory
❌ No logout (just stop sending header)
❌ No token expiration
❌ Not recommended for production!


SESSIONS (Traditional):

Login:
├─ User POST /login (username, password)
├─ Server verifies credentials
├─ Server creates session
├─ Server stores session in database
├─ Server sends cookie: session_id=abc123
└─ Browser stores cookie

Subsequent requests:
├─ Browser sends: Cookie: session_id=abc123
├─ Server looks up session in database
├─ Verifies session is valid (not expired)
└─ Grants access

Logout:
├─ Browser sends: POST /logout
├─ Server deletes session from database
└─ Cookie becomes invalid

Pros:
✅ Simple
✅ Server-side control (can revoke)
✅ Session can be revoked instantly

Cons:
❌ Requires database lookup per request (slow)
❌ Doesn't scale across servers (session on server 1, request to server 2 fails!)
❌ Server must store all sessions (memory usage)


JWT TOKENS (Stateless):

Login:
├─ User POST /login (username, password)
├─ Server verifies credentials
├─ Server creates JWT token:
│  ├─ Header: {alg: "HS256", typ: "JWT"}
│  ├─ Payload: {user_id: 123, role: "admin", exp: 1700000000}
│  ├─ Signature: HMAC(header.payload, secret_key)
│  └─ Token: header.payload.signature
├─ Server sends token to client
└─ Client stores token (localStorage, cookie)

Subsequent requests:
├─ Client sends: Authorization: Bearer token
├─ Server verifies signature:
│  ├─ Split token into parts
│  ├─ Recalculate signature
│  ├─ Does it match? Yes → Valid
│  └─ No server lookup needed!
├─ Server decodes payload
├─ Checks expiration time
└─ Grants access

Logout:
├─ Client deletes token (localStorage)
├─ Token still valid server-side (but client doesn't send it)
❌ Can't revoke instantly!

Pros:
✅ Stateless (no server database needed)
✅ Scalable (any server can verify)
✅ Fast (no database lookup)
✅ Mobile friendly

Cons:
❌ Can't revoke instantly (token valid until expiration)
❌ Large payload in every request
❌ Secret key must be kept secure
```

### OAuth 2.0 Flow

```
OAUTH 2.0 (Third-party login):

Scenario: Login with Google

User clicks: "Login with Google"
  ↓
App redirects to Google:
  GET https://accounts.google.com/o/oauth2/v2/auth?
    client_id=...
    redirect_uri=https://app.com/callback
    scope=profile email
    state=random123
  ↓
User logs in to Google
  ├─ Google shows: "Allow app.com to access your profile?"
  └─ User clicks: "Yes"
  ↓
Google redirects back to app:
  GET https://app.com/callback?
    code=auth_code_xyz
    state=random123
  ↓
App verifies state (CSRF protection)
  ↓
App exchanges code for token (backend):
  POST https://accounts.google.com/o/oauth2/token
    code=auth_code_xyz
    client_id=...
    client_secret=... (secret!)
  ↓
Google returns:
  {
    access_token: "token_xyz",
    expires_in: 3600,
    id_token: "jwt_token"
  }
  ↓
App uses token to get user info:
  GET https://www.googleapis.com/oauth2/v2/userinfo
    Authorization: Bearer token_xyz
  ↓
Google returns user profile
  ↓
App creates session/JWT for user
  ↓
User logged in!

Benefits:
✅ User doesn't give password to app
✅ OAuth provider handles security
✅ Works across multiple apps
✅ User can revoke access
```

---

## 🔬 Advanced Explanation

### JWT Deep Dive

```
JWT STRUCTURE:

Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsIm5hbWUiOiJBbGljZSIsImV4cCI6MTcwMDAwMDAwMH0.signature

Three parts (separated by dots):

1. HEADER (base64 encoded JSON):
{
  "alg": "HS256",     // Algorithm
  "typ": "JWT"        // Type
}

2. PAYLOAD (base64 encoded JSON):
{
  "user_id": 123,
  "name": "Alice",
  "role": "admin",
  "exp": 1700000000   // Expiration (unix timestamp)
}

3. SIGNATURE (HMAC signature):
HMAC-SHA256(
  base64(header) + "." + base64(payload),
  secret_key
)

How verification works:

Received token: header.payload.signature

1. Extract header and payload
2. Recalculate signature using secret_key
3. Compare: calculated_signature == received_signature?
4. If match: Token is valid (not tampered)
5. If mismatch: Token is invalid (tampered or wrong secret)

Note: base64 is ENCODING (not encryption!)
Anyone can decode and see payload!
Don't put passwords in JWT payload!
```

### Authorization Patterns

```
ROLE-BASED ACCESS CONTROL (RBAC):

User has role:
├─ admin
├─ user
└─ guest

Endpoint has required role:
├─ GET /users → requires: admin
├─ POST /orders → requires: user
├─ GET /public → requires: none
└─ DELETE /users → requires: admin

Check:
  if user.role in endpoint.required_roles:
    allow access
  else:
    deny access

Simple but inflexible!


ATTRIBUTE-BASED ACCESS CONTROL (ABAC):

User has attributes:
├─ role: "admin"
├─ department: "finance"
├─ location: "US"
├─ created_date: "2020-01-01"
└─ pay_grade: 5

Endpoint has policy:
  allow if (role == "admin") OR
           (role == "user" AND department == "finance") AND
           (location in ["US", "EU"])

Check:
  if evaluate_policy(user.attributes, endpoint.policy):
    allow access

Flexible but complex!


PERMISSION-BASED ACCESS CONTROL:

User has permissions:
├─ user.orders:read
├─ user.orders:write
├─ admin.users:read
├─ admin.users:delete
└─ billing.reports:read

Endpoint requires permission:
├─ GET /orders → requires: user.orders:read
├─ POST /orders → requires: user.orders:write
├─ GET /users → requires: admin.users:read
└─ DELETE /users/{id} → requires: admin.users:delete

Check:
  if required_permission in user.permissions:
    allow access

Granular and scalable!
```

### SSO (Single Sign-On)

```
MULTI-APP SCENARIO:

Apps:
├─ Email system
├─ Document system
├─ Messaging system
└─ Analytics system

Without SSO:
├─ Login to Email: alice / password1
├─ Login to Documents: alice / password1
├─ Login to Messaging: alice / password1
├─ Login to Analytics: alice / password1
└─ 4 separate sessions, 4 password prompts!

With SSO:
├─ Navigate to Email
├─ Not logged in, redirect to SSO login
├─ Enter: alice / password1
├─ SSO validates, creates central session
├─ Redirect back to Email
├─ Email gets SSO session token
├─ Navigate to Documents
├─ SSO cookie already set!
├─ Documents checks SSO
├─ SSO says: "Alice already logged in"
├─ No login prompt!
├─ Same for Messaging and Analytics

Benefits:
✅ Single login for all apps
✅ Consistent user experience
✅ Easy logout (logout from SSO logs out everywhere)
✅ Centralized user management

Implementation:
├─ Central SSO server
├─ OAuth/OIDC for integration
├─ Session cookies shared
├─ Can use SAML (enterprise)
└─ Examples: Okta, Auth0, Google Workspace
```

---

## 🐍 Python Code Example

### ❌ Without Proper Authentication (Insecure)

```python
# ===== INSECURE AUTHENTICATION =====

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders - NO authentication!"""
    
    # Anyone can call this!
    user_id = request.args.get('user_id')
    
    # No verification that user owns data!
    orders = db.query(f"SELECT * FROM orders WHERE user_id={user_id}")
    
    return jsonify(orders)

# Problems:
# ❌ No authentication (anyone can call)
# ❌ SQL injection (not using parameterized query)
# ❌ No authorization (can query any user)
# ❌ No token/session (stateless request)
```

### ✅ With JWT Authentication

```python
# ===== WITH JWT AUTHENTICATION =====

from flask import Flask, request, jsonify
import jwt
from functools import wraps
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Verify token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        # Add user to request context
        request.user_id = current_user
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - create JWT token"""
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Verify credentials
    user = verify_credentials(username, password)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create JWT token
    token = jwt.encode(
        {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=1)  # 1 hour expiration
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return jsonify({'token': token})

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders(user_id):
    """Get orders - requires JWT token"""
    
    # user_id is from token (trusted)
    orders = db.query(
        "SELECT * FROM orders WHERE user_id = %s",
        (user_id,)  # Parameterized query (safe!)
    )
    
    return jsonify(orders)

@app.route('/api/users/<int:target_user_id>', methods=['GET'])
@token_required
def get_user(user_id, target_user_id):
    """Get user data - with authorization check"""
    
    # AUTHORIZATION: User can only access own data
    if user_id != target_user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    user = db.query("SELECT * FROM users WHERE id = %s", (target_user_id,))
    return jsonify(user)

def verify_credentials(username, password):
    """Verify username and password"""
    
    user = db.query("SELECT * FROM users WHERE username = %s", (username,))
    
    if not user:
        return None
    
    # Hash and verify password (use bcrypt in production!)
    if not bcrypt.checkpw(password.encode(), user['password_hash']):
        return None
    
    return user

# Benefits:
# ✅ Authentication required (token check)
# ✅ Token verified (JWT signature)
# ✅ Authorization checked (ownership)
# ✅ SQL injection protected (parameterized)
# ✅ Token expiration (1 hour)
```

### ✅ Production OAuth 2.0 Integration

```python
# ===== PRODUCTION OAUTH 2.0 =====

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

oauth = OAuth(app)

# Configure OAuth with Google
google = oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'profile email'}
)

@app.route('/login')
def login():
    """Start OAuth login flow"""
    
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    """OAuth callback (after user logs in to Google)"""
    
    try:
        # Exchange code for token
        token = google.authorize_access_token()
    except Exception as e:
        return jsonify({'error': str(e)}), 401
    
    # Get user info
    user_info = token.get('userinfo')
    
    if not user_info:
        return jsonify({'error': 'Failed to get user info'}), 401
    
    email = user_info['email']
    name = user_info['name']
    
    # Find or create user
    user = db.query("SELECT * FROM users WHERE email = %s", (email,))
    
    if not user:
        # Create new user
        user = db.insert('users', {
            'email': email,
            'name': name,
            'oauth_provider': 'google'
        })
    
    # Create session
    session['user_id'] = user['id']
    session['email'] = email
    
    return redirect('/')  # Redirect to app

@app.route('/logout')
def logout():
    """Logout - clear session"""
    
    session.clear()
    return redirect('/')

# Benefits:
# ✅ User doesn't give password to app
# ✅ Google handles security
# ✅ Works across platforms
# ✅ Can revoke access in Google settings
```

---

## 💡 Mini Project: "Build Auth System"

### Phase 1: Basic JWT ⭐

**Requirements:**
- Login endpoint
- JWT token generation
- Token verification
- Token expiration

---

### Phase 2: Authorization ⭐⭐

**Requirements:**
- Role-based access
- Permission checking
- Authorization decorators
- Multi-role support

---

### Phase 3: OAuth Integration ⭐⭐⭐

**Requirements:**
- OAuth 2.0 setup
- Google/GitHub login
- SSO implementation
- Token refresh

---

## ⚖️ Authentication Methods Comparison

| Method | Security | Scalability | Complexity | Revocation |
|--------|----------|-----------|-----------|-----------|
| **Basic** | Very Low | Poor | Very Low | N/A |
| **Sessions** | Medium | Poor | Low | Instant |
| **JWT** | Good | Excellent | Low | Delayed |
| **OAuth** | Excellent | Excellent | High | Good |

---

## ❌ Common Mistakes

### Mistake 1: Storing Passwords in Plain Text

```python
# ❌ Plain text password
db.insert('users', {'email': 'alice@ex.com', 'password': 'secret123'})

# ✅ Hash password
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
db.insert('users', {'email': 'alice@ex.com', 'password_hash': password_hash})
```

### Mistake 2: Putting Secrets in JWT

```python
# ❌ JWT with secrets
jwt.encode({
    'user_id': 123,
    'password': 'secret123',  # NO!
    'api_key': 'secret_key'   # NO!
}, secret_key)

# ✅ JWT with public data only
jwt.encode({
    'user_id': 123,
    'role': 'admin',
    'exp': 1700000000
}, secret_key)
```

### Mistake 3: No Token Expiration

```python
# ❌ Token never expires
jwt.encode({'user_id': 123}, secret_key)
# Token valid forever!

# ✅ Token expires
jwt.encode({
    'user_id': 123,
    'exp': datetime.utcnow() + timedelta(hours=1)
}, secret_key)
```

---

## 📚 Additional Resources

**Standards:**
- [OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [JWT](https://tools.ietf.org/html/rfc7519)
- [OpenID Connect](https://openid.net/connect/)

**Libraries:**
- [AuthLib](https://authlib.org/)
- [PyJWT](https://pyjwt.readthedocs.io/)
- [Keycloak](https://www.keycloak.org/) (SSO)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Authentication vs authorization?**
   - Answer: Auth = who, Authz = what can do

2. **JWT benefits?**
   - Answer: Stateless, scalable, no database lookup

3. **Why use OAuth?**
   - Answer: User doesn't give password, provider handles security

4. **Token expiration importance?**
   - Answer: Limits damage if token compromised

5. **How to revoke JWT?**
   - Answer: Blacklist tokens or use short expiration

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **User:** "I forgot my password"
>
> **App:** "Resetting..."
>
> **Later:** "Your password reset link has expired"
>
> **User:** "It's only been 30 minutes!"
>
> **App:** "Yes, for security reasons"
>
> **User:** "This is insecure, I'm locked out!"
>
> **App:** "Welcome to security vs usability tradeoffs!" 🔐

---

[← Back to Main](../README.md) | [Previous: Chaos Engineering](40-chaos-engineering.md) |  [Next: Rate Limiting (Security)](42-rate-limiting-security.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (security)  
**Time to Read:** 27 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Authentication & Authorization: Making sure you are who you say you are, and can only do what you're allowed to.* 🚀