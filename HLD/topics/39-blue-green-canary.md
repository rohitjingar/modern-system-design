# 39. Blue-Green & Canary Deployments

Blue-Green deployment: you have two identical environments. Deploy to the green one while blue serves traffic. If green works, switch traffic. If green fails, users never notice. Sounds perfect until you realize it's twice the infrastructure cost. Canary deployment: deploy to 1% of users first. If it breaks, only 1% suffer. Then you have to explain to those 1% why they got the broken version. Welcome to modern deployments! 🚀🐤

[← Back to Main](../README.md) | [Previous: Disaster Recovery](38-disaster-recovery.md) | [Next: Chaos Engineering](40-chaos-engineering.md)

---

## 🎯 Quick Summary

**Blue-Green Deployment** maintains two identical environments (blue live, green staging). Deploy new version to green, test fully, switch traffic instantly. Zero downtime, instant rollback. Cost: 2x infrastructure. **Canary Deployment** rolls out to small percentage (1-5%) first, monitor, gradually increase. Catches bugs before hitting all users. Cost: low, but slower rollout. Netflix uses canaries, Amazon uses blue-green for critical services. Trade-off: cost vs safety vs rollout speed.

Think of it as: **Blue-Green = Safety Switch, Canary = Gradual Testing**

---

## 🌟 Beginner Explanation

### Deployment Strategies

```
TRADITIONAL DEPLOYMENT (Rolling):

V1 running on 10 servers
├─ Stop server 1
├─ Deploy V2 to server 1
├─ Start server 1 (now V2)
├─ Stop server 2
├─ Deploy V2 to server 2
├─ ... repeat for all servers

Problem:
├─ Mixed V1 and V2 during deployment
├─ API changes break things
├─ If V2 broken: Already deployed to 5 servers
├─ Slow rollback (must re-deploy V1)

Timeline:
T=0: V1 only
T=1: 1 V2, 9 V1 (mixed!)
T=5: 5 V2, 5 V1 (mixed!)
T=10: V2 only
└─ 10 minutes mixed state


BLUE-GREEN DEPLOYMENT:

Blue environment (V1 running):
├─ 10 servers running V1
├─ Handling all traffic
└─ Production

Green environment (V2 preparing):
├─ 10 servers (identical setup)
├─ Deploy V2 to all
├─ Test fully
├─ Staging (no traffic)

Switch:
├─ All tests pass
├─ Switch load balancer
├─ Traffic: Blue → Green instantly
└─ Green now production

Timeline:
T=0: Blue=V1 (100%), Green=V1 (0%)
T=5: Blue=V1 (100%), Green=V2 ready (0%)
T=5.001: Blue=V1 (0%), Green=V2 (100%) → Instant!
└─ No mixed state!

Rollback:
├─ V2 broken? No problem
├─ Switch back: Green → Blue instantly
└─ Back to V1 in 1 second!


CANARY DEPLOYMENT:

V1 running on 100 servers
├─ Deploy V2 to 1 server (canary)
├─ Route 1% traffic to canary
├─ Monitor metrics
├─ No errors? Increase to 5%
├─ No errors? Increase to 25%
├─ No errors? Increase to 100%

Timeline:
T=0: 100% V1
T=1: 99% V1, 1% V2 (canary)
T=2: 95% V1, 5% V2 (if canary healthy)
T=5: 75% V1, 25% V2 (if canary healthy)
T=10: 0% V1, 100% V2 (if canary healthy)

Benefits:
✅ Catches bugs before mass deployment
✅ Gradual rollout
✅ Easy rollback (just shift traffic)
✅ Normal infrastructure cost
❌ Slower than blue-green
```

### Comparison

```
DEPLOYMENT STRATEGY COMPARISON:

Rolling Update:
├─ Cost: 1x (reuse servers)
├─ Speed: Slow (gradual)
├─ Risk: Medium (mixed versions)
├─ Rollback: Slow (must re-deploy)
└─ Use case: Low-risk updates

Blue-Green:
├─ Cost: 2x (dual infrastructure)
├─ Speed: Instant (switch at once)
├─ Risk: Low (no mixed state)
├─ Rollback: Instant (switch back)
└─ Use case: High-risk, critical services

Canary:
├─ Cost: 1x (gradual shift)
├─ Speed: Medium (gradual)
├─ Risk: Low (catches bugs early)
├─ Rollback: Fast (shift traffic back)
└─ Use case: Most services (default!)

Shadow:
├─ Cost: 1.5x (duplicate traffic)
├─ Speed: N/A (testing only)
├─ Risk: None (shadow doesn't serve)
├─ Use case: Testing major changes
```


