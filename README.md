# [cite_start]Emulação de Infraestrutura de Rede com Mininet 🌐 [cite: 2, 3]

> [cite_start]**Projeto prático** da disciplina de Laboratório de Redes de Computadores e Cibersegurança do Programa de Pós-Graduação em Ciência da Computação (PPGCC) - UTFPR, Campo Mourão[cite: 4, 5, 6].

## 📄 Sobre o Projeto
[cite_start]O objetivo principal desta atividade foi criar uma infraestrutura de rede emulada utilizando o Mininet para aprofundar os conhecimentos práticos em emulação de redes e roteamento estático avançado[cite: 8, 9, 13].

[cite_start]A infraestrutura completa foi orquestrada de forma programática através da API Python do Mininet e engloba redes internas segmentadas, uma rede dedicada de servidores e acesso simulado à internet via NAT[cite: 10, 11, 12, 23].

## 🎯 Objetivos Alcançados
* [cite_start]**Rede Interna (`intnet`):** Projetada com subnetting para suportar o requisito de 500 máquinas simultâneas[cite: 28, 35].
* [cite_start]**Rede de Servidores (`servnet`):** Segmentada com máscara ajustada para suportar 64 máquinas[cite: 29, 37].
* [cite_start]**Roteamento e NAT:** Configuração de interfaces, IP Forwarding, tabelas de rotas em roteadores intermediários e nó NAT para garantir conectividade global[cite: 30, 74, 75].
* [cite_start]**QoS e Restrições:** Aplicação de limites físicos nos enlaces de comunicação (100Mb/s de largura de banda e 10ms de atraso) utilizando a classe `TCLink`[cite: 31, 55].

## 🛠️ Tecnologias Utilizadas
* [cite_start]**Ambiente:** Máquina virtual Linux (VirtualBox ou VMWare)[cite: 47, 48].
* [cite_start]**Emulação e Scripts:** Mininet e sua API nativa em Python[cite: 50].
* [cite_start]**Análise e Testes:** iPerf3 (vazão e throughput), Wireshark/tcpdump (análise de pacotes `.pcap`) e utilitários de rede (`ping`, `traceroute`)[cite: 51, 80].

## 🗺️ Topologia e Endereçamento (Subnetting)
[cite_start]Para atender à capacidade exigida de hosts em cada segmento, o endereçamento foi estruturado da seguinte forma[cite: 34]:

| Rede | Finalidade | Bloco CIDR | IP Gateway |
|---|---|---|---|
| **intnet** | Rede Interna | `10.0.0.0/23` | [cite_start]`10.0.1.1` [cite: 36] |
| **servnet**| Rede de Servidores | `10.0.4.0/25` | [cite_start]`10.0.4.1` [cite: 39] |
| **Ext/P2P**| Enlaces R1 <-> R2 | `10.0.3.0/30` | [cite_start]- [cite: 42] |
| **NAT** | Ligação R1 <-> Internet| `10.0.5.0/29` | [cite_start]`10.0.5.1` [cite: 43, 73] |

[cite_start]*(Dica: Salve a Figura 1 do seu relatório e insira a imagem da sua topologia aqui. Ex: `![Topologia Mininet](caminho/para/imagem.png)`)*[cite: 65].

## 🚀 Como Executar

1. Clone este repositório em sua máquina:
   ```bash
   git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/EricSL07/mininet.git)
   ```
2. [cite_start]Certifique-se de estar em um ambiente Linux com as dependências do Mininet perfeitamente instaladas[cite: 47].
3. Execute o script principal do laboratório exigindo os privilégios de superusuário:
   ```bash
   sudo python script_mininet.py
   ```

## 📊 Validação e Testes Práticos
[cite_start]O ambiente foi configurado para atestar ativamente a estabilidade e as restrições da rede[cite: 53, 77]:
1. [cite_start]**Conectividade Completa:** Pacotes disparam do host de origem, alcançam os servidores Web/DNS locais e pingam com sucesso em IPs públicos externos (ex: `8.8.8.8`), validando assim a tradução NAT[cite: 78].
2. [cite_start]**Throughput Rigoroso:** Testes de vazão com o `iPerf3` limitam eficientemente a banda a ~100 Mbits/sec dentro dos cabos virtuais[cite: 79].
3. [cite_start]**Captura e Inspeção:** O código de infraestrutura executa instâncias silenciosas do `tcpdump`, persistindo dados em disco para uma avaliação profunda e posterior no software Wireshark[cite: 80].

## ✒️ Autor
[cite_start]**Éric Seles Lourenço** [cite: 1]
