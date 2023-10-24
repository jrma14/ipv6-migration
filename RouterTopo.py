from mininet.topo import Topo

class RouterTopo(Topo):
    def build(self, **_opts):
        # Add 2 routers in two different subnets
        r1 = self.addHost('r1', ip='10.1.0.1/24')
        r2 = self.addHost('r2', ip='10.2.0.1/24')

        s1 = self.addSwitch('s1')
        self.addLink(s1,r1, intfName1='s1-eth0', intfName2='r1-lan')
        # Add router-router link in a new subnet for the router-router connection

        # Adding hosts specifying the default route
        h1 = self.addHost(name='h1',
                          ip='10.1.0.2/24',
                          defaultRoute='via 10.1.0.1')
        h2 = self.addHost(name='h2',
                          ip='10.2.0.2/24',
                          defaultRoute='via 10.2.0.1')
        h3 = self.addHost(name='h3',
                          ip='10.1.0.3/24',
                          defaultRoute='via 10.1.0.1')
        
        # Add host-switch links
        self.addLink(h1, s1, intfName1='h1-eth0', intfName2='s1-eth1')
        self.addLink(h3, s1, intfName1='h3-eth0', intfName2='s1-eth2')
        self.addLink(h2, r2, intfName1='h2-eth0', intfName2='r2-lan')
        self.addLink(r1, r2, intfName1='r1-wan', intfName2='r2-wan')