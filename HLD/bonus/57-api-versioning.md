# 57. API Versioning & Backward Compatibility

You ship an API. It's great. Then you need to add a feature. You add a required field. Now all old clients break. So you release v2 with the new field. Now you support two versions. Then v3 comes. And v4. Now you're supporting 10 versions, half the team is maintaining legacy code, and you still have clients using v1 from 2015. Welcome to API versioning hell! 🔥📱

[← Back to Main](../README.md) | [Next: Multi-Region Architecture →](58-multi-region-architecture.md)

---

## 🎯 Quick Summary

**API Versioning** manages changes to API contracts without breaking existing clients. **Backward compatibility** allows old clients to work with new versions. **Strategies:** path versioning (`/v1/users`), header versioning (`Accept-Version: 1`), query parameters. **Semantic versioning** (MAJOR.MINOR.PATCH) for communication. Netflix maintains 5+ API versions simultaneously. Twitter still supports v1.1 from 2012. **Challenge:** minimize versions while innovating, eventual deprecation. **Cost:** complexity, testing, documentation overhead.

Think of it as: **API Versioning = Social Contract with Clients**

---

## 🌟 Beginner Explanation

### Breaking vs Non-Breaking Changes

```
NON-BREAKING CHANGES (Safe, no version bump):

1. Add new optional field to request:
   Old: POST /users {"name": "Alice", "email": "alice@ex.com"}
   New: POST /users {"name": "Alice", "email": "alice@ex.com", "phone": null}
   ✓ Old clients ignore new field
   ✓ No version bump needed

2. Add new field to response:
   Old: GET /users/1 → {"id": 1, "name": "Alice"}
   New: GET /users/1 → {"id": 1, "name": "Alice", "phone": null}
   ✓ Old clients ignore extra field
   ✓ No version bump needed

3. Add new endpoint:
   Old: POST /users
   New: POST /users, POST /users/batch (new!)
   ✓ Old clients unaware
   ✓ No version bump needed

4. Add new optional query parameter:
   Old: GET /users?limit=10
   New: GET /users?limit=10&sort=name (optional)
   ✓ Old clients don't use sort
   ✓ No version bump needed

5. Extend enum (with default handling):
   Old: status ∈ {"active", "inactive"}
   New: status ∈ {"active", "inactive", "suspended"}
   ✓ If clients handle unknown values
   ✓ No version bump needed


BREAKING CHANGES (Requires version bump):

1. Remove field from response:
   Old: {"id": 1, "name": "Alice", "email": "alice@ex.com"}
   New: {"id": 1, "name": "Alice"} (removed email!)
   ❌ Old clients expect email
   ❌ REQUIRES NEW VERSION

2. Make optional field required:
   Old: POST /users {"name": "Alice", "email": null}
   New: POST /users {"name": "Alice", "email": "required!"}
   ❌ Old clients may not send email
   ❌ REQUIRES NEW VERSION

3. Change field type:
   Old: {"age": 30} (integer)
   New: {"age": "thirty"} (string!)
   ❌ Old clients expect integer
   ❌ REQUIRES NEW VERSION

4. Change semantic meaning:
   Old: {"price": 100} (in dollars)
   New: {"price": 100} (in cents!)
   ❌ Same field, different meaning
   ❌ REQUIRES NEW VERSION

5. Remove or rename endpoint:
   Old: GET /users/1
   New: GET /users/1 (removed!) or GET /people/1 (renamed!)
   ❌ Old clients expect /users/1
   ❌ REQUIRES NEW VERSION

6. Change HTTP method:
   Old: POST /users/1/delete
   New: DELETE /users/1
   ❌ Different method required
   ❌ REQUIRES NEW VERSION
```

### Versioning Strategies