### Canary Monitoring

```
CANARY METRICS (Watch for):

Error Rate:
├─ Canary error rate > 1%? → Rollback!
├─ Example: 0.1% for V1, 1.5% for V2
└─ Stop deploying immediately

Latency:
├─ Canary p99 latency > V1 by 50%? → Rollback!
├─ Example: V1 = 100ms, V2 = 200ms
└─ Users notice slowness

Memory Usage:
├─ Canary memory spike > 30%? → Rollback!
├─ Example: Memory leak in V2
└─ Servers crash soon

CPU Usage:
├─ Canary CPU > 80%? → Rollback!
├─ Example: Inefficient algorithm
└─ Servers struggle

Customer Complaints:
├─ Spike in support tickets? → Investigate
├─ Real user impact, not just metrics
└─ Human judgment matters

Alerting:
├─ If ANY metric bad: Alert engineer
├─ Don't wait for "all clear"
├─ Err on side of caution
└─ Can always fix and re-deploy
```

---

## 🔬 Advanced Explanation

### Blue-Green Architecture

```
SETUP:

Load Balancer (DNS):
├─ Blue pool: 10 servers (V1)
├─ Green pool: 10 servers (V1 initially)
└─ Initially routes to Blue

Pipeline:

1. Deploy stage:
   ├─ Build V2 image
   ├─ Start servers in Green pool
   ├─ Deploy V2 to Green
   └─ Green now running V2

2. Test stage:
   ├─ Run smoke tests
   ├─ Run integration tests
   ├─ Check health endpoints
   ├─ Load test Green
   └─ All must pass

3. Switch stage:
   ├─ Update load balancer config
   ├─ Change to route to Green
   ├─ Blue now idle
   └─ V2 now serving all traffic

4. Verify stage:
   ├─ Monitor metrics
   ├─ Check user reports
   ├─ If all good: Done!
   ├─ If problem: Switch back to Blue
   └─ Rollback in seconds

5. Cleanup stage:
   ├─ After N hours (24h) of Green stability
   ├─ Stop Blue servers
   ├─ Prepare Blue for next deployment
   └─ Now Blue and Green swap roles


FAILURE SCENARIOS:

Test fails:
├─ Fix code
├─ Rebuild V2
├─ Re-test
├─ Blue still running (users unaffected)
└─ Zero impact

Production issue after switch:
├─ Switch back: Green → Blue instantly
├─ V1 now serving traffic
├─ Customers likely didn't notice
└─ Investigate issue, fix, try again
```

### Canary Implementation

```
CANARY DEPLOYMENT PROCESS:

Phase 1: Canary (1-5% traffic)
├─ Deploy V2 to 1-2 servers
├─ Route 1-5% traffic to V2
├─ Monitor for 30 minutes
├─ Thresholds:
│  ├─ Error rate < 0.5%
│  ├─ Latency increase < 20%
│  ├─ CPU stable
│  └─ Memory stable
└─ If passes: Continue

Phase 2: Early (10-25% traffic)
├─ Deploy V2 to more servers
├─ Route 10-25% traffic to V2
├─ Monitor for 1 hour
├─ Same thresholds
└─ If passes: Continue

Phase 3: Main (50% traffic)
├─ Deploy V2 to half servers
├─ Route 50% traffic
├─ Monitor for 2 hours
├─ Broader metrics check
└─ If passes: Continue

Phase 4: Full (100% traffic)
├─ Deploy V2 to all servers
├─ Route 100% traffic
├─ Monitor for 24 hours
├─ High alert state
└─ If stable: Deployment complete


ROLLBACK CRITERIA:

Automatic rollback if:
├─ Error rate > 1% (vs baseline)
├─ P99 latency > baseline × 1.5
├─ CPU > 85%
├─ Memory > 85%
├─ Disk fill rate > 50%/hour
└─ Any critical error in logs

Manual rollback if:
├─ Customer complaints spike
├─ Unexpected behavior
├─ "This looks suspicious"
└─ Better safe than sorry!
```

### Traffic Splitting

