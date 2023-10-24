from mininet.topo import Topo

class NetworkTopo(Topo):
    def build(self, **_opts):
        # Add 2 routers in two different subnets
        r1 = self.addHost('r1', ip='10.0.0.1/24')
        r2 = self.addHost('r2', ip='10.1.0.1/24')

        # Add 2 switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add host-switch links in the same subnet
        self.addLink(s1,
                     r1)
                    #  intfName2='r1-eth1',
                    #  params2={'ip': '10.0.0.1/24'})

        self.addLink(s2,
                     r2)
                    #  intfName2='r2-eth1',
                    #  params2={'ip': '10.1.0.1/24'})

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(r1,
                     r2,
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': '10.100.0.1/24'},
                     params2={'ip': '10.100.0.2/24'})

        # Adding hosts specifying the default route
        h1 = self.addHost(name='h1',
                          ip='10.0.0.251/24',
                          defaultRoute='via 10.0.0.1')
        h2 = self.addHost(name='h2',
                          ip='10.1.0.252/24',
                          defaultRoute='via 10.1.0.1')

        # Add host-switch links
        self.addLink(h1, s1)
        self.addLink(h2, s2)