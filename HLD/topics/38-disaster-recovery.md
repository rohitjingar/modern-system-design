# 38. Disaster Recovery

Disaster recovery is preparing for the worst. You write detailed plans for recovering from fires, floods, earthquakes, nuclear war, and data centers catching on fire. Then a developer accidentally runs `rm -rf /` in production and everything burns down anyway. All that planning and it was the simple stuff that got you. Welcome to reality! 🔥💾

[← Back to Main](../README.md) | [Previous: Retry & Backoff Mechanisms](37-retry-backoff.md) | [Next: Blue-Green & Canary Deployments](39-blue-green-canary.md)

---

## 🎯 Quick Summary

**Disaster Recovery (DR)** prepares systems to recover from catastrophic failures (data center down, data corruption, all servers dead). Metrics: RTO (recovery time objective: how fast?), RPO (recovery point objective: how much data loss?). Strategies: backups (periodic snapshots), replicas (real-time copies), multi-region (separate data centers). Netflix spans regions automatically. Amazon has 99.99% SLA (52.6 minutes downtime/year). Trade-off: cost (replication expensive), complexity (multi-region hard), latency (may increase).

Think of it as: **Disaster Recovery = Insurance Policy**

---

## 🌟 Beginner Explanation

### Disaster Scenarios

```
SCENARIO 1: Data Center Fire

T=0: Fire starts in Amazon Virginia data center
├─ All servers gone
├─ All data deleted
├─ All customers: ERRORS
└─ System down

Without DR:
├─ No backup
├─ No replicas elsewhere
├─ Weeks to recover
└─ Data lost forever

With DR:
├─ Replicas in AWS Ohio (500 miles away)
├─ Auto-failover triggers
├─ Traffic rerouted to Ohio
├─ T=5 minutes: System back up
└─ Zero data loss!


SCENARIO 2: Database Corruption

T=0: Bug writes garbage to database
├─ Old data overwritten
├─ Corrupted data replicated everywhere
├─ Replication lag (5 seconds): Corruption spreads
└─ All copies corrupted

Without DR:
├─ No backup
├─ Manual recovery from logs: 2 hours
└─ Downtime: 2 hours

With DR:
├─ Hourly backups retained
├─ Detect corruption at T=30 minutes
├─ Restore from backup: 15 minutes old
├─ Data loss: 15 minutes of transactions
└─ Downtime: 45 minutes


SCENARIO 3: Ransomware Attack

T=0: Attacker encrypts all data
├─ Demand: $10 million
├─ Data inaccessible
└─ System down

Without DR:
├─ No unencrypted backup
├─ Must pay ransom (maybe)
└─ Months to recover

With DR:
├─ Backup isolated from network (air-gapped)
├─ Attacker can't access backup
├─ Restore from backup: 2 hours
├─ Don't pay ransom!
└─ Back to normal
```

### DR Metrics

```
RTO (Recovery Time Objective):
"How long can we be down?"

Low RTO (< 1 hour):
├─ Critical systems
├─ Requires: Hot standby, auto-failover
├─ Cost: Very expensive (2x infrastructure)
└─ Example: Banking, hospitals

Medium RTO (1-4 hours):
├─ Important systems
├─ Requires: Warm standby, manual failover
├─ Cost: Expensive (1.5x infrastructure)
└─ Example: SaaS platforms

High RTO (> 4 hours):
├─ Non-critical systems
├─ Requires: Cold standby, manual restore
├─ Cost: Moderate (regular backups)
└─ Example: Internal tools


RPO (Recovery Point Objective):
"How much data loss acceptable?"

Zero RPO:
├─ No data loss
├─ Requires: Synchronous replication
├─ Cost: Very expensive (high latency)
├─ Example: Financial transactions

Minutes RPO (5-60 min):
├─ Small data loss
├─ Requires: Regular backups + replication
├─ Cost: Expensive
└─ Example: E-commerce

Hours RPO (1-24 hours):
├─ Moderate data loss
├─ Requires: Daily backups
├─ Cost: Moderate
└─ Example: Analytics


FORMULA:
Downtime cost = (Hourly revenue loss) × (Hours down)

Example:
├─ Revenue: $1M/hour
├─ Downtime: 4 hours (no DR)
├─ Cost: $4M
├─ DR infrastructure: $500k/year
└─ Payback: 1 major disaster = pays for itself!
```

