"""Exercícios no formato do 2º teste do 1º turno (dezembro de 2026), dado pelo Ricardo:
  Ex. 1: ordem, grau de um vértice, arcos paralelos, subgrafo parcial, fortemente conexo, cadeia não elementar
  Ex. 2: matriz de adjacência, fecho transitivo direto e inverso, circuito euleriano, construir digrafo a partir da matriz
  Ex. 3: circuito hamiltoniano e descrição do circuito
  Ex. 4: árvore geradora mínima com o Prim feito na matriz triangular (tabela da aula)
Tudo calculado aqui (sem LaTeX, texto simples)."""
import itertools, math, random
from grafos import digraph_maps, reach, table, adj_from_edges, ham_cycle, dijkstra

N1, N2, N3, N4 = "Ex. 1 · Multigrafo orientado", "Ex. 2 · Matriz e fechos", "Ex. 3 · Circuito hamiltoniano", "Ex. 4 · Prim (matriz) e Dijkstra (tabela)"
FONTE = "Gerado no formato do teste do 1º turno"

def R(pede, passos, exame, termos=None):
    t = ("<b>📖 Termos</b>\n" + "\n".join(f"• {x}" for x in termos) + "\n\n") if termos else ""
    p = "\n".join(f"{i}) {x}" for i, x in enumerate(passos, 1))
    return (f"<b>📌 O que pedem</b>\n{pede}\n\n{t}<b>🪜 Como fazer</b>\n{p}\n\n<b>✍️ Resposta como no exame</b>\n"
            f"<div style='border-left:3px solid #1f9d55;padding:6px 10px;margin-top:4px;background:var(--chip);border-radius:8px'>{exame}</div>")

def S(xs, V):
    return "{" + ", ".join(sorted(xs, key=V.index)) + "}"

def seq(p):
    return "[" + ", ".join(p) + "]"

def arcs_txt(A):
    return ", ".join(f"({a},{b})" for a, b in A)

# ---------------------------------------------------------------- desenho (aceita arcos paralelos e opostos)
_id = [0]
def circ_pos(V):
    n = len(V)
    return {v: (.5 + .45 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), .5 + .45 * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i, v in enumerate(V)}

def svg_multi(V, A, directed=True, pos=None, weights=None, w=300, h=260, hl=None):
    _id[0] += 1; mid = f"tm{_id[0]}"
    pos = pos or circ_pos(V)
    pad = 24; r = 12
    P = {v: (pad + pos[v][0] * (w - 2 * pad), pad + pos[v][1] * (h - 2 * pad)) for v in V}
    s = [f"<svg viewBox='0 0 {w} {h}' width='{w}' style='max-width:100%;display:block;margin:6px auto' font-family='system-ui,sans-serif'>"]
    if directed:
        s.append(f"<defs><marker id='{mid}' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='currentColor'/></marker></defs>")
    grupos = {}
    for i, (a, b) in enumerate(A):
        grupos.setdefault(frozenset((a, b)), []).append(i)
    off = {}
    for k, idx in grupos.items():
        m = len(idx)
        for j, i in enumerate(idx):
            o = (j - (m - 1) / 2) * 26
            a, b = A[i]
            if m > 1 and V.index(a) > V.index(b):
                o = -o  # o deslocamento é medido sempre no mesmo sentido para o par
            off[i] = o
    hl = hl or []
    for i, (a, b) in enumerate(A):
        (x1, y1), (x2, y2) = P[a], P[b]
        d = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / d, (x2 - x1) / d
        cx, cy = (x1 + x2) / 2 + nx * off[i], (y1 + y2) / 2 + ny * off[i]
        # encurta nas pontas, seguindo a direção para o ponto de controlo
        def enc(px, py, qx, qy, k):
            dd = math.hypot(qx - px, qy - py) or 1
            return px + (qx - px) / dd * k, py + (qy - py) / dd * k
        sx, sy = enc(x1, y1, cx, cy, r)
        ex, ey = enc(x2, y2, cx, cy, r + (2 if directed else 0))
        on = (a, b) in hl
        st = "#e5484d" if on else "currentColor"
        mk = f" marker-end='url(#{mid})'" if directed else ""
        s.append(f"<path d='M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}' fill='none' stroke='{st}' stroke-width='{3 if on else 1.5}'{mk}/>")
        if weights is not None:
            t = str(weights[i]); tw = 7 * len(t) + 6
            lx, ly = (x1 + x2) / 4 + cx / 2, (y1 + y2) / 4 + cy / 2
            s.append(f"<rect x='{lx - tw / 2:.1f}' y='{ly - 8:.1f}' width='{tw}' height='15' rx='4' fill='var(--card)' opacity='.92'/><text x='{lx:.1f}' y='{ly + 3.5:.1f}' font-size='11' text-anchor='middle' fill='{st}' font-weight='600'>{t}</text>")
    for v in V:
        x, y = P[v]
        s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='var(--card)' stroke='currentColor' stroke-width='1.6'/><text x='{x:.1f}' y='{y + 4:.1f}' font-size='11' text-anchor='middle' fill='currentColor' font-weight='700'>{v}</text>")
    s.append("</svg>")
    return "".join(s)