```
IMPLEMENTATION METHODS:

Method 1: Weighted Load Balancer
├─ Load balancer has weight config
├─ Blue: 99%, Green: 1%
├─ Gradually adjust weights
└─ Examples: Nginx, HAProxy

Method 2: Service Mesh (Istio)
├─ VirtualService rules
├─ Can route by header/cookie
├─ A/B testing: Route by user ID
├─ Geographic: Route by location
└─ Advanced traffic splitting

Method 3: Feature Flags
├─ Both versions running
├─ Flag controls which code path
├─ Can toggle instantly
├─ Gradual feature rollout
└─ No deployment needed

Method 4: DNS
├─ Two DNS records: blue, green
├─ Update weight in DNS
├─ Slower propagation (TTL)
├─ Not ideal for fast rollback
└─ But used in some systems
```

---

## 🐍 Python Code Example

### ❌ Without Safe Deployment (Big Bang)

```python
# ===== BIG BANG DEPLOYMENT (RISKY) =====

import subprocess

def deploy_v2():
    """Deploy V2 to all servers at once"""
    
    servers = [f"server-{i}.prod.com" for i in range(1, 11)]
    
    for server in servers:
        print(f"Deploying to {server}...")
        
        # Stop server
        subprocess.run(['ssh', server, 'systemctl stop app'])
        
        # Deploy V2
        subprocess.run(['ssh', server, 'git pull && python setup.py install'])
        
        # Start server
        subprocess.run(['ssh', server, 'systemctl start app'])
    
    print("All servers updated to V2")

# Problem:
# ❌ All servers updated simultaneously
# ❌ If V2 broken: All users see error
# ❌ Must manually fix all 10 servers
# ❌ Slow rollback
# ❌ No testing before production
```

### ✅ Blue-Green Deployment

```python
# ===== BLUE-GREEN DEPLOYMENT =====

import subprocess
import time

class BlueGreenDeployment:
    """Blue-green deployment manager"""
    
    def __init__(self):
        self.blue_servers = [f"blue-{i}.prod.com" for i in range(1, 11)]
        self.green_servers = [f"green-{i}.prod.com" for i in range(1, 11)]
        self.load_balancer = "lb.prod.com"
        self.active_pool = "blue"  # Currently serving traffic
    
    def deploy_to_green(self):
        """Deploy V2 to green environment"""
        
        print("1. Deploying to green environment...")
        
        for server in self.green_servers:
            print(f"  Deploying to {server}...")
            subprocess.run(['ssh', server, 'git pull && python setup.py install'])
        
        print("✓ Green deployment complete")
    
    def test_green(self):
        """Test green environment before switching"""
        
        print("2. Testing green environment...")
        
        # Smoke tests
        for server in self.green_servers:
            response = subprocess.run(
                ['curl', '-f', f'http://{server}:8000/health'],
                capture_output=True
            )
            if response.returncode != 0:
                print(f"✗ Health check failed on {server}")
                return False
        
        print("✓ All health checks passed")
        
        # Load test
        print("  Load testing...")
        result = subprocess.run([
            'ab', '-n', '10000', '-c', '100',
            f'http://{self.green_servers[0]}:8000/api/test'
        ], capture_output=True)
        
        print("✓ Load test completed")
        
        return True
    
    def switch_traffic(self):
        """Switch traffic from blue to green"""
        
        print("3. Switching traffic...")
        
        # Update load balancer
        config = f"""
        upstream app {{
            server {self.green_servers[0]}:8000;
            # ... all green servers
        }}
        """
        
        # Update load balancer config
        with open('/tmp/lb-config.conf', 'w') as f:
            f.write(config)
        
        subprocess.run(['scp', '/tmp/lb-config.conf', f'{self.load_balancer}:/etc/nginx/'])
        subprocess.run(['ssh', self.load_balancer, 'systemctl reload nginx'])
        
        self.active_pool = "green"
        print("✓ Traffic switched to green")
    
    def verify_traffic(self):
        """Verify traffic is flowing correctly"""
        
        print("4. Verifying traffic...")
        
        time.sleep(5)  # Wait for traffic to stabilize
        
        # Check error rate
        errors = 0
        total = 100
        
        for i in range(total):
            response = subprocess.run(
                ['curl', '-s', f'http://{self.load_balancer}/api/test'],
                capture_output=True
            )
            if response.returncode != 0:
                errors += 1
        
        error_rate = errors / total
        
        if error_rate > 0.01:  # > 1% error
            print(f"✗ Error rate too high: {error_rate:.2%}")
            return False
        
        print(f"✓ Error rate acceptable: {error_rate:.2%}")
        return True
    
    def rollback_if_needed(self):
        """Rollback to blue if issues detected"""
        
        print("5. Checking for issues...")
        
        if not self.verify_traffic():
            print("✗ Issues detected, rolling back...")
            
            # Switch back to blue
            subprocess.run(['ssh', self.load_balancer, 'systemctl reload nginx'])
            
            self.active_pool = "blue"
            print("✓ Rolled back to blue")
            return False
        
        print("✓ All checks passed, staying on green")
        return True
    
    def deploy(self):
        """Execute full blue-green deployment"""
        
        print("\n=== Blue-Green Deployment ===")
        print(f"Current active: {self.active_pool}")
        
        # Deploy
        self.deploy_to_green()
        
        # Test
        if not self.test_green():
            print("✗ Testing failed, aborting deployment")
            return False
        
        # Switch
        self.switch_traffic()
        
        # Verify
        if not self.rollback_if_needed():
            return False
        
        print("\n✓ Deployment successful!")
        return True

# Usage
deployment = BlueGreenDeployment()
deployment.deploy()

# Benefits:
# ✅ No mixed V1/V2 state
# ✅ Instant switch
# ✅ Easy rollback (1 second)
# ✅ Full testing before switch
# ✅ Zero perceived downtime
```