### Backup Strategies

```
BACKUP TYPES:

Full Backup:
├─ Copy all data
├─ Size: Large (100GB+)
├─ Time: Slow (hours)
├─ Storage: Expensive
└─ Frequency: Weekly

Example:
├─ Size: 1TB database
├─ Full backup: 1TB stored
└─ Once/week: 52TB/year


Incremental Backup:
├─ Copy only changed data
├─ Size: Small (10GB+)
├─ Time: Fast (minutes)
├─ Storage: Cheap
└─ Frequency: Daily

Example:
├─ Database: 1TB
├─ Daily incremental: 10GB/day
├─ Weekly: 70GB
└─ 7 incrementals + 1 full backup


Differential Backup:
├─ Copy changes since last full
├─ Size: Medium (50GB)
├─ Time: Medium (30 min)
├─ Frequency: Daily

Restore strategy:
├─ Full backup (1TB)
├─ Plus latest differential (50GB)
└─ Fast restore (don't need all incrementals)


BACKUP LOCATIONS:

Local Backup:
├─ Same data center
├─ Speed: Fast (near local)
├─ Cost: Cheap
└─ Risk: Fire destroys backup too!

Regional Backup:
├─ Different city (100 miles)
├─ Speed: Slower (network transfer)
├─ Cost: Moderate
└─ Safety: Survives local disaster

Cross-Region Backup:
├─ Different country (1000s miles)
├─ Speed: Very slow
├─ Cost: Expensive
└─ Safety: Survives regional catastrophe

Rule of 3-2-1:
├─ 3 copies of data
├─ On 2 different media types
├─ 1 copy offsite
└─ Survives most disasters
```

---

## 🔬 Advanced Explanation

### DR Architectures

```
ACTIVE-PASSIVE (Failover):

Active data center (Primary):
├─ Handles all traffic
├─ Writes to local database
├─ Replicates to passive
└─ Region: Virginia

Passive data center (Standby):
├─ Receives replicated data
├─ Idle, waiting
├─ Keeps database in sync
└─ Region: Ohio

Disaster strikes Virginia:
├─ Health checks fail
├─ DNS switches to Ohio
├─ Ohio becomes active
├─ Traffic flows to Ohio
└─ Recovery time: 5-10 minutes

Data loss:
├─ Async replication lag: 5 seconds
├─ Worst case: 5 seconds lost
└─ RPO: 5 seconds


ACTIVE-ACTIVE (Multi-Region):

Active data center 1 (Virginia):
├─ Handles traffic
├─ Writes to database
└─ Replicates to DC2

Active data center 2 (Ohio):
├─ Handles traffic
├─ Writes to database
└─ Replicates to DC1

Both serving traffic simultaneously:
├─ Traffic split 50-50
├─ Both writing
├─ Both replicating
└─ Conflict resolution needed

Disaster strikes Virginia:
├─ Ohio continues serving
├─ No failover needed!
├─ Recovery time: 0 seconds

Data loss:
├─ Multi-master replication: Eventual consistency
├─ Worst case: Data race/conflict
└─ RPO: 0 seconds


BACKUP RECOVERY:

Database corrupted:
├─ Detect corruption at T=30 min
├─ Start restore from T=0 backup
├─ Restore takes 2 hours
├─ Recovery time: 2 hours
└─ Data loss: 30 minutes (to corruption)


TIERED DR:

Tier 1 (Critical):
├─ RTO: < 1 hour
├─ Requires: Active-active or hot standby
├─ Example: Payments, auth

Tier 2 (Important):
├─ RTO: < 4 hours
├─ Requires: Warm standby
├─ Example: Orders, inventory

Tier 3 (Nice-to-have):
├─ RTO: < 24 hours
├─ Requires: Daily backups
├─ Example: Analytics, reports
```

### Chaos Engineering (DR Testing)

