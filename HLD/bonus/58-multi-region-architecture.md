# 58. Multi-Region Architecture

 Your system works great in one region. Then you decide to expand globally. "Just replicate everything!" you say. Then you hit consistency issues, latency problems, data sovereignty laws, cost explosions, and operational complexity. Now you realize: running systems in one region was the easy part. Running them everywhere is the hard part. Welcome to multi-region! 🌍🔥

[← Back to Main](../README.md) | [Previous: API Versioning](57-api-versioning.md) | [Next: Event Sourcing →](59-event-sourcing.md)

---

## 🎯 Quick Summary

**Multi-Region Architecture** runs systems across geographic regions for latency, availability, and compliance. **Primary region** handles writes, **replica regions** handle reads. **Trade-offs:** consistency (eventual), complexity (operational), cost (2-3x), data residency (legal). Netflix, AWS, Google operate 30+ regions. **Challenges:** replication lag, failover, data sovereignty (GDPR, data localization laws). Essential for global scale.

Think of it as: **Multi-Region = Global Resilience at Cost of Complexity**

---

## 🌟 Beginner Explanation

### Why Multi-Region?

```
SINGLE REGION PROBLEM:

Server location: Virginia, USA
├─ Users in Virginia: 50ms latency ✓
├─ Users in London: 140ms latency ⚠️
├─ Users in Singapore: 300ms latency ❌
├─ Users in Sydney: 350ms latency ❌
└─ Regional outage: Everyone down!

Issues:
├─ Slow for international users
├─ No disaster recovery (entire region down)
├─ Compliance: Data must stay in-country
└─ Cost: Everyone uses same expensive region


MULTI-REGION SOLUTION:

Region 1 (Virginia - Primary):
├─ Serves: North America
├─ Latency: 50ms
├─ Role: Write operations
└─ Status: Primary

Region 2 (London - Replica):
├─ Serves: Europe
├─ Latency: 10ms (local)
├─ Role: Read operations
└─ Status: Replica (replicates from Region 1)

Region 3 (Singapore - Replica):
├─ Serves: Asia-Pacific
├─ Latency: 10ms (local)
├─ Role: Read operations
└─ Status: Replica (replicates from Region 1)

Region 4 (Sydney - Replica):
├─ Serves: Australia/NZ
├─ Latency: 10ms (local)
├─ Role: Read operations
└─ Status: Replica (replicates from Region 1)

Benefits:
✅ Low latency everywhere (10-50ms)
✅ If Virginia down: London/Singapore/Sydney still serve reads
✅ Compliance: Keep data local
✅ Scalability: Distribute load
```

### Replication Strategies

```
STRATEGY 1: Master-Replica (Primary-Secondary)

Primary (Virginia):
├─ Handles: All writes
├─ Database: Master
├─ Traffic: Read + Write
└─ Authority: Single source of truth

Replicas (London, Singapore, Sydney):
├─ Handles: Reads only
├─ Database: Replica (read-only copy)
├─ Traffic: Read only
├─ Replication: From master (continuous)

How it works:
├─ Write: Goes to Virginia master
├─ Master: Commits to database
├─ Master: Streams changes to replicas
├─ Replicas: Apply changes asynchronously
├─ Read: Can use any region (eventually consistent)

Latency:
├─ Write: 140ms (to Virginia) + replication lag (5-30s)
├─ Read: 10ms (local replica)

Issues:
├─ Write latency: High (must go to primary)
├─ Replication lag: Data inconsistent for seconds
├─ If primary down: Can't write (even if replicas up)

Use case:
✓ Read-heavy workloads
✓ Can tolerate replication lag
✓ Writes acceptable with high latency


STRATEGY 2: Multi-Master (Active-Active)

Region 1 (Virginia):
├─ Handles: All traffic
├─ Database: Master (can write)
├─ Replicates: Changes to regions 2,3,4
└─ Authority: Region 1 writes

Region 2 (London):
├─ Handles: All traffic
├─ Database: Master (can write)
├─ Replicates: Changes to regions 1,3,4
└─ Authority: Region 2 writes

Region 3 (Singapore):
├─ Handles: All traffic
├─ Database: Master (can write)
├─ Replicates: Changes to regions 1,2,4
└─ Authority: Region 3 writes

Region 4 (Sydney):
├─ Handles: All traffic
├─ Database: Master (can write)
├─ Replicates: Changes to regions 1,2,3
└─ Authority: Region 4 writes

Benefits:
✅ Write latency: 10-50ms (local)
✅ Low read latency: 10-50ms (local)
✅ If one region down: Others still write

Challenges:
❌ Conflicts: Two regions update same record simultaneously
❌ Resolution: Who wins? (Last-write-wins? Merge?)
❌ Complexity: Conflict resolution logic
❌ Consistency: Eventually consistent only

Conflict example:
├─ User in Virginia updates: profile.name = "Alice"
├─ User in London updates: profile.name = "Bob"
├─ Replicate to other: Which name is correct?
├─ Last-write-wins: Time-based (but clocks vary!)
├─ CRDTs: Special data types (see later topics)

Use case:
✓ Write-heavy workloads
✓ Tolerate eventual consistency
✓ Low write latency critical


STRATEGY 3: Geo-Sharding

Data partitioned by geography:
├─ Region 1 (Virginia): Owns users in North America
├─ Region 2 (London): Owns users in Europe
├─ Region 3 (Singapore): Owns users in Asia
└─ Region 4 (Sydney): Owns users in Oceania

How it works:
├─ Write: Route to owning region
├─ Read: Route to owning region
├─ Replication: Each region is primary for its shard

Benefits:
✅ No conflicts (each region owns data)
✅ Write latency: 10-50ms (local)
✅ Read latency: 10-50ms (local)
✅ Simpler: No conflict resolution needed

Challenges:
❌ Complex routing: Must know user → region mapping
❌ Global queries: "Show me all users" requires querying all regions
❌ Uneven load: If one region has more users, it gets overloaded
❌ Migration: User moves → Data moves

Use case:
✓ Data naturally partitionable by geography
✓ Most queries are scoped to user's region
✓ Simplicity > perfect distribution
```

