import shutil
from mininet.net import Mininet
from mininet.node import OVSController, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from NetworkTopo import NetworkTopo
from MyTopo import MyTopology
from RouterTopo import RouterTopo
import os

def ipv6_lan_simulation():
    topo = MyTopology()
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    s1 = net.get('s1')

    h1, h2 = net.get('h1', 'h2')
    h1.cmd('ip -6 addr add 2001:db8::1/64 dev h1-eth0')
    h2.cmd('ip -6 addr add 2001:db8::2/64 dev h1-eth0')

    print("IPv4 Ping:")
    print(h1.cmd('ping -c 3 192.168.0.2'))

    print("\nIPv6 Ping:")
    print(h1.cmd('ping -c 3 2001:db8::1'))

    net.stop()

def ipv6_2hop_simulation():
    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    h1, h2, r1, r2 = net.get('h1', 'h2','r1','r2')
    r1.cmd('ip route add 10.1.0.0/24 via 10.100.0.2')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('ip route add 10.0.0.0/24 via 10.100.0.1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    h1.cmd('ip -6 addr add 2001:db8::1/64 dev h1-eth0')
    h2.cmd('ip -6 addr add 2001:db8::2/64 dev h1-eth0')

    print("IPv4 Ping:")
    print(h1.cmd('ping -c 3 10.1.0.252'))

    print("\nIPv6 Ping:")
    print(h1.cmd('ping -c 3 2001:db8::2'))
    CLI(net)
    net.stop()

def ipv6_cross_router():
    topo = RouterTopo()
    net = Mininet(topo=topo, controller=OVSController)
    net.start()
    # net.pingAll()

    h1, h2, r1, r2, h3 = net.get('h1', 'h2','r1','r2', 'h3')

    r1.cmd('ip route add 10.2.0.0/24 dev r1-wan via 10.2.0.1 onlink')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    r2.cmd('ip route add 10.1.0.0/24 dev r2-wan via 10.1.0.1 onlink')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    r1.cmd('tcpdump -U -w caps/r1.pcap -i r1-wan not ip &')
    r2.cmd('tcpdump -U -w caps/r2.pcap -i r2-wan not ip &')


    subnet1 = '2001:db8::'
    r1LanAddr = f'{subnet1}1:0'
    r1WanAddr = f'{subnet1}1:1'

    subnet2 = '2002:db8::'
    r2LanAddr = f'{subnet2}1:0'
    r2WanAddr = f'{subnet2}1:1'
    ## ipv6 setup
    r1.cmd(f'ip -6 route add {subnet2}/64 dev r1-wan via {r2WanAddr} onlink')  
    r1.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')

    r2.cmd(f'ip -6 route add {subnet1}/64 dev r2-wan via {r1WanAddr} onlink')
    r2.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')


    ### Addrs
    r1.cmd(f'ip -6 addr add {r1LanAddr}/64 dev r1-lan')
    r1.cmd(f'ip -6 addr add {r1WanAddr}/64 dev r1-wan')
    r1.cmd(f'ip -6 route del {subnet1}/64 dev r1-wan')
    
    r2.cmd(f'ip -6 addr add {r2LanAddr}/64 dev r2-lan')
    r2.cmd(f'ip -6 addr add {r2WanAddr}/64 dev r2-wan')
    r2.cmd(f'ip -6 route del {subnet2}/64 dev r2-wan')

    h1.cmd(f'ip -6 addr add {subnet1}2:1/64 dev h1-eth0')
    h1.cmd(f'ip -6 route add default via {subnet1}1:0')
    h2.cmd(f'ip -6 addr add {subnet2}2:1/64 dev h2-eth0')
    h2.cmd(f'ip -6 route add default via {subnet2}1:0')
    h3.cmd(f'ip -6 addr add {subnet1}2:2/64 dev h3-eth0')
    h3.cmd(f'ip -6 route add default via {subnet1}1:0')

    # print(h1.cmd('ping6 -c 3 2001:db8::3'))

    # print("IPv4 Ping:")
    # print(h1.cmd('ping -c 3 10.2.0.2'))

    # print("\nIPv6 Ping:")
    # print(h1.cmd('ping -c 3 2001:db8::2'))
    CLI(net)

    net.stop()

if __name__ == '__main__':
    # ipv6_lan_simulation()
    # ipv6_2hop_simulation()
    shutil.rmtree('caps')
    os.mkdir('caps')
    ipv6_cross_router()

   