def mat_adj(V, A):
    rows = [[a] + [sum(1 for x in A if x == (a, b)) for b in V] for a in V]
    return table([""] + V, rows)

def strongly(V, A):
    o, i = digraph_maps(V, A)
    return all(reach(o, V[0]) == set(V) and reach(i, V[0]) == set(V) for _ in [0])

def comps_fortes(V, A):
    o, i = digraph_maps(V, A)
    done, out = set(), []
    for v in V:
        if v in done: continue
        c = reach(o, v) & reach(i, v); done |= c; out.append(sorted(c, key=V.index))
    return out

def camadas(viz, v, V):
    lay = [[v]]; seen = {v}
    while True:
        nxt = sorted({y for x in lay[-1] for y in viz[x]} - seen, key=V.index)
        if not nxt: break
        lay.append(nxt); seen |= set(nxt)
    return lay

def lay_txt(lay):
    return " ∪ ".join("{" + ", ".join(l) + "}" for l in lay)

# ================================================================ EX. 1
def ex1(idx):
    rnd = random.Random(1000 + idx)
    while True:
        n = rnd.randint(5, 6)
        V = list("ABCDEFG")[:n] if rnd.random() < .5 else [f"v{i}" for i in range(1, n + 1)]
        base = set()
        forte = rnd.random() < 0.5
        if forte:
            perm = V[:]; rnd.shuffle(perm)
            for a, b in zip(perm, perm[1:] + perm[:1]): base.add((a, b))
        while len(base) < n + rnd.randint(1, 3):
            a, b = rnd.sample(V, 2)
            if (b, a) in base and rnd.random() < .6: continue
            base.add((a, b))
        A = list(base)
        par = rnd.choice(A); A.append(par)  # um par de arcos paralelos
        if rnd.random() < .5:
            a, b = rnd.choice([x for x in base if x != par])
            if (b, a) not in base: A.append((b, a))  # arco oposto (armadilha: não é paralelo)
        rnd.shuffle(A)
        und = adj_from_edges(V, A)
        if any(len(und[v]) == 0 for v in V): continue
        o, i = digraph_maps(V, A)
        if strongly(V, A) != forte: continue
        break
    v = rnd.choice(V)
    dp, dm = sum(1 for a, b in A if a == v), sum(1 for a, b in A if b == v)
    opostos = sorted({(a, b) for a, b in A if (b, a) in A and V.index(a) < V.index(b)})
    # subgrafo parcial: tira 1 vértice e 1 arco
    tira = rnd.choice(V)
    Vs = [x for x in V if x != tira]
    As = [x for x in dict.fromkeys(A) if tira not in x]
    if len(As) > 2: As = As[:-1]
    # cadeia não elementar: ciclo na versão sem setas + mais um passo
    cad = None
    for s0 in V:
        st = [[s0]]
        while st and not cad:
            p = st.pop()
            for y in sorted(und[p[-1]], key=V.index):
                if y == s0 and len(p) >= 3:
                    ext = [z for z in und[s0] if z not in (p[1], p[-1])]
                    cad = p + [s0] + ([ext[0]] if ext else [p[1]]); break
                if y not in p: st.append(p + [y])
        if cad: break
    pos = circ_pos(V)
    comps = comps_fortes(V, A)
    if forte:
        ciclo_txt = f"ΓX = Γ⁻¹X = V para X = {V[0]}: de {V[0]} chega-se a todos e todos chegam a {V[0]}."
    else:
        ciclo_txt = "componentes fortemente conexas: " + ", ".join("{" + ", ".join(c) + "}" for c in comps)
    o, i = digraph_maps(V, A)
    Gd = reach(o, V[0]); Gi = reach(i, V[0])
    motivo = ""
    for x in V:
        if not o[x]: motivo = f"Do vértice {x} não sai nenhuma seta (deg⁺({x}) = 0), por isso de {x} não se chega a mais nenhum vértice."; break
        if not i[x]: motivo = f"Ao vértice {x} não chega nenhuma seta (deg⁻({x}) = 0), por isso nenhum outro vértice consegue chegar a {x}."; break
    al = [
        dict(enunciado="Indique a ordem do grafo.", cotacao=5, resolucao=R(
            "O número de vértices do grafo.",
            ["Conta as bolinhas (vértices). Não confundas com o nº de arcos, que é a dimensão."],
            f"A ordem de G é |V| = {n}, com V = {S(V, V)}.", ["Ordem: nº de vértices, |V|. Dimensão (ou tamanho): nº de arestas/arcos, |A|."])),
        dict(enunciado=f"Indique o grau do vértice {v}.", cotacao=7.5, resolucao=R(
            f"Quantos arcos tocam em {v}, separando os que saem dos que entram.",
            [f"Conta as setas que SAEM de {v}: deg⁺({v}).", f"Conta as setas que ENTRAM em {v}: deg⁻({v}).",
             "O grau é a soma dos dois. Arcos paralelos contam cada um."],
            f"deg⁺({v}) = {dp} (arcos que saem), deg⁻({v}) = {dm} (arcos que entram), logo deg({v}) = deg⁺({v}) + deg⁻({v}) = {dp} + {dm} = {dp + dm}.",
            ["deg⁺(v) (semigrau exterior): nº de arcos com origem em v.", "deg⁻(v) (semigrau interior): nº de arcos com destino em v."])),
        dict(enunciado="O grafo tem arcos paralelos? Justifique.", cotacao=7.5, resolucao=R(
            "Ver se há dois ou mais arcos com a MESMA origem e o MESMO destino.",
            ["Procura pares de setas entre os mesmos dois vértices.", "Vê o sentido: só são paralelos se apontarem para o mesmo lado.",
             "Dois arcos em sentidos contrários (u→v e v→u) NÃO são paralelos."],
            f"Sim: os arcos ({par[0]},{par[1]}) aparecem duas vezes (mesma origem {par[0]} e mesmo destino {par[1]}), logo são arcos paralelos e G é um multigrafo orientado." +
            (f"\nOs arcos {', '.join(f'({a},{b}) e ({b},{a})' for a, b in opostos)} não são paralelos, porque têm sentidos opostos." if opostos else ""),
            ["Arcos paralelos: arcos distintos com a mesma origem e o mesmo destino."])),
        dict(enunciado="Apresente um subgrafo parcial do grafo.", cotacao=10, resolucao=R(
            "Um grafo obtido de G tirando alguns vértices E alguns arcos.",
            ["Tira um vértice e todos os arcos que tocam nele (fica um subgrafo).", "Tira ainda pelo menos um arco (fica parcial).", "Escreve V' e A' e desenha."],
            f"Retirando o vértice {tira} (e os arcos que nele incidem) e mais um arco, obtém-se o subgrafo parcial G' = (V', A') com V' = {S(Vs, V)} ⊂ V e A' = {{{arcs_txt(As)}}} ⊂ A:\n" +
            svg_multi(Vs, As, pos={x: pos[x] for x in Vs}, w=260, h=220),
            ["Subgrafo: tiram-se vértices (e os arcos que lhes tocam).", "Grafo parcial: tiram-se arcos, ficam todos os vértices.", "Subgrafo parcial: tiram-se vértices e arcos."])),
        dict(enunciado="O grafo é fortemente conexo? Justifique.", cotacao=10, resolucao=R(
            "Ver se de qualquer vértice se chega a qualquer outro, respeitando o sentido das setas.",
            [f"Calcula ΓX e Γ⁻¹X de um vértice, por exemplo {V[0]}.", "Se os dois derem V, é fortemente conexo.",
             "Se não, indica as componentes fortemente conexas (ΓX ∩ Γ⁻¹X de cada vértice).", "Atalho para o não: um vértice sem setas a sair (ou a entrar) estraga logo."],
            (f"Γ{V[0]} = {S(Gd, V)} (onde se chega a partir de {V[0]}) e Γ⁻¹{V[0]} = {S(Gi, V)} (quem consegue chegar a {V[0]}). " +
             (f"Como ambos são iguais a V, de qualquer vértice chega-se a qualquer outro (passando por {V[0]}), logo G é fortemente conexo." if forte else
              (motivo + " " if motivo else "") +
              f"Como Γ{V[0]} ∩ Γ⁻¹{V[0]} ≠ V, G não é fortemente conexo.\nAs componentes fortemente conexas (grupos de vértices que vão e voltam uns aos outros) são: " +
              ", ".join("{" + ", ".join(c) + "}" for c in comps) + ".")),
            ["Fortemente conexo: para quaisquer u, v existe caminho de u para v e de v para u (a respeitar as setas)."])),
        dict(enunciado="Apresente uma cadeia não elementar.", cotacao=10, resolucao=R(
            "Uma cadeia (ignora-se o sentido das setas) que passe duas vezes pelo mesmo vértice.",
            ["Numa cadeia as setas não contam: basta haver ligação.", "Faz uma volta fechada e continua mais um passo, ou passa duas vezes num vértice."],
            f"{seq(cad)} é uma cadeia de G (vértices consecutivos ligados por arcos, ignorando a orientação) que passa duas vezes pelo vértice {cad[0]}, logo não é elementar.",
            ["Cadeia: sequência de vértices ligados por arestas/arcos, sem olhar ao sentido.", "Elementar: não repete vértices."])),
    ]
    return dict(id=f"t1-{idx}", grupo=N1, tipo="aberta", tema="Multigrafo orientado", fonte=FONTE,
                enunciado=f"Considere o grafo orientado G = (V, A) com os arcos {arcs_txt(A)}:\n" + svg_multi(V, A), alineas=al)

