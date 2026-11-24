# Gera src/estudo/bancos/rc-t2.json (Redes de Computadores, 2º teste).
# Matéria: endereçamento IPv4 (classes, CIDR, sub-redes, VLSM), encaminhamento IP e VLANs.
# Todos os exercícios numéricos são calculados com o módulo ipaddress.
# Correr: python3 tools/gerar_rc_t2.py
import ipaddress as ipa
import json
import os
import random

R = random.Random(20261210)
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "estudo", "bancos", "rc-t2.json")

G1 = "Grupo 1 · Escolha múltipla"
G2 = "Grupo 2 · Endereçamento"
G3 = "Grupo 3 · Sub-redes e VLSM"
G4 = "Grupo 4 · Encaminhamento e VLANs"

perguntas = []


def add(**q):
    perguntas.append(q)
    return q


# ---------------------------------------------------------------- utilitários
def N(s):
    return ipa.IPv4Network(s, strict=False)


def A(s):
    return ipa.IPv4Address(s)


def mask(n):
    return str(N(f"0.0.0.0/{n}").netmask)


def wild(n):
    return str(N(f"0.0.0.0/{n}").hostmask)


def bits(addr, corte=None):
    b = "".join(f"{o:08b}" for o in A(str(addr)).packed)
    out = ""
    for i, c in enumerate(b):
        if i and i % 8 == 0:
            out += "."
        if corte is not None and i == corte and corte % 8 != 0:
            out += "|"
        out += c
    return out


def classe(a):
    o = int(str(a).split(".")[0])
    if o < 128:
        return "A"
    if o < 192:
        return "B"
    if o < 224:
        return "C"
    if o < 240:
        return "D"
    return "E"


DEF = {"A": 8, "B": 16, "C": 24}
PRIV = [N("10.0.0.0/8"), N("172.16.0.0/12"), N("192.168.0.0/16")]


def privado(a):
    return any(A(str(a)) in p for p in PRIV)


def pub_txt(a):
    a = A(str(a))
    for p in PRIV:
        if a in p:
            return f"privado (está no bloco {p}, reservado para redes locais)"
    o1, o2 = a.packed[0], a.packed[1]
    if o1 == 172:
        return f"público (172.{o2} está fora de 172.16 a 172.31, que é a gama privada da classe B)"
    if o1 == 192 and o2 != 168:
        return f"público (só 192.168.x.x é privado; 192.{o2} não)"
    return "público (não pertence a 10.0.0.0/8, 172.16.0.0/12 nem 192.168.0.0/16)"


def fmt(n):
    return f"{n:,}".replace(",", " ")


def mono(*linhas):
    return ('<div style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;overflow-x:auto;white-space:pre">'
            + "\n".join(linhas) + "</div>")


TH = 'style="text-align:left;padding:6px 4px;border-bottom:1px solid var(--line);font-size:13px"'


def tabela(cab, linhas):
    h = "".join(f"<th {TH}>{c}</th>" for c in cab)
    corpo = "".join("<tr>" + "".join(f'<td style="font-size:13px">{c}</td>' for c in l) + "</tr>" for l in linhas)
    return f'<div style="overflow-x:auto"><table><tr>{h}</tr>{corpo}</table></div>'


def and_or(ip, n):
    rede = N(f"{ip}/{n}")
    return rede, mono(
        f"IP         {bits(ip, n)}   {ip}",
        f"Máscara    {bits(mask(n), n)}   {mask(n)}",
        f"AND        {bits(rede.network_address, n)}   {rede.network_address}",
    ), mono(
        f"IP         {bits(ip, n)}   {ip}",
        f"Máscara-1  {bits(wild(n), n)}   {wild(n)}",
        f"OR         {bits(rede.broadcast_address, n)}   {rede.broadcast_address}",
    )


def gama(rede):
    if rede.prefixlen >= 31:
        return "-"
    return f"{rede.network_address + 1} a {rede.broadcast_address - 1}"


def hosts(n):
    return 2 ** (32 - n) - 2