```
STRATEGY 1: PATH VERSIONING (Most common)

URLs:
├─ /v1/users
├─ /v1/users/1
├─ /v2/users
├─ /v2/users/1
└─ All v1 endpoints in /v1 path

How to call:
├─ Old clients: GET /v1/users/1
├─ New clients: GET /v2/users/1
└─ Both work simultaneously!

Pros:
✅ Very explicit (obvious from URL)
✅ Easy routing (path-based)
✅ Easy caching (different URLs)
✅ Easy documentation (different docs per version)
✅ Easy to see which versions exist

Cons:
❌ URL duplication (same resource, multiple paths)
❌ Larger codebase (multiple implementations)
❌ Harder to deprecate (redirect old URLs?)

Examples:
├─ GitHub: /repos/:owner/:repo → always latest
├─ Stripe: /v1/charges (no v2, still v1!)
├─ AWS: /2010-05-08/ (date-based!)
└─ Most REST APIs use this


STRATEGY 2: HEADER VERSIONING

URLs:
├─ GET /users (always same!)
├─ GET /users/1
└─ Single endpoint, version in header

How to call:
├─ Old clients: GET /users with Accept-Version: 1
├─ New clients: GET /users with Accept-Version: 2
└─ Server: Checks header, routes to v1 or v2 handler

Pros:
✅ Single URL (RESTful, resource-oriented)
✅ Less URL duplication
✅ Cleaner codebase
✅ Follows REST philosophy (content negotiation)

Cons:
❌ Not obvious from URL (need docs)
❌ Harder to cache (same URL, different content)
❌ Harder to debug (must check headers)
❌ Client tooling must support headers

Examples:
├─ GitHub API v3: Accept: application/vnd.github.v3+json
├─ Twitter (deprecated): X-API-Version header
└─ Some enterprise APIs


STRATEGY 3: QUERY PARAMETER VERSIONING

URLs:
├─ /users?version=1
├─ /users?version=2
└─ Version as query param

How to call:
├─ Old clients: /users/1?version=1
├─ New clients: /users/1?version=2
└─ Server: Checks param, routes accordingly

Pros:
✅ Simple to implement
✅ Easy to default to latest
✅ Works in URLs (easy to share links)

Cons:
❌ Not standard (weird for REST)
❌ Can break caching (?)
❌ Less discoverable

Examples:
├─ Some legacy APIs
├─ Google APIs (sometimes)
└─ Not recommended for new APIs


STRATEGY 4: CONTENT-TYPE NEGOTIATION

Header:
Content-Type: application/vnd.example.v2+json

Server interprets:
├─ application/vnd.example.v1+json → v1 handler
├─ application/vnd.example.v2+json → v2 handler
└─ Custom MIME type encodes version

Pros:
✅ RESTful (proper content negotiation)
✅ Single URL

Cons:
❌ Complex for clients
❌ Uncommon

Examples:
├─ GitHub uses this
└─ Rarely used in practice


RECOMMENDATION:

Use PATH VERSIONING (/v1, /v2) because:
✅ Most explicit
✅ Easy for all clients (curl, browser, etc.)
✅ Industry standard
✅ Easy to deprecate (show warning on v1)
✅ Future-proof
```

### API Lifecycle Management

```
VERSION LIFECYCLE:

v1 Launch (Year 1):
├─ Status: Active (GA - General Availability)
├─ Support: Full
├─ Changes: Bug fixes only (no new features)
└─ Clients: New clients use v1

v2 Launch (Year 2):
├─ Status: Active
├─ Support: Full
├─ Changes: New features, improvements
├─ v1 Status: Active but deprecated
├─ Announce: "v1 deprecated, migrate to v2"
└─ Clients: Mix of v1 and v2

v1 Sunset (Year 3):
├─ Announced: "v1 sunset in 12 months"
├─ Date: Jan 1, Year 4
├─ Status: Maintenance mode
├─ Support: Bug fixes critical only
└─ Clients: Most moved to v2, some holdouts

v1 End-of-Life (Year 4):
├─ Date: Jan 1
├─ Status: Shut down
├─ API returns: 410 Gone (on /v1 requests)
├─ Clients: Must use v2
└─ Codebase: Remove v1 handler (cleanup!)

Timeline summary:
├─ v1 Launch: Year 1 (12 months active)
├─ v2 Launch: Year 2 (overlap period)
├─ Deprecation: Year 2 (public notice)
├─ Sunset: Year 3 (6 month warning)
├─ End-of-Life: Year 4
└─ Total support: 3 years


DEPRECATION COMMUNICATION:

Email:
"Dear API user,

v1 of our API will be sunset on Jan 1, 2026.
Please migrate to v2 by Dec 1, 2025.

Migration guide: docs.com/migrate-v1-to-v2
Help: support@company.com"

Headers (in API responses):
├─ Deprecation: true
├─ Sunset: Sun, 01 Jan 2026 00:00:00 GMT
├─ API-Warn: 299 - "v1 deprecated, migrate to v2"
└─ Link: <v2 docs URL>; rel="successor-version"

Dashboard:
├─ Show: "You're using deprecated v1"
├─ Alert: "Action required: Upgrade to v2"
├─ Link: "Migrate now" button
└─ Deadline: "Sunset: Jan 1, 2026"
```