# ================================================================ EX. 2
def hierholzer_d(V, A, s):
    out = {v: [] for v in V}
    for a, b in A: out[a].append(b)
    for v in V: out[v].sort(key=V.index, reverse=True)
    st, c = [s], []
    while st:
        x = st[-1]
        if out[x]: st.append(out[x].pop())
        else: c.append(st.pop())
    return c[::-1]

def ex2(idx):
    rnd = random.Random(2000 + idx)
    euler = rnd.random() < 0.5
    while True:
        n = rnd.randint(5, 6)
        V = list("ABCDEF")[:n] if rnd.random() < .5 else [f"v{i}" for i in range(1, n + 1)]
        A = set()
        if euler:
            for _ in range(rnd.randint(2, 3)):
                k = rnd.randint(3, n)
                c = rnd.sample(V, k)
                arcs = list(zip(c, c[1:] + c[:1]))
                if any(x in A for x in arcs): break
                A |= set(arcs)
        else:
            while len(A) < n + rnd.randint(2, 4):
                a, b = rnd.sample(V, 2); A.add((a, b))
        A = sorted(A, key=lambda x: (V.index(x[0]), V.index(x[1])))
        und = adj_from_edges(V, A)
        if any(not und[v] for v in V): continue
        o, i = digraph_maps(V, A)
        bal = all(len([1 for a, b in A if a == v]) == len([1 for a, b in A if b == v]) for v in V)
        from grafos import connected
        if not connected(und) or bal != euler: continue
        v = rnd.choice(V)
        if len(reach(o, v)) < 3 or len(reach(i, v)) < 2: continue
        break
    o, i = digraph_maps(V, A)
    dp = {x: sum(1 for a, b in A if a == x) for x in V}; dm = {x: sum(1 for a, b in A if b == x) for x in V}
    tabg = table(["v", "deg⁺ (linha)", "deg⁻ (coluna)"], [[x, dp[x], dm[x]] for x in V])
    ld, li = camadas(o, v, V), camadas(i, v, V)
    if euler:
        circ = hierholzer_d(V, A, V[0])
        assert len(circ) == len(A) + 1
        eul = (tabg + f"D é conexo e deg⁺(v) = deg⁻(v) para todo o vértice v, logo D tem circuito euleriano. Por exemplo {seq(circ)} (usa os {len(A)} arcos, cada um uma vez).")
    else:
        mau = [x for x in V if dp[x] != dm[x]]
        eul = (tabg + f"Para haver circuito euleriano seria preciso deg⁺(v) = deg⁻(v) para todos os vértices. Mas, por exemplo, deg⁺({mau[0]}) = {dp[mau[0]]} ≠ {dm[mau[0]]} = deg⁻({mau[0]}), logo D não tem circuito euleriano.")
    # digrafo a construir a partir de uma matriz
    m = rnd.randint(4, 5)
    W = list("PQRST")[:m]
    B = set()
    while len(B) < m + 2:
        a, b = rnd.sample(W, 2); B.add((a, b))
    B = sorted(B, key=lambda x: (W.index(x[0]), W.index(x[1])))
    if rnd.random() < .4:
        B.append(B[0])  # entrada 2: arcos paralelos
    al = [
        dict(enunciado="Determine a matriz de adjacência de D.", cotacao=10, resolucao=R(
            "A tabela com o nº de arcos de cada vértice (linha) para cada vértice (coluna).",
            ["Ordena os vértices e faz uma tabela com eles nas linhas e nas colunas.", "Linha = de onde SAI a seta; coluna = para onde VAI.",
             "Escreve 1 (ou o nº de arcos, se houver paralelos) e 0 onde não há seta.", "Confirma: soma de cada linha = deg⁺, soma de cada coluna = deg⁻. Num digrafo a matriz NÃO tem de ser simétrica."],
            f"Ordenando os vértices {', '.join(V)}, a matriz de adjacência M = [mij], com mij = nº de arcos de vi para vj, é:\n" + mat_adj(V, A))),
        dict(enunciado=f"Determine o fecho transitivo direto e o fecho transitivo inverso do vértice {v}.", cotacao=10, resolucao=R(
            f"Γ{v}: onde se chega a partir de {v}. Γ⁻¹{v}: de onde se chega a {v}.",
            [f"Γ{v}: começa com {{{v}}}; junta os vértices para onde saem setas de {v} (linha {v} da matriz); depois os sucessores desses; até não entrar ninguém novo.",
             f"Γ⁻¹{v}: o mesmo, mas andando CONTRA as setas (coluna {v} da matriz): quem aponta para {v}, quem aponta para esses, …",
             "Escreve as camadas para se ver o raciocínio."],
            f"Γ{v} = {lay_txt(ld)} = {S(reach(o, v), V)}\nΓ⁻¹{v} = {lay_txt(li)} = {S(reach(i, v), V)}",
            ["Fecho transitivo direto ΓX: vértices atingíveis a partir de X por caminhos de qualquer comprimento (inclui X).", "Fecho transitivo inverso Γ⁻¹X: vértices a partir dos quais se atinge X."])),
        dict(enunciado="O digrafo D tem um circuito euleriano? Justifique.", cotacao=10, resolucao=R(
            "Ver se há um caminho fechado que use todos os arcos uma única vez.",
            ["Confirma que D é conexo (ignorando as setas).", "Faz a tabela deg⁺ / deg⁻ (somas das linhas e das colunas da matriz).",
             "Circuito euleriano ⇔ deg⁺(v) = deg⁻(v) em TODOS os vértices.", "Se existir, constrói-o riscando os arcos e confirma que os usaste todos."],
            eul)),
        dict(enunciado="Construa o digrafo cuja matriz de adjacência é:\n" + mat_adj(W, B), cotacao=10, resolucao=R(
            "Desenhar o digrafo que corresponde a esta matriz.",
            ["Desenha um ponto por vértice (as linhas/colunas).", "Para cada entrada mij ≠ 0, desenha mij setas da linha i para a coluna j.",
             "Um 2 quer dizer dois arcos paralelos; um número na diagonal seria um lacete.", "Confirma contando: nº de setas = soma de todas as entradas."],
            f"Os arcos são {arcs_txt(B)} ({len(B)} arcos = soma das entradas da matriz):\n" + svg_multi(W, B, w=260, h=220))),
    ]
    return dict(id=f"t2-{idx}", grupo=N2, tipo="aberta", tema="Digrafo e matriz", fonte=FONTE,
                enunciado=f"Considere o digrafo D com os arcos {arcs_txt(A)}:\n" + svg_multi(V, A), alineas=al)

