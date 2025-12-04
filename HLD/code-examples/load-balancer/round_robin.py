"""
Round-Robin Load Balancer
Distributes requests evenly across servers
"""

class RoundRobinLoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0
    
    def route_request(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server