---

## 🔬 Advanced Concepts

### Semantic Versioning for APIs

```
SEMVER: MAJOR.MINOR.PATCH

Example: 2.3.1

PATCH (2.3.0 → 2.3.1):
├─ Bug fixes only
├─ No new features
├─ No breaking changes
├─ Backward compatible
└─ Example: Fix typo, security patch

MINOR (2.2.0 → 2.3.0):
├─ New features
├─ New fields (optional)
├─ New endpoints
├─ Backward compatible
├─ No breaking changes
└─ Old clients still work

MAJOR (1.0.0 → 2.0.0):
├─ Breaking changes
├─ Removed fields
├─ Changed behavior
├─ Changed semantics
├─ Old clients break!
└─ Requires migration

How it applies to APIs:

External versioning (URL/header):
├─ Only MAJOR: /v1, /v2, /v3
├─ Never /v1.2, /v2.3
├─ Keep MAJOR stable, increment often
└─ Hide MINOR/PATCH internally

Internal versioning (response):
├─ Full SEMVER: api_version: "2.3.1"
├─ For documentation
├─ For debugging
└─ Never affects routing

Example:
API Version: /v2 (major)
Details: 2.3.1 (full semver)
├─ 2 = major breaking changes → /v2
├─ .3 = 3 minor features added (transparent)
├─ .1 = bug fix (transparent)
└─ Old /v1 clients unaware, /v2 clients get benefits
```

### Backward Compatibility Strategies

```
STRATEGY A: Additive Only (Preferred)

Rules:
├─ Never remove fields
├─ Never change field types
├─ Never change semantics
├─ Only add new optional fields
├─ Only add new endpoints
└─ Result: Can have ONE eternal version!

Example:
Year 1, v1:
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com"
}

Year 2 (add field):
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "phone": null  // NEW but optional
}

Year 3 (add endpoint):
GET /users/1/settings (NEW endpoint)

Result:
✅ Still /v1
✅ Old clients unaware of new field/endpoint
✅ New clients get more data
✅ No version bump!

Companies doing this:
├─ Stripe (still v1!)
├─ AWS (decades of additive changes)
└─ Goal: Never need v2


STRATEGY B: Adapter Pattern

When you MUST make breaking change:

Old behavior (v1):
├─ Request: POST /users {"name": "Alice", "age": "thirty"}
├─ Processing: String age
├─ Response: {"id": 1, "name": "Alice", "age": "thirty"}

New behavior (v2):
├─ Request: POST /users {"name": "Alice", "age": 30}
├─ Processing: Integer age
├─ Response: {"id": 1, "name": "Alice", "age": 30}

Solution: Adapter that handles both

def create_user_v1(request):
    # Adapter: Convert v1 format to internal format
    age = int(request['age'])  # Convert string to int
    return create_user_internal(request['name'], age)

def create_user_v2(request):
    # Direct: v2 format matches internal
    return create_user_internal(request['name'], request['age'])

Routes:
├─ POST /v1/users → create_user_v1 (adapter)
├─ POST /v2/users → create_user_v2 (direct)
└─ Both use same internal function

Cost: Small adapter layer per version


STRATEGY C: Deprecation Warnings

Soften breaking changes:

Year 1, v1:
├─ Endpoint: /users/1
├─ Works: 100%
└─ Status: Active

Year 2, deprecated:
├─ Endpoint: /users/1
├─ Works: 100% (still works!)
├─ Header: Deprecation: true
├─ Header: Sunset: Jan 1, 2024
└─ Status: Deprecated (but works)

Year 3, soft error:
├─ Endpoint: /users/1
├─ Status: 200 OK (still works!)
├─ Body: {"error": "v1 deprecated", "migrate_to": "/v2/users/1"}
└─ Status: Warn (works but complains)

Year 4, hard error:
├─ Endpoint: /users/1
├─ Status: 410 Gone
├─ Header: Sunset: Jan 1, 2023
└─ Status: Error (doesn't work)

Benefit: Gives clients time to migrate
```