# ================================================================ EX. 3
def ham_d(V, A):
    out = {v: set() for v in V}
    for a, b in A: out[a].add(b)
    for p in itertools.permutations(V[1:]):
        c = [V[0], *p, V[0]]
        if all(y in out[x] for x, y in zip(c, c[1:])): return c
    return None

def ex3(idx):
    rnd = random.Random(3000 + idx)
    orient = rnd.random() < 0.6
    tem = rnd.random() < 0.65
    for _ in range(4000):
        n = rnd.randint(5, 7)
        V = list("ABCDEFG")[:n]
        if orient:
            A = set()
            if tem:
                p = V[:]; rnd.shuffle(p); A |= set(zip(p, p[1:] + p[:1]))
            while len(A) < n + rnd.randint(2, 4):
                a, b = rnd.sample(V, 2)
                if (b, a) not in A: A.add((a, b))
            A = sorted(A, key=lambda x: (V.index(x[0]), V.index(x[1])))
            c = ham_d(V, A)
            if (c is not None) != tem: continue
            dp = {x: sum(1 for a, b in A if a == x) for x in V}; dm = {x: sum(1 for a, b in A if b == x) for x in V}
            if not tem:
                z = [x for x in V if dp[x] == 0 or dm[x] == 0]
                um_in = {}
                for x in V:
                    if dm[x] == 1: um_in.setdefault([a for a, b in A if b == x][0], []).append(x)
                dup = [(s, xs) for s, xs in um_in.items() if len(xs) > 1]
                if not z and not dup: continue
                if z:
                    x = z[0]
                    razao = (f"deg⁻({x}) = 0: nenhum arco chega a {x}, por isso nenhum circuito pode passar por {x}." if dm[x] == 0
                             else f"deg⁺({x}) = 0: nenhum arco sai de {x}, por isso um circuito que chegue a {x} não consegue continuar.")
                else:
                    s, xs = dup[0]
                    razao = (f"Os vértices {xs[0]} e {xs[1]} só recebem um arco cada, e ambos vêm de {s}: o circuito teria de usar ({s},{xs[0]}) e ({s},{xs[1]}), "
                             f"ou seja, sair duas vezes de {s}, o que é impossível num circuito hamiltoniano.")
            break
        else:
            E = set()
            if tem:
                p = V[:]; rnd.shuffle(p)
                E |= {tuple(sorted(e, key=V.index)) for e in zip(p, p[1:] + p[:1])}
            while len(E) < n + rnd.randint(1, 3):
                a, b = sorted(rnd.sample(V, 2), key=V.index); E.add((a, b))
            A = sorted(E, key=lambda x: (V.index(x[0]), V.index(x[1])))
            adj = adj_from_edges(V, A)
            if any(len(adj[x]) < 1 for x in V): continue
            c = ham_cycle(adj, V)
            if (c is not None) != tem: continue
            if not tem:
                g1 = [x for x in V if len(adj[x]) == 1]
                g2c = {}
                for x in V:
                    if len(adj[x]) == 2:
                        for y in adj[x]: g2c.setdefault(y, set()).add(x)
                tres = [(y, xs) for y, xs in g2c.items() if len(xs) >= 3]
                if g1:
                    razao = f"deg({g1[0]}) = 1: num ciclo cada vértice precisa de 2 arestas (entrar e sair), e {g1[0]} só tem uma."
                elif tres:
                    y, xs = tres[0]; xs = sorted(xs, key=V.index)[:3]
                    razao = (f"Os vértices {', '.join(xs)} têm grau 2 e são todos vizinhos de {y}: pela regra 1 as arestas {', '.join('{' + y + ',' + x + '}' for x in xs)} "
                             f"teriam de estar todas no ciclo, mas {y} só pode ter 2 arestas no ciclo.")
                else:
                    continue
            break
    pos = circ_pos(V)
    if tem:
        cyc_arcs = list(zip(c, c[1:]))
        if orient:
            dp = {x: sum(1 for a, b in A if a == x) for x in V}; dm = {x: sum(1 for a, b in A if b == x) for x in V}
            ob = [x for x in V if dm[x] == 1 or dp[x] == 1]
            dica = (f"Começa pelos vértices com só um arco a entrar ou a sair ({', '.join(ob)}): esse arco é obrigatório." if ob else
                    "Começa num vértice e escolhe arcos que não fechem a volta antes de passar por todos; se ficares preso, volta atrás.")
        else:
            adj = adj_from_edges(V, A)
            ob = [x for x in V if len(adj[x]) == 2]
            dica = (f"Os vértices de grau 2 ({', '.join(ob)}) obrigam as suas duas arestas a estar no ciclo." if ob else
                    "Começa num vértice e escolhe arestas sem fechar a volta antes do fim; se ficares preso, volta atrás.")
        exame = (f"Sim. {seq(c)} é um {'circuito' if orient else 'ciclo'} hamiltoniano: {'segue o sentido dos arcos ' if orient else ''}passa uma única vez por cada um dos {n} vértices e regressa ao vértice inicial {c[0]}.\n" +
                 svg_multi(V, A, directed=orient, pos=pos, hl=cyc_arcs + ([] if orient else [(b, a) for a, b in cyc_arcs])))
    else:
        dica = "Procura um vértice que impossibilite a volta: sem setas a entrar ou a sair, grau 1, ou regras dos vértices de grau 2 em contradição."
        exame = f"Não. {razao} Logo G não tem {'circuito' if orient else 'ciclo'} hamiltoniano."
    nome = "o digrafo" if orient else "o grafo"
    al = [dict(enunciado=f"Verifique se {nome} tem um {'circuito' if orient else 'ciclo'} hamiltoniano e, em caso afirmativo, descreva-o.", cotacao=25, resolucao=R(
        "Ver se existe uma volta que passe uma única vez por cada vértice e regresse ao início; se existir, escrevê-la.",
        ["Tem de passar por TODOS os vértices, uma vez cada (não interessa usar todas as arestas: isso é Euler).",
         ("Num digrafo, segue o sentido das setas. Um vértice com deg⁻ = 1 (ou deg⁺ = 1) obriga a usar esse arco." if orient else
          "Regra 1: vértice de grau 2 ⇒ as duas arestas entram no ciclo. Regra 2: um vértice com 2 arestas já escolhidas ⇒ apagam-se as outras."),
         dica, "Descreve a volta como sequência de vértices a começar e a acabar no mesmo, e confirma que tem os n vértices + o regresso."],
        exame, ["Circuito/ciclo hamiltoniano: passa por todos os vértices exatamente uma vez e volta ao vértice inicial."]))]
    lista = arcs_txt(A) if orient else ", ".join("{" + a + "," + b + "}" for a, b in A)
    return dict(id=f"t3-{idx}", grupo=N3, tipo="aberta", tema="Hamiltoniano", fonte=FONTE,
                enunciado=f"Considere {nome} com {'os arcos' if orient else 'as arestas'} {lista}:\n" + svg_multi(V, A, directed=orient, pos=pos), alineas=al)