```
PROBLEM: DR untested

Disaster happens:
├─ Recovery plan exists
├─ But nobody tested it
├─ Steps outdated
├─ Tools don't exist
├─ Panic ensues
└─ Recovery fails

SOLUTION: Chaos Engineering

Regularly test DR:
├─ Kill random servers
├─ Simulate network partition
├─ Delete databases
├─ Trigger backups
└─ Practice recovery

Netflix's Chaos Monkey:
├─ Randomly kills instances in production
├─ Developers must handle it
├─ Builds resilience culture
├─ Discovered many issues

Example test:
├─ Kill primary database
├─ Time to failover: 3 minutes
├─ Were alerts sent? Yes
├─ Did backup work? Yes
├─ Update DR plan: OK
└─ Ready for real disaster!
```

---

## 🐍 Python Code Example

### ❌ Without Disaster Recovery

```python
# ===== WITHOUT DISASTER RECOVERY =====

import psycopg2

# Single database server
db = psycopg2.connect("dbname=shop host=db.primary.com")

def save_order(user_id, items):
    """Save order to single database"""
    
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, items, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id
    """, (user_id, str(items)))
    
    order_id = cursor.fetchone()[0]
    db.commit()
    
    return order_id

# Problem:
# ❌ Single database server
# ❌ No backups
# ❌ No replicas
# ❌ If datacenter burns: Data gone forever
# ❌ No recovery plan
```

### ✅ With Backup & Replication

```python
# ===== WITH BACKUP & REPLICATION =====

import psycopg2
import psycopg2.pool
from datetime import datetime
import subprocess

# Primary database (Virginia)
primary_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    "dbname=shop host=db.primary.us-east-1.com user=app"
)

# Replica database (Ohio)
replica_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    "dbname=shop host=db.replica.us-west-1.com user=app"
)

class BackupManager:
    """Manage backups and replication"""
    
    def __init__(self):
        self.primary_pool = primary_pool
        self.replica_pool = replica_pool
    
    def save_order(self, user_id, items):
        """Save order to primary (auto-replicated)"""
        
        conn = self.primary_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (user_id, items, created_at)
                VALUES (%s, %s, NOW())
                RETURNING id
            """, (user_id, str(items)))
            
            order_id = cursor.fetchone()[0]
            conn.commit()
            
            # Replication happens automatically
            # (PostgreSQL streams WAL to replica)
            
            return order_id
        
        finally:
            self.primary_pool.putconn(conn)
    
    def create_backup(self):
        """Create point-in-time backup"""
        
        timestamp = datetime.utcnow().isoformat()
        backup_dir = f"/backups/shop-{timestamp}"
        
        print(f"Creating backup: {backup_dir}")
        
        # Use pg_basebackup
        result = subprocess.run([
            'pg_basebackup',
            '-h', 'db.primary.us-east-1.com',
            '-D', backup_dir,
            '-Ft',  # Tar format
            '-z',   # Compressed
            '-Pv'   # Verbose progress
        ], capture_output=True)
        
        if result.returncode == 0:
            print(f"✓ Backup created: {backup_dir}")
            
            # Copy to S3 (remote storage)
            subprocess.run([
                'aws', 's3', 'cp',
                backup_dir,
                f's3://backups-prod/shop-{timestamp}/',
                '--recursive'
            ])
            
            print(f"✓ Backup uploaded to S3")
            return backup_dir
        
        else:
            print(f"✗ Backup failed: {result.stderr}")
            return None
    
    def verify_replication(self):
        """Check replication lag"""
        
        # Get primary LSN (log sequence number)
        primary_conn = self.primary_pool.getconn()
        try:
            cursor = primary_conn.cursor()
            cursor.execute("SELECT pg_current_wal_lsn()")
            primary_lsn = cursor.fetchone()[0]
        finally:
            self.primary_pool.putconn(primary_conn)
        
        # Get replica LSN
        replica_conn = self.replica_pool.getconn()
        try:
            cursor = replica_conn.cursor()
            cursor.execute("SELECT pg_last_xact_replay_timestamp()")
            replica_timestamp = cursor.fetchone()[0]
        finally:
            self.replica_pool.putconn(replica_conn)
        
        print(f"Primary LSN: {primary_lsn}")
        print(f"Replica LSN timestamp: {replica_timestamp}")
        
        return True
    
    def promote_replica(self):
        """Promote replica to primary (manual failover)"""
        
        print("Promoting replica to primary...")
        
        replica_conn = self.replica_pool.getconn()
        try:
            cursor = replica_conn.cursor()
            cursor.execute("SELECT pg_promote()")
            replica_conn.commit()
            
            print("✓ Replica promoted to primary")
            return True
        
        finally:
            self.replica_pool.putconn(replica_conn)
    
    def restore_from_backup(self, backup_path):
        """Restore database from backup"""
        
        print(f"Restoring from backup: {backup_path}")
        
        # Extract backup
        result = subprocess.run([
            'tar', '-xzf', f'{backup_path}/base.tar.gz',
            '-C', '/var/lib/postgresql/new_cluster'
        ], capture_output=True)
        
        if result.returncode == 0:
            print("✓ Backup restored")
            return True
        
        else:
            print(f"✗ Restore failed: {result.stderr}")
            return False

# Usage
backup_mgr = BackupManager()

# Regular operations
order_id = backup_mgr.save_order(user_id=123, items=['item1', 'item2'])
print(f"Order created: {order_id}")

# Daily backup
backup_mgr.create_backup()

# Verify replication
backup_mgr.verify_replication()

# In case of disaster:
# backup_mgr.promote_replica()  # Failover
# backup_mgr.restore_from_backup("/path/to/backup")  # Restore

# Benefits:
# ✅ Replicated to another region
# ✅ Daily backups to S3
# ✅ Can failover automatically
# ✅ Can restore from backup
```