### ✅ Canary Deployment

```python
# ===== CANARY DEPLOYMENT =====

import time
import random

class CanaryDeployment:
    """Canary deployment manager"""
    
    def __init__(self):
        self.servers = [f"server-{i}.prod.com" for i in range(1, 101)]
        self.load_balancer = "lb.prod.com"
        self.metrics = {}
    
    def deploy_canary(self):
        """Deploy V2 to canary servers (1-2 servers)"""
        
        print("1. Deploying canary (1 server)...")
        
        canary_server = self.servers[0]
        print(f"  Deploying to {canary_server}...")
        
        import subprocess
        subprocess.run(['ssh', canary_server, 'git pull && python setup.py install'])
        
        print("✓ Canary deployed")
        return [canary_server]
    
    def route_traffic(self, percentage, canary_servers):
        """Route X% traffic to canary"""
        
        print(f"2. Routing {percentage}% traffic to canary...")
        
        # Update load balancer weights
        print(f"✓ {percentage}% traffic routed to canary")
    
    def monitor_canary(self, duration_minutes=5):
        """Monitor canary metrics"""
        
        print(f"3. Monitoring canary for {duration_minutes} minutes...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration_minutes * 60:
            # Get metrics
            error_rate = random.uniform(0.001, 0.002)  # Mock: 0.1-0.2%
            p99_latency = random.uniform(90, 110)  # Mock: 90-110ms
            
            print(f"  Error rate: {error_rate:.2%}, P99: {p99_latency:.0f}ms")
            
            # Check thresholds
            if error_rate > 0.01:  # > 1% error
                print(f"✗ Error rate too high: {error_rate:.2%}")
                return False
            
            if p99_latency > 150:  # > 150ms
                print(f"✗ Latency too high: {p99_latency:.0f}ms")
                return False
            
            time.sleep(10)
        
        print("✓ Canary monitoring passed")
        return True
    
    def gradually_deploy(self):
        """Gradual deployment: canary → 10% → 50% → 100%"""
        
        print("\n=== Canary Deployment ===\n")
        
        canary_servers = self.deploy_canary()
        
        # Phase 1: Canary (1%)
        self.route_traffic(1, canary_servers)
        if not self.monitor_canary(duration_minutes=5):
            print("✗ Canary failed, rolling back")
            return False
        
        # Phase 2: Early (10%)
        print("\nPhase 2: Increasing to 10%...")
        servers_10 = self.servers[:10]
        for s in servers_10:
            print(f"  Deploying to {s}...")
        self.route_traffic(10, servers_10)
        if not self.monitor_canary(duration_minutes=10):
            print("✗ Phase 2 failed, rolling back")
            return False
        
        # Phase 3: Main (50%)
        print("\nPhase 3: Increasing to 50%...")
        servers_50 = self.servers[:50]
        for s in servers_50[10:]:
            print(f"  Deploying to {s}...")
        self.route_traffic(50, servers_50)
        if not self.monitor_canary(duration_minutes=15):
            print("✗ Phase 3 failed, rolling back")
            return False
        
        # Phase 4: Full (100%)
        print("\nPhase 4: Increasing to 100%...")
        for s in self.servers[50:]:
            print(f"  Deploying to {s}...")
        self.route_traffic(100, self.servers)
        if not self.monitor_canary(duration_minutes=30):
            print("✗ Phase 4 failed, rolling back")
            return False
        
        print("\n✓ Canary deployment successful!")
        return True

# Usage
canary = CanaryDeployment()
canary.gradually_deploy()

# Benefits:
# ✅ Gradual rollout (catches bugs early)
# ✅ Only 1% affected if broken
# ✅ Normal infrastructure cost
# ✅ Can rollback easily
# ❌ Slower than blue-green
```