# ================================================================ EX. 4 (árvore geradora mínima: Prim na matriz triangular, como na aula)
from grafos import prim
CIDADES = ["Braga", "Porto", "Guimarães", "Viana", "Barcelos", "Famalicão", "Fafe", "Vila Real"]

def tri_table(V, W, chosen):
    """matriz triangular inferior; valores escolhidos em caixa com a ordem."""
    def val(a, b):
        return W.get((a, b), W.get((b, a)))
    hdr = "".join(f"<th style='padding:4px 6px;border:1px solid var(--line)'>{c}</th>" for c in [""] + V[:-1])
    trs = []
    for i, a in enumerate(V):
        if i == 0: continue
        tds = [f"<td style='padding:4px 6px;border:1px solid var(--line);font-weight:700'>{a}</td>"]
        for j, b in enumerate(V[:-1]):
            if j >= i:
                tds.append("<td style='border:1px solid var(--line);background:var(--chip)'></td>"); continue
            x = val(a, b)
            k = chosen.get(frozenset((a, b)))
            if k:
                cell = f"<span style='border:2px solid #e5484d;border-radius:4px;padding:0 4px;font-weight:700'>{x}</span><sup style='color:#e5484d'>{k}</sup>"
            else:
                cell = "" if x is None else str(x)
            tds.append(f"<td style='padding:4px 6px;border:1px solid var(--line);text-align:center'>{cell}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    return f"<div style='overflow-x:auto'><table style='border-collapse:collapse;font-size:13px;margin:6px 0'><tr>{hdr}</tr>{''.join(trs)}</table></div>"

def dijkstra_aula(V, W, s, t, directed):
    """tabela como no caderno: colunas l(v), p, Γ(p), cálculos; valor escolhido em caixa."""
    nb = {v: [] for v in V}
    for (a, b), w in W.items():
        nb[a].append((b, w))
        if not directed: nb[b].append((a, w))
    for v in V: nb[v].sort(key=lambda x: V.index(x[0]))
    lab = {v: math.inf for v in V}; ant = {v: None for v in V}; lab[s] = 0
    perm = []; rows = []; contas = []
    box = lambda x: f"<span style='border:2px solid #e5484d;border-radius:4px;padding:0 4px;font-weight:700'>{x}</span>"
    while True:
        temp = [v for v in V if v not in perm and lab[v] < math.inf]
        p = min(temp, key=lambda v: (lab[v], V.index(v)))
        cells = []
        for v in V:
            if v in perm: cells.append("")
            elif v == p: cells.append(box(lab[v]))
            elif lab[v] < math.inf: cells.append(str(lab[v]))
            else: cells.append("")
        perm.append(p)
        gam = [y for y, _ in nb[p]]
        calc = []
        if p != t:
            for y, w in nb[p]:
                if y in perm: continue
                novo = lab[p] + w
                velho = "∞" if lab[y] == math.inf else lab[y]
                if novo < lab[y]:
                    calc.append(f"ℓ({y}) = min({velho}, {lab[p]}+{w}) = {novo}")
                    lab[y] = novo; ant[y] = p
                else:
                    calc.append(f"ℓ({y}) = min({velho}, {lab[p]}+{w}) = {velho}")
        rows.append(cells + [p, "<span style='white-space:nowrap'>{" + ",".join(gam) + "}</span>"])
        contas.append(f"p = {p}: " + ("; ".join(calc) if calc else ("é o destino, parar." if p == t else "nenhum sucessor por escolher.")))
        if p == t: break
    path = [t]
    while path[-1] != s: path.append(ant[path[-1]])
    path = path[::-1]
    return path, lab[t], table([f"ℓ({v})" for v in V] + ["p", "Γ(p)"], rows, first_bold=False) + "Cálculos de cada linha (escreve-os ao lado da tabela):\n" + "\n".join(contas) + "\n"

def dijkstra_parte(rnd):
    from scipy.spatial import Delaunay
    from grafos import connected
    while True:
        n = rnd.randint(6, 8)
        cells = rnd.sample([(c, r) for c in range(4) for r in range(3)], n)
        pts = [((c + .5 + rnd.uniform(-.22, .22)) / 4, (r + .5 + rnd.uniform(-.22, .22)) / 3) for c, r in cells]
        order = sorted(range(n), key=lambda k: (pts[k][0], pts[k][1])); pts = [pts[k] for k in order]
        V = [str(i) for i in range(1, n + 1)]
        E = set()
        for sx in Delaunay(pts).simplices:
            for x, y in itertools.combinations(sorted(sx), 2): E.add((x, y))
        E = sorted(E); rnd.shuffle(E); E = E[:rnd.randint(int(1.5 * n), int(1.9 * n))]
        W = {}
        for x, y in E:
            a, b = (V[x], V[y]) if pts[x][0] <= pts[y][0] else (V[y], V[x])
            W[(a, b)] = rnd.randint(3, 30)
        if len(set(W.values())) < len(W) * .7 or not connected(adj_from_edges(V, list(W))): continue
        r = dijkstra(V, W, V[0], V[-1], True)
        if r is None or len(r[1]) < 4: continue
        break
    pos = {V[k]: pts[k] for k in range(n)}
    path, cost, tab = dijkstra_aula(V, W, V[0], V[-1], True)
    assert cost == r[2]
    A = list(W)
    fig = svg_multi(V, A, directed=True, pos=pos, weights=[W[x] for x in A], w=360, h=270)
    res = R(f"O percurso mínimo de {V[0]} para {V[-1]}: a tabela com todas as iterações, o caminho e o custo.",
        [f"1ª linha: ℓ({V[0]}) = 0, os outros ∞ (em branco). p = {V[0]}. Escreve Γ(p) (os vértices para onde saem setas de p) e calcula ℓ(y) = min(ℓ(y), ℓ(p) + peso).",
         "Nova linha: copia as etiquetas dos vértices ainda não escolhidos; a MENOR fica em caixa e esse vértice é o novo p.",
         "Para cada y em Γ(p) ainda não escolhido: ℓ(y) = min(valor atual, ℓ(p) + peso do arco p→y). Escreve a conta ao lado e guarda de onde veio (antecessor).",
         "Vértices já em caixa deixam de aparecer nas linhas seguintes.",
         f"Pára quando {V[-1]} ficar em caixa. O caminho lê-se de trás para a frente pelos antecessores; o percurso mínimo é o valor em caixa de {V[-1]}."],
        tab + f"Percurso mínimo = {cost}\nCaminho: μ = [{', '.join(path)}]",
        ["ℓ(v): menor custo conhecido de " + V[0] + " até v.", "p: vértice escolhido (etiqueta definitiva) nessa iteração.", "Γ(p): sucessores de p (para onde saem setas de p)."])
    return fig, res, V[0], V[-1]

def ex4(idx, dijkstra_html=None):
    rnd = random.Random(4000 + idx)
    from scipy.spatial import Delaunay
    from grafos import connected
    while True:
        n = rnd.randint(6, 8)
        cells = rnd.sample([(c, r) for c in range(4) for r in range(3)], n)
        pts = [((c + .5 + rnd.uniform(-.22, .22)) / 4, (r + .5 + rnd.uniform(-.22, .22)) / 3) for c, r in cells]
        V = rnd.sample(CIDADES, n) if rnd.random() < .35 else [str(i) for i in range(1, n + 1)]
        E = set()
        for sx in Delaunay(pts).simplices:
            for x, y in itertools.combinations(sorted(sx), 2): E.add((x, y))
        E = sorted(E); rnd.shuffle(E)
        E = E[:rnd.randint(int(1.5 * n), int(1.9 * n))]
        big = rnd.random() < .4
        W = {(V[x], V[y]): (rnd.randint(8, 99) if big else rnd.randint(1, 25)) for x, y in E}
        if len(set(W.values())) < len(W) * .75: continue
        if not connected(adj_from_edges(V, list(W))): continue
        steps, total = prim(V, W, V[0])
        if len(steps) == n - 1: break
    chosen = {frozenset((a, b)): k for k, (a, b, w) in enumerate(steps, 1)}
    pos = {V[k]: pts[k] for k in range(n)}
    A = list(W); ws = [W[x] for x in A]
    arv = []
    for k, (a, b, w) in enumerate(steps, 1):
        dentro = [V[0]] + [y for _, y, _ in steps[:k - 1]]
        arv.append(f"Passo {k}: árvore {{{', '.join(dentro)}}}. Nas colunas e linhas destes vértices, o menor valor que liga a um vértice ainda fora é {w} ({a}–{b}) ⇒ entra {b}.")
    hl = [(a, b) for a, b, _ in steps] + [(b, a) for a, b, _ in steps]
    soma = " + ".join(str(w) for _, _, w in steps)
    al = [dict(enunciado="Utilize o algoritmo de Prim, a partir da matriz, para determinar a árvore geradora mínima. Represente-a e indique a extensão mínima.", cotacao=25, resolucao=R(
        "As ligações que unem todos os vértices com a menor soma (árvore geradora mínima), feitas na matriz, o desenho e a soma.",
        [f"Começa no vértice {V[0]}: marca a sua linha/coluna (risco vertical, como na aula).",
         "Procura, nos valores que ligam os vértices já marcados a vértices AINDA NÃO marcados, o menor. Põe-no numa caixa (escreve a ordem ao lado).",
         "O vértice novo passa a estar marcado: risca também a coluna/linha dele. Os valores entre dois vértices já marcados deixam de contar (formariam ciclo).",
         f"Repete até teres n − 1 = {n - 1} caixas (todos os vértices ligados).",
         "Desenha só as ligações das caixas e soma os valores: é a extensão mínima."] + arv,
        "Matriz (os valores em caixa são as ligações escolhidas, pela ordem indicada):\n" + tri_table(V, W, chosen) +
        svg_multi(V, A, directed=False, pos=pos, weights=ws, w=360, h=270, hl=hl) +
        f"Árvore geradora mínima: {', '.join(f'{a}–{b}' for a, b, _ in steps)} ({n - 1} arestas para {n} vértices).\nExtensão mínima: {soma} = {total}.",
        ["Árvore: grafo conexo sem ciclos, com |E| = |V| − 1.", "Árvore geradora mínima: árvore com todos os vértices e com a menor soma de custos (extensão mínima)."]))]
    fig, resd, s0, t0 = dijkstra_parte(rnd)
    al.append(dict(enunciado=f"Considere agora a rede orientada da figura. Utilize o algoritmo de Dijkstra para determinar o percurso mínimo entre {s0} e {t0}, apresentando a tabela com todas as iterações e o caminho.\n" + fig,
                   cotacao=25, resolucao=resd))
    return dict(id=f"t4-{idx}", grupo=N4, tipo="aberta", tema="Prim na matriz e Dijkstra", fonte=FONTE,
                enunciado="Considere a rede com a seguinte matriz de custos (em branco: não há ligação):\n" + tri_table(V, W, {}),
                alineas=al)

def gerar(dijkstra_html, n=25):
    out = []
    for i in range(n):
        out += [ex1(i), ex2(i), ex3(i), ex4(i, dijkstra_html)]
    return out
