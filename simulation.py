import shutil
from mininet.net import Mininet
from mininet.node import OVSController, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from NetworkTopo import NetworkTopo
from MyTopo import MyTopology
from RouterTopo import RouterTopo
import os
import re

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

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

def parse_ping_output(ping_output):
    # Define a regular expression pattern to extract relevant information
    pattern = r'(\d+) packets transmitted, (\d+) received, (\d+%).*time (\d+)ms.*rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms'

    match = re.search(pattern, ping_output,re.DOTALL)
    if match:
        # Extract relevant groups from the match object
        transmitted, received, packet_loss, time_ms, rtt_min, rtt_avg, rtt_max, rtt_mdev = match.groups()

        # Convert strings to appropriate data types
        transmitted = int(transmitted)
        received = int(received)
        packet_loss = int(float(packet_loss.rstrip('%')))
        time_ms = int(time_ms)
        rtt_min = float(rtt_min)
        rtt_avg = float(rtt_avg)
        rtt_max = float(rtt_max)
        rtt_mdev = float(rtt_mdev)

        # Return a dictionary with parsed information
        return {
            'transmitted': transmitted,
            'received': received,
            'packet_loss': packet_loss,
            'time_ms': time_ms,
            'rtt_min': rtt_min,
            'rtt_avg': rtt_avg,
            'rtt_max': rtt_max,
            'rtt_mdev': rtt_mdev
        }
    else:
        # Return None if no match is found
        return None

def printPingStats(parsed_data):
    if parsed_data:
        print(f"Transmitted: {parsed_data['transmitted']}")
        print(f"Received: {parsed_data['received']}")
        print(f"Packet Loss: {parsed_data['packet_loss']}%")
        print(f"Time: {parsed_data['time_ms']}ms")
        print(f"RTT Min/Avg/Max/Mdev: {parsed_data['rtt_min']}/{parsed_data['rtt_avg']}/{parsed_data['rtt_max']}/{parsed_data['rtt_mdev']} ms")
    else:
        print("No match found in ping output.")

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

    ### Subnet definitions
    wannet = '2001:beef::'
    r1WanAddr = f'{wannet}1:1'
    r2WanAddr = f'{wannet}1:2'
    
    subnet1 = '2001:db8::'
    r1LanAddr = f'{subnet1}1:0'    

    subnet2 = '2002:db8::'
    r2LanAddr = f'{subnet2}1:0'

    ## ipv6 setup
    r1.cmd(f'ip -6 route add {subnet2}/64 dev r1-wan via {r2WanAddr} onlink')  
    r1.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')

    r2.cmd(f'ip -6 route add {subnet1}/64 dev r2-wan via {r1WanAddr} onlink')
    r2.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')

    ### Addrs
    r1.cmd(f'ip -6 addr add {r1LanAddr}/64 dev r1-lan')
    r1.cmd(f'ip -6 addr add {r1WanAddr}/128 dev r1-wan')
    r1.cmd(f'ip -6 route del {r1WanAddr} dev r1-wan')
    
    r2.cmd(f'ip -6 addr add {r2LanAddr}/64 dev r2-lan')
    r2.cmd(f'ip -6 addr add {r2WanAddr}/128 dev r2-wan')
    r2.cmd(f'ip -6 route del {r2WanAddr} dev r2-wan')

    h1.cmd(f'ip -6 addr add {subnet1}1:1/64 dev h1-eth0')
    h1.cmd(f'ip -6 route add default via {subnet1}1:0')
    h2.cmd(f'ip -6 addr add {subnet2}1:1/64 dev h2-eth0')
    h2.cmd(f'ip -6 route add default via {subnet2}1:0')
    h3.cmd(f'ip -6 addr add {subnet1}1:2/64 dev h3-eth0')
    h3.cmd(f'ip -6 route add default via {subnet1}1:0')

    ping4Stats = h1.cmd('ping -c 4',h2.IP())
    ping6Stats = h1.cmd(f'ping6 -c 4 {subnet2}1:1')

    parsed_data = parse_ping_output(ping4Stats)
    parsed_6_data = parse_ping_output(ping6Stats)
    print(RED,'IPv4')
    printPingStats(parsed_data)
    print(RESET)
    print('IPv6')
    printPingStats(parsed_6_data)
    
    CLI(net)

    net.stop()

if __name__ == '__main__':
    # ipv6_lan_simulation()
    # ipv6_2hop_simulation()
    shutil.rmtree('caps')
    os.mkdir('caps')
    ipv6_cross_router()

   

