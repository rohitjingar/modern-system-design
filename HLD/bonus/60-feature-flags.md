# 60. Feature Flags & Config Management

You deploy a feature with a bug. It breaks production. You have two choices: rollback (lose 2 hours of work) or fix-and-redeploy (risk more bugs). With feature flags, you just flip a switch: OFF. Bug gone. Meanwhile, you fix it. Flip switch: ON. Feature back. No deployment, no downtime, no panic at 3 AM. Netflix uses thousands of feature flags. Stripe uses them for gradual rollouts. Google uses them for A/B testing. The only downside? Now you have thousands of flags to manage. Welcome to feature flag entropy! 🚩✨

[← Back to Main](../README.md) | [Previous: Event Sourcing](59-event-sourcing.md) | [Next: Data Consistency Patterns →](61-data-consistency-patterns.md)

---

## 🎯 Quick Summary

**Feature Flags** toggle features ON/OFF without redeploying. **Config Management** centralizes settings (database URLs, API keys, thresholds). **Benefits:** instant rollback, gradual rollouts, A/B testing, canary deployments. Netflix has 10,000+ flags in production. Stripe uses flags for everything. Google uses for feature experiments. **Challenges:** flag sprawl (too many flags), tech debt (old flags), stale flags (forgotten), consistency (across regions). Trade-off: deployment flexibility vs complexity.

Think of it as: **Feature Flags = Kill Switch for Any Feature**

---

## 🌟 Beginner Explanation

### Feature Flags vs Code Deployment

```
TRADITIONAL DEPLOYMENT:

Release cycle:
├─ Develop feature (1 week)
├─ Test in staging (2 days)
├─ Code review (1 day)
├─ Deploy to production (1 hour)
├─ Feature live immediately
└─ Bug found after deployment?
   ├─ Option 1: Rollback (lose 2 hours work)
   ├─ Option 2: Hotfix (risky, may break more)
   └─ Result: Panic!

Timeline:
├─ Monday: Feature complete
├─ Tuesday: Testing
├─ Wednesday: Review
├─ Thursday 2 PM: Deploy
├─ Thursday 3 PM: Bug found
├─ Thursday 5 PM: Rolled back
└─ Loss: 2 hours of work, reputation damage


FEATURE FLAGS:

Deploy with flag OFF:
├─ Thursday 2 PM: Deploy (feature OFF)
├─ Feature code: In production but disabled
├─ Users: See nothing (flag is OFF)
├─ Developers: Can still test (toggle flag locally)
├─ Thursday 3 PM: Bug found
├─ Action: Flip flag OFF (already OFF!)
├─ Impact: Zero (nobody affected)
└─ Thursday 6 PM: Fix committed

Enable for testing:
├─ Friday: Enable flag for 1% users
├─ Monitor: No errors in 1% cohort
├─ Saturday: Enable for 10% users
├─ Monitor: All good
├─ Sunday: Enable for 100% users
├─ Timeline: Gradual, safe rollout
└─ If error at 5%: Flip OFF, no rollback

Timeline with flags:
├─ Thursday 2 PM: Deploy (flag OFF)
├─ Thursday 3 PM: Bug found, flag OFF (safe)
├─ Friday: Fix + test
├─ Friday 5 PM: Flip flag ON for 1%
├─ Saturday: Flip flag ON for 10%
├─ Sunday: Flip flag ON for 100%
└─ Result: Gradual, controlled rollout!
```

### Types of Feature Flags

