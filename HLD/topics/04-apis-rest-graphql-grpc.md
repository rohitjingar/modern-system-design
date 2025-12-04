# 04. APIs (REST, GraphQL, gRPC)

APIs are like restaurant menus: REST gives you the whole dish even if you only want the sauce, GraphQL lets you order exactly what you want, and gRPC shows up at your door in 10ms with everything perfectly organized. 🍽️

[← Back to Main](../README.md) | [Previous: IP, DNS, and HTTP Basics](03-ip-dns-http-basics.md) | [Next: JSON vs Protobuf →](05-json-vs-protobuf.md)

---

## 🎯 Quick Summary

**APIs (Application Programming Interfaces)** let programs talk to each other. REST, GraphQL, and gRPC are three different ways to design APIs. REST is simple and everywhere, GraphQL is flexible and efficient, and gRPC is blazingly fast. Each has trade-offs.

Think of it as: **REST = Full Menu, GraphQL = Custom Order, gRPC = Express Delivery**

---

## 🌟 Beginner Explanation

### What Even Is an API?

Imagine you're at a restaurant:

```
RESTAURANT ANALOGY

Without API (chaos):
- You walk into the kitchen
- You try to cook your own food
- You mess everything up
- Food is ruined 😱

With API (organized):
- You stay at the table (client)
- You order from the menu (API)
- Kitchen prepares food (server)
- You get exactly what you want ✅
```

**An API is a contract between client and server:**

```
Client: "I need user data for user_id=123"
Server: "Sure! Here's the API endpoint to call"
Client: "OK, calling GET /users/123"
Server: "Here's the response: {id: 123, name: 'Alice'...}"
```

### The Three API Styles

#### 1. **REST (Representational State Transfer)** - The Traditional One

```
RESTAURANT ANALOGY

Menu is printed (fixed options)
├─ Burger with fries + drink
├─ Pizza with salad + drink
├─ Pasta with bread + drink

You order: "I want burger with fries and drink"
You get: Burger + fries + drink (even though you only want burger)
```

**REST API Example:**

```
GET    /users           → Get all users
GET    /users/123       → Get user 123
POST   /users           → Create new user
PUT    /users/123       → Replace user 123
DELETE /users/123       → Delete user 123
```

**Problems with REST:**
```
GET /users/123
Response: {
  id: 123,
  name: 'Alice',
  email: 'alice@example.com',
  age: 28,
  address: '123 Main St',
  phone: '555-1234',
  ... 50 more fields
}

You only wanted the name and email!
You got 50 extra fields you didn't need.
```

#### 2. **GraphQL (Graph Query Language)** - The Flexible One

```
RESTAURANT ANALOGY

Menu is interactive:
You say: "I want burger, but only the patty and bun"
You get: Just burger patty and bun (no fries, no drink)

You say: "I want pizza with salad and drink but no cheese on pizza"
You get: Exactly that
```

**GraphQL Query:**

```graphql
query GetUser {
  user(id: 123) {
    name
    email
  }
}
```

**Response:**
```json
{
  "user": {
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

You only get what you asked for! ✅

#### 3. **gRPC (Google Remote Procedure Call)** - The Fast One

```
RESTAURANT ANALOGY

You call restaurant before going
Restaurant has everything pre-prepared
You show up, get your food in 5 seconds
You leave

No waiting, super fast.
```

**gRPC Features:**
- Binary protocol (faster than text)
- HTTP/2 (multiple requests at once)
- Streaming (continuous data flow)
- Super fast (microseconds instead of milliseconds)

---

## 🔬 Advanced Explanation

### REST Deep Dive

**REST Principles:**

```
1. CLIENT-SERVER (separation of concerns)
   Client handles UI
   Server handles data/business logic

2. STATELESS (no server memory)
   Every request includes all needed info
   Server doesn't remember previous requests

3. CACHEABLE (responses can be cached)
   GET requests can be cached
   POST/PUT/DELETE typically not cached