def bloco_txt(n):
    """Tamanho do bloco no octeto onde está o corte."""
    oct_i = min((n - 1) // 8, 3)
    resto = n - oct_i * 8
    return 2 ** (8 - resto), oct_i + 1


def ord_pt(k):
    return f"{k}ª"


def ip_aleatorio(cls=None, priv=None):
    while True:
        cls_ = cls or R.choice("ABC")
        if cls_ == "A":
            o1 = 10 if priv else R.choice([x for x in range(1, 127) if x != 10])
        elif cls_ == "B":
            o1 = 172 if priv else R.choice([x for x in range(128, 192) if x != 172] + [172])
        else:
            o1 = 192 if priv else R.choice([x for x in range(193, 224)])
        o2 = R.randint(0, 255)
        if cls_ == "B" and o1 == 172:
            o2 = R.randint(16, 31) if priv else R.choice(list(range(32, 255)) + list(range(0, 16)))
        if cls_ == "C" and o1 == 192 and priv:
            o2 = 168
        a = A(f"{o1}.{o2}.{R.randint(0, 255)}.{R.randint(1, 254)}")
        if priv is None or privado(a) == priv:
            return a


# ---------------------------------------------------------------- SVG topologias
def svg_cadeia(routers, lans, wans, pcs=None):
    """routers: nomes; lans[i]=(rede, sufixo_router); wans[i]=(rede, suf_esq, suf_dir) entre router i e i+1."""
    k = len(routers)
    W = 680
    xs = [110 + i * (460 / (k - 1)) for i in range(k)]
    s = [f'<svg viewBox="0 0 {W} 200" width="100%" style="max-width:{W}px;display:block;margin:6px 0" font-family="system-ui,sans-serif" font-size="12" fill="currentColor">']
    for i in range(k - 1):
        x1, x2 = xs[i] + 22, xs[i + 1] - 22
        rede, se, sd = wans[i]
        s.append(f'<line x1="{x1}" y1="50" x2="{x2}" y2="50" stroke="currentColor" stroke-width="2"/>')
        s.append(f'<text x="{(x1 + x2) / 2}" y="40" text-anchor="middle" font-weight="600">{rede}</text>')
        s.append(f'<text x="{x1 + 6}" y="66">{se}</text>')
        s.append(f'<text x="{x2 - 6}" y="66" text-anchor="end">{sd}</text>')
    for i, x in enumerate(xs):
        rede, suf = lans[i]
        s.append(f'<line x1="{x}" y1="72" x2="{x}" y2="128" stroke="currentColor" stroke-width="2"/>')
        s.append(f'<text x="{x + 6}" y="92">{suf}</text>')
        s.append(f'<circle cx="{x}" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="2"/>')
        s.append(f'<text x="{x}" y="54" text-anchor="middle" font-weight="700">{routers[i]}</text>')
        s.append(f'<rect x="{x - 78}" y="128" width="156" height="50" rx="8" fill="none" stroke="currentColor" stroke-width="1.5"/>')
        s.append(f'<text x="{x}" y="148" text-anchor="middle" font-weight="600">LAN {i + 1}</text>')
        s.append(f'<text x="{x}" y="166" text-anchor="middle">{rede}{"  · PC " + pcs[i] if pcs else ""}</text>')
    s.append("</svg>")
    return "".join(s)


# ================================================================ GRUPO 1 · escolha múltipla (conceitos)
NENHUMA = "Nenhuma das outras afirmações está correta."
MC = [
    # ---- endereçamento
    ("Endereço IPv4", "Um endereço IPv4:",
     ["É um identificador de 32 bits, escrito em 4 números decimais de 0 a 255, com parte de rede e parte de host.",
      "É um identificador de 48 bits gravado na placa de rede pelo fabricante.",
      "É um identificador de 128 bits escrito em hexadecimal.",
      "Identifica o fabricante da interface nos primeiros 24 bits.", NENHUMA], 0,
     "IPv4 = 32 bits (4 octetos). Os 48 bits são do endereço MAC e os 128 bits são do IPv6.",
     {1: "isso é o endereço MAC", 2: "isso é o IPv6", 3: "isso é o OUI do endereço MAC"}),
    ("Classes", "Um endereço de classe B:",
     ["Tem o primeiro octeto entre 128 e 191 e máscara padrão 255.255.0.0.",
      "Tem o primeiro octeto entre 192 e 223 e máscara padrão 255.255.255.0.",
      "Tem o primeiro octeto entre 1 e 126 e máscara padrão 255.0.0.0.",
      "Começa sempre pelos bits 110 e é usado para multicast.", NENHUMA], 0,
     "Classe B: 10xxxxxx = 128 a 191, /16. A classe C é 192 a 223 (/24) e a A é 1 a 126 (/8).",
     {1: "isso é a classe C", 2: "isso é a classe A", 3: "110 é a classe C; multicast é a classe D (1110)"}),
    ("Classes", "Os endereços da classe D (224.0.0.0 a 239.255.255.255):",
     ["Estão reservados para multicast, comunicação um-para-muitos.",
      "Estão reservados para uso futuro e investigação.",
      "São endereços privados para redes locais.",
      "São usados para broadcast limitado.", NENHUMA], 0,
     "Classe D (1110xxxx) = multicast (streaming, videoconferência, atualizações de rotas). A classe E (1111xxxx) é que está reservada para uso futuro.",
     {1: "isso é a classe E", 3: "o broadcast limitado é 255.255.255.255"}),
    ("Endereços especiais", "O endereço 127.0.0.1:",
     ["É o endereço de loopback (localhost), usado para testes na própria máquina.",
      "É o primeiro endereço de host da classe A.",
      "É o endereço de broadcast da rede 127.0.0.0/8.",
      "É atribuído automaticamente quando o DHCP falha.", NENHUMA], 0,
     "A rede 127 está reservada para testes locais e 127.0.0.1 é o loopback.",
     {3: "isso é o APIPA, 169.254.0.0/16"}),
    ("Endereços especiais", "Um PC configurado para obter IP por DHCP aparece com o endereço 169.254.23.7. Isto significa que:",
     ["Não conseguiu contactar um servidor DHCP e autoconfigurou-se (APIPA).",
      "Recebeu um endereço público do servidor DHCP.",
      "Está ligado a uma rede privada da classe B.",
      "Está a usar o endereço de loopback.", NENHUMA], 0,
     "169.254.0.0/16 é a gama APIPA: o host atribui-se um endereço quando não obtém resposta de um servidor DHCP (configuração automática).",
     {2: "a gama privada da classe B é 172.16.0.0/12"}),
    ("Endereços privados", "Qual destes endereços é privado?",
     ["172.20.5.4", "172.32.1.1", "192.169.1.10", "11.0.0.1", "169.255.0.1"], 0,
     "Privados: 10.0.0.0/8, 172.16.0.0/12 (172.16 a 172.31) e 192.168.0.0/16. 172.20 está dentro de 172.16 a 172.31.",
     {1: "172.32 já está fora de 172.16 a 172.31", 2: "só 192.168 é privado", 3: "só a rede 10 é privada na classe A"}),
    ("Endereços privados", "Sobre os endereços privados (10/8, 172.16/12, 192.168/16):",
     ["Os routers da Internet não os encaminham, por isso é preciso NAT para os hosts acederem à Internet.",
      "São atribuídos pelos ISP a cada cliente para navegar na Internet.",
      "Só podem ser usados em redes da classe C.",
      "Dispensam o uso de máscara de rede.", NENHUMA], 0,
     "Um router com NAT traduz os endereços privados (internos) num endereço público, visível na Internet.",
     {}),
    ("Endereços especiais", "Numa sub-rede, o endereço com todos os bits de host a 1:",
     ["É o endereço de broadcast dessa sub-rede e não pode ser atribuído a um host.",
      "É o endereço de rede (ID da sub-rede).",
      "É o endereço do gateway por defeito.",
      "É o último endereço atribuível a um host.", NENHUMA], 0,
     "Bits de host todos a 0 = endereço de rede; todos a 1 = broadcast. Nenhum dos dois é atribuível. O gateway é uma convenção, não uma regra.",
     {1: "o endereço de rede tem os bits de host a 0", 3: "o último atribuível é o broadcast menos 1"}),
    ("Endereços especiais", "O endereço 255.255.255.255:",
     ["É o broadcast limitado: atinge todas as máquinas da rede local e não passa routers.",
      "Representa a própria rede onde o pacote foi gerado.",
      "É a máscara da rota por defeito.",
      "É o broadcast de toda a Internet.", NENHUMA], 0,
     "0.0.0.0 representa a própria rede; 255.255.255.255 é o broadcast limitado (só a rede local).",
     {1: "isso é 0.0.0.0", 2: "a rota por defeito usa máscara 0.0.0.0", 3: "os routers não reencaminham este broadcast"}),
    ("Máscara de rede", "A máscara de rede:",
     ["É um número de 32 bits em que os bits a 1 identificam a parte de rede e os bits a 0 a parte de host.",
      "É um número de 32 bits em que os bits a 0 identificam a parte de rede.",
      "Só existe nas redes da classe C.",
      "Serve para converter nomes em endereços IP.", NENHUMA], 0,
     "1s = rede (e sub-rede), 0s = host. Converter nomes em IPs é o trabalho do DNS.",
     {3: "isso é o DNS"}),
    ("Sub-redes", "Para obter o endereço da sub-rede a que pertence um IP, o router:",
     ["Faz o AND binário entre o IP e a máscara.",
      "Faz o OR binário entre o IP e a máscara.",
      "Faz o OR binário entre o IP e a máscara invertida.",
      "Soma a máscara ao endereço IP.", NENHUMA], 0,
     "Sub-rede = IP AND máscara. Broadcast = IP OR máscara invertida (wildcard).",
     {2: "isso dá o endereço de broadcast"}),
    ("Sub-redes", "A máscara invertida (wildcard) de 255.255.255.224 é:",
     ["0.0.0.31", "0.0.0.32", "0.0.0.224", "255.255.255.31", "0.0.0.63"], 0,
     "Wildcard = 255.255.255.255 menos a máscara: 255 - 224 = 31. Usa-se com OR para obter o broadcast.",
     {1: "é o tamanho do bloco (32), não 32 - 1", 4: "isso seria para 255.255.255.192"}),
    ("Sub-redes", "No subnetting:",
     ["A máscara estende-se para a direita, usando bits de host para identificar sub-redes: mais redes, menos hosts por rede.",
      "A máscara estende-se para a esquerda, usando bits de rede para identificar hosts.",
      "O número de hosts de cada sub-rede aumenta.",
      "Todos os endereços passam a ser públicos.", NENHUMA], 0,
     "Emprestar bits de host à parte de rede: a máscara passa a ter mais 1s do que a máscara padrão da classe.",
     {}),
    ("Sub-redes", "Com 5 bits de host, cada sub-rede tem:",
     ["30 hosts (2^5 - 2)", "32 hosts (2^5)", "31 hosts (2^5 - 1)", "62 hosts (2^6 - 2)", NENHUMA], 0,
     "Hosts = 2^n - 2: tira-se o endereço de rede e o de broadcast. 2^5 = 32 endereços, 30 hosts.",
     {1: "32 é o número de endereços, faltam tirar rede e broadcast", 2: "são dois endereços reservados, não um"}),
    ("Sub-redes", "A máscara 255.255.255.192 aplicada a uma rede classe C:",
     ["Cria 4 sub-redes com 62 hosts cada.", "Cria 2 sub-redes com 126 hosts cada.",
      "Cria 8 sub-redes com 30 hosts cada.", "Cria 4 sub-redes com 64 hosts cada.", NENHUMA], 0,
     "192 = 11000000: 2 bits emprestados (2^2 = 4 sub-redes) e 6 bits de host (2^6 - 2 = 62 hosts). 64 é o número de endereços.",
     {3: "64 são endereços; hosts são 62"}),
    ("CIDR", "O CIDR (Classless Inter-Domain Routing):",
     ["Substitui o sistema rígido de classes e permite que um prefixo (/x) represente um bloco contíguo de endereços, agregando rotas.",
      "Divide todos os endereços em 5 classes fixas.",
      "Só permite máscaras /8, /16 e /24.",
      "É um protocolo de encaminhamento dinâmico como o RIP.", NENHUMA], 0,
     "Surgiu no início dos anos 90 para atenuar a escassez de IPv4 e o crescimento das tabelas dos routers (sumarização de rotas).",
     {3: "CIDR é um esquema de endereçamento, não um protocolo de routing"}),
    ("VLSM", "No cálculo de sub-redes com VLSM:",
     ["Ordenam-se as sub-redes por ordem decrescente do número de hosts e cada uma recebe a máscara mais ajustada.",
      "Todas as sub-redes têm obrigatoriamente a mesma máscara.",
      "Começa-se pela sub-rede com menos hosts, para não desperdiçar endereços.",
      "Usa-se sempre a máscara padrão da classe.", NENHUMA], 0,
     "VLSM = máscaras de tamanho variável no mesmo espaço. Começar pelas maiores garante que os blocos ficam alinhados e sem sobreposição.",
     {1: "isso é o subnetting tradicional", 2: "é ao contrário: maiores primeiro"}),
    ("Notação CIDR", "O prefixo /27 corresponde à máscara:",
     ["255.255.255.224", "255.255.255.240", "255.255.255.192", "255.255.255.248", NENHUMA], 0,
     "/27 = 24 + 3 bits: 11100000 = 128 + 64 + 32 = 224.", {1: "isso é /28", 2: "isso é /26", 3: "isso é /29"}),
    ("Configuração TCP/IP", "Para um host comunicar com hosts de OUTRAS redes, além do IP e da máscara precisa de:",
     ["O endereço do gateway por defeito (router da rede local).",
      "O endereço MAC do servidor DNS.",
      "O endereço de broadcast da rede de destino.",
      "Uma rota para cada rede da Internet.", NENHUMA], 0,
     "IP + máscara bastam na própria rede. Para sair dela é preciso o gateway; para usar nomes é preciso o DNS.",
     {}),
    ("Configuração TCP/IP", "As três abordagens de configuração da pilha TCP/IP de um host são:",
     ["Estática (manual), dinâmica (DHCP) e automática (autoconfiguração, ex: APIPA).",
      "Estática, dinâmica (RIP) e híbrida (OSPF).",
      "Classful, classless e VLSM.",
      "Access, trunk e nativa.", NENHUMA], 0,
     "Estática: definida pelo administrador. Dinâmica: fornecida por um servidor DHCP. Automática: a máquina autoconfigura-se na ausência de configuração.",
     {1: "RIP e OSPF são protocolos de encaminhamento", 3: "isso são tipos de porta de switch"}),
    # ---- encaminhamento
    ("Encaminhamento", "O encaminhamento IP é não orientado à conexão. Isto significa que:",
     ["Não se estabelece um caminho prévio: cada datagrama é independente e pode seguir rotas diferentes.",
      "Os routers confirmam a entrega de cada datagrama.",
      "Os pacotes chegam sempre pela ordem de envio.",
      "É reservado um circuito em cada router antes do envio.", NENHUMA], 0,
     "Vantagens: flexibilidade e robustez. Não há garantia de entrega nem de ordem; isso é da camada de transporte (TCP) nos hosts.",
     {1: "não há confirmação ao nível IP", 2: "podem chegar fora de ordem"}),
    ("Encaminhamento", "A fiabilidade da comunicação entre dois hosts (entrega garantida e por ordem) é responsabilidade:",
     ["Da camada de transporte (TCP) nos hosts terminais.", "Dos routers intermédios.",
      "Do protocolo ARP.", "Da tabela de encaminhamento.", NENHUMA], 0,
     "Os routers trabalham na camada de rede e não participam na camada de transporte.", {}),
    ("Encaminhamento estático", "O encaminhamento estático:",
     ["É configurado manualmente pelo administrador e não reage sozinho a falhas ou alterações da topologia.",
      "Atualiza as tabelas automaticamente com mensagens entre routers.",
      "Usa o algoritmo de Dijkstra para escolher o caminho.",
      "Envia atualizações a cada 30 segundos.", NENHUMA], 0,
     "Estático: controlo absoluto dos caminhos, mas manutenção proporcional ao tamanho da rede e sujeito a erros humanos.",
     {1: "isso é o dinâmico", 2: "isso é o OSPF", 3: "isso é o RIP"}),
    ("Encaminhamento dinâmico", "Uma desvantagem do encaminhamento dinâmico é:",
     ["Consumir recursos (CPU e largura de banda) e haver risco de loops.",
      "Não reagir a falhas na topologia.",
      "Exigir que o administrador escreva todas as rotas à mão.",
      "Só funcionar com duas redes.", NENHUMA], 0,
     "O dinâmico adapta-se sozinho e reduz a manutenção, mas os protocolos gastam CPU/largura de banda e podem gerar loops.",
     {1: "isso é uma desvantagem do estático", 2: "isso é o estático"}),
    ("RIP", "O RIP (Routing Information Protocol):",
     ["É distance-vector, usa o número de saltos como métrica (máximo 15) e envia atualizações a cada 30 segundos.",
      "É link-state e envia LSAs apenas quando a topologia muda.",
      "Calcula o custo com base na largura de banda das ligações.",
      "É um protocolo externo usado entre sistemas autónomos.", NENHUMA], 0,
     "RIP: vetor-distância, métrica = saltos (16 = inalcançável), updates periódicos de 30 s, mais overhead.",
     {1: "isso é o OSPF", 2: "isso é o OSPF", 3: "isso é o BGP"}),
    ("OSPF", "O OSPF (Open Shortest Path First):",
     ["É link-state: troca LSAs só quando há alterações e calcula os caminhos mais curtos com o algoritmo de Dijkstra.",
      "Usa o número de saltos (máximo 15) como métrica.",
      "Envia a tabela completa aos vizinhos a cada 30 segundos.",
      "É um protocolo de encaminhamento externo (EGP).", NENHUMA], 0,
     "OSPF: estado da ligação, custo baseado na largura de banda, árvore de caminhos mais curtos (Dijkstra).",
     {1: "isso é o RIP", 2: "isso é o RIP", 3: "é um IGP"}),
    ("Tabela de encaminhamento", "Quando várias entradas da tabela de encaminhamento correspondem ao destino de um datagrama, o router escolhe:",
     ["A entrada com o maior prefixo (a mais específica).", "A primeira entrada da tabela.",
      "A rota por defeito.", "A entrada com o menor prefixo.", NENHUMA], 0,
     "Regra do maior prefixo (longest prefix match). A rota por defeito /0 é a menos específica e só se usa se nenhuma outra corresponder.",
     {2: "a default só se usa quando nada mais corresponde", 3: "é ao contrário"}),
    ("Rota por defeito", "A rota por defeito:",
     ["É representada por 0.0.0.0/0 e só é usada quando nenhuma outra entrada corresponde ao destino.",
      "É representada por 255.255.255.255/32.",
      "Tem prioridade sobre todas as outras rotas.",
      "Só existe em routers com RIP.", NENHUMA], 0,
     "0.0.0.0 com máscara 0.0.0.0: indica o router de saída (gateway por defeito) para destinos desconhecidos.",
     {2: "é a menos específica, a última escolha"}),
    ("Tabela de encaminhamento", "Ao receber um datagrama IP, o router começa por:",
     ["Identificar o endereço IP de destino no cabeçalho e procurar a regra correspondente na tabela.",
      "Ler o endereço IP de origem e devolver o pacote.",
      "Enviar um broadcast ARP para todas as redes.",
      "Estabelecer uma ligação TCP com o destino.", NENHUMA], 0,
     "Aplica a máscara ao destino, compara com as redes da tabela e escolhe o próximo salto (next hop).", {}),
    ("Comandos", "No Windows, o comando que mostra a tabela de encaminhamento é:",
     ["route print", "show ip route", "ipconfig /renew", "tracert -r", NENHUMA], 0,
     "route print (ou netstat -r) no Windows. show ip route é o comando dos routers Cisco.",
     {1: "isso é num router Cisco"}),
    ("Comandos", "Num router Cisco, a rota estática para a rede 192.168.2.0/24 através do próximo salto 172.31.1.1 configura-se com:",
     ["ip route 192.168.2.0 255.255.255.0 172.31.1.1", "ip route 172.31.1.1 255.255.255.0 192.168.2.0",
      "route add 192.168.2.0/24 172.31.1.1", "network 192.168.2.0 172.31.1.1", NENHUMA], 0,
     "Sintaxe: ip route <rede destino> <máscara> <próximo salto>.",
     {1: "a ordem está trocada", 2: "isso é sintaxe de Windows/Linux", 3: "network é usado dentro de router rip"}),
    ("Sistema autónomo", "Um sistema autónomo (AS) é:",
     ["Um conjunto de routers e redes administrados pela mesma organização, que usam um protocolo de encaminhamento comum.",
      "Um router que funciona sem tabela de encaminhamento.",
      "Uma VLAN com encaminhamento próprio.",
      "Um ponto de troca de tráfego entre operadores.", NENHUMA], 0,
     "Dentro do AS usa-se um IGP; entre AS usa-se um EGP (BGP).", {3: "isso é um IXP"}),
    ("IGP e EGP", "Qual destes é um protocolo de encaminhamento EXTERNO?",
     ["BGP", "OSPF", "RIP v2", "EIGRP", "IS-IS"], 0,
     "BGP troca rotas entre AS distintos sem conhecer a topologia interna. RIP, OSPF, IGRP, EIGRP e IS-IS são internos (IGP).", {}),
    ("IGP e EGP", "Um protocolo de encaminhamento interno (IGP):",
     ["Troca informação de rotas dentro de um AS e precisa de informação detalhada da topologia.",
      "Troca rotas entre AS diferentes sem conhecer a topologia interna.",
      "Só pode ser usado em IXPs.",
      "Só aceita rotas estáticas.", NENHUMA], 0,
     "Exemplos de IGP: RIP (v1, v2, RIPng), IGRP, OSPF, IS-IS, EIGRP.", {1: "isso é o EGP (BGP)"}),
    ("IXP", "Os pontos de troca de tráfego (IXP), como o GigaPIX ou o DE-CIX:",
     ["São locais onde operadores de AS diferentes se ligam diretamente para trocar tráfego com menor latência.",
      "São servidores DHCP de grande dimensão.",
      "São routers que só usam RIP.",
      "São gamas de endereços privados.", NENHUMA], 0,
     "A troca física de tráfego entre AS acontece muitas vezes em IXPs.", {}),
    ("Algoritmos", "Os algoritmos de encaminhamento dinâmico dividem-se em:",
     ["Distance-vector (vetor distância), link-state (estado da ligação) e híbridos.",
      "Classful e classless.", "Estáticos e por defeito.", "Access e trunk.", NENHUMA], 0,
     "RIP é distance-vector, OSPF é link-state, EIGRP é considerado híbrido.", {}),
    # ---- VLANs e domínios
    ("Domínio de colisão", "Um domínio de colisão:",
     ["É a parte da rede onde podem ocorrer colisões; num hub todas as portas partilham o mesmo domínio.",
      "É separado por cada porta de um hub.",
      "Corresponde sempre a uma VLAN.",
      "Só é separado por routers.", NENHUMA], 0,
     "Hub = um único domínio de colisão. Cada porta de bridge, switch ou router é um domínio de colisão separado.",
     {1: "é ao contrário: o hub junta tudo", 3: "switches e bridges também separam"}),
    ("Domínio de broadcast", "Sobre domínios de broadcast:",
     ["Todas as portas de um switch estão, por defeito, no mesmo domínio de broadcast; cada porta de um router é um domínio diferente.",
      "Cada porta de um switch é um domínio de broadcast diferente.",
      "Um hub separa domínios de broadcast.",
      "Os routers reencaminham broadcasts entre redes.", NENHUMA], 0,
     "Um domínio de broadcast contém todos os dispositivos alcançáveis pela camada 2. Só um equipamento de camada 3 (ou VLANs) o divide.",
     {1: "cada porta é um domínio de colisão, não de broadcast"}),
    ("VLAN", "Uma VLAN:",
     ["É uma rede lógica criada por software sobre a mesma infraestrutura física, com o seu próprio domínio de broadcast.",
      "É um domínio de colisão criado por um hub.",
      "Opera na camada 3 e dispensa routers para comunicar com outras VLANs.",
      "Obriga a que os dispositivos estejam no mesmo piso.", NENHUMA], 0,
     "As VLANs operam na camada 2 (subcamada MAC). Entre VLANs é preciso um equipamento de camada 3 (router ou switch L3).",
     {2: "operam na camada 2 e precisam de L3 para comunicar", 3: "são independentes da localização física"}),
    ("VLAN", "A comunicação entre duas VLANs diferentes:",
     ["Exige um equipamento de camada 3 (router ou switch multilayer).",
      "Acontece automaticamente se estiverem no mesmo switch.",
      "Exige um hub entre os switches.",
      "É feita pelo protocolo ARP.", NENHUMA], 0,
     "Cada VLAN é uma rede/sub-rede diferente: o tráfego entre elas tem de ser encaminhado (router-on-a-stick ou SVIs).", {}),
    ("VLAN", "Critério de adesão a uma VLAN em que a porta do switch é associada manualmente a uma VLAN:",
     ["VLAN estática (baseada em porta).", "VLAN dinâmica por endereço MAC (VMPS).",
      "VLAN por autenticação IEEE 802.1X.", "VLAN por sub-rede IP.", NENHUMA], 0,
     "Critérios: porta (estática), MAC (dinâmica via VMPS ou RADIUS), protocolo (EtherType), sub-rede IP (switches L3) ou autenticação 802.1X.", {}),
    ("VLAN", "Qual NÃO é uma vantagem das VLANs?",
     ["Juntar todos os dispositivos num único domínio de broadcast.",
      "Reduzir o tráfego desnecessário ao segmentar domínios de broadcast.",
      "Isolar departamentos com dados sensíveis.",
      "Criar várias redes lógicas no mesmo switch, poupando cabos e equipamento.", NENHUMA], 0,
     "Vantagens: desempenho, segurança, gestão e controlo, redução de custos e transparência. Segmentam, não juntam.", {}),
    ("802.1Q", "Numa ligação trunk IEEE 802.1Q, a trama Ethernet:",
     ["Leva uma etiqueta de 4 bytes (TPID + TCI) que identifica a VLAN.",
      "Leva uma etiqueta de 12 bytes com o endereço IP da VLAN.",
      "É enviada sem alterações, porque os trunks só transportam uma VLAN.",
      "Leva o nome da VLAN no campo de dados.", NENHUMA], 0,
     "Tag 802.1Q = 4 bytes: TPID (2 bytes, 0x8100) e TCI (2 bytes: prioridade 3 bits, CFI 1 bit, VID 12 bits).",
     {2: "o trunk transporta várias VLANs"}),
    ("802.1Q", "No cabeçalho 802.1Q, o campo VLAN ID (VID):",
     ["Tem 12 bits: 4096 combinações, das quais 4094 são VLANs utilizáveis (1 a 4094).",
      "Tem 16 bits: 65 536 VLANs possíveis.", "Tem 3 bits e indica a prioridade.",
      "Tem 8 bits: 256 VLANs possíveis.", NENHUMA], 0,
     "2^12 = 4096; 0 e 4095 são reservados. Os 3 bits são do campo User Priority.",
     {2: "isso é o User Priority"}),
    ("802.1Q", "O campo TPID (Tag Protocol Identifier) da etiqueta 802.1Q:",
     ["Tem 2 bytes e para Ethernet vale 0x8100.", "Tem 12 bits e identifica a VLAN.",
      "Tem 1 bit e indica Token Ring.", "Tem 3 bits e indica a prioridade.", NENHUMA], 0,
     "TPID = 0x8100 indica que a trama tem etiqueta 802.1Q. O VID (12 bits), o CFI (1 bit) e a prioridade (3 bits) estão no TCI.",
     {1: "isso é o VID", 2: "isso é o CFI", 3: "isso é o User Priority"}),
    ("Portas", "Uma porta de switch em modo trunk:",
     ["Transporta tramas de várias VLANs entre switches ou entre switch e router, com etiquetas 802.1Q.",
      "Liga um PC a uma única VLAN.",
      "Bloqueia todo o tráfego de broadcast.",
      "Só pode existir em hubs.", NENHUMA], 0,
     "Access: liga dispositivos finais a uma VLAN. Trunk: várias VLANs etiquetadas.", {1: "isso é uma porta access"}),
    ("Comandos", "Para colocar a porta Fa0/5 de um switch Cisco na VLAN 20 como porta de acesso:",
     ["interface Fa0/5 → switchport mode access → switchport access vlan 20",
      "interface Fa0/5 → switchport mode trunk → encapsulation dot1q 20",
      "vlan 20 → ip address 192.168.20.1 255.255.255.0",
      "interface Fa0/5.20 → encapsulation dot1q 20", NENHUMA], 0,
     "encapsulation dot1q é para sub-interfaces de router (router-on-a-stick); switchport mode trunk é para ligações entre switches/router.", {}),
    ("Comandos", "No encaminhamento entre VLANs com router-on-a-stick, em cada sub-interface do router configura-se:",
     ["encapsulation dot1Q <nº VLAN> e o endereço IP do gateway dessa VLAN.",
      "switchport access vlan <nº VLAN>.",
      "router rip e network <rede>.",
      "ip routing e interface vlan <nº>.", NENHUMA], 0,
     "Ex: interface Gi0/0.10 → encapsulation dot1Q 10 → ip address 192.168.10.254 255.255.255.0. Na interface física basta no shutdown.",
     {3: "isso é a alternativa com switch L3 (SVIs)"}),
    ("VLAN", "PC1 na VLAN 10 (192.168.10.1/24) e PC2 na VLAN 20 (192.168.10.2/24) estão no mesmo switch, sem router. Fazem ping entre si?",
     ["Não: estão em domínios de broadcast diferentes, o pedido ARP do PC1 nunca chega ao PC2.",
      "Sim, porque estão na mesma gama IP.",
      "Sim, porque estão no mesmo switch físico.",
      "Só se a porta for trunk.", NENHUMA], 0,
     "As VLANs isolam na camada 2. Mesmo com um router não funcionaria bem: os PCs acham-se na mesma rede e nem usam o gateway. Cada VLAN deve ter a sua sub-rede.", {}),
    ("Switch", "Um switch:",
     ["Opera na camada 2 e usa os endereços MAC para enviar a trama apenas para a porta de destino.",
      "Opera na camada 3 e usa endereços IP para encaminhar entre redes.",
      "Repete o sinal para todas as portas, como um hub.",
      "Separa domínios de broadcast em todas as portas.", NENHUMA], 0,
     "Cada porta do switch é um domínio de colisão; o domínio de broadcast é comum (por VLAN).", {}),
]
for i, (tema, enun, opc, cor, expl, porque) in enumerate(MC):
    q = dict(id=f"mc-{i + 1}", grupo=G1, tipo="escolha", tema=tema, enunciado=enun, opcoes=opc, correta=cor, explicacao=expl)
    if porque:
        q["porque"] = [porque.get(j, "") for j in range(len(opc))]
    add(**q)


# ---------------------------------------------------------------- G1 · escolha múltipla gerada (cálculo)
def mc_num(tema, enun, certa, erradas, expl, idq):
    erradas = [e for e in dict.fromkeys(erradas) if e != certa][:4]
    opc = [certa] + erradas
    # às vezes a certa é "nenhuma" (estilo do professor)
    if R.random() < 0.15 and len(erradas) >= 4:
        opc = erradas[:4] + [NENHUMA]
        expl = f"A resposta certa ({certa}) não está nas opções. " + expl
        add(id=idq, grupo=G1, tipo="escolha", tema=tema, enunciado=enun, opcoes=opc, correta=4, explicacao=expl)
        return
    add(id=idq, grupo=G1, tipo="escolha", tema=tema, enunciado=enun, opcoes=opc, correta=0, explicacao=expl)


for i in range(8):
    n = R.choice([19, 20, 21, 22, 23, 25, 26, 27, 28, 29])
    ip = ip_aleatorio()
    r = N(f"{ip}/{n}")
    bl, octn = bloco_txt(n)
    errs = [str(r.network_address), str(N(f"{ip}/{n + 1}").broadcast_address), str(N(f"{ip}/{n - 1}").broadcast_address),
            str(r.broadcast_address + 1), str(r.broadcast_address - 1)]
    mc_num("Broadcast", f"Qual o endereço de broadcast da sub-rede a que pertence {ip}/{n}?", str(r.broadcast_address), errs,
           f"/{n}: blocos de {bl} no {octn}º octeto. Sub-rede {r.network_address}, broadcast = próximo bloco - 1 = {r.broadcast_address}.",
           f"mcg-bc-{i}")
for i in range(8):
    n = R.choice([18, 20, 21, 22, 25, 26, 27, 28, 29, 30])
    ip = ip_aleatorio()
    r = N(f"{ip}/{n}")
    bl, octn = bloco_txt(n)
    errs = [str(N(f"{ip}/{n + 1}").network_address), str(N(f"{ip}/{n - 1}").network_address), str(r.broadcast_address),
            str(r.network_address + 1), str(N(f"{ip}/{DEF.get(classe(ip), 24)}").network_address)]
    mc_num("Endereço de sub-rede", f"A que sub-rede pertence o endereço {ip} com máscara {mask(n)}?", str(r.network_address), errs,
           f"{mask(n)} = /{n}: blocos de {bl} no {octn}º octeto. O maior múltiplo de {bl} que não passa o valor do IP dá {r.network_address} (é o AND do IP com a máscara).",
           f"mcg-rede-{i}")
for i, n in enumerate(R.sample([20, 22, 23, 24, 25, 26, 27, 28, 29, 30], 6)):
    h = 32 - n
    mc_num("Nº de hosts", f"Quantos endereços se podem atribuir a hosts numa sub-rede /{n}?", fmt(2 ** h - 2),
           [fmt(2 ** h), fmt(2 ** h - 1), fmt(2 ** (h - 1) - 2), fmt(2 ** (h + 1) - 2), fmt(2 ** n)],
           f"/{n} deixa {h} bits de host: 2^{h} - 2 = {fmt(2 ** h - 2)} (tira-se o endereço de rede e o de broadcast).", f"mcg-hosts-{i}")
for i, hneed in enumerate(R.sample([5, 9, 12, 20, 25, 30, 33, 50, 60, 70, 100, 126, 130, 200, 300, 500], 7)):
    h = next(b for b in range(2, 32) if 2 ** b - 2 >= hneed)
    n = 32 - h
    mc_num("Máscara para N hosts", f"Qual a máscara mais ajustada (que desperdiça menos endereços) para uma sub-rede com {hneed} hosts?",
           f"{mask(n)} (/{n})", [f"{mask(n + 1)} (/{n + 1})", f"{mask(n - 1)} (/{n - 1})", f"{mask(n - 2)} (/{n - 2})", f"{mask(n + 2)} (/{n + 2})"],
           f"Precisa de 2^h - 2 ≥ {hneed}: h = {h} bits de host dá {2 ** h - 2} hosts ({'com' if h > 2 else ''} h = {h - 1} só dava {2 ** (h - 1) - 2}). 32 - {h} = /{n}.",
           f"mcg-mask-{i}")
for i in range(6):
    n = R.choice([25, 26, 27, 28, 29])
    ip = ip_aleatorio(cls="C")
    r = N(f"{ip}/{n}")
    dentro = r.network_address + R.randint(1, r.num_addresses - 2)
    while dentro == ip:
        dentro = r.network_address + R.randint(1, r.num_addresses - 2)
    fora = [str(r.broadcast_address + R.randint(1, 5)), str(r.network_address - R.randint(1, 5)) if int(r.network_address) % 256 else str(r.broadcast_address + 9),
            str(r.network_address), str(r.broadcast_address)]
    mc_num("Mesma sub-rede", f"Qual destes endereços pode ser atribuído a um host da mesma sub-rede que {ip}/{n}?", str(dentro), fora,
           f"A sub-rede é {r.network_address}/{n} (hosts de {gama(r)}). O endereço de rede e o broadcast não se atribuem.", f"mcg-mesma-{i}")
for i in range(5):
    tipo = R.choice(["A", "B", "C"])
    ip = ip_aleatorio(cls=tipo)
    certa = f"Classe {tipo}, máscara padrão {mask(DEF[tipo])}"
    outras = [f"Classe {c}, máscara padrão {mask(DEF[c])}" for c in "ABC" if c != tipo] + [f"Classe {tipo}, máscara padrão {mask(DEF[tipo] + 8 if tipo != 'C' else 16)}", "Classe D, sem máscara padrão"]
    mc_num("Classes", f"O endereço {ip} (classful) é de que classe?", certa, outras,
           f"1º octeto = {str(ip).split('.')[0]}: A 1-126, B 128-191, C 192-223. É {pub_txt(ip)}.", f"mcg-classe-{i}")

# longest prefix match (escolha)
for i in range(6):
    o1 = R.choice([10, 172, 192])
    o2 = R.randint(16, 31) if o1 == 172 else (168 if o1 == 192 else R.randint(1, 250))
    o3 = R.randint(1, 250)
    tab = [(N(f"{o1}.0.0.0/8"), "10.0.0.1"), (N(f"{o1}.{o2}.0.0/16"), "10.0.0.5"), (N(f"{o1}.{o2}.{o3}.0/24"), "10.0.0.9"),
           (N(f"{o1}.{o2}.{o3}.128/25"), "10.0.0.13"), (N("0.0.0.0/0"), "10.0.0.17")]
    dest = A(f"{o1}.{o2}.{o3}.{R.choice([R.randint(1, 126), R.randint(129, 254)])}") if R.random() < .6 else A(f"{o1}.{o2}.{(o3 + R.randint(1, 4)) % 250}.{R.randint(1, 254)}")
    cands = [(t, nh) for t, nh in tab if dest in t]
    best = max(cands, key=lambda x: x[0].prefixlen)
    tabtxt = "\n".join(f"{t}  via {nh}" for t, nh in tab)
    add(id=f"mcg-lpm-{i}", grupo=G1, tipo="escolha", tema="Maior prefixo",
        enunciado=f"Um router tem esta tabela:\n{mono(tabtxt)}\nPara onde envia um datagrama com destino {dest}?",
        opcoes=[f"via {nh}" for _, nh in tab], correta=tab.index(best),
        explicacao=f"Correspondem: {', '.join(str(t) for t, _ in cands)}. Ganha a mais específica (maior prefixo): {best[0]} → via {best[1]}.")

# domínios de colisão e broadcast
for i in range(6):
    k = R.randint(2, 3)
    ramos, txt, col = [], [], 0
    for j in range(k):
        pcs = R.randint(2, 6)
        hub = R.random() < .5
        hpcs = R.randint(2, 4) if hub else 0
        col += 1 + pcs + (1 if hub else 0)
        txt.append(f"a interface {j + 1} liga a um switch com {pcs} PCs" + (f" e um hub (com {hpcs} PCs) ligado a esse switch" if hub else ""))
    enun = f"Um router tem {k} interfaces LAN: " + "; ".join(txt) + ". Sem VLANs, quantos domínios de colisão e de broadcast existem?"
    certa = f"{col} de colisão e {k} de broadcast"
    errs = [f"{col} de colisão e 1 de broadcast", f"{k} de colisão e {col} de broadcast", f"{col + 3} de colisão e {k} de broadcast",
            f"{col - 2} de colisão e {k} de broadcast", f"{col} de colisão e {k + 1} de broadcast"]
    mc_num("Domínios", enun, certa, errs,
           f"Colisão: cada porta de switch/router em uso é um domínio, e cada hub com os seus PCs conta como um só. Por ramo: ligação router-switch + 1 por PC no switch + 1 pelo hub. Total {col}. Broadcast: um por interface do router = {k}.",
           f"mcg-dom-{i}")


# ================================================================ GRUPO 2 · endereçamento (aberta)
def ex_analisa(idq, ip, n, fonte=None, cot=(5, 10, 10, 5, 5, 5)):
    cls = classe(ip)
    d = DEF[cls]
    r, and_txt, or_txt = and_or(ip, n)
    bl, octn = bloco_txt(n)
    nsub = 2 ** (n - d)
    k = R.randint(2, min(9, nsub - 1))
    j = R.randint(k + 1, min(14, nsub))
    base = N(f"{ip}/{d}").network_address
    sk = N(f"{A(int(base) + (k - 1) * 2 ** (32 - n))}/{n}")
    sj = N(f"{A(int(base) + (j - 1) * 2 ** (32 - n))}/{n}")
    al = [
        dict(enunciado="Indique a classe (conceito classful) e se o endereço é público ou privado. Justifique.", cotacao=cot[0],
             resolucao=f"1º octeto = {str(ip).split('.')[0]} → classe {cls} (máscara padrão /{d} = {mask(d)}).\nÉ {pub_txt(ip)}."),
        dict(enunciado="A que sub-rede pertence este endereço? (utilize lógica binária)", cotacao=cot[1],
             resolucao=f"AND entre o IP e a máscara /{n} ({mask(n)}):\n{and_txt}Sub-rede: {r.network_address}/{n}\n(Atalho: blocos de {bl} no {octn}º octeto.)"),
        dict(enunciado="Qual o endereço de broadcast desta sub-rede? (utilize lógica binária)", cotacao=cot[2],
             resolucao=f"OR entre o IP e a máscara invertida ({wild(n)}):\n{or_txt}Broadcast: {r.broadcast_address}"),
        dict(enunciado="Qual a gama de endereços atribuíveis e quantos hosts pode ter cada sub-rede?", cotacao=cot[3],
             resolucao=f"Gama: {gama(r)}\nBits de host: 32 - {n} = {32 - n} → 2^{32 - n} - 2 = {fmt(hosts(n))} hosts."),
        dict(enunciado=f"Quantas sub-redes se obtêm com esta máscara a partir da rede classful?", cotacao=cot[4],
             resolucao=f"Máscara padrão /{d}, máscara usada /{n}: {n} - {d} = {n - d} bits emprestados → 2^{n - d} = {fmt(2 ** (n - d))} sub-redes."),
        dict(enunciado=f"Dividindo a rede {base}/{d} em sub-redes /{n} (a 1ª é {base}), qual o endereço da {ord_pt(k)} sub-rede e o broadcast da {ord_pt(j)}?", cotacao=cot[5],
             resolucao=f"Cada sub-rede tem {fmt(2 ** (32 - n))} endereços.\n{ord_pt(k)} sub-rede = {base} + ({k} - 1) × {fmt(2 ** (32 - n))} = {sk.network_address}\n{ord_pt(j)} sub-rede = {sj.network_address}, broadcast {sj.broadcast_address}"),
    ]
    return add(id=idq, grupo=G2, tipo="aberta", tema="Análise de um endereço", fonte=fonte,
               enunciado=f"Considerando o endereço IP {ip} com máscara CIDR /{n}, responda justificando:", alineas=al)


for i in range(14):
    cls = R.choice("AABBCCC")
    d = DEF[cls]
    n = R.randint(max(d + 2, 18 if cls == "A" else d + 2), 30)
    ex_analisa(f"g2-an-{i}", ip_aleatorio(cls=cls, priv=R.random() < .4), n)


def ex_simnao(idq, fonte=None):
    n = R.choice([24, 25, 26, 27, 28, 29])
    ip = ip_aleatorio(cls=R.choice("BC"))
    r = N(f"{ip}/{n}")
    perg = []
    # 1 pertence?
    if R.random() < .5:
        x = r.network_address + R.randint(1, r.num_addresses - 2)
        perg.append((f"O IP {x} pertence a esta sub-rede?", "SIM", f"A sub-rede vai de {r.network_address} a {r.broadcast_address}; {x} está lá dentro."))
    else:
        x = r.broadcast_address + R.randint(1, 20)
        perg.append((f"O IP {x} pertence a esta sub-rede?", "NÃO", f"A sub-rede vai de {r.network_address} a {r.broadcast_address}; {x} já é da sub-rede seguinte."))
    # 2 hosts
    hh = hosts(n)
    if R.random() < .5:
        perg.append((f"É possível configurar {hh} hosts nesta sub-rede?", "SIM", f"{32 - n} bits de host: 2^{32 - n} - 2 = {hh}."))
    else:
        perg.append((f"É possível configurar {hh + 2} hosts nesta sub-rede?", "NÃO", f"Há {hh + 2} endereços, mas só {hh} hosts (rede e broadcast não contam)."))
    # 3 rede / último / broadcast
    c = R.choice(["rede", "ultimo", "bc", "rede_falso"])
    if c == "rede":
        perg.append((f"O IP {r.network_address} pode ser atribuído a um host?", "NÃO", "É o endereço de rede (bits de host a 0)."))
    elif c == "ultimo":
        perg.append((f"O IP {r.broadcast_address - 1} é o último endereço atribuível desta sub-rede?", "SIM", f"Broadcast = {r.broadcast_address}; o último atribuível é o anterior."))
    elif c == "bc":
        perg.append((f"O IP {r.broadcast_address} é o endereço de broadcast desta sub-rede?", "SIM", "Bits de host todos a 1."))
    else:
        falso = r.network_address + 2 ** (32 - n - 1) if n < 30 else r.network_address + 1
        perg.append((f"O IP {falso} é o endereço de rede desta sub-rede?", "NÃO", f"O endereço de rede é {r.network_address} (AND do IP com {mask(n)})."))
    # 4 máscara invertida
    perg.append((f"A máscara invertida desta sub-rede é {wild(n)}?", "SIM", f"255.255.255.255 - {mask(n)} = {wild(n)}.") if R.random() < .5
                else (f"A máscara invertida desta sub-rede é {wild(n + 1 if n < 30 else n - 1)}?", "NÃO", f"A certa é {wild(n)} (255.255.255.255 - {mask(n)})."))
    enun = f"Endereço IP: {ip}\nMáscara: {mask(n)}\nResponda SIM ou NÃO, justificando:"
    return add(id=idq, grupo=G2, tipo="aberta", tema="Sim ou Não", fonte=fonte, enunciado=enun,
               alineas=[dict(enunciado=p, cotacao=10, resolucao=f"{res}. {porq}") for p, res, porq in perg])


for i in range(10):
    ex_simnao(f"g2-sn-{i}")


def ex_conversoes(idq):
    a = ip_aleatorio()
    b = ip_aleatorio()
    g1 = R.randint(0, 0xFFFF)
    g2 = R.randint(0, 0xFF)
    hx = f"FE80::{R.randint(1, 0xFFF):X}"
    hx_val = int(hx.split("::")[1], 16)
    ult = R.choice([1, 15, 127, 255, 0x8C])
    al = [
        dict(enunciado=f"Binário → Decimal: {bits(a)}", cotacao=10,
             resolucao=f"Converte-se cada octeto (pesos 128 64 32 16 8 4 2 1):\n" + "\n".join(f"{x} = {int(x, 2)}" for x in bits(a).split(".")) + f"\n→ {a}"),
        dict(enunciado=f"Decimal → Binário: {b}", cotacao=10,
             resolucao="\n".join(f"{o} = {o:08b}" for o in A(str(b)).packed) + f"\n→ {bits(b)}"),
        dict(enunciado=f"Binário → Hexadecimal (grupos IPv6): {g1:016b}:{g2:08b}::{ult:08b}", cotacao=10,
             resolucao="Cada 4 bits = 1 dígito hexadecimal.\n"
             f"{g1:016b} = {' '.join(f'{g1:016b}'[i:i + 4] for i in range(0, 16, 4))} = {g1:X}\n"
             f"{g2:08b} = {g2 >> 4:04b} {g2 & 15:04b} = {g2:X}\n"
             f"{ult:08b} = {ult >> 4:04b} {ult & 15:04b} = {ult:X}\n"
             f"→ {g1:X}:{g2:X}::{ult:X} (os zeros à esquerda de cada grupo omitem-se)"),
        dict(enunciado=f"Hexadecimal → Binário: {hx}", cotacao=10,
             resolucao=f"FE80 = 1111 1110 1000 0000\n:: = grupos de zeros (aqui 6 grupos de 16 bits a 0)\n{hx.split('::')[1]} = {hx_val:016b}\n→ 1111111010000000::{hx_val:016b}"),
    ]
    return add(id=idq, grupo=G2, tipo="aberta", tema="Conversões", enunciado="Efetue as conversões (mostre o cálculo):", alineas=al)


for i in range(5):
    ex_conversoes(f"g2-conv-{i}")


def ex_tabela_cidr(idq):
    linhas_res, al = [], []
    for _ in range(3):
        n = R.choice([16, 20, 22, 26, 27, 28, 29, 30])
        ip = ip_aleatorio(cls="C" if n >= 24 else R.choice("AB"))
        r = N(f"{ip}/{n}")
        cls = classe(ip)
        d = DEF[cls]
        nsr = f"2^{n - d} = {fmt(2 ** (n - d))}" if n >= d else "- (super-rede)"
        al.append(dict(enunciado=f"{ip}/{n}: endereço de sub-rede, gama, broadcast, máscara, nº de sub-redes e nº de hosts por sub-rede.", cotacao=round(40 / 3, 1),
                       resolucao=tabela(["Sub-rede", "Gama", "Broadcast", "Máscara", "Nº sub-redes", "Hosts"],
                                        [[str(r.network_address), gama(r), str(r.broadcast_address), mask(n), nsr, fmt(hosts(n))]])
                       + f"\nClasse {cls} (padrão /{d}); blocos de {bloco_txt(n)[0]} no {bloco_txt(n)[1]}º octeto."))
    return add(id=idq, grupo=G2, tipo="aberta", tema="Tabela CIDR", enunciado="Preencha os campos da tabela (conceito classless, CIDR) para cada endereço:", alineas=al)


for i in range(6):
    ex_tabela_cidr(f"g2-tab-{i}")


# ================================================================ GRUPO 3 · sub-redes e VLSM
DEPS = ["Comercial", "Financeiro", "Administrativo", "Produção", "Informática", "Logística", "Direção", "Armazém", "Qualidade", "Marketing"]


def vlsm(base, pedidos):
    """pedidos: [(nome, hosts)] → lista de (nome, hosts, rede) por ordem de atribuição."""
    ordem = sorted(pedidos, key=lambda x: -x[1])
    cur = int(base.network_address)
    out = []
    for nome, h in ordem:
        hb = next(b for b in range(2, 32) if 2 ** b - 2 >= h)
        rede = N(f"{A(cur)}/{32 - hb}")
        out.append((nome, h, rede))
        cur += 2 ** hb
    assert cur <= int(base.broadcast_address) + 1
    return out, cur


def tabela_vlsm(res):
    return tabela(["Nome", "Nº hosts", "Nº end. aloc.", "End. sub-rede", "Gama", "Broadcast", "Máscara", "CIDR"],
                  [[n, h, fmt(r.num_addresses - 2), str(r.network_address), gama(r), str(r.broadcast_address), str(r.netmask), f"/{r.prefixlen}"] for n, h, r in res])


def ex_vlsm(idq, base, pedidos, fonte=None, extra=True):
    res, livre = vlsm(base, pedidos)
    passos = "\n".join(f"{n} ({h} hosts): 2^{32 - r.prefixlen} - 2 = {r.num_addresses - 2} ≥ {h} → /{r.prefixlen}, começa em {r.network_address}" for n, h, r in res)
    al = [dict(enunciado="Construa a tabela de endereçamento com CIDR/VLSM: nome, nº de hosts, nº de endereços alocados, endereço de sub-rede, gama, broadcast, máscara decimal e CIDR.", cotacao=30,
               resolucao=f"Ordenar por ordem decrescente de hosts e dar a cada um o bloco mais pequeno que chega:\n{passos}\n{tabela_vlsm(res)}")]
    if extra:
        fim = int(base.broadcast_address) + 1
        sobra = fim - livre
        wan = N(f"{A(livre)}/30") if sobra >= 4 else None
        al.append(dict(enunciado="Quantos endereços ficam livres e que sub-rede /30 usaria para uma ligação ponto-a-ponto entre dois routers?", cotacao=10,
                       resolucao=(f"Usados até {A(livre - 1)}. Livres: {fmt(sobra)} endereços (de {A(livre)} a {base.broadcast_address}).\n"
                                  + (f"Ligação WAN: {wan} (routers {wan.network_address + 1} e {wan.network_address + 2}, broadcast {wan.broadcast_address})." if wan else "Não sobra espaço para uma /30."))))
    pedtxt = "\n".join(f"Dep. {n} = {h} hosts" for n, h in pedidos)
    return add(id=idq, grupo=G3, tipo="aberta", tema="VLSM", fonte=fonte,
               enunciado=f"Construa um esquema de endereçamento para a empresa utilizando CIDR/VLSM, com o endereço {base}, para as seguintes necessidades:\n{pedtxt}",
               alineas=al)


bases = ["192.168.77.0/24", "193.18.50.0/24", "200.10.{}.0/24", "192.168.{}.0/24", "10.{}.5.0/24", "172.16.{}.0/23", "195.20.{}.0/24", "172.20.{}.0/22"]
k = 0
while k < 16:
    b = R.choice(bases)
    if "{}" in b:
        b = b.format(R.randint(1, 60) * (2 if "/23" in b else 4 if "/22" in b else 1))
    base = N(b)
    nd = R.randint(3, 5)
    cap = base.num_addresses
    nomes = R.sample(DEPS, nd)
    ped = [(nm, R.randint(3, max(4, int(cap * R.choice([.12, .2, .25, .35]))))) for nm in nomes]
    try:
        _, fim = vlsm(base, ped)
    except AssertionError:
        continue
    if fim - int(base.network_address) < cap * .5:
        continue
    ex_vlsm(f"g3-vlsm-{k}", base, ped)
    k += 1


def ex_fixo(idq):
    if R.random() < .5:
        base = N(f"192.168.{R.randint(1, 254)}.0/24")
    else:
        base = N(f"172.{R.randint(16, 31)}.0.0/16")
    precisa = R.choice([3, 4, 5, 6, 8, 10, 12])
    b = next(x for x in range(1, 10) if 2 ** x >= precisa)
    n = base.prefixlen + b
    subs = list(base.subnets(new_prefix=n))
    linhas = [[chr(65 + i), str(s.network_address), gama(s), fmt(s.num_addresses), str(s.broadcast_address), str(s.netmask), f"/{n}"] for i, s in enumerate(subs)]
    if len(linhas) > 8:
        linhas = linhas[:3] + [["…"] * 7] + linhas[-2:]
        nota = f"(mostram-se as 3 primeiras e as 2 últimas das {len(subs)})"
    else:
        nota = ""
    al = [
        dict(enunciado=f"Que máscara deve usar para obter pelo menos {precisa} sub-redes iguais? Justifique.", cotacao=10,
             resolucao=f"2^{b} = {2 ** b} ≥ {precisa} → emprestar {b} bits: /{base.prefixlen} + {b} = /{n} ({mask(n)})."),
        dict(enunciado="Quantos hosts pode ter cada sub-rede?", cotacao=5,
             resolucao=f"{32 - n} bits de host: 2^{32 - n} - 2 = {fmt(hosts(n))} hosts."),
        dict(enunciado="Construa o esquema: nome, endereço de sub-rede, gama, nº de endereços, broadcast, máscara decimal e CIDR.", cotacao=20,
             resolucao=f"Blocos de {bloco_txt(n)[0]} no {bloco_txt(n)[1]}º octeto. {nota}\n{tabela(['Nome', 'Sub-rede', 'Gama', 'Nº end.', 'Broadcast', 'Máscara', 'CIDR'], linhas)}"),
        dict(enunciado="Qual o broadcast da última sub-rede?", cotacao=5,
             resolucao=f"Última sub-rede {subs[-1].network_address}/{n}: broadcast {subs[-1].broadcast_address} (é também o broadcast da rede original)."),
    ]
    return add(id=idq, grupo=G3, tipo="aberta", tema="Subnetting com máscara fixa",
               enunciado=f"A rede {base} tem de ser dividida em sub-redes do mesmo tamanho para {precisa} departamentos.", alineas=al)


for i in range(8):
    ex_fixo(f"g3-fixo-{i}")


# ================================================================ GRUPO 4 · encaminhamento e VLANs
def ex_rotas(idq):
    k = R.choice([2, 2, 3])
    routers = [f"R{i + 1}" for i in range(k)]
    usa_vlsm = R.random() < .5
    if usa_vlsm:
        base = N(f"192.168.{R.randint(1, 200)}.0/24")
        while True:
            try:
                res, cur = vlsm(base, [(f"LAN {i + 1}", R.choice([10, 20, 25, 50, 60, 100])) for i in range(k)])
                break
            except AssertionError:
                pass
        res = sorted(res, key=lambda x: x[0])
        lans = [r for _, _, r in res]
    else:
        lans = [N(f"192.168.{x}.0/24") for x in R.sample(range(1, 250), k)]
    wb = R.choice(["10.0.0.0", "172.31.1.0", "100.100.100.0", "10.10.10.0"])
    wans = list(N(f"{wb}/24").subnets(new_prefix=30))[:k - 1]
    ultimo = R.random() < .5
    rlan = [(l.broadcast_address - 1) if ultimo else (l.network_address + 1) for l in lans]
    pc = [(l.network_address + 1) if ultimo else (l.network_address + 2) for l in lans]
    # WAN: router da esquerda .1, da direita .2
    svg = svg_cadeia(routers, [(str(l), f".{str(rlan[i]).split('.')[-1]}") for i, l in enumerate(lans)],
                     [(str(w), f".{str(w.network_address + 1).split('.')[-1]}", f".{str(w.network_address + 2).split('.')[-1]}") for w in wans],
                     [f".{str(p).split('.')[-1]}" for p in pc])

    def nh(i, j):  # próximo salto de Ri para LAN j
        return (wans[i].network_address + 2) if j > i else (wans[i - 1].network_address + 1)

    def iface(i, j):
        return "Se0/0/0" if j > i else "Se0/0/1"

    rotas_txt = []
    for i in range(k):
        rs = [f"ip route {lans[j].network_address} {lans[j].netmask} {nh(i, j)}" for j in range(k) if j != i]
        rotas_txt.append(f"{routers[i]}:\n" + mono(*rs))
    # tabela do último router (ou R2)
    t = 1 if k == 3 else 0
    show = [f"C    {lans[t]} is directly connected, GigabitEthernet0/0"]
    if t < k - 1:
        show.append(f"C    {wans[t]} is directly connected, Serial0/0/0")
    if t > 0:
        show.append(f"C    {wans[t - 1]} is directly connected, Serial0/0/1")
    for j in range(k):
        if j != t:
            show.append(f"S    {lans[j]} [1/0] via {nh(t, j)}")
    default = []
    for i in (0, k - 1):
        viz = nh(i, k - 1 if i == 0 else 0)
        default.append(f"{routers[i]}: ip route 0.0.0.0 0.0.0.0 {viz}")
    al = [
        dict(enunciado="Indique a configuração IP (endereço, máscara e gateway) do PC de cada LAN.", cotacao=10,
             resolucao="\n".join(f"PC LAN {i + 1}: {pc[i]}  {lans[i].netmask}  gateway {rlan[i]}" for i in range(k))
             + "\nO gateway é o endereço da interface do router nessa LAN."),
        dict(enunciado="Escreva as rotas estáticas (comandos Cisco) necessárias em cada router para todas as LANs comunicarem.", cotacao=15,
             resolucao="ip route <rede destino> <máscara> <próximo salto>. As redes diretamente ligadas não precisam de rota.\n" + "\n".join(rotas_txt)
             + ("\n(Para fazer ping às interfaces da WAN do outro lado, R1 e R3 precisariam também de uma rota para a WAN que não lhes está ligada.)" if k == 3 else "")),
        dict(enunciado=f"Mostre a tabela de encaminhamento de {routers[t]} (show ip route) e interprete-a.", cotacao=10,
             resolucao=mono(*show) + "\nC = rede diretamente ligada (aparece quando a interface tem IP e está up). S = rota estática; [1/0] = distância administrativa 1, métrica 0; via = próximo salto."),
        dict(enunciado="Que routers podiam usar uma rota por defeito em vez das rotas estáticas? Escreva-as.", cotacao=5,
             resolucao="Os routers das pontas só têm uma saída, por isso basta-lhes a rota por defeito:\n" + mono(*default)
             + ("\nR2 (no meio) não: tem duas saídas e precisa de saber qual a direção de cada LAN." if k == 3 else "")),
    ]
    return add(id=idq, grupo=G4, tipo="aberta", tema="Encaminhamento estático",
               enunciado=f"Considere a seguinte rede. Os routers ligam-se por ligações série /30 (o router da esquerda usa o 1º endereço). Em cada LAN o router usa o {'último' if ultimo else 'primeiro'} endereço atribuível.\n{svg}",
               alineas=al)


for i in range(10):
    ex_rotas(f"g4-rot-{i}")


def ex_lpm(idq):
    o2 = R.randint(16, 31)
    o3 = R.randint(0, 200)
    tab = [(N(f"172.{o2}.0.0/16"), "10.1.1.2", "Se0/0/0"), (N(f"172.{o2}.{o3}.0/24"), "10.1.2.2", "Se0/0/1"),
           (N(f"172.{o2}.{o3}.64/26"), "10.1.3.2", "Gi0/1"), (N(f"172.{o2}.{o3 + 4}.0/22"), "10.1.4.2", "Gi0/2"), (N("0.0.0.0/0"), "10.1.9.1", "Gi0/0")]
    tab[3] = (N(f"172.{o2}.{(o3 + 4) // 4 * 4}.0/22"), "10.1.4.2", "Gi0/2")
    dests = [A(f"172.{o2}.{o3}.{R.randint(65, 126)}"), A(f"172.{o2}.{o3}.{R.randint(130, 250)}"),
             A(f"172.{o2}.{(o3 + 4) // 4 * 4 + R.randint(0, 3)}.{R.randint(1, 254)}"), A(f"172.{o2}.{(o3 + 40) % 250}.{R.randint(1, 254)}"),
             A(f"{R.choice([8, 85, 193, 151])}.{R.randint(0, 255)}.{R.randint(0, 255)}.{R.randint(1, 254)}")]
    R.shuffle(dests)
    linhas = [[str(t), str(t.netmask), nh, itf] for t, nh, itf in tab]
    al = []
    for d in dests[:4]:
        cands = [x for x in tab if d in x[0]]
        best = max(cands, key=lambda x: x[0].prefixlen)
        al.append(dict(enunciado=f"Destino {d}: por onde sai?", cotacao=10,
                       resolucao=f"Correspondem: {', '.join(str(c[0]) for c in cands)}.\nMaior prefixo: {best[0]} → via {best[1]} ({best[2]})."
                       + ("\nSó a rota por defeito serve." if best[0].prefixlen == 0 else "")))
    return add(id=idq, grupo=G4, tipo="aberta", tema="Tabela de encaminhamento",
               enunciado=f"Um router tem a seguinte tabela de encaminhamento:\n{tabela(['Rede', 'Máscara', 'Próximo salto', 'Interface'], linhas)}\nPara cada destino indique a rota usada, justificando com a regra do maior prefixo.",
               alineas=al)


for i in range(6):
    ex_lpm(f"g4-lpm-{i}")

VNOMES = ["Alunos", "Docentes", "Servicos", "Admin", "Visitantes", "Producao", "Gestao", "Voz"]


def ex_vlan(idq):
    nv = R.choice([2, 2, 3])
    vids = sorted(R.sample([10, 20, 30, 40, 50, 60, 99], nv))
    nomes = R.sample(VNOMES, nv)
    if R.random() < .5:
        redes = [N(f"192.168.{v}.0/24") for v in vids]
        gw = [r.broadcast_address - 1 for r in redes]
        plano = ""
    else:
        base = N(f"10.{R.randint(1, 200)}.{R.randint(0, 50) * 4}.0/24")
        while True:
            try:
                res, _ = vlsm(base, [(f"VLAN {v}", R.choice([12, 25, 50, 100])) for v in vids])
                break
            except AssertionError:
                pass
        mapa = {n: r for n, _, r in res}
        redes = [mapa[f"VLAN {v}"] for v in vids]
        gw = [r.broadcast_address - 1 for r in redes]
        plano = "\nEndereçamento já calculado (VLSM a partir de " + str(base) + "):\n" + tabela(["VLAN", "Rede", "Gateway (router)"], [[f"{v} ({nm})", str(r), str(g)] for v, nm, r, g in zip(vids, nomes, redes, gw)])
    pcs = []
    porta = {"SW1": 1, "SW2": 1}
    for v, nm in zip(vids, nomes):
        for sw in ("SW1", "SW2"):
            for _ in range(R.randint(1, 2)):
                pcs.append((f"PC{len(pcs) + 1}", sw, f"Fa0/{porta[sw]}", v))
                porta[sw] += 1
    tab = tabela(["PC", "Switch", "Porta", "VLAN"], [[p, s, pt, f"{v} ({nomes[vids.index(v)]})"] for p, s, pt, v in pcs])
    if not plano:
        plano = "\nCada VLAN usa a rede 192.168.&lt;VLAN&gt;.0/24 e o router usa o endereço .254."
    alvo = R.choice([p for p in pcs if p[1] == "SW2"])
    vi = vids.index(alvo[3])
    rede_alvo, gw_alvo = redes[vi], gw[vi]
    pcs_sw1 = [p for p in pcs if p[1] == "SW1" and p[3] == alvo[3]]
    cmd_sw = ["enable", "configure terminal"] + sum([[f"vlan {v}", f" name {nm}"] for v, nm in zip(vids, nomes)], []) + \
             ["interface Gi0/1", " switchport mode trunk", "interface Gi0/2", " switchport mode trunk"]
    if pcs_sw1:
        cmd_sw += [f"interface {pcs_sw1[0][2]}", " switchport mode access", f" switchport access vlan {alvo[3]}"]
    cmd_r = ["interface Gi0/0", " no shutdown"] + sum([[f"interface Gi0/0.{v}", f" encapsulation dot1Q {v}", f" ip address {g} {r.netmask}"] for v, r, g in zip(vids, redes, gw)], [])
    col = len(pcs) + 2
    al = [
        dict(enunciado="Que portas dos switches devem ser access e quais devem ser trunk?", cotacao=5,
             resolucao="Access: as portas Fa0/x dos PCs (cada uma numa só VLAN, sem etiqueta).\nTrunk: SW1 Gi0/2 ↔ SW2 Gi0/2 e SW1 Gi0/1 ↔ R1 Gi0/0, porque transportam tramas de várias VLANs (802.1Q)."),
        dict(enunciado=f"Escreva os comandos de SW1 para criar as VLANs, configurar os trunks" + (f" e a porta do {pcs_sw1[0][0]}." if pcs_sw1 else "."), cotacao=10,
             resolucao=mono(*cmd_sw) + "\nEm SW2 criam-se as mesmas VLANs (vlan/name) e o trunk na Gi0/2."),
        dict(enunciado="Configure o router R1 para fazer o encaminhamento entre VLANs (router-on-a-stick).", cotacao=10,
             resolucao=mono(*cmd_r) + "\nUma sub-interface por VLAN, cada uma com o encapsulamento 802.1Q e o IP do gateway da VLAN. Alternativa: switch L3 com SVIs (interface vlan X + ip routing)."),
        dict(enunciado=f"Indique uma configuração IP válida para o {alvo[0]}.", cotacao=5,
             resolucao=f"{alvo[0]} está na VLAN {alvo[3]} → rede {rede_alvo}.\nIP: {rede_alvo.network_address + 2}  Máscara: {rede_alvo.netmask}  Gateway: {gw_alvo}\n(qualquer IP de {gama(rede_alvo)} que não seja o do gateway)"),
        dict(enunciado=f"Uma trama do {alvo[0]} atravessa o trunk SW2 → SW1. O que é acrescentado à trama? Indique os valores de TPID e VID.", cotacao=5,
             resolucao=f"Uma etiqueta 802.1Q de 4 bytes, entre o MAC de origem e o EtherType:\nTPID = 0x8100 (2 bytes)\nTCI (2 bytes) = prioridade (3 bits) + CFI (1 bit) + VID (12 bits)\nVID = {alvo[3]} = {alvo[3]:012b} (0x{alvo[3]:03X})\nAo sair numa porta access, o switch retira a etiqueta."),
        dict(enunciado="Quantos domínios de broadcast e de colisão existem?", cotacao=5,
             resolucao=f"Broadcast: {nv} (um por VLAN).\nColisão: {col} (cada ligação a uma porta de switch/router é um domínio: {len(pcs)} PCs + trunk SW1-SW2 + trunk SW1-R1)."),
    ]
    return add(id=idq, grupo=G4, tipo="aberta", tema="VLANs",
               enunciado=f"Uma empresa tem dois edifícios: SW1 (edifício A) e SW2 (edifício B), ligados pelas portas Gi0/2. O router R1 liga à porta Gi0/1 de SW1 pela sua interface Gi0/0. VLANs: "
               + ", ".join(f"{v} ({nm})" for v, nm in zip(vids, nomes)) + f".\n{tab}{plano}",
               alineas=al)


for i in range(8):
    ex_vlan(f"g4-vlan-{i}")


# ================================================================ Ficha EX3 (enunciado do professor, resolução própria)
FONTE_F = "Ficha EX3 · Endereçamento"
add(id="ex3-1", grupo=G2, tipo="aberta", tema="Conversões", fonte=FONTE_F,
    enunciado="1. Efetuar a conversão dos seguintes endereços (apresentar pelo menos um cálculo da conversão manualmente em cada um dos 4 grupos):",
    alineas=[
        dict(enunciado="1.1 Binário → Decimal: 10101100.01011000.1101001.00010101", cotacao=10,
             resolucao="10101100 = 128+32+8+4 = 172\n01011000 = 64+16+8 = 88\n1101001 = 64+32+8+1 = 105 (o enunciado só tem 7 bits; lê-se 01101001)\n00010101 = 16+4+1 = 21\n→ 172.88.105.21"),
        dict(enunciado="1.2 Decimal → Binário: 192.168.30.12", cotacao=10,
             resolucao="192 = 128+64 = 11000000\n168 = 128+32+8 = 10101000\n30 = 16+8+4+2 = 00011110\n12 = 8+4 = 00001100\n→ 11000000.10101000.00011110.00001100"),
        dict(enunciado="1.3 Binário → Hexadecimal: 1111111100000011:11000100::01111111", cotacao=10,
             resolucao="Grupos de 4 bits:\n1111 1111 0000 0011 = FF03\n1100 0100 = C4\n0111 1111 = 7F\n→ FF03:C4::7F (o :: mantém-se: são grupos de zeros)"),
        dict(enunciado="1.4 Hexadecimal → Binário: FE80::8C", cotacao=10,
             resolucao="F = 1111, E = 1110, 8 = 1000, 0 = 0000 → FE80 = 1111111010000000\n8C = 1000 1100 → 0000000010001100 (16 bits)\n→ 1111111010000000::0000000010001100\n(:: = 6 grupos de 16 zeros)"),
    ])
r2 = N("77.70.20.30/28")
_, a2, o2 = and_or("77.70.20.30", 28)
add(id="ex3-2", grupo=G2, tipo="aberta", tema="Análise de um endereço", fonte=FONTE_F,
    enunciado="2. Considerando o endereço IP 77.70.20.30 com máscara CIDR /28, responda às seguintes questões, justificando a resposta sempre que possível.",
    alineas=[
        dict(enunciado="2.1 É um endereço privado ou público?", cotacao=5, resolucao="Público: classe A (1º octeto 77) e a única rede privada da classe A é 10.0.0.0/8."),
        dict(enunciado="2.2 A que sub-rede pertence este endereço IP? (utilize lógica binária)", cotacao=10, resolucao=f"{a2}Sub-rede 77.70.20.16/28"),
        dict(enunciado="2.3 Qual o endereço broadcast desta sub-rede? (utilize lógica binária)", cotacao=10, resolucao=f"{o2}Broadcast 77.70.20.31"),
        dict(enunciado="2.4 Quantas sub-redes podemos obter com esta máscara?", cotacao=5, resolucao="Classe A (padrão /8) → 28 - 8 = 20 bits emprestados → 2^20 = 1 048 576 sub-redes."),
        dict(enunciado="2.5 Quantos dispositivos de rede podemos endereçar em cada sub-rede?", cotacao=5, resolucao="32 - 28 = 4 bits de host → 2^4 - 2 = 14."),
        dict(enunciado="2.6 Qual o endereço que identifica a 6ª sub-rede?", cotacao=5,
             resolucao="Blocos de 16. A 1ª sub-rede da rede 77.0.0.0/8 é 77.0.0.0, a 6ª é 77.0.0.0 + 5×16 = 77.0.0.80/28.\n(Se o professor contar dentro do último octeto de 77.70.20.x, fica 77.70.20.80.)"),
        dict(enunciado="2.7 Qual o endereço de broadcast da 10ª sub-rede?", cotacao=5,
             resolucao="10ª sub-rede = 9×16 = 144 → 77.0.0.144/28, broadcast 77.0.0.159.\n(Contando em 77.70.20.x: 77.70.20.159.)"),
    ])
add(id="ex3-3a", grupo=G2, tipo="aberta", tema="Tabela classful", fonte=FONTE_F,
    enunciado="3.1 Preencher a tabela utilizando o conceito classful: classe, parte de rede, parte de host, máscara de rede e público/privado.",
    alineas=[dict(enunciado=ip, cotacao=8, resolucao=res) for ip, res in [
        ("194.100.10.120", "Classe C · rede 194.100.10 · host 120 · 255.255.255.0 · público"),
        ("192.168.52.25", "Classe C · rede 192.168.52 · host 25 · 255.255.255.0 · privado (192.168.0.0/16)"),
        ("120.100.3.80", "Classe A · rede 120 · host 100.3.80 · 255.0.0.0 · público"),
        ("172.88.100.5", "Classe B · rede 172.88 · host 100.5 · 255.255.0.0 · público (172.88 está fora de 172.16 a 172.31)"),
        ("210.40.1.20", "Classe C · rede 210.40.1 · host 20 · 255.255.255.0 · público"),
    ]])
cidr_ex = ["180.10.20.50/16", "192.168.50.85/28", "195.20.12.218/29", "205.16.44.55/27", "210.40.50.101/30"]
add(id="ex3-3b", grupo=G2, tipo="aberta", tema="Tabela CIDR", fonte=FONTE_F,
    enunciado="3.2 Preencher a tabela utilizando o conceito classless (CIDR): endereço de sub-rede, gama, broadcast, máscara, nº de sub-redes e nº de hosts por sub-rede.",
    alineas=[dict(enunciado=c, cotacao=8, resolucao=tabela(["Sub-rede", "Gama", "Broadcast", "Máscara", "Nº SR", "Hosts"],
                                                          [[str(N(c).network_address), gama(N(c)), str(N(c).broadcast_address), str(N(c).netmask),
                                                            fmt(2 ** (N(c).prefixlen - DEF[classe(c.split('/')[0])])), fmt(hosts(N(c).prefixlen))]]))
             for c in cidr_ex])
subs4 = list(N("192.168.5.0/24").subnets(new_prefix=26))
add(id="ex3-4", grupo=G3, tipo="aberta", tema="Subnetting com máscara fixa", fonte=FONTE_F,
    enunciado="4. Construa um esquema de endereçamento para a rede 192.168.5.0/26 com: nome da sub-rede, endereço de sub-rede, gama de IPs, nº de endereços por sub-rede, broadcast, máscara decimal e CIDR.",
    alineas=[dict(enunciado="Tabela completa (sub-redes A a D).", cotacao=40,
                  resolucao="A rede 192.168.5.0/24 dividida em /26: blocos de 64 → 4 sub-redes de 62 hosts.\n"
                  + tabela(["Nome", "End SR", "Gama", "End por SR", "Broadcast", "Mk dec", "CIDR"],
                           [[chr(65 + i), str(s.network_address), gama(s), "64", str(s.broadcast_address), "255.255.255.192", "/26"] for i, s in enumerate(subs4)]))])
ex3_5 = vlsm(N("193.18.50.0/24"), [("Dep. A", 24), ("Dep. B", 55), ("Dep. C", 40), ("Dep. D", 5)])[0]
add(id="ex3-5", grupo=G3, tipo="aberta", tema="VLSM", fonte=FONTE_F,
    enunciado="5. Construa um esquema de endereçamento para a empresa AddressK utilizando CIDR/VLSM com o endereço 193.18.50.0/24:\nDep. A = 24 hosts\nDep. B = 55 hosts\nDep. C = 40 hosts\nDep. D = 5 hosts",
    alineas=[dict(enunciado="Tabela: nome, nº hosts, nº end. alocados, endereço de sub-rede, gama, broadcast, máscara decimal e CIDR.", cotacao=40,
                  resolucao="Ordem decrescente: B (55) → /26, C (40) → /26, A (24) → /27, D (5) → /29.\n" + tabela_vlsm(ex3_5)
                  + "\nBate com as pistas da ficha: Dep. C /26, 24 hosts em 193.18.50.128 e Dep. D de .161 a .166.")])

# ================================================================ Exercícios dos slides (resolução própria)
FONTE_S = "Exercício das aulas"
add(id="sl-sn-1", grupo=G2, tipo="aberta", tema="Sim ou Não", fonte=FONTE_S, enunciado="Endereço de rede: 193.10.1.0\nMáscara de rede: 255.255.255.0\nResponda SIM ou NÃO:",
    alineas=[dict(enunciado="O endereço IP 193.10.10.100 pertence a esta rede?", cotacao=10, resolucao="NÃO. A rede é 193.10.1.x; o 3º octeto é 10, não 1."),
             dict(enunciado="É possível configurar 254 hosts nesta rede?", cotacao=10, resolucao="SIM. 8 bits de host: 2^8 - 2 = 254."),
             dict(enunciado="O endereço IP 193.10.1.256 é válido nesta rede?", cotacao=10, resolucao="NÃO. Um octeto vai de 0 a 255.")])
add(id="sl-sn-2", grupo=G2, tipo="aberta", tema="Sim ou Não", fonte=FONTE_S, enunciado="Endereço IP: 10.10.10.12 /25\nResponda SIM ou NÃO:",
    alineas=[dict(enunciado="O IP 10.10.10.0 pode ser atribuído a um host nesta sub-rede?", cotacao=10, resolucao="NÃO. É o endereço da sub-rede (10.10.10.0/25)."),
             dict(enunciado="O IP 10.10.10.126 é o último endereço endereçável nesta sub-rede?", cotacao=10, resolucao="SIM. Sub-rede .0 a .127; broadcast .127, último atribuível .126."),
             dict(enunciado="O IP 10.10.10.130 pertence a esta mesma sub-rede?", cotacao=10, resolucao="NÃO. Está na 2ª sub-rede /25 (.128 a .255).")])
add(id="sl-sn-3", grupo=G2, tipo="aberta", tema="Sim ou Não", fonte=FONTE_S, enunciado="Endereço IP: 192.168.10.140\nMáscara: 255.255.255.192\nResponda SIM ou NÃO:",
    alineas=[dict(enunciado="O IP 192.168.10.128 é o endereço de rede desta sub-rede?", cotacao=10, resolucao="SIM. Blocos de 64: 140 está no bloco 128 a 191."),
             dict(enunciado="É possível configurar 64 hosts nesta sub-rede?", cotacao=10, resolucao="NÃO. 64 endereços, mas 62 hosts."),
             dict(enunciado="O IP 192.168.10.170 pertence a esta sub-rede?", cotacao=10, resolucao="SIM. 128 ≤ 170 ≤ 191.")])
add(id="sl-wild", grupo=G2, tipo="aberta", tema="Máscara invertida", fonte=FONTE_S, enunciado="Qual o valor da máscara invertida para os seguintes exemplos:",
    alineas=[dict(enunciado=m, cotacao=10, resolucao=f"255.255.255.255 - {m} = {w}") for m, w in
             [("255.255.0.0", "0.0.255.255"), ("255.255.128.0", "0.0.127.255"), ("255.255.255.224", "0.0.0.31")]])
add(id="sl-vlsm", grupo=G3, tipo="aberta", tema="VLSM", fonte=FONTE_S,
    enunciado="Endereço padrão: 192.168.77.0/24\nDep. Comercial: 50 hosts\nDep. Financeiro: 20 hosts\nDep. Administrativo: 5 hosts\nConstrua a tabela de endereçamento com CIDR/VLSM.",
    alineas=[dict(enunciado="Tabela resumo.", cotacao=40, resolucao=tabela_vlsm(vlsm(N("192.168.77.0/24"), [("Comercial", 50), ("Financeiro", 20), ("Administrativo", 5)])[0]))])
svg16 = svg_cadeia(["R1", "R2"], [("192.168.1.0/24", ".1"), ("192.168.2.0/24", ".1")], [("172.31.1.0/24", ".2", ".1")], [".2", ".2"])
add(id="sl-rot-1", grupo=G4, tipo="aberta", tema="Encaminhamento estático", fonte=FONTE_S,
    enunciado=f"Complete a configuração dos PCs e as rotas dos routers para as duas LANs comunicarem:\n{svg16}",
    alineas=[dict(enunciado="Configuração dos PCs (IP, máscara, gateway).", cotacao=20,
                  resolucao="PC LAN 1: 192.168.1.2  255.255.255.0  gateway 192.168.1.1\nPC LAN 2: 192.168.2.2  255.255.255.0  gateway 192.168.2.1"),
             dict(enunciado="Rota estática em cada router.", cotacao=20,
                  resolucao="R1 (WAN .2) chega à LAN 2 pela WAN de R2 (.1):\n" + mono("R1: ip route 192.168.2.0 255.255.255.0 172.31.1.1", "R2: ip route 192.168.1.0 255.255.255.0 172.31.1.2")
                  + "\nAlternativa: rotas por defeito 0.0.0.0 0.0.0.0 172.31.1.1 em R1 e 0.0.0.0 0.0.0.0 172.31.1.2 em R2.")])
svg23 = svg_cadeia(["R1", "R2"], [("192.168.1.0/26", ".62"), ("10.10.10.16/28", ".30")], [("100.100.100.0/30", ".1", ".2")], [".1", ".17"])
add(id="sl-rot-2", grupo=G4, tipo="aberta", tema="Encaminhamento estático e RIP", fonte=FONTE_S,
    enunciado=f"Exercício prático: efetuar o encaminhamento estático e dinâmico entre as duas redes de modo a que ambas possam comunicar entre si.\n{svg23}",
    alineas=[
        dict(enunciado="Endereçamento estático das interfaces e dos PCs.", cotacao=10,
             resolucao="R1 Gi0/0: 192.168.1.62 255.255.255.192 · R1 Se0/0/0: 100.100.100.1 255.255.255.252\nR2 Se0/0/0: 100.100.100.2 255.255.255.252 · R2 Gi0/0: 10.10.10.30 255.255.255.240\nPC1: 192.168.1.1/26 gw 192.168.1.62 · PC2: 10.10.10.17/28 gw 10.10.10.30\n(.62 e .30 são os últimos atribuíveis de cada LAN.)"),
        dict(enunciado="Encaminhamento estático em ambos os routers.", cotacao=10,
             resolucao=mono("R1(config)# ip route 10.10.10.16 255.255.255.240 100.100.100.2", "R2(config)# ip route 192.168.1.0 255.255.255.192 100.100.100.1")),
        dict(enunciado="Tabela de encaminhamento de R1 e interpretação.", cotacao=10,
             resolucao=mono("C    100.100.100.0/30 is directly connected, Serial0/0/0", "C    192.168.1.0/26 is directly connected, GigabitEthernet0/0",
                            "S    10.10.10.16/28 [1/0] via 100.100.100.2") + "\nDuas redes ligadas (C) e uma estática (S) para a LAN de R2 pelo próximo salto 100.100.100.2."),
        dict(enunciado="Segunda versão com RIP v2: configuração e o que muda na tabela.", cotacao=10,
             resolucao=mono("R1(config)# router rip", " version 2", " no auto-summary", " network 192.168.1.0", " network 100.0.0.0",
                            "R2(config)# router rip", " version 2", " no auto-summary", " network 10.0.0.0", " network 100.0.0.0")
             + "\nO comando network é classful (100.100.100.0 vira 100.0.0.0). O no auto-summary evita que o RIP resuma as sub-redes.\nNa tabela a rota remota passa a R: R 10.10.10.16/28 [120/1] via 100.100.100.2 (120 = distância administrativa do RIP, 1 = saltos)."),
    ])
add(id="sl-vlan-1", grupo=G4, tipo="aberta", tema="VLANs", fonte=FONTE_S,
    enunciado="Caso prático: dois computadores no mesmo switch, PC1 na VLAN 10 com 192.168.10.1/24 e PC2 na VLAN 20 com 192.168.10.2/24 (mesma gama IP). Conseguem fazer ping entre si sem um router?",
    alineas=[dict(enunciado="Responda e justifique.", cotacao=20,
                  resolucao="Não. Cada VLAN é um domínio de broadcast separado: o PC1 envia um pedido ARP em broadcast para descobrir o MAC de 192.168.10.2 e o switch só o entrega a portas da VLAN 10. Sem resposta ARP não há ping."),
             dict(enunciado="E se ligarmos um router com sub-interfaces nas duas VLANs?", cotacao=20,
                  resolucao="Continua a não funcionar bem: como estão na mesma sub-rede, cada PC acha que o outro é local e nunca usa o gateway. A solução é dar uma sub-rede a cada VLAN (ex: 192.168.10.0/24 e 192.168.20.0/24) e encaminhar no router.")])
add(id="sl-vlan-2", grupo=G4, tipo="aberta", tema="VLANs", fonte=FONTE_S,
    enunciado="Exercício prático: definir as VLANs 10 e 20 em dois switches (edifícios A e B), com trunk entre eles e até ao router, e encaminhar entre VLANs com sub-interfaces (gateway .254 em cada VLAN). Hosts .1 e .2 em cada VLAN.\n(Assume-se VLAN 10 = 192.168.10.0/24 e VLAN 20 = 192.168.20.0/24.)",
    alineas=[
        dict(enunciado="Nos switches, criar as VLANs e definir as portas trunk e de acesso.", cotacao=15,
             resolucao=mono("vlan 10", " name VLAN10", "vlan 20", " name VLAN20", "interface Fa0/1", " switchport mode access", " switchport access vlan 10",
                            "interface Fa0/2", " switchport mode access", " switchport access vlan 20", "interface Gi0/1", " switchport mode trunk")),
        dict(enunciado="Encapsulamento dot1Q e endereçamento das sub-interfaces do router.", cotacao=15,
             resolucao=mono("interface Gi0/0", " no shutdown", "interface Gi0/0.10", " encapsulation dot1Q 10", " ip address 192.168.10.254 255.255.255.0",
                            "interface Gi0/0.20", " encapsulation dot1Q 20", " ip address 192.168.20.254 255.255.255.0")),
        dict(enunciado="O que se vê numa trama capturada no trunk e no show vlan brief?", cotacao=10,
             resolucao="Na trama: campo 802.1Q depois do MAC de origem com TPID 0x8100, prioridade, CFI e VLAN ID 10 ou 20.\nshow vlan brief: lista as VLANs (1 default, 10, 20) e as portas de acesso de cada uma; as portas trunk não aparecem na lista (vê-se com show interfaces trunk)."),
    ])

# ---------------------------------------------------------------- limpeza e escrita
import re
TAGS = r"(?!/?(?:div|table|tr|th|td|svg|line|text|circle|rect|b|br|span|small)\b)"


def esc_ph(x):
    if isinstance(x, str):
        return re.sub(r"<" + TAGS + r"([^<>]*)>", r"&lt;\1&gt;", x)
    if isinstance(x, list):
        return [esc_ph(y) for y in x]
    if isinstance(x, dict):
        return {k: esc_ph(v) for k, v in x.items()}
    return x


perguntas[:] = [esc_ph(q) for q in perguntas]
for q in perguntas:
    if q.get("fonte") is None:
        q.pop("fonte", None)

fichas = [
    dict(titulo="Ficha EX3 · Endereçamento", ids=["ex3-1", "ex3-2", "ex3-3a", "ex3-3b", "ex3-4", "ex3-5"]),
    dict(titulo="Exercícios dos slides", ids=["sl-sn-1", "sl-sn-2", "sl-sn-3", "sl-wild", "sl-vlsm", "sl-rot-1", "sl-rot-2", "sl-vlan-1", "sl-vlan-2"]),
]
banco = dict(
    uc="RC",
    titulo="2º teste · Endereçamento, encaminhamento e VLANs",
    descricao="Estrutura estimada a partir do 1º teste do prof. Paulo Macedo (escolhas múltiplas a 2 valores + exercícios). Matéria dos slides 7 (endereçamento IP), 10 (encaminhamento) e 11 (VLANs). Exercícios gerados e calculados automaticamente.",
    cabula="/estudo/paginas/rc-cabula.html",
    estrutura=[
        dict(grupo=G1, n=4, cotacao=8),
        dict(grupo=G2, n=1, cotacao=4),
        dict(grupo=G3, n=1, cotacao=4),
        dict(grupo=G4, n=1, cotacao=4),
    ],
    fichasTitulo="Ficha e exercícios das aulas (resolução própria)",
    fichas=fichas,
    perguntas=perguntas,
)
ids = [q["id"] for q in perguntas]
assert len(ids) == len(set(ids)), "ids repetidos"
for f in fichas:
    for i in f["ids"]:
        assert i in ids, i
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(banco, fh, ensure_ascii=False, indent=1)
from collections import Counter
print(len(perguntas), "perguntas", Counter(q["grupo"] for q in perguntas))