```
TYPE 1: KILL SWITCH (Simple OFF/ON)

Purpose: Emergency disable
Example:
  if (!flags.isEnabled("expensive_calculation")) {
    return cached_result;
  }
  return calculate_expensive();

Use case:
├─ Bug found: Flip OFF
├─ Emergency: Quick response
├─ Zero latency (flag check is fast)

Duration: Hours to days (short-lived)


TYPE 2: GRADUAL ROLLOUT (Percentage)

Purpose: Slow rollout to users
Example:
  if (flags.isEnabledForUser(user_id, "new_feature", 10)) {
    // 10% of users
    return new_feature();
  }
  return old_feature();

Use case:
├─ New feature: Gradually enable
├─ Monitor: Errors in 1% cohort
├─ Expand: If good
├─ Rollback: If bad

Rollout process:
├─ 1% Monday (1000 users)
├─ 5% Tuesday (5000 users)
├─ 25% Wednesday (25000 users)
├─ 50% Thursday (50000 users)
├─ 100% Friday (all users)

Duration: Days to weeks


TYPE 3: USER/REGION TARGETING

Purpose: Enable for specific users or regions
Example:
  if (flags.isEnabledForUser(user_id, "premium_feature")) {
    return premium();
  }
  return free();

Use case:
├─ Beta: Only for specific users
├─ Enterprise: Only for paying customers
├─ Region: Only for Europe (GDPR compliant)
├─ A/B testing: Half get A, half get B

Targeting:
├─ User ID: if user_id in [1, 2, 3, 5]
├─ Email: if email.endswith("@mycompany.com")
├─ Region: if location == "EU"
├─ Custom: if user.plan == "premium"

Duration: Weeks to months


TYPE 4: A/B TESTING

Purpose: Experiment (control vs treatment)
Example:
  variant = flags.getVariant("checkout_ui", user_id)
  
  if (variant == "control") {
    return old_checkout();
  } else if (variant == "treatment_a") {
    return new_checkout_blue();
  } else if (variant == "treatment_b") {
    return new_checkout_green();
  }

Use case:
├─ Experiment: Compare A vs B
├─ Measure: Click-through rate, conversion
├─ Analyze: Which performs better?
├─ Scale: Deploy winner to 100%

Common experiments:
├─ Button color (blue vs green)
├─ Copy text ("Buy now" vs "Add to cart")
├─ Price ($9.99 vs $10.00)
├─ Flow (3 steps vs 1 step)

Duration: Weeks (analysis phase)


TYPE 5: OPERATIONAL FLAGS (Technical)

Purpose: Control system behavior
Example:
  if (flags.isEnabled("enable_new_database")) {
    return new_db.query();
  }
  return old_db.query();

Use case:
├─ Database migration: Dual-write, toggle read
├─ Cache: Enable/disable
├─ Circuit breaker: Open/close
├─ Rate limiter: Adjust threshold
├─ Timeout: Change timeout value

Duration: Hours to days (short-lived)
```

### Config Management

```
CONFIG TYPES:

Static config (rarely changes):
├─ Database connection strings
├─ Service endpoints
├─ API keys
├─ Credentials
└─ Baked into binary/container


Dynamic config (changes often):
├─ Feature flags (OFF/ON)
├─ Rate limits (100 req/s → 1000)
├─ Cache TTLs (1 hour → 2 hours)
├─ Feature percentages (1% → 50%)
└─ User quotas (1000 → 5000 requests)


CONFIG STORAGE:

Option 1: Hardcoded
└─ Code: const RATE_LIMIT = 100
   Problem: Need recompile/redeploy to change

Option 2: Config file
└─ File: config.yaml
   ├─ Problem: Need restart
   └─ Still requires deployment

Option 3: Environment variables
└─ Env: RATE_LIMIT=100
   ├─ Dynamic: Can change via env
   ├─ Problem: Container restart needed
   └─ Docker/Kubernetes friendly

Option 4: Central config server (Recommended)
└─ Server: Config service
   ├─ Service fetches config
   ├─ Changes: Instant (no redeploy)
   ├─ Cached: In-memory + refresh
   └─ Examples: Consul, etcd, AWS Systems Manager

Option 5: Feature flag service
└─ Service: Feature flag server
   ├─ All flags centralized
   ├─ SDK: Light client library
   ├─ Changes: Real-time push
   └─ Examples: LaunchDarkly, Unleash, Split


CONFIG HIERARCHY:

├─ Default (global, all users)
│  └─ Rate limit: 100 req/s
├─ Region override
│  └─ EU rate limit: 50 req/s (GDPR)
├─ User override
│  └─ Premium user: 10,000 req/s
└─ Context override
   └─ During migration: 1 req/s (throttled)

Evaluation order:
├─ Check context → Check user → Check region → Check default
└─ Use first match

Example:
├─ Query: isEnabled("new_payment", user_id=123, region="EU")
├─ Check user 123: Not in override list
├─ Check region EU: new_payment = false
├─ Result: false
└─ User in EU doesn't get new_payment
```