4. UNIFORM INTERFACE (standard methods)
   GET, POST, PUT, DELETE, PATCH
   Same for all resources

5. LAYERED (can have intermediaries)
   Request might go through: Client → CDN → Load Balancer → Server
   Each layer doesn't need to know about others
```

**REST Request/Response:**

```
REQUEST:
GET /api/users/123 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer token123

RESPONSE:
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600

{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "age": 28,
  "address": "123 Main St",
  "phone": "555-1234",
  "company": "Google",
  "avatar_url": "...",
  ... 20 more fields
}
```

**REST Advantages:**
- ✅ Simple to understand
- ✅ Easy to cache (HTTP cache)
- ✅ Works with standard HTTP tools
- ✅ Stateless (easy to scale)

**REST Disadvantages:**
- ❌ Over-fetching (get too much data)
- ❌ Under-fetching (need multiple requests)
- ❌ No versioning standard (GET /v1/users vs /v2/users)

---

### GraphQL Deep Dive

**How GraphQL Works:**

```
STEP 1: Client sends query (tells server exactly what it needs)
query GetUserWithPosts {
  user(id: 123) {
    name
    email
    posts(limit: 5) {
      title
      likes
    }
  }
}

STEP 2: Server resolves query (fetches only requested data)
SELECT name, email FROM users WHERE id = 123
SELECT title, likes FROM posts WHERE user_id = 123 LIMIT 5

STEP 3: Server returns exact response
{
  "user": {
    "name": "Alice",
    "email": "alice@example.com",
    "posts": [
      {"title": "GraphQL is awesome", "likes": 42},
      {"title": "System Design rocks", "likes": 128}
    ]
  }
}

EXACTLY what was requested. No extra fields! ✅
```

**GraphQL Schema (Contract):**

```graphql
type Query {
  user(id: Int!): User
  users(limit: Int): [User]
  post(id: Int!): Post
}

type User {
  id: Int!
  name: String!
  email: String!
  age: Int
  posts: [Post]
}

type Post {
  id: Int!
  title: String!
  content: String!
  likes: Int!
  author: User!
}
```

**GraphQL Advantages:**
- ✅ Exactly what you ask for (no over/under-fetching)
- ✅ Single request gets all related data
- ✅ Type-safe (schema defines all fields)
- ✅ Real-time subscriptions (streaming data)
- ✅ Easy versioning (add new fields, old queries still work)

**GraphQL Disadvantages:**
- ❌ Hard to cache (most queries are POST)
- ❌ Steep learning curve
- ❌ Can be expensive (complex queries = heavy processing)
- ❌ File uploads more complicated
- ❌ Learning curve for developers

---

### gRPC Deep Dive

**How gRPC Works:**

```
1. DEFINE SERVICE (Protocol Buffers)
service UserService {
  rpc GetUser(UserRequest) returns (UserResponse);
  rpc ListUsers(ListRequest) returns (stream UserResponse);
}

2. COMPILE (generates client/server code)
protoc --go_out=. *.proto
← Generates Go code for client & server

3. IMPLEMENT SERVER
func (s *Server) GetUser(ctx context.Context, req *UserRequest) (*UserResponse, error) {
  user := db.GetUser(req.Id)
  return &UserResponse{User: user}, nil
}

4. CALL FROM CLIENT
client.GetUser(ctx, &UserRequest{Id: 123})
← Direct function call (feels like local code)

Result: Response in microseconds ⚡
```

**gRPC vs REST Comparison:**

```
REST:
Client: POST /api/users/123 HTTP/1.1
Server: Parses HTTP, JSON, generates response
Response: JSON string (text, large size)
Speed: 50-200ms

gRPC:
Client: Binary message (compact)
Server: Directly calls function (no parsing)
Response: Binary message (compressed)
Speed: 1-10ms ⚡ (10-20x faster!)