### Contract Testing

```
PROBLEM: How to ensure backward compatibility?

Without testing:
├─ Modify API
├─ Deploy to production
├─ Old client breaks (oops!)
└─ Emergency rollback

SOLUTION: Automated contract testing

Contract definition (OpenAPI/AsyncAPI):
{
  "paths": {
    "/users/{id}": {
      "get": {
        "responses": {
          "200": {
            "schema": {
              "type": "object",
              "required": ["id", "name"],
              "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"}  // Can be absent
              }
            }
          }
        }
      }
    }
  }
}

Test 1: Response matches contract
├─ API returns: {"id": 1, "name": "Alice"}
├─ Validator: Check against schema
├─ Result: ✓ PASS (matches contract)

Test 2: New field is optional
├─ API returns: {"id": 1, "name": "Alice", "phone": null}
├─ Validator: Check against schema
├─ Result: ✓ PASS (extra field OK)

Test 3: Breaking change (field removed)
├─ API returns: {"id": 1} (removed name!)
├─ Validator: Check against schema
├─ Result: ✗ FAIL (required field missing!)
├─ Alert: Contract violation!
└─ Block: Deployment prevented!

CI/CD integration:
├─ Before merge: Run contract tests
├─ If fail: Block PR (prevent breaking changes)
├─ If pass: Safe to deploy
└─ Result: No surprises in production

Tools:
├─ Swagger/OpenAPI
├─ Postman Contract Tests
├─ Pact (consumer-driven contracts)
└─ Spring Cloud Contract
```

---

## 🐍 Python Code Example

### ❌ Without Versioning (Breaks Clients)

```python
# ===== WITHOUT VERSIONING =====

from flask import Flask, request, jsonify

app = Flask(__name__)

# Year 1: First API version
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user - no versioning"""
    
    user = db.query("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

# Year 2: Need to add phone field
# Problem: BREAKING change for old clients!
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user - NOW WITH PHONE"""
    
    user = db.query(
        "SELECT id, name, email, phone FROM users WHERE id = %s",
        (user_id,)
    )
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone  # NEW FIELD!
    })

# Issue:
# ❌ Old clients expect: {"id": 1, "name": "Alice", "email": "alice@ex.com"}
# ❌ New response: {"id": 1, "name": "Alice", "email": "alice@ex.com", "phone": "555-1234"}
# ❌ Clients break: Unexpected field causes parsing errors
# ❌ No way to rollback: Both old and new clients affected!
```

### ✅ With PATH Versioning (Safe)

```python
# ===== WITH PATH VERSIONING =====

from flask import Flask, request, jsonify

app = Flask(__name__)

# V1 Endpoints (backward compatible)
@app.route('/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    """Get user - v1 (no phone)"""
    
    user = db.query(
        "SELECT id, name, email FROM users WHERE id = %s",
        (user_id,)
    )
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

# V2 Endpoints (with new features)
@app.route('/v2/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    """Get user - v2 (with phone)"""
    
    user = db.query(
        "SELECT id, name, email, phone FROM users WHERE id = %s",
        (user_id,)
    )
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone  # NEW in v2
    })

# Both endpoints coexist:
# ✅ Old clients: GET /v1/users/1 → Still works!
# ✅ New clients: GET /v2/users/1 → Get phone field
# ✅ No breaking changes!

# Benefits:
# ✅ Old clients unaffected
# ✅ New clients get new features
# ✅ Clear separation
# ✅ Easy deprecation (sunset /v1 later)
```

### ✅ Production API Versioning