---

## 🔬 Advanced Concepts

### Feature Flag Architecture

```
SIMPLE ARCHITECTURE (Startup):

Client (App) → Feature Flag Service
                ├─ In-memory flags
                ├─ HTTP API
                └─ Reload on timer (every 5 sec)

Problem:
├─ Latency: Network call for each flag check
├─ QPS: Flag service becomes bottleneck
├─ Reliability: Flag service down = all flags default


PRODUCTION ARCHITECTURE (Scale):

┌─────────────────┐
│   Client (App)  │
└────────┬────────┘
         │
    ┌────▼────────────────────────┐
    │ Local Cache (In-Memory)      │
    │ ├─ Flags: {"new_ui": false}  │
    │ ├─ TTL: 30 seconds           │
    │ └─ Fallback: If cache empty  │
    └────┬─────────────────────────┘
         │ (Cache miss or refresh)
         │
    ┌────▼────────────────────────┐
    │ Feature Flag Service         │
    │ ├─ Database: All flags       │
    │ ├─ API: Get flags for user   │
    │ └─ Webhook: Push updates     │
    └────────────────────────────┘

Flow:
├─ Check local cache (< 1ms)
├─ Hit: Use cached value
├─ Miss: Call service (10ms)
├─ Service returns: New value
├─ Store locally: 30 sec TTL
├─ Refresh: Background job every 5 sec
└─ Webhook: Real-time updates (optional)


WEBHOOK PUSH (Real-time):

Instead of polling (check every 5 sec):
├─ Service: Maintains websocket
├─ Change: Flag changed in admin panel
├─ Push: Service sends update to client
├─ Client: Updates local cache immediately
└─ Latency: < 100ms (real-time)

Trade-off:
├─ Polling: Simple, 5-30s latency
├─ Push: Complex, real-time latency
└─ Hybrid: Push for critical flags, poll for others
```

### Storage & Evaluation

```
FLAG STORAGE:

Database schema:
┌─────────────────────────────────────────┐
│ Feature_Flags                           │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ flag_name: "new_payment_flow"           │
│ enabled: true/false                     │
│ rollout_percentage: 25 (for 25% users)  │
│ targeting_rules: JSON                   │
│ created_at, updated_at                  │
└─────────────────────────────────────────┘

Targeting rules (JSON):
{
  "enabled_for_users": [123, 456, 789],
  "enabled_for_regions": ["EU", "US"],
  "disabled_for_regions": ["CN"],
  "enabled_for_emails": ["*@company.com"],
  "rollout_percentage": 50
}


FLAG EVALUATION:

Given flag and user context:
context = {
  user_id: 123,
  email: "alice@company.com",
  region: "EU",
  plan: "premium"
}

Evaluation logic:
├─ Rule 1: Check enabled_for_users
│  ├─ 123 in [123, 456, 789]? YES → return true
│  └─ Early exit
├─ Rule 2 (if rule 1 not matched): Check region
├─ Rule 3 (if rule 2 not matched): Check email
├─ Rule 4 (if rule 3 not matched): Check percentage
└─ Default: Global enabled/disabled

Performance:
├─ In-memory: < 1ms
├─ Network call: 5-20ms
├─ Database query: 50-100ms
└─ Caching: Essential!


CONSISTENT ASSIGNMENT:

Problem: Same user gets different flag on different requests

Request 1: is_enabled("feature", user_id=123, percentage=50)
├─ Hash user_id: 123 % 100 = 23
├─ 23 < 50? YES
└─ Result: TRUE

Request 2: Same user
├─ Hash user_id: 123 % 100 = 23 (same!)
├─ 23 < 50? YES
└─ Result: TRUE (consistent!)

Hash function:
└─ Deterministic: hash(user_id) always same
   └─ Ensures: User always gets same variant
      └─ Critical: For A/B testing (need consistency)
```