### Failover & Disaster Recovery

```
PRIMARY REGION FAILS:

Scenario: Virginia data center fire

Option A: Read-only failover
├─ London, Singapore, Sydney replicas still serving
├─ No new writes possible
├─ Customers can READ their data
├─ But CAN'T create orders, posts, etc.
├─ Duration: Until Virginia back online
└─ Impact: Partial service

Option B: Promote replica
├─ Detect: Virginia is down (health check fails)
├─ Promote: London replica → Master
├─ London: Now handles writes
├─ Issue: Replication lag data loss
│  ├─ Last write before failure: LOST
│  ├─ Data in flight: LOST
│  └─ Example: User had 100 in account, wrote 50
│     ├─ If not replicated: Write lost
│     └─ Account now shows 100 (should be 50)
└─ Duration: Until Virginia back + failover complete

Recovery process:
├─ Detect down: Health check fails (5-10s)
├─ Alert: Page on-call engineers (1-5 min)
├─ Promote: Replica to master (5-10 min)
├─ Update: DNS / client routing (30s - 5 min TTL)
├─ Verify: Check data consistency (5-10 min)
├─ Total: 20-40 minutes typical

Data loss risk:
├─ Replication lag (5-30s): Data lost
├─ Network partition: Some writes lost
├─ Complex failure: Data in-flight lost
└─ Typical: 1-5 minutes of data loss
```

### Data Sovereignty & Compliance

```
GDPR (Europe):

Requirement:
├─ Personal data of EU citizens
├─ Must be stored IN Europe
├─ Cannot be replicated outside Europe
└─ Cannot be processed outside Europe

Multi-region strategy:
├─ EU users' data: London region only
├─ Cannot replicate to Virginia/Singapore
├─ EU users' queries: Processed in Europe
├─ Cannot send data to US servers
└─ Architecture: Geo-sharded by compliance zone


CCPA (California):

Requirement:
├─ Personal data of California residents
├─ Must be accessible for deletion
├─ Cannot sell to third parties
└─ Must disclose storage location

Multi-region strategy:
├─ CA users' data: Can store in any US region
├─ But: Replicate to backup region
├─ Deletion: Can only delete from California region
└─ Process: Carefully audit data flows


STRATEGY: Compliance Zones

Zone 1 (EU):
├─ Contains: EU citizens' data
├─ Regions: London, Frankfurt
├─ Replication: Within EU only
├─ Transfer: None outside (violates GDPR)
└─ Users: EU citizens

Zone 2 (US):
├─ Contains: US citizens' data
├─ Regions: Virginia, Oregon
├─ Replication: Anywhere in US
├─ Transfer: Limited (CCPA)
└─ Users: US citizens

Zone 3 (Global):
├─ Contains: Non-sensitive data
├─ Regions: Any (Virginia, London, Singapore, Sydney)
├─ Replication: Anywhere
└─ Users: Everyone else

Data path:
├─ EU user: Data → London only (GDPR compliant)
├─ US user: Data → Virginia + Oregon (CCPA compliant)
├─ Global user: Data → Anywhere
```

---