BANDWIDTH:
REST: Same query 10,000 times = 10,000 × 5KB = 50MB
gRPC: Same query 10,000 times = 10,000 × 0.5KB = 5MB (10x less!)
```

**gRPC Advantages:**
- ✅ Super fast (binary, no parsing)
- ✅ Uses HTTP/2 (multiplexing)
- ✅ Streaming (bidirectional)
- ✅ Type-safe (Protocol Buffers)
- ✅ Works on microservices

**gRPC Disadvantages:**
- ❌ Hard to debug (binary format)
- ❌ Doesn't work well with browsers (needs special proxy)
- ❌ Steeper learning curve
- ❌ Overkill for simple APIs
- ❌ Less caching support

---

## 🐍 Python Code Example

### REST API (Flask)

```python
# ===== ❌ SIMPLE REST API (Problems) =====
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 28},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 32},
}

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """REST endpoint - returns ALL user data"""
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    
    # Problem 1: Over-fetching (client only wants name, but gets all fields)
    return jsonify(user)

@app.route('/api/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """Separate endpoint for user's posts"""
    # Problem 2: Under-fetching (need multiple requests)
    # Client has to call:
    # 1. GET /api/users/1 → get user info
    # 2. GET /api/users/1/posts → get posts
    # 3. GET /api/posts/1/comments → get comments
    # Total: 3 requests!
    
    posts = [
        {"id": 101, "title": "GraphQL is awesome", "likes": 42},
        {"id": 102, "title": "System Design rocks", "likes": 128},
    ]
    return jsonify(posts)

if __name__ == '__main__':
    app.run()

# Problems:
# ❌ Client gets all user fields (waste of bandwidth)
# ❌ Need multiple requests to get related data
# ❌ No versioning (hard to add new fields)
```

### ✅ GraphQL API (Flask-GraphQL)

```python
# ===== ✅ GRAPHQL API (Flexible) =====
import graphene
from graphene import Schema, ObjectType, String, Int, List, Field

# Define types
class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    email = graphene.String()
    age = graphene.Int()
    posts = graphene.List(lambda: PostType)

class PostType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()
    likes = graphene.Int()
    author = Field(UserType)

# Define queries
class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    users = graphene.List(UserType, limit=graphene.Int(default_value=10))
    
    def resolve_user(self, info, id):
        """Fetch single user"""
        return {
            "id": id,
            "name": "Alice",
            "email": "alice@example.com",
            "age": 28,
            "posts": [
                {"id": 101, "title": "GraphQL is awesome", "likes": 42},
                {"id": 102, "title": "System Design rocks", "likes": 128},
            ]
        }
    
    def resolve_users(self, info, limit):
        """Fetch all users"""
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ][:limit]

# Create schema
schema = Schema(query=Query)

# Usage: Client can ask for exactly what it needs
query = """
{
  user(id: 1) {
    name
    email
    posts {
      title
      likes
    }
  }
}
"""

result = schema.execute(query)
print(result.data)
# Output: {'user': {'name': 'Alice', 'email': 'alice@example.com', 'posts': [...]}}

# Benefits:
# ✅ Client gets only requested fields
# ✅ Single request gets user + posts
# ✅ Type-safe
# ✅ No over-fetching or under-fetching
```

### ✅ gRPC API (Protocol Buffers + gRPC)

```python
# ===== ✅ GRPC API (Fast) =====

# 1. DEFINE SERVICE (user.proto)
"""
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc ListUsers (Empty) returns (stream UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  int32 age = 4;
}

message Empty {}
"""

# 2. COMPILE (generates Python code)
# protoc -I=. --python_out=. --grpc_python_out=. user.proto
# Generates: user_pb2.py, user_pb2_grpc.py

# 3. IMPLEMENT SERVER
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        """Get single user"""
        if request.id == 1:
            return user_pb2.UserResponse(
                id=1,
                name="Alice",
                email="alice@example.com",
                age=28
            )
        
        # User not found
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return user_pb2.UserResponse()
    
    def ListUsers(self, request, context):
        """Stream all users"""
        users = [
            user_pb2.UserResponse(id=1, name="Alice", email="alice@example.com", age=28),
            user_pb2.UserResponse(id=2, name="Bob", email="bob@example.com", age=32),
            user_pb2.UserResponse(id=3, name="Charlie", email="charlie@example.com", age=25),
        ]
        
        for user in users:
            yield user  # Stream each user

def start_server():
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(),
        server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    start_server()

# 4. USE FROM CLIENT
import grpc
import user_pb2
import user_pb2_grpc

def get_user(user_id):
    """Call gRPC service"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UserServiceStub(channel)
    
    request = user_pb2.UserRequest(id=user_id)
    response = stub.GetUser(request)  # Direct function call!
    
    print(f"User: {response.name} ({response.email})")
    channel.close()

def list_users():
    """Stream users from server"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UserServiceStub(channel)
    
    request = user_pb2.Empty()
    responses = stub.ListUsers(request)  # Stream!
    
    for user in responses:
        print(f"- {user.name}")
    
    channel.close()

# Usage
get_user(1)
# Output: User: Alice (alice@example.com)
# Speed: ~1-5ms ⚡

list_users()
# Output:
# - Alice
# - Bob
# - Charlie

# Benefits:
# ✅ Super fast (binary protocol)
# ✅ Type-safe (Protocol Buffers)
# ✅ Streaming support
# ✅ HTTP/2 multiplexing
# ✅ Generates client/server code
```

---

## 💡 Mini Project: "Build a Flexible User API"

### Phase 1: Simple REST API ⭐

**Requirements:**
- Get user by ID
- Get all users
- Create user
- Use Flask

**Code:**
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "Not found"}), 404

@app.route('/users', methods=['GET'])
def get_all_users():
    return jsonify(list(users.values()))

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_id = max(users.keys()) + 1
    users[new_id] = {"id": new_id, "name": data['name'], "email": data['email']}
    return jsonify(users[new_id]), 201

if __name__ == '__main__':
    app.run(port=5000)
```

**Limitations:**
- ❌ No field selection (over-fetching)
- ❌ No pagination
- ❌ Hard to add new fields

---

### Phase 2: Intermediate (GraphQL + REST) ⭐⭐

**Requirements:**
- REST endpoint (for compatibility)
- GraphQL endpoint (for flexibility)
- Multiple queries (user, posts, comments)

**Code:**
```python
from flask import Flask
from flask_graphql import GraphQLView
import graphene

app = Flask(__name__)

# GraphQL schema
class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    email = graphene.String()

class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    users = graphene.List(UserType)
    
    def resolve_user(self, info, id):
        return {"id": id, "name": "Alice", "email": "alice@example.com"}
    
    def resolve_users(self, info):
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]

schema = graphene.Schema(query=Query)

# GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == '__main__':
    app.run(port=5000)

# Now clients can:
# REST: GET /api/users/1 → Full user object
# GraphQL: POST /graphql → Send query, get only what they ask for
```

**Improvements:**
- ✅ Flexibility (clients choose fields)
- ✅ Backward compatibility (REST still works)
- ✅ Single request for related data

---

### Phase 3: Enterprise (gRPC + Load Balancing) ⭐⭐⭐

**Requirements:**
- High-performance gRPC API
- Multiple gRPC servers
- Load balancer
- Streaming support

**Architecture:**
```
CLIENT APPLICATIONS
├─ Web (uses REST for browsers)
├─ Mobile (uses gRPC for speed)
└─ Backend (uses gRPC for inter-service)

↓
LOAD BALANCER (round-robin)
├─ gRPC Server 1 (port 50051)
├─ gRPC Server 2 (port 50052)
└─ gRPC Server 3 (port 50053)

↓
SHARED DATABASE (PostgreSQL)
```

**Features:**
```python
# 1. gRPC service definition
"""
service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc ListUsers (Empty) returns (stream UserResponse);
  rpc UpdateUser (UpdateRequest) returns (UserResponse);
  rpc WatchUser (UserRequest) returns (stream UserUpdate);
}
"""

# 2. Streaming results
def ListUsers(self, request, context):
    """Stream 10M users efficiently"""
    for batch in db.query_in_batches():
        for user in batch:
            yield user  # Stream each user

# 3. Bidirectional streaming
def WatchUser(self, request, context):
    """Real-time user updates"""
    user_id = request.id
    for update in subscribe_to_changes(user_id):
        yield update

# 4. Load balancing
import grpc
from grpc.health.v1 import health_pb2

# Server registers health checks
register_health_check(server)

# Client uses load balancing
options = [
    ('grpc.lb_policy_name', 'round_robin'),
]
channel = grpc.secure_channel(
    'user-service.prod.example.com:50051',
    credentials,
    options=options
)
```

**Capabilities:**
- ✅ 100,000+ QPS per server
- ✅ Real-time streaming
- ✅ Automatic load balancing
- ✅ Health checks & failover
- ✅ Enterprise-grade reliability

---

## ⚖️ REST vs GraphQL vs gRPC

| Feature | REST | GraphQL | gRPC |
|---------|------|---------|------|
| **Speed** | 50-200ms | 50-150ms | 1-10ms ⚡ |
| **Ease** | ✅ Easy | 🟡 Medium | ❌ Hard |
| **Bandwidth** | High | Medium | Very Low ⚡ |
| **Caching** | ✅ Excellent | ❌ Hard | 🟡 Medium |
| **Browser Support** | ✅ Yes | ✅ Yes | ❌ No (needs proxy) |
| **Streaming** | ❌ No | ✅ Yes | ✅ Yes |
| **Over-fetching** | ❌ Common | ✅ No | ✅ No |
| **Under-fetching** | ❌ Common | ✅ No | ✅ No |
| **Use Case** | Public APIs | Flexible APIs | Microservices |

---

## 🎯 When to Use Each

### Use REST When:
```
✅ Simple CRUD operations
✅ Public API (easy to understand)
✅ Need good HTTP caching
✅ Browser clients only
✅ Quick prototype
✅ Mobile apps (simple calls)
```

### Use GraphQL When:
```
✅ Complex, flexible queries
✅ Multiple client types (web, mobile, desktop)
✅ Reduce over-fetching
✅ Reduce under-fetching
✅ Need type system
✅ Real-time subscriptions
✅ Multiple consumers with different needs
```

### Use gRPC When:
```
✅ Microservices communication
✅ High-performance requirements
✅ Large data transfers
✅ Real-time streaming
✅ Mobile apps (want speed)
✅ Internal services (don't need browser)
✅ Bandwidth-constrained (IoT, satellite)
```

---

## 🔐 API Security

```python
# 1. AUTHENTICATION (prove who you are)
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return {"error": "Unauthorized"}, 401
    
    return jsonify(get_user_data(user_id))

# 2. AUTHORIZATION (prove you have permission)
def get_user(user_id):
    current_user = get_current_user()
    target_user = get_user_data(user_id)
    
    if current_user.id != target_user.id and not current_user.is_admin:
        return {"error": "Forbidden"}, 403
    
    return jsonify(target_user)

# 3. RATE LIMITING (prevent abuse)
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/users')
@limiter.limit("100 per hour")
def get_users():
    return jsonify(list_users())

# 4. HTTPS (encrypt traffic)
# Always use HTTPS in production!
# Never send API keys/tokens over HTTP

# 5. INPUT VALIDATION (prevent injection)
def create_user():
    data = request.json
    
    # Validate email format
    if not is_valid_email(data['email']):
        return {"error": "Invalid email"}, 400
    
    # Validate name length
    if len(data['name']) > 100:
        return {"error": "Name too long"}, 400
    
    return create_new_user(data)
```

---

## ❌ Common Mistakes

### Mistake 1: Building One API For Everyone

```python
# ❌ Bad: Force all clients to use same API
# Web needs: id, name, email
# Mobile needs: id, name (want to save bandwidth)
# Both must fetch: id, name, email, age, address, phone, company...
# (waste for mobile)

# ✅ Good: Offer multiple endpoints
# REST: /users/1 (for browsers)
# GraphQL: /graphql (for smart clients)
# gRPC: :50051 (for services)
# Mobile can choose what's best
```

### Mistake 2: No Versioning

```python
# ❌ Bad: Break existing clients when you change API
# Version 1: GET /users/1 → returns {id, name}
# Version 2: GET /users/1 → returns {id, name, email} (old clients confused!)

# ✅ Good: Version your APIs
# GET /v1/users/1 → returns {id, name}
# GET /v2/users/1 → returns {id, name, email}
# Old clients keep using /v1, new clients use /v2
```

### Mistake 3: Slow GraphQL Queries

```python
# ❌ Bad: N+1 query problem
query {
  users {           # Gets 100 users
    id
    name
    posts {         # For EACH user, query their posts (100 queries!)
      title         # Total: 1 + 100 = 101 queries 😱
    }
  }
}

# ✅ Good: Use dataloaders
# Fetch all user IDs first
# Then fetch ALL posts for those IDs in ONE query
# Total: 1 + 1 = 2 queries ✅
```

### Mistake 4: Exposing Internal Complexity

```python
# ❌ Bad: API exposes implementation details
GET /api/search?query=python&index=user_idx_v2&cache_key=abc123

# Clients now depend on index names, cache keys, etc.
# When you change internals, you break clients

# ✅ Good: Hide implementation
GET /api/search?query=python

# Client doesn't know/care about indexes or cache
# You can change internals without breaking API
```

---

## 📚 Additional Resources

**API Design:**
- [REST API Best Practices](https://restfulapi.net/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [gRPC Best Practices](https://grpc.io/docs/guides/performance-best-practices/)

**Tools:**
- **REST:** Postman, Insomnia, curl
- **GraphQL:** GraphiQL, Apollo Studio, GraphQL Playground
- **gRPC:** grpcurl, gRPC UI

**Security:**
- API Keys: Hard to invalidate, risky if exposed
- OAuth 2.0: Industry standard, use this
- JWT: Stateless tokens, good for microservices
- mTLS: Certificate-based, for service-to-service


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What does REST stand for and what are its main methods?**
   - Answer: Representational State Transfer; GET, POST, PUT, DELETE

2. **What's the main advantage of GraphQL over REST?**
   - Answer: Get exactly what you ask for (no over/under-fetching)

3. **Why is gRPC faster than REST?**
   - Answer: Binary protocol, HTTP/2, no parsing needed

4. **When should you use GraphQL vs gRPC?**
   - Answer: GraphQL for flexible queries; gRPC for speed

5. **What's the N+1 query problem in GraphQL?**
   - Answer: Querying once for parents, then once for each child (expensive)

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Backend Developer:** "I built a REST API, a GraphQL endpoint, and a gRPC service."
>
> **Product Manager:** "Do we need all three?"
>
> **Backend Developer:** "No."
>
> **Product Manager:** "Then why did you build all three?"
>
> **Backend Developer:** "Because someone will eventually ask for it." 😅

---

[← Back to Main](../README.md) | [Previous: IP, DNS, and HTTP Basics](03-ip-dns-http-basics.md) | [Next: JSON vs Protobuf →](05-json-vs-protobuf.md)

---

**Last Updated:** November 10, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate (requires some backend knowledge)  
**Time to Read:** 25 minutes  
**Time to Build User APIs:** 3-5 hours per phase  

---

*Making APIs simple: REST for everyone, GraphQL for flexibility, gRPC for speed.* 🚀