---

## 🐍 Python Code Example

### ❌ Without Feature Flags (Rigid)

```python
# ===== WITHOUT FEATURE FLAGS =====

from flask import Flask

app = Flask(__name__)

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Checkout - new implementation hardcoded"""
    
    # New UI always used
    # If bug found: Must rollback entire deployment!
    order = new_payment_flow(request.json)
    
    return {'order_id': order.id}

# Problems:
# ❌ Bug found: Must rollback (lose work)
# ❌ Gradual rollout: Impossible (all-or-nothing)
# ❌ A/B testing: Hard (requires two branches)
# ❌ Emergency disable: Requires redeployment
```

### ✅ With Feature Flags (Flexible)

```python
# ===== WITH FEATURE FLAGS =====

from flask import Flask, request, jsonify
from typing import Dict, Optional

app = Flask(__name__)

class FeatureFlagService:
    """Simple feature flag service"""
    
    def __init__(self):
        # In production: Load from database
        self.flags: Dict = {
            'new_payment_flow': {
                'enabled': True,
                'rollout_percentage': 50,
                'description': 'New payment UI'
            },
            'premium_features': {
                'enabled': True,
                'rollout_percentage': 100,
                'enabled_for_users': [123, 456],  # Specific users
                'description': 'Premium tier features'
            }
        }
    
    def is_enabled(self, flag_name: str, user_id: Optional[int] = None):
        """Check if flag is enabled for user"""
        
        if flag_name not in self.flags:
            return False  # Unknown flag
        
        flag = self.flags[flag_name]
        
        # Check if globally enabled
        if not flag.get('enabled', False):
            return False
        
        # Check if user in specific list
        enabled_users = flag.get('enabled_for_users', [])
        if enabled_users and user_id in enabled_users:
            return True
        
        # Check rollout percentage
        rollout = flag.get('rollout_percentage', 100)
        if user_id:
            # Consistent hashing: same user always gets same result
            user_hash = hash(f"{flag_name}:{user_id}") % 100
            return user_hash < rollout
        
        return rollout >= 100
    
    def set_flag(self, flag_name: str, enabled: bool, rollout: int = 100):
        """Update flag (admin only)"""
        
        if flag_name not in self.flags:
            self.flags[flag_name] = {}
        
        self.flags[flag_name]['enabled'] = enabled
        self.flags[flag_name]['rollout_percentage'] = rollout

# Initialize
feature_flags = FeatureFlagService()

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Checkout with feature flag"""
    
    user_id = request.json.get('user_id')
    
    # Check flag
    use_new_flow = feature_flags.is_enabled('new_payment_flow', user_id)
    
    if use_new_flow:
        order = new_payment_flow(request.json)
    else:
        order = old_payment_flow(request.json)
    
    return {'order_id': order.id}

@app.route('/admin/flags/<flag_name>', methods=['POST'])
def update_flag(flag_name):
    """Admin: Update flag"""
    
    data = request.json
    enabled = data.get('enabled', True)
    rollout = data.get('rollout_percentage', 100)
    
    feature_flags.set_flag(flag_name, enabled, rollout)
    
    return {'status': 'updated', 'flag': flag_name}

# Benefits:
# ✅ Bug found: Flip flag OFF (instant)
# ✅ Gradual rollout: 1% → 50% → 100%
# ✅ A/B testing: Route users to variants
# ✅ Emergency disable: No redeployment
# ✅ User targeting: Specific users first
```