## 🔬 Advanced Design

### Consistency Models

```
STRONG CONSISTENCY:

Guarantee:
├─ All reads: See latest write
├─ Across: All regions
├─ Example: Write $100 to account
│  └─ All regions: See $100 immediately

Implementation:
├─ Master: Handle all writes
├─ Replicas: Wait for ack before returning
├─ Cost: High latency (must wait for replication)

Latency:
├─ Write latency: 140ms (round trip to primary)
└─ Not practical for global systems


EVENTUAL CONSISTENCY:

Guarantee:
├─ Eventually: All regions have same data
├─ But: May be temporarily inconsistent
├─ Example: Write $100 to account
│  ├─ Virginia: Sees $100 immediately
│  ├─ London: Sees $100 after 5 seconds
│  └─ Singapore: Sees $100 after 10 seconds

Implementation:
├─ Master: Write immediately
├─ Replicate: Asynchronously
├─ Cost: Low latency, high complexity

Latency:
├─ Write latency: 10ms (local, no wait)
├─ Consistency delay: Replication lag (5-30s)


CAUSAL CONSISTENCY:

Guarantee:
├─ Causally related writes: Ordered
├─ Example:
│  ├─ User writes: Post1 at Virginia
│  ├─ User reads: In London (post not visible yet)
│  ├─ User writes: Post2 in London (references Post1)
│  └─ Guarantee: Post1 visible before Post2

Implementation:
├─ Track: Causality (version vectors)
├─ Replicate: In order
├─ Cost: Medium latency, medium complexity


RECOMMENDATION FOR GLOBAL SYSTEMS:

Tier 1 (Consistency critical):
├─ Accounts, money, orders
├─ Use: Master-replica (accept write latency)
├─ Or: Geo-sharded by user

Tier 2 (Eventual OK):
├─ Posts, feeds, analytics
├─ Use: Multi-master active-active
└─ Accept: Temporary inconsistency

Tier 3 (Very eventual):
├─ Cache, recommendations
├─ Use: Eventually consistent
└─ Accept: Stale data is OK
```

### Replication Lag Management

```
PROBLEM: Replication lag (replicas behind master)

Scenario:
├─ User in Virginia: Writes post
├─ Post: Committed in Virginia
├─ Replication: Takes 10 seconds to London
├─ User in London: Reads immediately
├─ Result: Doesn't see own post!

Solutions:

Option 1: Read-your-write consistency
├─ After write: Remember that write
├─ Next read: Route to master if possible
├─ Or: Wait until replica has replication acked
└─ Latency: High (wait for replication)

Option 2: Session tokens
├─ After write: Return token (includes version)
├─ Next read: Include token
├─ Read: "At least this version"
├─ Replica: Waits until has that version
└─ Latency: Acceptable

Option 3: Local-first reads
├─ After write: Cache result locally
├─ Read cache first (before querying backend)
├─ Prevents: Read-after-write anomaly
└─ Latency: Very fast

Option 4: Accept lag
├─ For some features: Lag is OK
├─ Example: Feed updates fine in 10 seconds
├─ Example: Analytics fine in hours
└─ Cost: None (simplest)
```

---

## 🐍 Python Code Example

### ❌ Single Region (No Resilience)

```python
# ===== SINGLE REGION =====

from flask import Flask
import psycopg2

app = Flask(__name__)

# Single database in Virginia
db = psycopg2.connect(
    host='db.virginia.us-east-1.rds.amazonaws.com',
    database='app',
    user='admin',
    password='secret'
)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order - single region"""
    
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, amount)
        VALUES (%s, %s)
        RETURNING id
    """, (request.json['user_id'], request.json['amount']))
    
    order_id = cursor.fetchone()[0]
    db.commit()
    
    return {'order_id': order_id}

# Problems:
# ❌ Virginia outage = entire system down
# ❌ High latency for non-US users
# ❌ No compliance with data residency laws
# ❌ No disaster recovery
```

### ✅ Multi-Region Master-Replica