### ✅ Production DR (Complete Strategy)

```python
# ===== PRODUCTION DR STRATEGY =====

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import boto3

@dataclass
class DRMetrics:
    """DR metrics tracking"""
    rto_minutes: int  # Recovery time objective
    rpo_minutes: int  # Recovery point objective
    last_backup: datetime
    replication_lag: float
    backup_verified: bool

class DisasterRecoveryManager:
    """Production-grade DR management"""
    
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.cloudwatch = boto3.client('cloudwatch')
        self.metrics = {}
    
    def get_metrics(self) -> DRMetrics:
        """Get current DR metrics"""
        
        return DRMetrics(
            rto_minutes=5,  # Can failover in 5 min
            rpo_minutes=1,  # Max 1 min data loss
            last_backup=datetime.utcnow() - timedelta(hours=1),
            replication_lag=0.5,  # 500ms lag
            backup_verified=True
        )
    
    def failover_to_region(self, target_region: str):
        """Automatic failover to another region"""
        
        print(f"Initiating failover to {target_region}...")
        
        # 1. Promote replica
        print("1. Promoting replica...")
        
        # 2. Update DNS
        print("2. Updating DNS...")
        
        # 3. Update service discovery
        print("3. Updating service discovery...")
        
        # 4. Verify traffic flowing
        print("4. Verifying traffic...")
        
        print(f"✓ Failover to {target_region} complete")
    
    def verify_dr_readiness(self) -> bool:
        """Verify DR plan is ready"""
        
        checks = {
            'backups_recent': self._check_backups(),
            'replication_lag': self._check_replication_lag(),
            'failover_tested': self._check_failover_tested(),
            'runbook_updated': self._check_runbook(),
        }
        
        all_pass = all(checks.values())
        
        print("DR Readiness Check:")
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
        
        return all_pass
    
    def _check_backups(self) -> bool:
        """Verify backups exist and are recent"""
        # Implementation
        return True
    
    def _check_replication_lag(self) -> bool:
        """Verify replication lag acceptable"""
        # Implementation
        return True
    
    def _check_failover_tested(self) -> bool:
        """Verify failover was tested recently"""
        # Implementation
        return True
    
    def _check_runbook(self) -> bool:
        """Verify runbook is up to date"""
        # Implementation
        return True

# Usage
dr_mgr = DisasterRecoveryManager()

# Check readiness
dr_mgr.verify_dr_readiness()

# Get metrics
metrics = dr_mgr.get_metrics()
print(f"RTO: {metrics.rto_minutes} minutes")
print(f"RPO: {metrics.rpo_minutes} minutes")

# In case of disaster
dr_mgr.failover_to_region("us-west-1")

# Benefits:
# ✅ DR plan verified
# ✅ Metrics tracked
# ✅ Automatic failover ready
# ✅ Production-ready
```