### ✅ Production Feature Flag Service

```python
# ===== PRODUCTION FEATURE FLAG SERVICE =====

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import redis
import json
from datetime import datetime

class TargetingRule(Enum):
    """Types of targeting rules"""
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    EMAIL_DOMAIN = "email_domain"
    REGION = "region"
    CUSTOM = "custom"

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    enabled: bool
    rules: List[Dict]  # Targeting rules
    variants: Optional[Dict] = None  # For A/B testing
    created_at: datetime = None
    updated_at: datetime = None

class FeatureFlagStore:
    """Store flags in database/cache"""
    
    def __init__(self, db, cache: redis.Redis):
        self.db = db
        self.cache = cache
    
    def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Get flag (cache-first)"""
        
        # Try cache first
        cached = self.cache.get(f"flag:{flag_name}")
        if cached:
            return json.loads(cached)
        
        # Cache miss: Query database
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT name, enabled, rules, variants
            FROM feature_flags
            WHERE name = %s
        """, (flag_name,))
        
        result = cursor.fetchone()
        
        if not result:
            return None
        
        flag = {
            'name': result[0],
            'enabled': result[1],
            'rules': json.loads(result[2]),
            'variants': json.loads(result[3]) if result[3] else None
        }
        
        # Cache for 30 seconds
        self.cache.setex(
            f"flag:{flag_name}",
            30,
            json.dumps(flag)
        )
        
        return flag
    
    def update_flag(self, flag_name: str, enabled: bool, rules: List[Dict]):
        """Update flag"""
        
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE feature_flags
            SET enabled = %s, rules = %s, updated_at = NOW()
            WHERE name = %s
        """, (enabled, json.dumps(rules), flag_name))
        
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(f"flag:{flag_name}")

class FlagEvaluator:
    """Evaluate flags for user context"""
    
    def __init__(self, store: FeatureFlagStore):
        self.store = store
    
    def evaluate(self, flag_name: str, context: Dict) -> bool:
        """Evaluate flag for context"""
        
        flag = self.store.get_flag(flag_name)
        
        if not flag or not flag['enabled']:
            return False
        
        # No rules = enabled for all
        if not flag['rules']:
            return True
        
        # Evaluate rules (first match wins)
        for rule in flag['rules']:
            if self._match_rule(rule, context):
                return True
        
        return False
    
    def _match_rule(self, rule: Dict, context: Dict) -> bool:
        """Check if rule matches context"""
        
        rule_type = rule.get('type')
        
        if rule_type == TargetingRule.PERCENTAGE.value:
            # Consistent hashing
            user_id = context.get('user_id')
            percentage = rule.get('percentage', 0)
            
            if user_id:
                user_hash = hash(f"flag:{user_id}") % 100
                return user_hash < percentage
            
            return percentage >= 100
        
        elif rule_type == TargetingRule.USER_LIST.value:
            # Specific users
            user_id = context.get('user_id')
            enabled_users = rule.get('user_ids', [])
            return user_id in enabled_users
        
        elif rule_type == TargetingRule.EMAIL_DOMAIN.value:
            # Email domain
            email = context.get('email', '')
            domains = rule.get('domains', [])
            
            for domain in domains:
                if email.endswith(f"@{domain}"):
                    return True
            
            return False
        
        elif rule_type == TargetingRule.REGION.value:
            # Region targeting
            region = context.get('region')
            enabled_regions = rule.get('regions', [])
            return region in enabled_regions
        
        elif rule_type == TargetingRule.CUSTOM.value:
            # Custom logic
            custom_fn = rule.get('function')
            if custom_fn:
                return custom_fn(context)
            
            return False
        
        return False
    
    def get_variant(self, flag_name: str, context: Dict) -> Optional[str]:
        """Get A/B variant for user"""
        
        flag = self.store.get_flag(flag_name)
        
        if not flag or not flag['variants']:
            return None
        
        # Consistent assignment
        user_id = context.get('user_id')
        variants = list(flag['variants'].keys())
        
        if user_id:
            user_hash = hash(f"variant:{flag_name}:{user_id}") % len(variants)
            return variants[user_hash]
        
        return variants[0]

# API Endpoints

@app.route('/api/feature/<flag_name>')
def check_flag(flag_name):
    """Check if flag enabled for user"""
    
    user_id = request.args.get('user_id', type=int)
    email = request.args.get('email')
    region = request.args.get('region', 'US')
    
    context = {
        'user_id': user_id,
        'email': email,
        'region': region
    }
    
    evaluator = FlagEvaluator(flag_store)
    enabled = evaluator.evaluate(flag_name, context)
    variant = evaluator.get_variant(flag_name, context)
    
    return jsonify({
        'flag': flag_name,
        'enabled': enabled,
        'variant': variant,
        'context': context
    })

@app.route('/admin/flags/<flag_name>', methods=['PUT'])
def update_flag(flag_name):
    """Admin: Update flag"""
    
    data = request.json
    enabled = data.get('enabled', True)
    rules = data.get('rules', [])
    
    flag_store.update_flag(flag_name, enabled, rules)
    
    return jsonify({
        'status': 'updated',
        'flag': flag_name
    })

@app.route('/admin/flags/<flag_name>/rollout/<int:percentage>', methods=['POST'])
def gradual_rollout(flag_name, percentage):
    """Admin: Gradual rollout (1% → 50% → 100%)"""
    
    rules = [{
        'type': TargetingRule.PERCENTAGE.value,
        'percentage': percentage
    }]
    
    flag_store.update_flag(flag_name, True, rules)
    
    return jsonify({
        'status': 'rollout_updated',
        'flag': flag_name,
        'percentage': percentage
    })

# Benefits:
# ✅ In-memory caching (fast, < 1ms)
# ✅ Database-backed (persistent)
# ✅ Real-time updates (cache invalidation)
# ✅ Multiple targeting rules
# ✅ Gradual rollout support
# ✅ A/B testing (variants)
# ✅ Production-ready
```