```python
# ===== MULTI-REGION MASTER-REPLICA =====

from flask import Flask, request, jsonify
import psycopg2
from functools import wraps

app = Flask(__name__)

# Primary (master) - Virginia
primary_db = psycopg2.connect(
    host='db-primary.virginia.rds.amazonaws.com',
    database='app',
    user='admin',
    password='secret'
)

# Replicas (read-only)
replica_dbs = {
    'london': psycopg2.connect(
        host='db-replica.london.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    ),
    'singapore': psycopg2.connect(
        host='db-replica.singapore.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    ),
    'sydney': psycopg2.connect(
        host='db-replica.sydney.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    )
}

class RegionalRouter:
    """Route operations to correct region"""
    
    def __init__(self, primary, replicas):
        self.primary = primary
        self.replicas = replicas
    
    def get_user_region(self, user_id):
        """Determine user's region"""
        
        # Query user table (primary)
        cursor = self.primary.cursor()
        cursor.execute(
            "SELECT region FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        return result[0] if result else 'london'  # Default
    
    def get_replica_for_region(self, region):
        """Get replica connection for region"""
        
        # In real system: Route to closest replica
        # For now: Simple mapping
        return self.replicas.get(region, self.replicas['london'])
    
    def read(self, user_id, query, params):
        """Read from closest replica"""
        
        region = self.get_user_region(user_id)
        replica = self.get_replica_for_region(region)
        
        cursor = replica.cursor()
        cursor.execute(query, params)
        
        return cursor.fetchall()
    
    def write(self, query, params):
        """Write to primary (replicates automatically)"""
        
        cursor = self.primary.cursor()
        cursor.execute(query, params)
        self.primary.commit()

router = RegionalRouter(primary_db, replica_dbs)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order - multi-region"""
    
    user_id = request.json['user_id']
    amount = request.json['amount']
    
    # Write to primary
    router.write("""
        INSERT INTO orders (user_id, amount, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id
    """, (user_id, amount))
    
    # Note: Replica lag means London user may not see order immediately
    
    return {'order_id': order_id}

@app.route('/api/orders/<int:user_id>')
def get_orders(user_id):
    """Get orders - read from replica"""
    
    orders = router.read(user_id, """
        SELECT id, amount, created_at FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    return {'orders': [dict(o) for o in orders]}

# Benefits:
# ✅ Write latency acceptable (primary handles)
# ✅ Read latency: Low (local replica)
# ✅ Virginia down: Replicas still serve reads
# ✅ Replication: Automatic (database feature)
```

### ✅ Multi-Region Geo-Sharding

```python
# ===== MULTI-REGION GEO-SHARDING =====

from flask import Flask, request, jsonify
import psycopg2
from geoip2.database import Reader

app = Flask(__name__)

# Regional databases (primary in each region)
regional_dbs = {
    'us': psycopg2.connect(
        host='db.virginia.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    ),
    'eu': psycopg2.connect(
        host='db.london.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    ),
    'asia': psycopg2.connect(
        host='db.singapore.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    ),
    'oceania': psycopg2.connect(
        host='db.sydney.rds.amazonaws.com',
        database='app',
        user='admin',
        password='secret'
    )
}

class GeoShardRouter:
    """Route operations to correct geographic shard"""
    
    def __init__(self, dbs, geoip_reader):
        self.dbs = dbs
        self.geoip = geoip_reader
    
    def get_shard_for_ip(self, ip_address):
        """Determine shard based on IP location"""
        
        try:
            response = self.geoip.country(ip_address)
            country_code = response.country.iso_code
            
            # Map countries to shards
            if country_code in ['US', 'CA', 'MX']:
                return 'us'
            elif country_code in ['GB', 'DE', 'FR', 'IT', 'ES']:
                return 'eu'
            elif country_code in ['SG', 'JP', 'IN', 'CN', 'KR']:
                return 'asia'
            else:
                return 'oceania'
        
        except:
            return 'us'  # Default
    
    def get_db_for_shard(self, shard):
        """Get database connection for shard"""
        
        return self.dbs[shard]
    
    def read(self, ip_address, user_id, query, params):
        """Read from user's regional shard"""
        
        shard = self.get_shard_for_ip(ip_address)
        db = self.get_db_for_shard(shard)
        
        cursor = db.cursor()
        cursor.execute(query, params)
        
        return cursor.fetchall()
    
    def write(self, ip_address, query, params):
        """Write to user's regional shard"""
        
        shard = self.get_shard_for_ip(ip_address)
        db = self.get_db_for_shard(shard)
        
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

geoip_reader = Reader('/usr/share/GeoIP/GeoLite2-Country.mmdb')
router = GeoShardRouter(regional_dbs, geoip_reader)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order - geo-sharded"""
    
    user_id = request.json['user_id']
    amount = request.json['amount']
    ip_address = request.remote_addr
    
    # Write to regional shard
    router.write(ip_address, """
        INSERT INTO orders (user_id, amount, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id
    """, (user_id, amount))
    
    return {'order_id': order_id}

@app.route('/api/orders/<int:user_id>')
def get_orders(user_id):
    """Get orders from regional shard"""
    
    ip_address = request.remote_addr
    
    orders = router.read(ip_address, user_id, """
        SELECT id, amount, created_at FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    return {'orders': [dict(o) for o in orders]}

# Benefits:
# ✅ Low write latency (local region)
# ✅ Low read latency (local region)
# ✅ No replication lag (each region owns its data)
# ✅ GDPR compliant (data stays local)
# ✅ Simpler: No conflict resolution needed
```

