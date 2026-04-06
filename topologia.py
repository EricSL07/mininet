 #!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI

import time


OVSSwitch.OVSVersion = '2.13.1'


class LabTopo(Topo):
    "Topologia do Laboratório 1"

    def build(self):
        r1 = self.addHost('r1', cls=Node, ip=None)
        r2 = self.addHost('r2', cls=Node, ip=None)

        # Switches
        switchIntnet = self.addSwitch('s1')
        switchServnet = self.addSwitch('s2')
        switchExt = self.addSwitch('s3')
        ext_host = self.addHost('ext_host', ip='8.8.8.8/24', defaultRoute='via 8.8.8.1')
        self.addLink(ext_host, switchExt)

        # --- Servidores (servnet) ---
        serverWeb = self.addHost('Web', ip='10.0.4.5/25', defaultRoute='via 10.0.4.1')
        serverDNS = self.addHost('DNS', ip='10.0.4.10/25', defaultRoute='via 10.0.4.1')
        self.addLink(serverWeb, switchServnet)
        self.addLink(serverDNS, switchServnet)

        # --- Hosts (intnet) ---
        h1 = self.addHost('h1', ip='10.0.0.10/23', defaultRoute='via 10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.20/23', defaultRoute='via 10.0.0.1')
        h3 = self.addHost('h3', ip='10.0.0.30/23', defaultRoute='via 10.0.0.1')
        h4 = self.addHost('h4', ip='10.0.0.40/23', defaultRoute='via 10.0.0.1')

        self.addLink(h1, switchIntnet)
        self.addLink(h2, switchIntnet)
        self.addLink(h3, switchIntnet)
        self.addLink(h4, switchIntnet)

        # --- Links dos Roteadores ---
        self.addLink(
            r1,
            switchExt,
            intfName1='r1-eth0',
            params1={'ip': '8.8.8.1/24'},
        )

        # 2. Ligação extnet: R1 <-> R2
        self.addLink(
            r1,
            r2,
            intfName1='r1-eth1',
            params1={'ip': '10.0.3.1/30'},
            intfName2='r2-eth0',
            params2={'ip': '10.0.3.2/30'},
        )

        # 3. Ligação servnet: R2 <-> switchServnet
        self.addLink(
            switchServnet,
            r2,
            intfName2='r2-eth1',
            params2={'ip': '10.0.4.1/25'},
        )

        # 4. Ligação intnet: R2 <-> switchIntnet
        self.addLink(
            switchIntnet,
            r2,
            intfName2='r2-eth2',
            params2={'ip': '10.0.0.1/23'},
        )


def simpleTest():
    "Criar e testar a rede Mininet"

    topo = LabTopo()
    net = Mininet(topo=topo, switch=OVSSwitch)
    net.start()

    r1 = net.get('r1')
    r2 = net.get('r2')

    # Habilitar encaminhamento de pacotes IPv4 (IP Forwarding)
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Configurar roteamento no R2
    r2.cmd('ip route add default via 10.0.3.1')

    # Configurar roteamento no R1
    r1.cmd('ip route add 10.0.0.0/23 via 10.0.3.2')
    r1.cmd('ip route add 10.0.4.0/25 via 10.0.3.2')

    r1.cmd('iptables -t nat -A POSTROUTING -o r1-eth0 -j MASQUERADE')

    print("\n--- Dumping host connections ---")
    dumpNodeConnections(net.hosts)

    print("\nAguardando os switches")
    time.sleep(2)

    print("\n--- Testing network connectivity (pingAll) ---")
    net.pingAll()

    # Teste extra para validar a comunicação entre hosts e servidores
    print("\nValidando Comunicação entre Hosts e Servidores")
    h1 = net.get('h1')
    resultado_ping_web = h1.cmd('ping -c 3 10.0.4.5')
    resultado_ping_dns = h1.cmd('ping -c 3 10.0.4.10')
    print(resultado_ping_web)
    print(resultado_ping_dns)

    # Teste extra para validar a comunicação entre hosts e os servidores usando iperf3
    print("\nValidando Comunicação entre Hosts e Servidores usando iperf3")
    serverWeb = net.get('Web')
    serverDNS = net.get('DNS')
    serverWeb.cmd('iperf3 -s -D')
    serverDNS.cmd('iperf3 -s -D')
    resultado_iperf_web = h1.cmd(f'iperf3 -c {serverDNS.IP()} -t 5')
    resultado_iperf_dns = h1.cmd(f'iperf3 -c {serverWeb.IP()} -t 5')
    print(resultado_iperf_web)
    print(resultado_iperf_dns)

    # Teste extra para validar a comunicação entre servidores e hosts
    print("\nValidando Comunicação entre Servidores e Hosts")
    resultado_ping_h1_web = net.get('Web').cmd('ping -c 3 10.0.0.10')
    print(resultado_ping_h1_web)

    # Teste extra para validar a comunicação entre servidores e a internet
    print("\nValidando Comunicação entre Servidores e Internet")
    resultado_ping_web_ext = net.get('Web').cmd('ping -c 3 8.8.8.8')
    print(resultado_ping_web_ext)

    # Teste extra para validar o host h1 acessando a internet via NAT
    print("\nValidando Acesso à Internet via NAT")
    resultado_ping = h1.cmd('ping -c 3 8.8.8.8')
    print(resultado_ping)

    # CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    simpleTest() 