---

## 💡 Design Decisions

### When to Use Feature Flags?

```
USE FEATURE FLAGS FOR:

✅ New features (gradual rollout)
✅ Experimental changes (A/B testing)
✅ Risky changes (emergency kill switch)
✅ Regional rollout (GDPR compliance)
✅ Beta testing (specific users)
✅ Performance experiments (cache vs no-cache)

DON'T USE FOR:

❌ Configuration (use config management)
❌ Business logic (if-else everywhere = mess)
❌ Temporary debugging (remove before deploy)
❌ Static content (use CDN versioning)

BALANCE:

Too few flags:
├─ Deployment risk increases
├─ Can't rollback quickly
└─ Slow rollout

Too many flags:
├─ Tech debt (100s of old flags)
├─ Hard to test (2^N combinations)
├─ Confusion (which flags matter?)
└─ Need flag cleanup strategy

Recommended:
├─ 10-50 active flags (mature)
├─ Review quarterly (clean old ones)
├─ Auto-remove after 30 days (if not used)
└─ Document purpose (why does this exist?)
```

### Feature Flag vs Config Management

```
FEATURE FLAGS:

Purpose: Control feature availability
Example: new_payment_ui = true/false
Duration: Days to weeks
Scope: Specific code paths
Audience: End users

Query:
├─ if (isEnabled("feature")) { new_code() }
└─ Defaults to false (safe)


CONFIG MANAGEMENT:

Purpose: Control system behavior
Example: rate_limit = 100 req/s
Duration: Always (permanent)
Scope: System behavior
Audience: System operators

Query:
├─ max_requests = getConfig("rate_limit")
└─ Has default, but usually set

Overlap:
├─ Both can be dynamic (real-time updates)
├─ Both can be targeted (by user/region)
├─ Both can have webhooks (real-time push)
└─ Feature flags = subset of config management
```