---

## 💡 Design Decisions

### When to Use Multi-Region?

```
Use multi-region if:
├─ Global user base (>50% non-local)
├─ Latency matters (< 100ms critical)
├─ Compliance requirements (GDPR, data residency)
├─ Disaster recovery needed (99.99% uptime)
└─ Budget: Can afford 2-3x infrastructure cost

Don't use if:
├─ Single country only
├─ Latency not critical
├─ Small scale (fits in one region)
├─ Budget: Cannot afford replication overhead
└─ Simple > availability

Example timeline:
├─ Year 1: Single region (Virginia)
├─ Year 2: 100K DAU, add London (for EU)
├─ Year 3: 1M DAU, add Singapore + Sydney
└─ Year 4: 10M DAU, consider multi-master
```

### Master-Replica vs Geo-Sharding vs Multi-Master

```
DECISION TABLE:

                    Master-Replica  Geo-Shard  Multi-Master
Write latency       High (140ms)    Low        Low
Read latency        Low             Low        Low
Consistency         Eventual        Strong     Eventual
Complexity          Medium          Medium     High
Failover            Hard            Medium     Medium
Recommended for:    Reads heavy     Global     Writes heavy
                    EU compliance   Multi-use  Edge computing
```

---

## ❌ Common Mistakes

### Mistake 1: Ignoring Replication Lag

```python
# ❌ Write then immediately read
router.write("INSERT INTO orders...", params)
orders = router.read(user_id, "SELECT...")
# Order may not be visible! Replication lag!

# ✅ Explicitly handle lag
token = router.write("INSERT...", params)
orders = router.read_at_least(user_id, token, "SELECT...")
# Wait until replica has replication acked
```

### Mistake 2: Not Planning for Failover

```python
# ❌ No failover plan
# Primary goes down → No writes possible
# Data lost forever

# ✅ Plan failover
# Primary down: Promote replica to master (10 min)
# Communicate: Affected users (5 min)
# Verify: Data consistency (10 min)
# Total: 25 minutes RTO, 5 min RPO
```

### Mistake 3: Forgetting Compliance Zones

```python
# ❌ GDPR violation
# Store EU user data in Virginia
# Send to analytics in US
# = Illegal!

# ✅ Compliance zones
# EU data: London only
# EU processing: European servers
# Data residency: Enforced in code
```

---

## 📚 Additional Resources

**Multi-Region:**
- [AWS Multi-Region](https://docs.aws.amazon.com/general/latest/gr/rande.html)
- [Google Cloud Regions](https://cloud.google.com/about/locations)

**GDPR & Data Residency:**
- [GDPR Data Residency](https://gdpr-info.eu/issues/data-location/)
- [CCPA California](https://oag.ca.gov/privacy/ccpa)

**Replication:**
- [MySQL Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/warm-standby.html)

---


## 🎯 Before You Leave

**Can you answer these?**

1. **Master-replica vs multi-master?**
   - Answer: Master = single write region; Multi-master = write anywhere

2. **What is replication lag?**
   - Answer: Delay before replicas catch up to master

3. **Geo-sharding vs geo-distributed?**
   - Answer: Shard = partition data; distributed = replicate all

4. **GDPR compliance in multi-region?**
   - Answer: EU data = EU only, cannot cross borders

5. **RTO and RPO trade-offs?**
   - Answer: Lower RTO/RPO = higher cost/complexity

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **CEO:** "Let's expand to Europe!"
>
> **Engineer:** "Sure, need multi-region"
>
> **CEO:** "How hard?"
>
> **Engineer:** "3-6 months, 2x cost"
>
> **CEO:** "That's a lot. What if we just use CDN?"
>
> **Engineer:** "CDN doesn't fix writes..."
>
> **CEO:** "People in Europe don't write?"
>
> **Engineer:** "They do. And they want GDPR compliance too"
>
> **CEO:** "Ah. Multi-region it is then" 💸

---

[← Back to Main](../README.md) | [Previous: API Versioning](57-api-versioning.md) | [Next: Event Sourcing →](59-event-sourcing.md)

---

**Last Updated:** December 09, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (distributed systems)  
**Time to Read:** 30 minutes  
**Time to Implement:** 40-80 hours (infrastructure + testing)  

---

*Multi-Region Architecture: Serving the world, managing the complexity.* 🌍🚀