```python
# ===== PRODUCTION API VERSIONING =====

from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Version metadata
API_VERSIONS = {
    'v1': {
        'launched': '2023-01-01',
        'status': 'deprecated',
        'sunset': '2025-12-31',
        'successor': 'v2'
    },
    'v2': {
        'launched': '2024-01-01',
        'status': 'active',
        'sunset': None,
        'successor': None
    }
}

def add_version_headers(version):
    """Decorator to add version headers"""
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = jsonify(f(*args, **kwargs))
            
            # Add version info
            version_info = API_VERSIONS.get(version, {})
            response.headers['API-Version'] = version
            response.headers['API-Status'] = version_info.get('status', 'unknown')
            
            if version_info.get('status') == 'deprecated':
                response.headers['Deprecation'] = 'true'
                response.headers['Sunset'] = version_info.get('sunset')
                successor = version_info.get('successor')
                if successor:
                    response.headers['API-Warn'] = f'299 - "Use {successor} instead"'
            
            return response
        
        return wrapped
    
    return decorator

# V1 API (Deprecated)
@app.route('/v1/users/<int:user_id>', methods=['GET'])
@add_version_headers('v1')
def get_user_v1(user_id):
    """Get user - v1 (deprecated)"""
    
    user = {
        'id': user_id,
        'name': 'Alice',
        'email': 'alice@example.com'
    }
    
    return user

# V2 API (Active)
@app.route('/v2/users/<int:user_id>', methods=['GET'])
@add_version_headers('v2')
def get_user_v2(user_id):
    """Get user - v2 (current)"""
    
    user = {
        'id': user_id,
        'name': 'Alice',
        'email': 'alice@example.com',
        'phone': '555-1234',  # NEW in v2
        'created_at': '2024-01-01T00:00:00Z'  # NEW in v2
    }
    
    return user

# Contract validation
from jsonschema import validate

V1_SCHEMA = {
    'type': 'object',
    'required': ['id', 'name', 'email'],
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'email': {'type': 'string'}
    },
    'additionalProperties': False  # No extra fields!
}

V2_SCHEMA = {
    'type': 'object',
    'required': ['id', 'name', 'email'],
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'email': {'type': 'string'},
        'phone': {'type': 'string'},
        'created_at': {'type': 'string'}
    },
    'additionalProperties': False
}

def validate_response(schema):
    """Decorator to validate API response"""
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            validate(instance=result, schema=schema)
            return result
        
        return wrapped
    
    return decorator

# Apply validation
@app.route('/v1/users/<int:user_id>', methods=['GET'])
@validate_response(V1_SCHEMA)
@add_version_headers('v1')
def get_user_v1(user_id):
    return {'id': user_id, 'name': 'Alice', 'email': 'alice@example.com'}

# Testing contract compliance
import pytest

def test_v1_contract():
    """Test v1 response matches contract"""
    response = client.get('/v1/users/1')
    assert response.status_code == 200
    validate(instance=response.json, schema=V1_SCHEMA)

def test_v2_contract():
    """Test v2 response matches contract"""
    response = client.get('/v2/users/1')
    assert response.status_code == 200
    validate(instance=response.json, schema=V2_SCHEMA)

def test_no_breaking_changes():
    """Test v2 doesn't break v1 contract"""
    # If v2 removes a required field, this fails
    response = client.get('/v2/users/1')
    # Modified schema: still has id, name, email
    modified_schema = V1_SCHEMA.copy()
    modified_schema['additionalProperties'] = True  # Allow extra fields
    validate(instance=response.json, schema=modified_schema)

# Benefits:
# ✅ Version information clear
# ✅ Deprecation communicated
# ✅ Contract validation automatic
# ✅ Breaking changes caught in tests
# ✅ Safe deployment
```

---

## 💡 Design Decisions

### When to Version?

```
BREAK GLASS ONLY:

Use new version ONLY when:
├─ Removing field required by clients
├─ Changing field type
├─ Changing semantic meaning
├─ Renaming endpoints
├─ Changing HTTP method
└─ Result: Old clients cannot work

Otherwise:
✓ Add optional fields (no version)
✓ Add new endpoints (no version)
✓ Extend enums (no version)
✓ Make optional better (no version)
└─ Stay on same version!

Goal:
├─ Minimize versions
├─ Keep one stable version as long as possible
├─ Netflix strategy: Additive changes forever
└─ Stripe: Still v1 after 10 years
```

### How Many Versions to Support?