---

## 💡 Mini Project: "Build DR System"

### Phase 1: Backups ⭐

**Requirements:**
- Daily database backups
- Upload to S3
- Verify backups
- Track backup schedule

---

### Phase 2: Replication ⭐⭐

**Requirements:**
- Setup replica database
- Monitor replication lag
- Manual failover process
- Test failover

---

### Phase 3: Automated DR ⭐⭐⭐

**Requirements:**
- Automatic failover
- Multi-region setup
- Chaos engineering tests
- Full runbook

---

## ⚖️ DR Strategy Comparison

| Strategy | RTO | RPO | Cost | Complexity |
|----------|-----|-----|------|-----------|
| **Backups only** | Hours | Hours | Low | Low |
| **Backup + Replication** | Minutes | Minutes | Medium | Medium |
| **Hot standby** | Seconds | 0 | High | High |
| **Active-active** | 0 | 0 | Very High | Very High |

---

## ❌ Common Mistakes

### Mistake 1: Never Testing DR

```python
# ❌ Create backup, never test restore
backup_created = True
# But: Does restore actually work?
# Find out during real disaster: Too late!

# ✅ Test restore regularly
backup_mgr.create_backup()
backup_mgr.test_restore()  # Actually restore
backup_mgr.verify_data()   # Verify integrity
```

### Mistake 2: Backups in Same Region

```python
# ❌ Backup in Virginia, data center burns
backup = create_backup("us-east-1")
# Fire destroys both primary and backup!

# ✅ Backup in different region
backup = create_backup("us-east-1")
upload_to_s3_region("us-west-1")  # Cross-region backup
```

### Mistake 3: Outdated Runbook

```python
# ❌ Runbook written 2 years ago
# Tools changed
# Passwords changed
# Team structure changed
# Runbook useless during disaster!

# ✅ Update runbook regularly
# Test recovery procedures
# Keep passwords current
# Document recent changes
```

---

## 📚 Additional Resources

**DR Planning:**
- [AWS Disaster Recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/)
- [DR Best Practices](https://www.gartner.com/en/information-technology/glossary/disaster-recovery-dr)

**Chaos Engineering:**
- [Chaos Monkey (Netflix)](https://github.com/Netflix/chaosmonkey)
- [Gremlin (Chaos as a Service)](https://www.gremlin.com/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **What's RTO vs RPO?**
   - Answer: RTO = time to recover; RPO = data loss acceptable

2. **Backup strategies?**
   - Answer: Full, incremental, differential

3. **Active-passive vs active-active?**
   - Answer: Passive = one way failover; Active = both running

4. **Why test DR?**
   - Answer: Real disaster won't be like your assumptions

5. **What's chaos engineering?**
   - Answer: Intentionally break things to find weaknesses

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Plan:** "In case of disaster, we'll recover in 4 hours"
>
> **Reality:** Fire starts
>
> **Team:** "Where's the runbook?"
>
> **Someone:** "It's in the burning data center"
>
> **Everyone:** "OK, we'll wing it"
>
> **4 hours later:** "We're back online!"
>
> **Everyone:** "That was lucky, let's write that runbook now"

---

[← Back to Main](../README.md) | [Previous: Retry & Backoff Mechanisms](37-retry-backoff.md) | [Next: Blue-Green & Canary Deployments](39-blue-green-canary.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐⭐ Advanced (operational resilience)  
**Time to Read:** 26 minutes  
**Time to Implement:** 8-12 hours per phase  

---

*Disaster Recovery: Hope for the best, prepare for the worst, expect the unexpected.* 🚀