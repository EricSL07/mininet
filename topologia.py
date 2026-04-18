 #!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI

import time


OVSSwitch.OVSVersion = '2.13.1'

LOG = True
TESTE = True
ANALISE_REDE = False

captura_host = {}

class LabTopo(Topo):
    "Topologia do Laboratório 1"

    def build(self):
        r1 = self.addHost('r1', cls=Node, ip=None)
        r2 = self.addHost('r2', cls=Node, ip=None)

        # Switches
        switchIntnet = self.addSwitch('s1')
        switchServnet = self.addSwitch('s2')
        switchExt = self.addSwitch('s3')

        # --- Servidores (servnet) ---
        serverWeb = self.addHost('Web', ip='10.0.4.5/25', defaultRoute='via 10.0.4.1')
        serverDNS = self.addHost('DNS', ip='10.0.4.10/25', defaultRoute='via 10.0.4.1')
        self.addLink(serverWeb, switchServnet)
        self.addLink(serverDNS, switchServnet)

        # --- Hosts (intnet) ---
        h1 = self.addHost('h1', ip='10.0.1.10/23', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.1.20/23', defaultRoute='via 10.0.1.1')
        h3 = self.addHost('h3', ip='10.0.1.30/23', defaultRoute='via 10.0.1.1')
        h4 = self.addHost('h4', ip='10.0.1.40/23', defaultRoute='via 10.0.1.1')

        self.addLink(h1, switchIntnet)
        self.addLink(h2, switchIntnet)
        self.addLink(h3, switchIntnet)
        self.addLink(h4, switchIntnet)

        # --- Links dos Roteadores ---
        self.addLink(
            r1,
            switchExt,
            intfName1='r1-eth0',
            params1={'ip': '10.0.5.2/30'},
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
            params2={'ip': '10.0.1.1/23'},
        )


def simpleTest():
    "Criar e testar a rede Mininet"

    topo = LabTopo()
    net = Mininet(topo=topo, switch=OVSSwitch)
    nat0 = net.addNAT(name='nat0', connect=net.get('s3'), ip='10.0.5.1/29')
    nat0.configDefault()
    net.start()

    r1 = net.get('r1')
    r2 = net.get('r2')
    nat0 = net.get('nat0')

    # Ensinar ao NAT como alcançar as redes internas devolvendo os pacotes para o r1
    nat0.cmd('ip route add 10.0.0.0/23 via 10.0.5.2')
    nat0.cmd('ip route add 10.0.4.0/25 via 10.0.5.2')

    # --- Forçar a rota padrão que o addNAT apagou ---
    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')
    serverWeb, serverDNS = net.get('Web', 'DNS')

    for host in [h1, h2, h3, h4]:
        host.cmd('ip route add default via 10.0.1.1')
        
    for server in [serverWeb, serverDNS]:
        server.cmd('ip route add default via 10.0.4.1')

    # Habilitar encaminhamento de pacotes IPv4 (IP Forwarding)
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Configurar roteamento no R2
    r2.cmd('ip route add default via 10.0.3.1')

    # Configurar roteamento no R1
    r1.cmd('ip route add 10.0.0.0/23 via 10.0.3.2')
    r1.cmd('ip route add 10.0.4.0/25 via 10.0.3.2')
    r1.cmd('ip route add default via 10.0.5.1')

    print("\n--- Dumping host connections ---")
    dumpNodeConnections(net.hosts)

    print("\nAguardando os switches")
    time.sleep(1)

    # print("\n--- Testing network connectivity (pingAll) ---")
    # net.pingAll()

    # Invocar os hosts, servidores, roteadores e switches
    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')
    serverWeb, serverDNS = net.get('Web', 'DNS')
    r1, r2 = net.get('r1', 'r2')
    s1, s2, s3 = net.get('s1', 's2', 's3')

    if ANALISE_REDE:
        # CLI(net)
        print("\nSerá salvo todos o trafego de rede em um arquivo pcap para análise posterior.")
        for host in [h1, h2, h3, h4, serverWeb, serverDNS, r1, r2]:
            interface = "any" if host.name in ['r1', 'r2'] else host.intfNames()[0]

            captura_host[host.name] = host.popen(f'tcpdump -i {interface} -w {host.name}.pcap')
        
        time.sleep(3)

    if LOG:
        print("\n--- Hosts ---")
        for host in [h1, h2, h3, h4]:
            print(f"{host.name}: {host.IP()}")
            print(f"Rota padrão: {host.cmd('ip route').strip()}")

        print("\n--- Servidores ---")
        for server in [serverWeb, serverDNS]:
            print(f"{server.name}: {server.IP()}")
            print(f"Rota padrão: {server.cmd('ip route').strip()}")

        print("\n--- Roteadores ---")
        for router in [r1, r2]:
            print(f"{router.name}: {router.IP()}")
            print(f"Rota padrão: {router.cmd('ip route').strip()}")

        print("\n--- Switches ---")
        for switch in [s1, s2, s3]:
            print(f"{switch.name}: {switch.IP()}")
            print(f"  Conexões: {switch.connectionsTo(switch)}")


    if TESTE:
        # Teste extra para validar a comunicação entre hosts e servidores
        print("\nValidando Comunicação entre Hosts e Servidores")
        resultado_ping_web = h1.cmd('ping -c 3 10.0.4.5')
        print(resultado_ping_web)

        print("\nRoteamento do h1 para o servidor Web:")
        tracert_web_h1 = h1.cmd('traceroute -n 10.0.4.5')
        print(tracert_web_h1)

        print("\nRoteamento do h1 para o servidor DNS:")
        tracert_dns_h1 = h1.cmd('traceroute -n 10.0.4.10')
        print(tracert_dns_h1)


        # Teste extra para validar a comunicação entre servidores e hosts
        print("\nValidando Comunicação entre Servidores e Hosts")
        resultado_ping_h1_web = serverWeb.cmd('ping -c 3 10.0.1.10')
        print(resultado_ping_h1_web)

        print("\nRoteamento do servidor Web para h1:")
        tracert_h1_web = serverWeb.cmd('traceroute -n 10.0.1.10')
        print(tracert_h1_web)

        # Teste extra para validar a comunicação entre hosts e os servidores usando iperf3
        print("\nValidando Comunicação entre Hosts e Servidores usando iperf3")
        serverWeb.cmd('iperf3 -s -D')
        serverDNS.cmd('iperf3 -s -D')
        resultado_iperf_web = h1.cmd(f'iperf3 -c {serverDNS.IP()} -t 5')
        resultado_iperf_dns = h1.cmd(f'iperf3 -c {serverWeb.IP()} -t 5')
        print(resultado_iperf_web)
        print(resultado_iperf_dns)

        # Teste extra para validar a comunicação entre servidores e a internet
        print("\nValidando Comunicação entre Servidores e Internet")
        resultado_ping_web_ext = serverWeb.cmd('ping -c 3 8.8.8.8')
        print(resultado_ping_web_ext)

        print("\nRoteamento do servidor Web para a internet:")
        tracert_web_ext = serverWeb.cmd('traceroute -n 8.8.8.8')
        print(tracert_web_ext)

        # Teste extra para validar o host h1 acessando a internet via NAT
        print("\nValidando Acesso de h1 à Internet via NAT")
        resultado_ping = h1.cmd('ping -c 3 8.8.8.8')
        print(resultado_ping)

        print("\nRoteamento do h1 para a internet:")
        tracert_h1_ext = h1.cmd('traceroute -n 8.8.8.8')
        print(tracert_h1_ext)

    else:
        print("\nTeste de conectividade entre hosts e servidores desabilitado. Use TESTE=True para habilitar.")

    if ANALISE_REDE:
        print("\nParando a rede para análise dos arquivos pcap.")
        for nome_host, processo in captura_host.items():
            processo.terminate()

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    simpleTest() 