---

## ❌ Common Mistakes

### Mistake 1: Flag Sprawl (Too Many Flags)

```python
# ❌ 500 flags in production
if flag("legacy_api"):
    # Old API
if flag("new_ui_blue"):
    # Blue button
if flag("new_ui_green"):
    # Green button
if flag("cache_v1"):
    # Old cache
if flag("cache_v2"):
    # New cache
# ... multiply by 50 more combinations

# Testing: 2^500 combinations (impossible!)

# ✅ Cleanup strategy
# Delete flags not used in 30 days
# Review quarterly (remove unused)
# Document purpose (why exists?)
# Test combinations (matrix testing)
```

### Mistake 2: No Observability

```python
# ❌ No tracking
if feature_flags.is_enabled("new_feature"):
    new_code()

# Problem: No data on who got new_feature
# Hard to debug: User reports bug, don't know if flag ON/OFF

# ✅ Track flag usage
def is_enabled(flag_name, context):
    enabled = flags.get(flag_name, context)
    
    # Log for analysis
    analytics.track_flag(
        flag_name,
        context['user_id'],
        enabled,
        context['variant']
    )
    
    return enabled

# Now: Can see adoption, error rates per variant
```

### Mistake 3: Rollout Mistakes

```python
# ❌ Instant rollout (10% → 100%)
# New feature to 100% of users immediately
flags.set_rollout("payment_v2", 100)
# Bug: Now all users broken!

# ✅ Staged rollout
# Monday: 1% (100 users)
# Check: No errors
# Tuesday: 5% (500 users)
# Check: No errors
# Wednesday: 25% (2500 users)
# Check: Metrics good
# Thursday: 50% (5000 users)
# Check: No regression
# Friday: 100% (all users)
# Result: Safe, controlled, observable
```

---

## 📚 Additional Resources

**Feature Flag Services:**
- [LaunchDarkly](https://launchdarkly.com/) (enterprise)
- [Unleash](https://www.getunleash.io/) (open source)
- [Split.io](https://www.split.io/) (enterprise)
- [CloudBees Feature Flags](https://www.cloudbees.com/)

**Config Management:**
- [Consul](https://www.consul.io/) (HashiCorp)
- [etcd](https://etcd.io/) (Kubernetes)
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

**A/B Testing:**
- [A/B Testing Best Practices](https://www.optimizely.com/optimization-glossary/ab-testing/)
- [Experimentation at Scale](https://research.fb.com/publications/practical-lessons-from-running-a-modern-large-scale-ab-testing-platform-at-scale/)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **Feature flag vs config management?**
   - Answer: Flags = feature availability; Config = system behavior

2. **Why gradual rollout?**
   - Answer: Monitor errors, rollback safely if bad

3. **Consistent assignment?**
   - Answer: Hash(user_id) ensures same variant always

4. **When to clean up flags?**
   - Answer: Delete after 30 days unused, review quarterly

5. **A/B testing requirement?**
   - Answer: Consistent assignment, measurement, statistical analysis

**If you got these right, you're ready for data consistency!** ✅

---

## 🤣 Closing Thoughts

> **Developer:** "Feature flag? Seems overkill for one feature"
>
> **DevOps:** "Just add one"
>
> **6 months later:** "We have 3000 flags"
>
> **Developer:** "I can't find the flag that controls this feature"
>
> **DevOps:** "There are 47 with that name"
>
> **CEO:** "How do we know what's in production?"
>
> **Developer:** "I'll check... give me a week" 😭

---

[← Back to Main](../README.md) | [Previous: Event Sourcing](59-event-sourcing.md) | [Next: Data Consistency Patterns →](61-data-consistency-patterns.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (operations)  
**Time to Read:** 30 minutes  
**Time to Implement:** 20-40 hours (depends on scale)  

---

*Feature Flags: The safety net for safe deployments.* 🚩✨