```
Support window:

Company policy:
├─ Support: 2 major versions
├─ Example: If current is v3
│  ├─ v3: Active (full support)
│  ├─ v2: Maintenance (bug fixes only)
│  ├─ v1: Unsupported (will sunset)
│  └─ v0: Removed
└─ Rationale: Balance support vs simplicity


Timeline:
├─ Year 1: v1 launches (active)
├─ Year 2: v2 launches (v1 → maintenance)
├─ Year 3: v3 launches (v1 → sunset notice)
├─ Year 4: v1 removed (v2 → maintenance)
├─ Result: Always 2 live versions


Cost analysis:
├─ Versions to support: N
├─ Engineers: 1 per version (minimum)
├─ Testing: Exponential (test all combos)
├─ Documentation: 2x
├─ Support: More questions
└─ Budget: ~2x per additional version


Recommendation:
- Keep 2-3 versions maximum
- Migrate clients aggressively
- Sunset old versions on schedule
- Don't let clients drag you down
```

---

## ❌ Common Mistakes

### Mistake 1: Too Many Versions

```python
# ❌ Support 10 versions (nightmare!)
routes = [
    ('/v1/users', get_users_v1),
    ('/v2/users', get_users_v2),
    ('/v3/users', get_users_v3),
    # ... v4, v5, v6, v7, v8, v9, v10
]
# Maintenance burden: Huge!
# Testing: Exponential!
# Bugs: In every version!

# ✅ Support 2 versions maximum
routes = [
    ('/v2/users', get_users_v2),  # Current
    ('/v1/users', get_users_v1),  # Legacy (sunset in 6 months)
]
# Maintenance: Manageable
# Testing: 2x
# Plan: v1 → /v3 migration
```

### Mistake 2: Unclear Deprecation

```python
# ❌ Silent removal
# Old endpoint just stops working
# No warning, no migration guide
# Clients break randomly

# ✅ Clear deprecation
headers = {
    'Deprecation': 'true',
    'Sunset': 'Sun, 01 Jan 2026 00:00:00 GMT',
    'API-Warn': '299 - "Use v2 instead"',
    'Link': '<docs/migrate>; rel="documentation"'
}
# Email: Sent 6 months before sunset
# Dashboard: Shows deprecation warning
# Docs: Migration guide provided
# Result: No surprises
```

### Mistake 3: Breaking Changes in Patch

```python
# ❌ Breaking change in "patch" version
# Version: v1.2.1 → v1.2.2
# Change: Removed optional field (!)
# Clients: May break

# ✅ Patch = bug fixes ONLY
# Patch versions should NEVER break
# Minor = new optional features
# Major = breaking changes
# Semantic versioning: Means something!
```

---

## 📚 Additional Resources

**API Versioning:**
- [Semantic Versioning](https://semver.org/)
- [REST API Versioning Best Practices](https://restfulapi.net/versioning/)
- [GitHub API Versioning](https://docs.github.com/en/rest/overview/api-versions)

**Contract Testing:**
- [Pact - Consumer Driven Contracts](https://pact.foundation/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [AsyncAPI Specification](https://www.asyncapi.com/)

**Deprecation:**
- [HTTP Deprecation Header (RFC 8594)](https://datatracker.ietf.org/doc/html/draft-dalal-deprecation-header)
- [Sunset Header](https://datatracker.ietf.org/doc/html/draft-wilde-sunset-header)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **Breaking vs non-breaking change?**
   - Answer: Breaking = old clients fail; non-breaking = they still work

2. **Best versioning strategy?**
   - Answer: Path versioning (/v1, /v2) - most explicit

3. **When to introduce new version?**
   - Answer: Only when making breaking changes

4. **How to minimize versions?**
   - Answer: Additive changes only (add, don't remove)

5. **How to communicate deprecation?**
   - Answer: Headers, email, dashboard, runbooks

**If you got these right, you're ready for multi-region!** ✅

---

## 🤣 Closing Thoughts

> **Year 1:** "We'll keep v1 forever, just add features!"
>
> **Year 3:** "We need v2 for the new UI"
>
> **Year 4:** "v2 is slow, let's make v3"
>
> **Year 5:** "Why are we supporting 5 versions??"
>
> **Year 6:** "We have 10 versions now... 😭"
>
> **Engineer:** "I should have read the API versioning guide" 📚

---

[← Back to Main](../README.md) | [Next: Multi-Region Architecture →](58-multi-region-architecture.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (API design)  
**Time to Read:** 28 minutes  
**Time to Implement:** 10-20 hours per version

---

*API Versioning: The art of changing everything while breaking nothing.* 🚀