---

## 💡 Mini Project: "Implement Safe Deployment"

### Phase 1: Blue-Green ⭐

**Requirements:**
- Two environments setup
- Deploy to inactive
- Test before switch
- Instant rollback

---

### Phase 2: Canary ⭐⭐

**Requirements:**
- Canary phase (1%)
- Gradual increase
- Metric monitoring
- Automatic rollback

---

### Phase 3: Advanced ⭐⭐⭐

**Requirements:**
- A/B testing
- Feature flags
- Shadow traffic
- Multi-region

---

## ⚖️ Deployment Strategies Comparison

| Strategy | Risk | Speed | Cost | Rollback |
|----------|------|-------|------|----------|
| **Rolling** | High | Slow | 1x | Slow |
| **Blue-Green** | Low | Instant | 2x | Instant |
| **Canary** | Low | Medium | 1x | Fast |
| **Shadow** | None | N/A | 1.5x | N/A |

---

## ❌ Common Mistakes

### Mistake 1: No Automated Tests

```python
# ❌ Deploy and hope
deploy_to_green()
switch_traffic()
# What if V2 broken?

# ✅ Comprehensive testing
deploy_to_green()
run_smoke_tests()
run_integration_tests()
run_load_tests()
check_health_endpoints()
# Only then switch
```

### Mistake 2: Canary Too Small

```python
# ❌ 0.1% canary
# Might miss bugs
# 1 user gets broken version

# ✅ 2-5% canary
# More realistic traffic
# Catches more bugs
# 20-50 users maximum impact
```

### Mistake 3: No Automatic Rollback

```python
# ❌ Monitor manually
# Humans miss issues
# Takes 10 minutes to notice

# ✅ Automatic rollback
# Metrics monitored continuously
# Rollback in < 1 minute
# Humans get alert
```

---

## 📚 Additional Resources

**Deployment Strategies:**
- [Blue-Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary Releases](https://martinfowler.com/bliki/CanaryRelease.html)

**Tools:**
- [Flagger (Canary automation)](https://flagger.app/)
- [Spinnaker (Deployment platform)](https://www.spinnaker.io/)


---

## 🎯 Before You Leave

**Can you answer these?**

1. **Blue-green vs canary?**
   - Answer: Blue-green instant, canary gradual

2. **When to use blue-green?**
   - Answer: Critical services, high risk

3. **When to use canary?**
   - Answer: Most services, default choice

4. **Canary success criteria?**
   - Answer: Error rate, latency, resource usage

5. **How to rollback?**
   - Answer: Switch traffic/feature flag

**If you got these right, you're ready for the next topic!** ✅

---

## 🤣 Closing Thoughts

> **Manager:** "Deploy the new version!"
>
> **Engineer:** "OK, deploying to blue..."
>
> **5 minutes later:** "Testing... all good!"
>
> **Switch:** Blue → Green (instant)
>
> **2 minutes later:** "OH NO, ERRORS!"
>
> **Switch:** Green → Blue (instant)
>
> **Manager:** "What happened?"
>
> **Engineer:** "A feature worked great in staging but broke in production"
>
> **Everyone:** "Classic!" 🤷

---

[← Back to Main](../README.md) | [Previous: Disaster Recovery](38-disaster-recovery.md) | [Next: Chaos Engineering](40-chaos-engineering.md)

---

**Last Updated:** November 11, 2025  
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced (DevOps)  
**Time to Read:** 25 minutes  
**Time to Implement:** 5-8 hours per phase  

---

*Blue-Green & Canary: Making deployments safe, predictable, and rollback-friendly.* 🚀