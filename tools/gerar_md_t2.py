"""Gera src/estudo/bancos/md-t2.json (MD, 2º teste, Teoria de Grafos).
Formato inspirado no teste do prof. Ricardo Gonçalves (2025/26):
  G1 grafo não orientado (8 val.), G2 digrafo (4,5), G3 planaridade (3,5), G4 redes (4).
Correr:  python3 tools/gerar_md_t2.py
"""
import json, math, os, random, itertools, sys
sys.path.insert(0, os.path.dirname(__file__))
from grafos import *
from scipy.spatial import Delaunay

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "estudo", "bancos", "md-t2.json")
random.seed(2026)

G1, G2, G3, G4, MC = "Grupo 1 · Grafo", "Grupo 2 · Digrafo", "Grupo 3 · Planaridade", "Grupo 4 · Redes", "Conceitos"

def S(xs, V):
    return fmt_set(xs, V)

def edges_txt(E):
    return ", ".join("\\{" + f"{a},{b}" + "\\}" for a, b in E)

def seq(p):
    return "[" + ", ".join(map(str, p)) + "]"

def jitter_grid(n, cols, rows, jit=0.28):
    cells = random.sample([(c, r) for c in range(cols) for r in range(rows)], n)
    pts = []
    for c, r in cells:
        x = (c + 0.5 + random.uniform(-jit, jit)) / cols
        y = (r + 0.5 + random.uniform(-jit, jit)) / rows
        pts.append((x, y))
    return pts

def labels(n, kind):
    if kind == "num":
        return [str(i) for i in range(1, n + 1)]
    if kind == "low":
        return list("abcdefghijk")[:n]
    return list("ABCDEFGHIJKLMN")[:n]

# ============================================================ GRUPO 1
def planar_graph(n):
    for _ in range(200):
        pts = jitter_grid(n, 4, 3 if n <= 10 else 4)
        tri = Delaunay(pts)
        E = set()
        for s in tri.simplices:
            for a, b in itertools.combinations(sorted(s), 2):
                E.add((a, b))
        # retirar arestas muito compridas/finas e algumas ao acaso
        E = sorted(E, key=lambda e: -math.dist(pts[e[0]], pts[e[1]]))
        target = random.randint(int(1.35 * n), int(1.75 * n))
        Es = set(E)
        for e in E:
            if len(Es) <= target:
                break
            if random.random() < 0.75:
                Es.discard(e)
                adj = {i: set() for i in range(n)}
                for a, b in Es:
                    adj[a].add(b); adj[b].add(a)
                if not connected(adj) or min(len(adj[i]) for i in adj) < 2:
                    Es.add(e)
        adj = {i: set() for i in range(n)}
        for a, b in Es:
            adj[a].add(b); adj[b].add(a)
        if connected(adj) and len(Es) >= n + 2:
            return pts, sorted(Es)
    raise RuntimeError

def ex_grupo1(idx):
    n = random.randint(8, 11)
    pts, Ei = planar_graph(n)
    V = labels(n, random.choice(["up", "num"]))
    pos = {V[i]: pts[i] for i in range(n)}
    E = [norm_edge(V[a], V[b], V) for a, b in Ei]
    adj = adj_from_edges(V, E)
    m = len(E)
    deg = {v: len(adj[v]) for v in V}
    nome = "G"
    fig = svg(V, pos, E, h=270)
    al = []

    # 1.1 Euler
    faces, ext = faces_from_drawing(pos, adj)
    f = len(faces)
    linhas = []
    ordem = [i for i in range(len(faces)) if i != ext] + [ext]
    for k, i in enumerate(ordem, 1):
        fc = faces[i]
        nomef = f"f_{{{k}}}" + (" \\text{ (exterior)}" if i == ext else "")
        linhas.append(f"${nomef}$: fronteira {seq(fc)} → deg = {len(fc)}")
    soma = sum(len(fc) for fc in faces)
    al.append(dict(
        enunciado="Ilustre a fórmula de Euler para grafos planares.",
        cotacao=15,
        resolucao=(f"O desenho não tem arestas a cruzar, logo {nome} é planar, e é conexo.\n"
                   f"n = |V| = {n}, m = |E| = {m}, faces f = {f} (incluindo a exterior):\n" + "\n".join(linhas) +
                   f"\n\nFórmula de Euler: $n - m + f = {n} - {m} + {f} = {n - m + f}$ ✓\n"
                   f"Verificação extra: $\\sum \\deg(f_i) = {soma} = 2m = {2 * m}$ ✓")))

    # 1.2 variantes
    var = random.choice(["sub", "gamma", "parcial"])
    if var == "sub":
        for _ in range(50):
            Vp = sorted(random.sample(V, random.randint(4, 6)), key=V.index)
            if sum(1 for a, b in E if a in Vp and b in Vp) >= len(Vp) - 1:
                break
        Ep = [(a, b) for a, b in E if a in Vp and b in Vp]
        adjp = adj_from_edges(Vp, Ep)
        al.append(dict(
            enunciado=f"Represente o subgrafo $G_{{V'}}$ gerado por $V' = {S(Vp, V)}$ e indique o grau de cada um dos seus vértices. É conexo?",
            cotacao=10,
            resolucao=(f"O subgrafo gerado por V' tem os vértices de V' e TODAS as arestas de G com ambas as extremidades em V'.\n"
                       f"$E' = {{{edges_txt(Ep)}}}$\n" +
                       svg(Vp, {v: pos[v] for v in Vp}, Ep, w=260, h=200) +
                       "Graus: " + ", ".join(f"deg({v}) = {len(adjp[v])}" for v in Vp) +
                       f"\n{'É conexo: existe cadeia entre quaisquer dois vértices.' if connected(adjp) else 'Não é conexo: há vértices sem cadeia entre si.'}")))
    elif var == "gamma":
        a, b = random.sample(V, 2)
        al.append(dict(
            enunciado=f"Determine $\\deg({a})$, $\\Gamma({a})$, $\\deg({b})$ e $\\Gamma({b})$. Verifique que $\\sum \\deg(v) = 2|E|$.",
            cotacao=10,
            resolucao=(f"$\\Gamma(v)$ é o conjunto dos vizinhos de v.\n"
                       f"$\\deg({a}) = {deg[a]}$, $\\Gamma({a}) = {S(adj[a], V)}$\n"
                       f"$\\deg({b}) = {deg[b]}$, $\\Gamma({b}) = {S(adj[b], V)}$\n"
                       "Graus: " + ", ".join(f"{v}:{deg[v]}" for v in V) +
                       f"\n$\\sum \\deg(v) = {sum(deg.values())} = 2 \\times {m}$ ✓")))
    else:
        Ep = sorted(random.sample(E, random.randint(3, 5)), key=E.index)
        adjp = adj_from_edges(V, Ep)
        iso = [v for v in V if not adjp[v]]
        al.append(dict(
            enunciado=f"Represente o grafo parcial de G gerado por $E' = {{{edges_txt(Ep)}}}$.",
            cotacao=10,
            resolucao=(f"O grafo parcial G' = (V, E') mantém TODOS os vértices de G e só as arestas de E'.\n" +
                       svg(V, pos, Ep, w=260, h=200) +
                       f"Vértices isolados (grau 0): {S(iso, V) if iso else 'nenhum'}.")))

    # 1.3 completo + bipartido
    ok, info = bipartite(adj, V)
    kn = n * (n - 1) // 2
    nao_adj = next((a, b) for a, b in itertools.combinations(V, 2) if b not in adj[a])
    if ok:
        bip = (f"É bipartido: partição $V_1 = {S(info[0], V)}$, $V_2 = {S(info[1], V)}$; "
               "todas as arestas ligam um vértice de $V_1$ a um de $V_2$ (não há arestas dentro do mesmo conjunto).")
    else:
        cyc = info
        bip = (f"Não é bipartido: tem o ciclo de comprimento ímpar {seq(cyc)} (comprimento {len(cyc) - 1}). "
               "Num grafo bipartido todos os ciclos têm comprimento par, porque se alterna sempre entre os dois conjuntos.")
    al.append(dict(
        enunciado="Justifique que o grafo não é completo e investigue, justificando, se o grafo é bipartido.",
        cotacao=15,
        resolucao=(f"Não é completo: {nome} tem {m} arestas e $K_{{{n}}}$ teria $\\frac{{{n}\\times{n - 1}}}{{2}} = {kn}$. "
                   f"Por exemplo, {nao_adj[0]} e {nao_adj[1]} não são adjacentes.\n{bip}")))

    # 1.4 Dirac / Ore
    ham = ham_cycle(adj, V)
    ham_txt = (f"Ainda assim, procurando diretamente, {nome} tem o ciclo hamiltoniano {seq(ham)}." if ham
               else f"De facto, {nome} não tem ciclo hamiltoniano (por exemplo pelas regras: os vértices de grau 2 obrigam a usar as duas arestas e forma-se um ciclo antes de visitar todos).")
    if random.random() < 0.5:
        lim = n / 2
        maus = [v for v in V if deg[v] < lim]
        cumpre = not maus
        res = (f"Teorema de Dirac: G simples, conexo, n ≥ 3 e $\\deg(v) \\ge n/2$ para todo o v ⇒ G tem ciclo hamiltoniano.\n"
               f"n = {n}, $n/2 = {lim:g}$. Grau mínimo = {min(deg.values())}.\n")
        if cumpre:
            res += f"Todos os vértices têm grau ≥ {lim:g}, logo pelo teorema de Dirac G é hamiltoniano. Exemplo: {seq(ham)}."
        else:
            res += (f"Não se verifica: por exemplo deg({maus[0]}) = {deg[maus[0]]} < {lim:g}. "
                    f"Como Dirac é uma condição SUFICIENTE (não necessária), não se pode concluir nada sobre ser hamiltoniano. " + ham_txt)
        al.append(dict(enunciado="Ilustre para o grafo a aplicação do teorema de Dirac.", cotacao=15, resolucao=res))
    else:
        pares = [(a, b) for a, b in itertools.combinations(V, 2) if b not in adj[a]]
        maus = [(a, b) for a, b in pares if deg[a] + deg[b] < n]
        res = (f"Teorema de Ore: G simples, conexo, n ≥ 3 e $\\deg(u) + \\deg(v) \\ge n$ para quaisquer u, v NÃO adjacentes ⇒ G tem ciclo hamiltoniano.\n"
               f"n = {n}. ")
        if not maus:
            res += f"Todos os pares não adjacentes somam ≥ {n}, logo G é hamiltoniano. Exemplo: {seq(ham)}."
        else:
            a, b = maus[0]
            res += (f"Não se verifica: {a} e {b} não são adjacentes e $\\deg({a}) + \\deg({b}) = {deg[a]} + {deg[b]} = {deg[a] + deg[b]} < {n}$. "
                    "Ore é condição suficiente, por isso não permite concluir. " + ham_txt)
        enun = ("Mostre que G não cumpre o teorema de Ore, mas tem um ciclo hamiltoniano." if (maus and ham)
                else "Investigue se G verifica o teorema de Ore. O que pode concluir?")
        al.append(dict(enunciado=enun, cotacao=15, resolucao=res))

    # 1.5 sequência mu
    path = ham_cycle(adj, V, need_cycle=False)
    tipos = []
    if ham: tipos.append("ciclo")
    if path and path[0] not in adj[path[-1]]: tipos.append("cadeia_h")
    tipos += ["nao_elem", "invalida"]
    t = random.choice(tipos)
    if t == "ciclo":
        mu = ham
        concl = (f"μ é uma cadeia fechada que não repete arestas nem vértices (exceto o inicial = final) e passa por todos os {n} vértices: "
                 f"é um CICLO HAMILTONIANO, logo {nome} é um grafo hamiltoniano.")
    elif t == "cadeia_h":
        mu = path
        concl = (f"Todas as ligações consecutivas são arestas de {nome}, nenhum vértice se repete e passa pelos {n} vértices: é uma CADEIA HAMILTONIANA. "
                 f"Não é um ciclo hamiltoniano porque {mu[-1]} e {mu[0]} não são adjacentes (não dá para fechar).")
    elif t == "nao_elem":
        # passeio que repete um vértice sem repetir arestas
        for _ in range(200):
            s = random.choice(V); w = [s]; used = set()
            for _ in range(random.randint(5, 8)):
                cand = [y for y in adj[w[-1]] if norm_edge(w[-1], y, V) not in used]
                if not cand: break
                y = random.choice(cand); used.add(norm_edge(w[-1], y, V)); w.append(y)
            if len(set(w)) < len(w) and len(w) >= 5 and w[0] != w[-1]:
                break
        mu = w
        rep = next(v for v in mu if mu.count(v) > 1)
        concl = (f"Todas as ligações consecutivas são arestas e nenhuma aresta se repete: é uma cadeia SIMPLES de comprimento {len(mu) - 1}. "
                 f"Não é elementar porque passa duas vezes pelo vértice {rep}.")
    else:
        for _ in range(200):
            mu = random.sample(V, random.randint(5, 7))
            bad = [(a, b) for a, b in zip(mu, mu[1:]) if b not in adj[a]]
            if len(bad) == 1:
                break
        a, b = bad[0]
        concl = f"μ NÃO é uma cadeia de {nome}: {a} e {b} são consecutivos em μ mas $\\{{{a},{b}\\}} \\notin E$."
    al.append(dict(enunciado=f"Seja $\\mu = {seq(mu)}$. O que pode concluir deste resultado à luz da Teoria de Grafos?",
                   cotacao=15, resolucao=concl))

    # 1.6 Euler / eulerização
    odd = odd_vertices(adj, V)
    if len(odd) >= 4:
        _, pares, dup = eulerize(adj, V)
        res = (f"Vértices de grau ímpar: " + ", ".join(f"{v}({deg[v]})" for v in odd) + f" → {len(odd)} vértices.\n"
               "Para ser euleriano todos têm de ficar com grau par. Emparelham-se os vértices ímpares pelo caminho mais curto e duplicam-se as arestas desse caminho:\n" +
               "\n".join(f"{a} ↔ {b}" for a, b in pares) +
               f"\nArestas a duplicar ({len(dup)}): {edges_txt(dup)}\n"
               f"Mínimo: {len(dup)} arestas duplicadas.")
        al.append(dict(enunciado="A eulerização de um grafo consiste em transformar um grafo que não é euleriano num grafo euleriano, duplicando arestas já existentes. Indique o menor número de arestas necessárias e quais.",
                       cotacao=10, resolucao=res))
    else:
        if not odd:
            cyc = hierholzer(E, V[0])
            res = f"Todos os vértices têm grau par e G é conexo ⇒ (Euler) tem ciclo euleriano:\n{seq(cyc)}"
        else:
            ch = hierholzer(E, odd[0])
            res = (f"G é conexo e tem exatamente 2 vértices de grau ímpar ({odd[0]} e {odd[1]}) ⇒ tem cadeia euleriana (mas não ciclo), "
                   f"que começa num e acaba no outro:\n{seq(ch)}")
        al.append(dict(enunciado="Verifique se o grafo admite uma cadeia ou um ciclo euleriano. Em caso afirmativo, indique-o.",
                       cotacao=10, resolucao=res))

    return dict(id=f"g1-{idx}", grupo=G1, tipo="aberta", tema="Grafo não orientado",
                fonte="Gerado no formato do teste do Ricardo",
                enunciado=f"Considere o seguinte grafo {nome}:\n{fig}", alineas=al)

# ============================================================ GRUPO 2
def ex_grupo2(idx):
    for _ in range(500):
        n = random.randint(5, 7)
        V = labels(n, "up")
        pts = jitter_grid(n, 3, 3, 0.2)
        pos = {V[i]: pts[i] for i in range(n)}
        m = random.randint(n + 2, n + 4)
        # passeio aleatório sem repetir arcos, sem antiparalelos
        cur = random.choice(V); A = []
        for _ in range(m * 6):
            if len(A) == m: break
            cand = [y for y in V if y != cur and (cur, y) not in A and (y, cur) not in A]
            if not cand: break
            y = random.choice(cand); A.append((cur, y)); cur = y
        if len(A) < m: continue
        if set(V) != {x for a in A for x in a}: continue
        if random.random() < 0.25:  # às vezes estraga o euleriano
            a, b = random.sample(V, 2)
            if (a, b) not in A and (b, a) not in A:
                A.append((a, b))
        # evitar arcos a passar por cima de vértices
        bad = False
        for a, b in A:
            for v in V:
                if v in (a, b): continue
                (x1, y1), (x2, y2), (px, py) = pos[a], pos[b], pos[v]
                L = math.dist(pos[a], pos[b]); t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / L ** 2
                if 0 < t < 1 and math.dist((px, py), (x1 + t * (x2 - x1), y1 + t * (y2 - y1))) < 0.11:
                    bad = True
        if not bad: break
    out, inn = digraph_maps(V, A)
    fig = svg(V, pos, A, directed=True, w=280, h=230)
    al = []
    comps = scc(V, A)
    fecho = {v: reach(out, v) for v in V}; inv = {v: reach(inn, v) for v in V}
    v0 = V[0]
    linhas = "\n".join(f"$\\Gamma_{{{c[0]}}} \\cap \\Gamma^{{-1}}_{{{c[0]}}} = {S(c, V)}$" for c in comps)
    if len(comps) == 1:
        r = (f"$\\Gamma_{{{v0}}} = {S(fecho[v0], V)}$ e $\\Gamma^{{-1}}_{{{v0}}} = {S(inv[v0], V)}$.\n"
             f"A interseção é V inteiro, logo existe caminho entre quaisquer dois vértices: o digrafo É fortemente conexo.")
    else:
        r = ("Não é fortemente conexo. As componentes fortemente conexas obtêm-se com $\\Gamma_v \\cap \\Gamma^{-1}_v$:\n" + linhas +
             f"\nComponentes: " + ", ".join(S(c, V) for c in comps) + ".")
    al.append(dict(enunciado="Investigue se o digrafo é fortemente conexo. Caso não seja, indique todas as componentes fortemente conexas.", cotacao=10, resolucao=r))

    nec = non_elementary_circuit(V, A)
    if nec:
        rep = next(v for v in nec[1:-1] if nec[1:-1].count(v) > 1 or v == nec[0])
        al.append(dict(enunciado="Apresente um circuito não elementar.", cotacao=10,
                       resolucao=f"{seq(nec)}\nÉ fechado e não repete arcos (circuito), mas passa duas vezes por {rep}, por isso não é elementar."))
    else:
        ec = elementary_circuit(V, A)
        if ec:
            al.append(dict(enunciado="Apresente um circuito elementar e indique o seu comprimento.", cotacao=10,
                           resolucao=f"{seq(ec)}, comprimento {len(ec) - 1}. Não repete vértices (exceto o inicial = final).\nNota: neste digrafo não existe circuito não elementar."))
        else:
            al.append(dict(enunciado="O digrafo tem algum circuito? Justifique.", cotacao=10,
                           resolucao="Não: a partir de nenhum vértice é possível voltar a ele próprio ($v \\notin$ sucessores alcançáveis sem ser pelo próprio). É um digrafo acíclico."))

    dp = {v: len(out[v]) for v in V}; dm = {v: len(inn[v]) for v in V}
    tab = table(["v", "deg⁺", "deg⁻"], [[v, dp[v], dm[v]] for v in V])
    ini = [v for v in V if dp[v] == dm[v] + 1]; fim = [v for v in V if dm[v] == dp[v] + 1]
    outros = [v for v in V if abs(dp[v] - dm[v]) > 0 and v not in ini + fim]
    und = adj_from_edges(V, A)
    if not connected(und):
        r = "O digrafo não é conexo, logo não tem caminho nem circuito euleriano."; en = "Verifique se o digrafo admite caminho ou circuito euleriano."
    elif all(dp[v] == dm[v] for v in V):
        cyc = hierholzer(A, A[0][0], directed=True)
        r = tab + f"Conexo e $\\deg^+(v) = \\deg^-(v)$ em todos os vértices ⇒ tem CIRCUITO euleriano:\n{seq(cyc)}"; en = "Justifique que o digrafo tem um circuito euleriano e indique-o."
    elif len(ini) == 1 and len(fim) == 1 and not outros:
        p = hierholzer(A, ini[0], directed=True)
        r = (tab + f"Conexo, $\\deg^+({ini[0]}) = \\deg^-({ini[0]}) + 1$, $\\deg^-({fim[0]}) = \\deg^+({fim[0]}) + 1$ e nos restantes $\\deg^+ = \\deg^-$ "
             f"⇒ tem CAMINHO euleriano de {ini[0]} para {fim[0]}:\n{seq(p)}")
        en = "Justifique que o digrafo tem um caminho euleriano e indique-o."
    else:
        r = tab + "Não cumpre as condições: há vértices com diferença entre $\\deg^+$ e $\\deg^-$ que não permitem caminho (nem circuito) euleriano."
        en = "Verifique se o digrafo admite caminho ou circuito euleriano."
    al.append(dict(enunciado=en, cotacao=10, resolucao=r))

    v = random.choice(V)
    if random.random() < 0.7:
        al.append(dict(enunciado=f"Determine $\\Gamma_{{{v}}}$ e $\\Gamma^{{-1}}_{{{v}}}$.", cotacao=15,
                       resolucao=(f"Fecho transitivo direto (vértices atingíveis a partir de {v}, incluindo {v}): $\\Gamma_{{{v}}} = {S(fecho[v], V)}$\n"
                                  f"Fecho transitivo inverso (vértices a partir dos quais se chega a {v}): $\\Gamma^{{-1}}_{{{v}}} = {S(inv[v], V)}$")))
    else:
        bm = table([""] + V, [[a] + [1 if b in out[a] else 0 for b in V] for a in V])
        al.append(dict(enunciado=f"Construa a matriz booleana do digrafo e, a partir dela, indique $\\deg^+({v})$, $\\deg^-({v})$, $\\Gamma^+({v})$ e $\\Gamma^-({v})$.", cotacao=15,
                       resolucao=(bm + f"$\\deg^+({v})$ = soma da linha {v} = {dp[v]}; $\\deg^-({v})$ = soma da coluna {v} = {dm[v]}.\n"
                                  f"Sucessores $\\Gamma^+({v}) = {S(out[v], V) if out[v] else '\\emptyset'}$; antecessores $\\Gamma^-({v}) = {S(inn[v], V) if inn[v] else '\\emptyset'}$.")))
    return dict(id=f"g2-{idx}", grupo=G2, tipo="aberta", tema="Digrafo", fonte="Gerado no formato do teste do Ricardo",
                enunciado=f"Considere o digrafo D:\n{fig}", alineas=al)

# ============================================================ GRUPO 3
def metodo_ciclico(V, E, C):
    n = len(C) - 1; cyc = C[:-1]
    m = len(E)
    ciclo = {norm_edge(cyc[i], cyc[(i + 1) % n], V) for i in range(n)}
    chords = [e for e in E if e not in ciclo]
    conf = chord_conflicts(cyc, chords)
    ok, info = split_chords(chords, conf)
    incomp = [f"{edges_txt([a])} × {edges_txt([b])}" for a, b in itertools.combinations(chords, 2) if b in conf[a]]
    txt = (f"1) Ciclo hamiltoniano C = {seq(C)} (fica desenhado como um polígono).\n"
           f"2) Arestas que não estão em C: L = {{{edges_txt(chords)}}}\n"
           f"3) Pares incompatíveis (as extremidades alternam ao longo de C, por isso cruzam-se se ficarem do mesmo lado):\n" +
           ("\n".join(incomp) if incomp else "nenhum") + "\n")
    if ok:
        A_, B_ = info
        txt += (f"Distribuição sem conflitos: A (dentro de C) = {{{edges_txt(A_)}}}, B (fora de C) = {{{edges_txt(B_)}}}. L fica vazio ⇒ o grafo É planar.\n"
                f"Representação planar (é este o desenho a apresentar quando pedem \"apresente uma representação planar\"):\n" + planar_svg(cyc, A_, B_) +
                f"Faces: $F = 2 - V + A = 2 - {n} + {m} = {2 - n + m}$ (confirma contando as regiões do desenho, incluindo a de fora).")
    else:
        oc = info
        txt += ("Distribuindo à vez (cada uma obriga a seguinte a ir para o outro lado): " +
                ", ".join(f"{edges_txt([c])} → {'A' if i % 2 == 0 else 'B'}" for i, c in enumerate(oc)) +
                f".\nA última, {edges_txt([oc[-1]])}, teria de ficar em A, mas é incompatível com {edges_txt([oc[0]])}, que já está em A. "
                f"É um ciclo de {len(oc)} incompatibilidades (número ímpar), por isso é impossível pôr todas as arestas dentro ou fora sem cruzamentos. L ≠ ∅ ⇒ o grafo NÃO é planar.")
    return ok, txt

def ex_grupo3(idx):
    kind = random.choice(["k33", "k33", "k5", "planar"])
    for _ in range(500):
        if kind == "k33":
            n = random.choice([6, 6, 7]); idxs = list(range(n))
            P, Q = idxs[:3], idxs[3:6]
            E = {(a, b) for a in P for b in Q}
            for _ in range(random.randint(0, 2)):
                a, b = random.sample(idxs[:6], 2); E.add(tuple(sorted((a, b))))
            if n == 7:
                for b in random.sample(range(6), random.randint(2, 3)): E.add((b, 6))
        elif kind == "k5":
            n = random.choice([5, 6]); E = {(a, b) for a, b in itertools.combinations(range(5), 2)}
            if n == 6:
                for b in random.sample(range(5), random.randint(2, 3)): E.add((b, 5))
        else:
            n = random.choice([6, 7]); E = {(i, (i + 1) % n) for i in range(n)}
            E = {tuple(sorted(e)) for e in E}
            ins, outs = [], []
            for a, b in random.sample(list(itertools.combinations(range(n), 2)), 12):
                if (a, b) in E: continue
                for grp in (ins, outs):
                    cyc = list(range(n))
                    if all(not chord_conflicts(cyc, [(a, b), c])[(a, b)] for c in grp):
                        grp.append((a, b)); E.add((a, b)); break
                if len(ins) + len(outs) >= random.randint(3, 5): break
        E = sorted({tuple(sorted(e)) for e in E})
        V = labels(n, random.choice(["num", "low"]))
        perm = random.sample(range(n), n)
        Eg = [norm_edge(V[perm[a]], V[perm[b]], V) for a, b in E]
        adj = adj_from_edges(V, Eg)
        C = ham_cycle(adj, V)
        if C: break
    ang = {v: 2 * math.pi * i / n - math.pi / 2 for i, v in enumerate(V)}
    pos = {v: (0.5 + 0.48 * math.cos(ang[v]), 0.5 + 0.48 * math.sin(ang[v])) for v in V}
    m = len(Eg)
    fig = svg(V, pos, Eg, w=240, h=220)
    tri = has_triangle(adj)
    ok, metodo = metodo_ciclico(V, Eg, C)
    assert ok == (kind == "planar"), (kind, Eg)
    lim3 = 3 * n - 6; lim2 = 2 * n - 4
    if kind == "planar":
        r1 = (f"n = {n}, m = {m}. Corolário: se G fosse não planar por contagem teria $m > 3n - 6 = {lim3}$. Como {m} ≤ {lim3}, o corolário NÃO permite concluir nada; "
              "é preciso outro método (método cíclico ou encontrar uma representação plana).")
        e1 = "Verifique se o corolário da fórmula de Euler ($m \\le 3n - 6$) permite concluir sobre a planaridade do grafo."
        e2 = "Aplique o método cíclico para investigar se o grafo é planar. Se for, indique quantas faces tem uma representação planar."
    else:
        e1 = "Justifique que o grafo não é planar."
        e2 = "Aplique o método cíclico para comprovar que o grafo não é planar."
        if m > lim3:
            r1 = f"G é simples e conexo com n = {n} e m = {m}. Como $m = {m} > 3n - 6 = {lim3}$, pelo corolário da fórmula de Euler G não é planar."
        elif not tri and m > lim2:
            r1 = f"G não tem triângulos, n = {n}, m = {m}. Como $m = {m} > 2n - 4 = {lim2}$, pelo lema G não é planar."
        else:
            k33 = find_k33(adj, V); k5 = find_k5(adj, V)
            if k33:
                P, Q = k33
                r1 = (f"Aqui $m = {m} \\le 3n - 6 = {lim3}$, por isso o corolário não chega (e G tem triângulos, o lema de $2n-4$ não se aplica).\n"
                      f"Mas G contém $K_{{3,3}}$: $V_1 = {S(P, V)}$, $V_2 = {S(Q, V)}$, todas as 9 ligações entre os dois conjuntos existem. "
                      f"$K_{{3,3}}$ não tem triângulos e tem $9 > 2\\cdot 6 - 4 = 8$ arestas, logo não é planar; um grafo que o contém também não é.")
            else:
                r1 = (f"$m = {m} \\le {lim3}$, mas G contém $K_5$ nos vértices {S(k5, V)}: $K_5$ tem 10 arestas > $3\\cdot 5 - 6 = 9$, logo não é planar; G contém-no, logo também não é.")
    al = [dict(enunciado=e1, cotacao=15, resolucao=r1), dict(enunciado=e2, cotacao=20, resolucao=metodo)]
    return dict(id=f"g3-{idx}", grupo=G3, tipo="aberta", tema="Planaridade", fonte="Gerado no formato do teste do Ricardo",
                enunciado=f"Considere o seguinte grafo:\n{fig}", alineas=al)

# ============================================================ GRUPO 4
LUGARES = [["Braga", "Guimarães", "Barcelos", "Famalicão", "Fafe", "Vizela", "Póvoa", "Esposende"],
           ["Aveiro", "Coimbra", "Porto", "Viseu", "Leiria", "Guarda", "Lamego", "Régua"],
           ["Sede", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]]

def prim_html(V, W, start):
    steps, total = prim(V, W, start)
    rows = [[i + 1, f"{{{', '.join([start] + [b for _, b, _ in steps[:i]])}}}", f"{{{a},{b}}}", w] for i, (a, b, w) in enumerate(steps)]
    return steps, total, table(["Passo", "Árvore antes", "Ligação escolhida (mínima)", "Peso"], rows)

def kruskal_html(V, W):
    log, tree, total = kruskal(V, W)
    rows = [[f"{{{a},{b}}}", w, "✓ aceite" if ok else "✗ forma ciclo"] for a, b, w, ok in log]
    return tree, total, table(["Aresta (ordem crescente)", "Peso", "Decisão"], rows)

def dijkstra_html(V, W, s, t, directed):
    rows, path, cost = dijkstra(V, W, s, t, directed)
    hdr = ["Iteração (p)"] + V
    trs = []
    fixed = set()
    for p, lab, perm in rows:
        r = [p]
        for v in V:
            if v in fixed:
                r.append("—")
            else:
                d, pr = lab[v]
                cell = "∞" if d == math.inf else (f"{d} ({pr})" if pr else f"{d}")
                if v == p: cell = f"<b>{cell} ✓</b>"
                r.append(cell)
        fixed.add(p)
        trs.append(r)
    return path, cost, table(hdr, trs)

def ex_grupo4(idx, directed=None):
    directed = random.random() < 0.3 if directed is None else directed
    for _ in range(300):
        n = random.randint(6, 8)
        nomes = random.choice(LUGARES)
        V = nomes[:n] if nomes[0] == "Sede" else random.sample(nomes, n)
        if nomes[0] != "Sede" and random.random() < 0.4: V = labels(n, "up")
        pts = jitter_grid(n, 3, 3, 0.25)
        tri = Delaunay(pts); E = set()
        for sx in tri.simplices:
            for a, b in itertools.combinations(sorted(sx), 2): E.add((a, b))
        E = list(E); random.shuffle(E)
        E = E[:random.randint(int(1.4 * n), int(1.8 * n))]
        adj = {i: set() for i in range(n)}
        for a, b in E: adj[a].add(b); adj[b].add(a)
        if not connected(adj): continue
        big = random.random() < 0.5
        W = {}
        for a, b in E:
            w = random.randint(20, 160) if big else random.randint(2, 25)
            if directed and random.random() < 0.5: a, b = b, a
            W[(V[a], V[b])] = w
        if len(set(W.values())) < len(W) * 0.7: continue
        s, t = random.sample(V, 2)
        if dijkstra(V, W, s, t, directed) is None: continue
        d, _ = bfs_dist({v: {y for (a, y) in W if a == v} | ({a for (a, y) in W if y == v} if not directed else set()) for v in V}, s)
        if d.get(t, 0) >= 2: break
    pos = {V[i]: pts[i] for i in range(n)}
    Wu = {}
    for (a, b), w in W.items():
        k = norm_edge(a, b, V)
        Wu[k] = min(w, Wu.get(k, w))
    mat = matrix_table(V, W, directed)
    al = []
    unidade = "km" if any(len(v) > 3 for v in V) else ""
    if directed and random.random() < 0.5:
        out, inn = digraph_maps(V, list(W))
        v = random.choice(V)
        al.append(dict(enunciado=f"Determine $\\Gamma^{{-1}}_{{{v}}}$ (fecho transitivo inverso de {v}).", cotacao=15,
                       resolucao=f"Vértices a partir dos quais se consegue chegar a {v} seguindo os arcos (linha → coluna):\n$\\Gamma^{{-1}}_{{{v}}} = {S(reach(inn, v), V)}$"))
    else:
        if random.random() < 0.6:
            start = V[0]
            steps, total, tab = prim_html(V, Wu, start)
            tree = [(a, b) for a, b, _ in steps]
            res = ("Algoritmo de Prim (a partir da matriz): começa-se num vértice e em cada passo junta-se a ligação de menor peso entre a árvore e um vértice fora dela.\n" +
                   (("Como a matriz não é simétrica, consideram-se as ligações sem orientação.\n") if directed else "") +
                   tab + svg(V, pos, list(Wu), weights=Wu, highlight=tree) + f"Valor da árvore geradora mínima: {total} {unidade}".strip())
            en = "Usando um algoritmo a partir da matriz, determine a árvore geradora mínima, indicando o valor obtido."
        else:
            tree, total, tab = kruskal_html(V, Wu)
            res = ("Algoritmo de Kruskal: ordenam-se as arestas por peso crescente e aceita-se cada uma desde que não forme ciclo, até ter n − 1 arestas.\n" +
                   (("Como a matriz não é simétrica, consideram-se as ligações sem orientação.\n") if directed else "") +
                   tab + svg(V, pos, list(Wu), weights=Wu, highlight=[(a, b) for a, b, _ in tree]) + f"Árvore com {n - 1} arestas. Valor total: {total} {unidade}".strip())
            en = "Usando o algoritmo de Kruskal, determine a árvore geradora mínima (indique a aresta escolhida em cada iteração) e o seu valor."
        al.append(dict(enunciado=en, cotacao=15, resolucao=res))
    path, cost, tab = dijkstra_html(V, W, s, t, directed)
    al.append(dict(enunciado=f"Usando o algoritmo de Dijkstra, determine o percurso mínimo entre {s} e {t} e o respetivo custo.", cotacao=25,
                   resolucao=("Etiquetas no formato custo (antecessor); ✓ = etiqueta passa a permanente.\n" + tab +
                              f"Percurso mínimo: {' → '.join(path)}, custo {cost} {unidade}".strip())))
    tipo = "rede orientada" if directed else "rede"
    return dict(id=f"g4-{idx}", grupo=G4, tipo="aberta", tema="Redes", fonte="Gerado no formato do teste do Ricardo",
                enunciado=f"Considere a {tipo} com a seguinte matriz de adjacência (os espaços em branco indicam que não há ligação{'; a linha é a origem e a coluna o destino' if directed else ''}):\n{mat}",
                alineas=al)

# ============================================================ TESTES REAIS
def reais():
    out = []
    # ---- Ricardo 2025/26 G1
    V = list("CDEFGHIJKLMNOPQ")
    E = [norm_edge(a, b, V) for a, b in ["CQ", "QP", "PD", "PO", "ON", "ND", "NG", "GI", "IM", "ML", "LG", "GK", "IJ", "JK", "KH", "HF", "FD", "FE", "EC", "CD"]]
    adj = adj_from_edges(V, E); deg = {v: len(adj[v]) for v in V}
    ok, (P1, P2) = bipartite(adj, V)
    assert ok
    odd, pares, dup = eulerize(adj, V)
    mu = list("DFECQPONGLMIJKH")
    assert all(b in adj[a] for a, b in zip(mu, mu[1:])) and len(set(mu)) == 15 and "D" not in adj["H"]
    def R(pede, termos, usar, passos, exame):
        t = "\n".join(f"• {x}" for x in termos)
        p = "\n".join(f"{i}) {x}" for i, x in enumerate(passos, 1))
        return (f"<b>📌 O que pedem</b>\n{pede}\n\n<b>📖 Termos</b>\n{t}\n\n<b>🧰 O que usar e porquê</b>\n{usar}\n\n<b>🪜 Passo a passo</b>\n{p}\n\n"
                f"<b>✍️ Resposta como no exame</b>\n<div style='border-left:3px solid #1f9d55;padding:6px 10px;margin-top:4px;background:var(--chip);border-radius:8px'>{exame}</div>")
    out.append(dict(id="r-ric25-1", grupo=G1, tipo="aberta", tema="Grafo não orientado", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o seguinte grafo G1:", imagem="/estudo/img/md/ric25-g1.png", alineas=[
        dict(enunciado="Ilustre a fórmula de Euler para grafos planares.", cotacao=15, resolucao=R(
            "Mostrar, com os números deste grafo, que a fórmula de Euler V − A + F = 2 se verifica.",
            ["Vértice: cada ponto (C, D, …, Q). Aresta: cada linha entre dois pontos.",
             "Face: cada região do papel fechada por arestas, como uma sala. A região de fora também conta (face exterior).",
             "Grau de uma face: número de arestas à volta dela.",
             "Planar: dá para desenhar sem arestas a cruzar. Conexo: está tudo numa só peça (de qualquer vértice chega-se a qualquer outro)."],
            "A fórmula de Euler, V − A + F = 2 (o professor escreve n − m + f = 2). Só vale para grafos PLANARES e CONEXOS, por isso a primeira coisa a escrever é que G1 cumpre essas duas condições.",
            ["Planar: olha para o desenho. Nenhuma aresta cruza outra, logo é planar.",
             "Conexo: escreve uma cadeia que passe por todos os vértices. A sequência da alínea 1.5 serve: [D,F,E,C,Q,P,O,N,G,L,M,I,J,K,H].",
             "Conta os vértices: C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, logo V = 15.",
             "Conta as arestas: soma os graus e divide por 2. Graus: C3 D4 E2 F3 G4 H2 I3 J2 K3 L2 M2 N3 O2 P3 Q2, soma 40, logo A = 40 / 2 = 20.",
             "Conta as faces: as 6 zonas cinzentas do desenho mais a de fora, logo F = 7. Escreve o grau de cada uma: [C,Q,P,D] 4, [P,O,N,D] 4, [C,D,F,E] 4, [D,N,G,K,H,F] 6, [G,I,J,K] 4, [G,L,M,I] 4, exterior 14.",
             "Substitui: 15 − 20 + 7 = 2.",
             "Confirma (opcional): a soma dos graus das faces tem de dar 2A. 4+4+4+6+4+4+14 = 40 = 2 × 20 ✓"],
            "G1 é planar, porque a representação dada não tem arestas a cruzar-se, e é conexo, porque a cadeia [D,F,E,C,Q,P,O,N,G,L,M,I,J,K,H] passa por todos os vértices. Logo aplica-se a fórmula de Euler V − A + F = 2.\n"
            "V = nº de vértices = 15; A = nº de arestas = 20; F = nº de faces = 7 (f1 = [C,Q,P,D], f2 = [P,O,N,D], f3 = [C,D,F,E], f4 = [D,N,G,K,H,F], f5 = [G,I,J,K], f6 = [G,L,M,I] e f7 a face exterior).\n"
            "V − A + F = 15 − 20 + 7 = 2, logo verifica-se a fórmula de Euler.\nConfirmação: Σ deg(fi) = 4+4+4+6+4+4+14 = 40 = 2A.")),
        dict(enunciado="Indique deg(F1), sendo F1 o subgrafo de G1 gerado pelo conjunto de vértices {F, D, N, G, K, H}.", cotacao=10, resolucao=R(
            "Construir o subgrafo formado por esses 6 vértices e dizer o seu grau.",
            ["Subgrafo gerado por um conjunto de vértices: ficas SÓ com esses vértices e com TODAS as arestas de G1 que ligam dois deles.",
             "Grau de um vértice: nº de arestas que tocam nele. Grau de uma face: nº de arestas à volta dela.",
             "Ciclo: percurso que volta ao início sem repetir arestas."],
            "A definição de subgrafo gerado. A pergunta é ambígua (\"deg\" de um subgrafo não existe), mas o F de F1 sugere uma face: estes 6 vértices são precisamente a fronteira da face grande da direita. Por isso respondes as duas coisas: os graus dos vértices e o grau da face.",
            ["Para cada par dos 6 vértices, vê no desenho se há aresta: F–D sim, D–N sim, N–G sim, G–K sim, K–H sim, H–F sim. Os outros pares (por exemplo D–G ou F–K) não têm aresta.",
             "Ficam 6 arestas que formam uma volta fechada: o ciclo [F, D, N, G, K, H, F].",
             "Cada vértice tem 2 arestas neste subgrafo, logo grau 2 (soma 12 = 2 × 6 arestas ✓).",
             "Essa volta é a fronteira da face f4, rodeada por 6 arestas: grau 6."],
            "O subgrafo F1 gerado por {F, D, N, G, K, H} tem as arestas {F,D}, {D,N}, {N,G}, {G,K}, {K,H} e {H,F}: é o ciclo [F, D, N, G, K, H, F], em que cada vértice tem grau 2.\n"
            "Este ciclo delimita uma face de G1 com 6 arestas na fronteira, logo deg(F1) = 6.")),
        dict(enunciado="Justifique que o grafo não é completo e investigue, justificando, se o grafo é bipartido.", cotacao=15, resolucao=R(
            "Duas coisas: (a) mostrar que G1 não é completo; (b) descobrir se é bipartido e justificar.",
            ["Completo (Kn): todos os vértices ligados a todos os outros.",
             "Adjacentes: dois vértices ligados diretamente por uma aresta.",
             "Bipartido: dá para dividir os vértices em dois grupos V1 e V2 de forma que TODAS as arestas liguem um vértice de V1 a um de V2 (nenhuma aresta dentro do mesmo grupo)."],
            "(a) A definição de completo: basta encontrar 2 vértices que NÃO estejam ligados. Como reforço, um completo com 15 vértices teria 15 × 14 / 2 = 105 arestas (cada um liga aos outros 14 e cada aresta é contada 2 vezes, uma por ponta), e G1 só tem 20.\n"
            "(b) Para o bipartido não há fórmula, há um método: pintar com 2 cores. Pintas um vértice de azul, os vizinhos dele de vermelho, os vizinhos desses de azul, e assim sucessivamente. Se nunca aparecer uma aresta com as duas pontas da mesma cor, é bipartido.",
            ["(a) Procura dois vértices sem aresta entre eles: C e H, por exemplo. Já chega.",
             "(b) C fica azul (V1). Os vizinhos de C (Q, E, D) ficam vermelhos (V2).",
             "Vizinhos de Q, E, D ainda sem cor: P, F, N ficam azuis.",
             "Vizinhos de P, F, N ainda sem cor: O, H, G ficam vermelhos.",
             "Vizinhos de O, H, G ainda sem cor: K, I, L ficam azuis.",
             "Vizinhos de K, I, L ainda sem cor: J, M ficam vermelhos. Todos têm cor.",
             "Confirma as 20 arestas: todas ligam um azul a um vermelho. Não há conflito, logo é bipartido.",
             "Atalho para confirmar: num grafo plano, se todas as faces têm grau par, é bipartido. Aqui os graus são 4, 4, 4, 6, 4, 4 e 14, todos pares ✓"],
            "G1 não é completo, porque há vértices não adjacentes, por exemplo C e H (um grafo completo com 15 vértices teria 15 × 14 / 2 = 105 arestas e G1 tem apenas 20).\n"
            "G1 é bipartido: com V1 = {C, F, I, K, L, N, P} e V2 = {D, E, G, H, J, M, O, Q}, V1 ∩ V2 = ∅, V1 ∪ V2 = V e todas as arestas têm uma extremidade em V1 e a outra em V2.")),
        dict(enunciado="Ilustre para o grafo a aplicação do teorema de Dirac.", cotacao=15, resolucao=R(
            "Verificar se G1 cumpre a condição do teorema de Dirac e dizer o que se conclui.",
            ["Teorema de Dirac: se G é simples, conexo, tem V ≥ 3 vértices e TODOS os vértices têm grau ≥ V/2, então G tem um ciclo hamiltoniano.",
             "Ciclo hamiltoniano: volta que passa por TODOS os vértices uma única vez e regressa ao início.",
             "Simples: sem lacetes nem arestas repetidas. Conexo: tudo numa só peça.",
             "Condição suficiente: se se cumpre, conclui-se; se falha, NÃO se conclui nada."],
            "O próprio teorema de Dirac. \"Ilustrar\" é: verificar as hipóteses, testar a condição com os números do grafo e escrever a conclusão.",
            ["Hipóteses: G1 é simples, conexo e V = 15 ≥ 3 ✓",
             "Calcula V/2 = 15/2 = 7,5. Todos os graus teriam de ser ≥ 7,5 (na prática ≥ 8).",
             "Procura o grau mais baixo: deg(E) = 2 (o maior grau de G1 é 4).",
             "2 < 7,5, logo a condição falha.",
             "Como Dirac é condição suficiente, falhar não prova que G1 não é hamiltoniano: nada se conclui."],
            "G1 é simples, conexo e tem V = 15 ≥ 3 vértices. Para aplicar o teorema de Dirac seria preciso deg(v) ≥ V/2 = 7,5 para todo o vértice v. Mas, por exemplo, deg(E) = 2 < 7,5, logo a condição do teorema de Dirac não se verifica.\n"
            "Como o teorema dá apenas uma condição suficiente, não se pode concluir, por ele, se G1 tem ou não ciclo hamiltoniano.")),
        dict(enunciado="Seja μ = [D, F, E, C, Q, P, O, N, G, L, M, I, J, K, H]. O que pode concluir deste resultado à luz da Teoria de Grafos?", cotacao=15, resolucao=R(
            "Classificar a sequência μ: que tipo de percurso é e o que isso diz sobre G1.",
            ["Cadeia: sequência de vértices em que cada par seguido está ligado por uma aresta.",
             "Elementar: não repete vértices.",
             "Cadeia hamiltoniana: cadeia elementar que passa por TODOS os vértices.",
             "Ciclo hamiltoniano: a mesma coisa, mas fechada (volta ao vértice inicial)."],
            "As definições de cadeia, elementar e hamiltoniana. Verifica-se por ordem: é cadeia? repete vértices? passa por todos? fecha?",
            ["É cadeia? Confirma cada par seguido no desenho: D–F, F–E, E–C, C–Q, Q–P, P–O, O–N, N–G, G–L, L–M, M–I, I–J, J–K, K–H. Todos são arestas ✓",
             "Repete vértices? Não: os 15 são todos diferentes, logo é elementar.",
             "Passa por todos? Sim, G1 tem 15 vértices e μ tem 15 vértices diferentes: é hamiltoniana.",
             "Fecha? Para ser ciclo, o último (H) teria de estar ligado ao primeiro (D). H e D não são adjacentes, logo não é ciclo."],
            "μ é uma cadeia de G1 (todos os pares consecutivos são arestas), elementar (não repete vértices) e passa pelos 15 vértices de G1. Logo μ é uma cadeia hamiltoniana e G1 é semi-hamiltoniano.\n"
            "μ não é um ciclo hamiltoniano, porque os vértices H e D não são adjacentes.")),
        dict(enunciado="A eulerização de um grafo consiste em transformar um grafo que não é euleriano num grafo euleriano, por meio da duplicação das arestas já existentes. Indique o menor número de arestas necessárias para obter um grafo euleriano, e quais.", cotacao=10, resolucao=R(
            "Quantas arestas (já existentes) é preciso duplicar, no mínimo, para G1 ficar euleriano, e quais.",
            ["Grafo euleriano: tem um ciclo euleriano, uma volta que passa por TODAS as arestas uma única vez.",
             "Teorema de Euler: um grafo conexo é euleriano se e só se TODOS os vértices têm grau par.",
             "Duplicar uma aresta: desenhá-la outra vez ao lado. Soma 1 ao grau de cada uma das suas duas pontas."],
            "O teorema de Euler: temos de pôr todos os graus pares. Duplicar uma aresta muda a paridade das suas 2 pontas. Para corrigir um vértice ímpar sem estragar os outros, junta-se cada vértice ímpar a outro ímpar pelo caminho mais curto e duplicam-se as arestas desse caminho (os vértices do meio recebem +2 e continuam pares).",
            ["Lista os vértices de grau ímpar: C(3), F(3), I(3), K(3), N(3), P(3). São 6.",
             "Precisas de 3 pares. Vê se algum par de ímpares está ligado diretamente (custaria só 1 aresta): nenhum está.",
             "Logo cada par custa pelo menos 2 arestas, e o mínimo é 3 × 2 = 6.",
             "Escolhe pares a distância 2: C–E–F, P–O–N e I–J–K.",
             "Duplica {C,E}, {E,F}, {P,O}, {O,N}, {I,J}, {J,K}. Confirma: C, F, P, N, I e K passam a grau 4; E, O e J passam de 2 para 4. Todos pares ✓"],
            "G1 é conexo e tem 6 vértices de grau ímpar: C, F, I, K, N e P (todos de grau 3), logo não é euleriano (pelo teorema de Euler, todos os graus teriam de ser pares).\n"
            "Como nenhum par destes vértices é adjacente, cada par precisa de pelo menos 2 arestas duplicadas, logo o mínimo é 6 arestas. Por exemplo, duplicando {C,E}, {E,F}, {P,O}, {O,N}, {I,J} e {J,K}, todos os vértices ficam com grau par e o grafo fica euleriano."))]))
    # ---- Ricardo 2025/26 G2
    Vd = list("ABCDEF"); A = [("A", "B"), ("B", "E"), ("E", "C"), ("C", "A"), ("A", "D"), ("D", "C"), ("C", "F")]
    o, i = digraph_maps(Vd, A)
    assert reach(o, "C") == set(Vd) and reach(i, "C") == set("ABCDE")
    out.append(dict(id="r-ric25-2", grupo=G2, tipo="aberta", tema="Digrafo", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o digrafo (arcos: A→B, B→E, E→C, C→A, A→D, D→C, C→F):", imagem="/estudo/img/md/ric25-d2.png", alineas=[
        dict(enunciado="Investigue se o digrafo é fortemente conexo. Caso não seja, indique todas as componentes conexas.", cotacao=10, resolucao=R(
            "Dizer se o digrafo é fortemente conexo e, como não é, indicar as suas componentes (fortemente) conexas.",
            ["Digrafo: grafo com setas (arcos). Só se pode andar no sentido da seta.",
             "Fortemente conexo: de QUALQUER vértice consegue-se chegar a QUALQUER outro, respeitando as setas.",
             "Γv (fecho direto): todos os vértices onde se chega a partir de v. Γ⁻¹v (fecho inverso): todos os vértices de onde se chega a v.",
             "Componente fortemente conexa: grupo de vértices em que todos chegam a todos. Calcula-se com Γv ∩ Γ⁻¹v."],
            "Primeiro um atalho: um vértice sem setas a sair impede logo a forte conexidade. Depois, para encontrar as componentes, os fechos: a componente de v é Γv ∩ Γ⁻¹v (os vértices que v alcança E que alcançam v).",
            ["Faz a tabela de setas: F tem 1 seta a entrar (C→F) e 0 a sair, logo deg⁺(F) = 0.",
             "De F não se chega a nenhum vértice, logo NÃO é fortemente conexo.",
             "Componente de A: ΓA = {A,B,C,D,E,F} (A→B→E→C→F, A→D). Γ⁻¹A = {A,B,C,D,E} (só F não chega a A). Interseção: {A,B,C,D,E}.",
             "Sobra F, que forma sozinho outra componente: {F}."],
            "O digrafo não é fortemente conexo, porque deg⁺(F) = 0, ou seja, não existe caminho de F para nenhum outro vértice.\n"
            "ΓA ∩ Γ⁻¹A = {A,B,C,D,E,F} ∩ {A,B,C,D,E} = {A,B,C,D,E}. As componentes fortemente conexas são {A, B, C, D, E} e {F}.")),
        dict(enunciado="Apresente um circuito não elementar.", cotacao=10, resolucao=R(
            "Um exemplo de circuito que passe duas vezes pelo mesmo vértice.",
            ["Circuito: caminho (a respeitar as setas) que acaba onde começou, sem repetir arcos.",
             "Elementar: não repete vértices. Não elementar: passa pelo menos duas vezes num vértice."],
            "Juntar dois circuitos que partilham um vértice: percorre-se um, e quando se volta ao vértice comum segue-se pelo outro.",
            ["Encontra circuitos pequenos: A→B→E→C→A e A→D→C→A.",
             "Partilham A (e C). Junta-os: A→B→E→C→A→D→C→A.",
             "Passa duas vezes por A e por C, logo não é elementar.",
             "Cuidado: este percurso usa a seta C→A duas vezes, porque é a única seta que entra em A. Com a definição rigorosa (circuito não repete arcos), este digrafo não tem circuito não elementar. Vale a pena escrever isto."],
            "Por exemplo [A, B, E, C, A, D, C, A]: é um caminho fechado que passa duas vezes pelos vértices A e C, logo não é elementar.\n"
            "(Observação: o arco (C,A) é o único que chega a A, pelo que qualquer caminho fechado que volte duas vezes a A tem de o repetir; sem repetir arcos não existe circuito não elementar.)")),
        dict(enunciado="Justifique que o digrafo tem um caminho euleriano e indique-o.", cotacao=10, resolucao=R(
            "Mostrar que existe um caminho que passa por TODAS as setas uma única vez, e escrevê-lo.",
            ["Caminho euleriano: percurso que usa todos os arcos exatamente uma vez, a respeitar as setas.",
             "deg⁺(v): setas que saem de v. deg⁻(v): setas que entram em v.",
             "Conexo (num digrafo): ignorando as setas, está tudo numa só peça."],
            "O teorema para digrafos: um digrafo conexo tem caminho euleriano de v0 para v1 se e só se v0 tem uma seta a sair a mais (deg⁺ = deg⁻ + 1), v1 tem uma seta a entrar a mais (deg⁻ = deg⁺ + 1) e todos os outros têm deg⁺ = deg⁻.",
            ["Faz a tabela: A sai 2, entra 1; B 1, 1; C 2, 2; D 1, 1; E 1, 1; F sai 0, entra 1.",
             "A tem uma seta a sair a mais: é o início. F tem uma seta a entrar a mais: é o fim. Os outros estão equilibrados ✓",
             "É conexo (ignorando as setas está tudo ligado) ✓",
             "Constrói a partir de A, riscando cada seta usada: A→B→E→C→A→D→C→F.",
             "Confirma: usaste 7 setas e o digrafo tem 7 ✓"],
            table(["v", "deg⁺", "deg⁻"], [["A", 2, 1], ["B", 1, 1], ["C", 2, 2], ["D", 1, 1], ["E", 1, 1], ["F", 0, 1]]) +
            "O digrafo é conexo, deg⁺(A) = deg⁻(A) + 1, deg⁻(F) = deg⁺(F) + 1 e, para os restantes vértices, deg⁺(v) = deg⁻(v). Logo admite um caminho euleriano de A para F, por exemplo [A, B, E, C, A, D, C, F].")),
        dict(enunciado="Determine ΓC e Γ⁻¹C.", cotacao=15, resolucao=R(
            "Os dois fechos transitivos do vértice C.",
            ["ΓC (fecho transitivo direto): todos os vértices onde se consegue chegar a partir de C, seguindo as setas, por caminhos de qualquer tamanho. Inclui o próprio C.",
             "Γ⁻¹C (fecho transitivo inverso): todos os vértices de onde se consegue chegar a C. Inclui o próprio C.",
             "Não confundir com Γ⁺(C) e Γ⁻(C), que são só os vizinhos diretos."],
            "Expansão em camadas: começa com {C} e vai juntando, até não entrar ninguém novo. Para o inverso, faz o mesmo andando contra as setas.",
            ["ΓC: começa {C}. C→A e C→F: {C, A, F}. A→B e A→D: {C, A, F, B, D}. B→E: junta E. Já estão todos: {A, B, C, D, E, F}.",
             "Γ⁻¹C: começa {C}. Chegam a C: E (E→C) e D (D→C): {C, E, D}. Chegam a E: B. Chegam a D: A. Chegam a B: A. Chegam a A: C (já está). Fica {A, B, C, D, E}.",
             "F não está em Γ⁻¹C porque de F não sai nenhuma seta."],
            "ΓC = {A, B, C, D, E, F}, porque C→A, C→F, A→B, A→D e B→E.\nΓ⁻¹C = {A, B, C, D, E}, porque D→C, E→C, B→E e A→B (de F não se chega a C)."))]))
    # ---- Ricardo 2025/26 G3
    V3 = list("123456"); E3 = [norm_edge(a, b, V3) for a, b in ["15", "14", "13", "25", "24", "23", "63", "65", "64", "35"]]
    adj3 = adj_from_edges(V3, E3)
    C3 = ["1", "3", "2", "4", "6", "5", "1"]
    assert all(b in adj3[a] for a, b in zip(C3, C3[1:]))
    assert metodo_ciclico(V3, E3, C3)[0] is False
    out.append(dict(id="r-ric25-3", grupo=G3, tipo="aberta", tema="Planaridade", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o seguinte grafo (numerei os vértices no sentido horário a partir do de cima à esquerda: 1 cima-esq., 2 cima-dir., 3 direita, 4 baixo-dir., 5 baixo-esq., 6 esquerda):",
        imagem="/estudo/img/md/ric25-g3.png", alineas=[
        dict(enunciado="Justifique que o grafo não é planar.", cotacao=15, resolucao=R(
            "Provar que é impossível desenhar este grafo sem arestas a cruzar.",
            ["Planar: PODE ser desenhado sem cruzamentos. O desenho dado ter cruzamentos não prova nada.",
             "K3,3: dois grupos de 3 vértices, cada vértice de um grupo ligado aos 3 do outro grupo (9 arestas). É o exemplo clássico de grafo não planar.",
             "Triângulo: 3 vértices todos ligados entre si."],
            "Tenta por esta ordem: (1) A > 3V − 6? (2) sem triângulos e A > 2V − 4? (3) contém K5 ou K3,3? Aqui as duas primeiras não decidem, por isso procura-se um K3,3 escondido.",
            ["Conta: V = 6, A = 10.",
             "3V − 6 = 12. Como 10 ≤ 12, este teste não decide.",
             "Há triângulos (3, 5, 6 estão todos ligados), por isso o teste 2V − 4 também não se aplica.",
             "Procura K3,3: os vértices 1, 2 e 6 estão os três ligados a 3, 4 e 5. São 9 arestas: {1,3} {1,4} {1,5} {2,3} {2,4} {2,5} {6,3} {6,4} {6,5}. Sobra só {3,5}.",
             "K3,3 não tem triângulos e tem 9 arestas > 2 × 6 − 4 = 8, logo não é planar. Um grafo que contém um bocado não planar também não é planar."],
            "V = 6 e A = 10 ≤ 3V − 6 = 12, pelo que o corolário da fórmula de Euler não permite concluir.\n"
            "Mas, com V1 = {1, 2, 6} e V2 = {3, 4, 5}, existem as 9 arestas entre V1 e V2: o grafo contém K3,3. K3,3 é simples, conexo, sem triângulos e tem 9 > 2 × 6 − 4 = 8 arestas, logo não é planar. Portanto o grafo também não é planar.")),
        dict(enunciado="Aplique o método cíclico para comprovar que o grafo não é planar.", cotacao=20, resolucao=R(
            "Usar o método cíclico (o dos slides TG_3) e concluir que não é planar.",
            ["Ciclo hamiltoniano: volta que passa por todos os vértices uma vez.",
             "Cordas (conjunto L): as arestas que não fazem parte desse ciclo.",
             "Incompatíveis: duas cordas que se cruzam se forem desenhadas do mesmo lado do ciclo. Acontece quando as pontas alternam ao longo do ciclo (a, c, b, d).",
             "A: cordas desenhadas dentro do ciclo. B: cordas desenhadas por fora."],
            "O método cíclico: desenha-se o ciclo como um polígono e tenta-se pôr cada corda dentro (A) ou fora (B) sem cruzar. Se não houver maneira, o grafo não é planar.",
            ["Ciclo hamiltoniano: C = [1, 3, 2, 4, 6, 5, 1]. Escreve os vértices nesta ordem à volta de um círculo.",
             "Cordas que sobram: L = {1,4}, {2,5}, {3,6}, {3,5}.",
             "Testa cada par: {1,4} e {2,5}: na ordem 1, 3, 2, 4, 6, 5 as pontas alternam (1 … 2 … 4 … 5), logo incompatíveis. Do mesmo modo {1,4}×{3,6}, {1,4}×{3,5} e {2,5}×{3,6} são incompatíveis.",
             "Põe {1,4} em A (dentro). Então {2,5} tem de ir para B (fora). Então {3,6}, incompatível com {2,5}, tem de ir para A.",
             "Mas {3,6} também é incompatível com {1,4}, que já está em A. Não cabe em nenhum lado: L nunca fica vazio, logo não é planar."],
            "Ciclo hamiltoniano C = [1, 3, 2, 4, 6, 5, 1]. Arestas fora de C: L = {{1,4}, {2,5}, {3,6}, {3,5}}.\n"
            "Pares incompatíveis: {1,4}×{2,5}, {1,4}×{3,6}, {1,4}×{3,5}, {2,5}×{3,6}.\n"
            "Colocando {1,4} em A, {2,5} tem de ficar em B e então {3,6} tem de ficar em A; mas {3,6} é incompatível com {1,4} ∈ A. As arestas {1,4}, {2,5} e {3,6} são incompatíveis duas a duas, pelo que não podem ser distribuídas por A e B sem interseções. L ≠ ∅, logo o grafo não é planar."))]))
    # ---- Ricardo 2025/26 G4
    V4 = ["Aveiro", "Braga", "Coimbra", "Porto", "Viana", "Vila Real", "Viseu"]
    W4 = {("Aveiro", "Coimbra"): 58, ("Aveiro", "Porto"): 68, ("Aveiro", "Vila Real"): 184, ("Aveiro", "Viseu"): 95, ("Braga", "Porto"): 53,
          ("Braga", "Viana"): 48, ("Braga", "Vila Real"): 106, ("Coimbra", "Porto"): 117, ("Coimbra", "Viseu"): 96, ("Porto", "Viana"): 71,
          ("Porto", "Vila Real"): 116, ("Porto", "Viseu"): 133, ("Viana", "Vila Real"): 154, ("Vila Real", "Viseu"): 110}
    steps, total, ptab = prim_html(V4, W4, "Aveiro")
    path, cost, dtab = dijkstra_html(V4, W4, "Coimbra", "Viana", False)
    assert total == 428 and cost == 188
    pos4 = {"Aveiro": (.25, .55), "Braga": (.5, .1), "Coimbra": (.2, .95), "Porto": (.3, .3), "Viana": (.15, .05), "Vila Real": (.85, .3), "Viseu": (.75, .75)}
    out.append(dict(id="r-ric25-4", grupo=G4, tipo="aberta", tema="Redes", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere as seguintes distâncias, em km, entre algumas cidades portuguesas (em branco: sem ligação):\n" + matrix_table(V4, W4, False),
        alineas=[
        dict(enunciado="A empresa TIR-INTERNACIONAL pretende estabelecer um percurso que permita a um camião recolher, entre as cidades e ligações assinaladas, os bens a transportar. Por meio de um algoritmo adequado, represente e determine a menor distância possível que o camião terá de percorrer se tiver de passar por todas as cidades.", cotacao=15, resolucao=R(
            "Ligar as 7 cidades usando as estradas da tabela, com a menor soma de quilómetros.",
            ["Rede: grafo com números (pesos) nas arestas, aqui quilómetros.",
             "Árvore: ligações que unem todos os pontos sem formar nenhuma volta fechada. Com V pontos tem V − 1 ligações.",
             "Árvore geradora mínima: a árvore que liga TODOS os vértices com a menor soma de pesos."],
            "\"Passar por todas as cidades com a menor distância\", nesta UC, é tratado como árvore geradora mínima. \"Algoritmo a partir da matriz\" = Prim: começa numa cidade e, em cada passo, junta a cidade nova mais barata de ligar a partir das que já estão na árvore.",
            ["Começa em Aveiro. Estradas de Aveiro: Coimbra 58, Porto 68, Viseu 95, Vila Real 184. A mais barata é Coimbra (58).",
             "Árvore {Aveiro, Coimbra}. Candidatas para cidades novas: Porto 68 (Av), Viseu 95 (Av), Vila Real 184 (Av), Porto 117 (Co), Viseu 96 (Co). Mínima: Porto 68.",
             "Árvore {Av, Co, Porto}. Novas candidatas a partir do Porto: Braga 53, Viana 71, Vila Real 116, Viseu 133. Mínima de todas: Braga 53.",
             "Árvore {Av, Co, Po, Braga}. De Braga: Viana 48, Vila Real 106. Mínima: Viana 48.",
             "Árvore {Av, Co, Po, Br, Viana}. Faltam Viseu e Vila Real. Candidatas: Viseu 95 (Av), Vila Real 106 (Br), 116 (Po), 154 (Vi). Mínima: Viseu 95.",
             "Falta Vila Real: Vila Real 106 (Br) ou 110 (Vis). Mínima: 106.",
             "6 ligações para 7 cidades ✓. Soma: 58 + 68 + 53 + 48 + 95 + 106 = 428 km."],
            "Trata-se de um problema de árvore geradora mínima. Aplicando o algoritmo de Prim a partir da matriz, com início em Aveiro:\n" + ptab +
            svg(V4, pos4, list(W4), weights=W4, highlight=[(a, b) for a, b, _ in steps], w=360, h=280) +
            "Árvore geradora mínima: Aveiro–Coimbra, Aveiro–Porto, Porto–Braga, Braga–Viana, Aveiro–Viseu, Braga–Vila Real. Distância mínima: 428 km.")),
        dict(enunciado="Um funcionário encontra-se em Coimbra e tem de fazer um transporte até Viana do Castelo. Determine, por meio de um algoritmo adequado, o percurso mais curto e a respetiva distância.", cotacao=25, resolucao=R(
            "O caminho mais curto de Coimbra até Viana do Castelo e quantos km tem.",
            ["Percurso mínimo: caminho entre DOIS pontos com a menor soma de pesos.",
             "Etiqueta de um vértice: a menor distância conhecida até ele, escrita como custo (antecessor).",
             "Temporária: ainda pode melhorar. Permanente (✓): já é de certeza a menor."],
            "É um percurso mínimo entre dois pontos, logo Dijkstra. Em cada iteração, a menor etiqueta temporária passa a permanente e, a partir dela, tentam melhorar-se os vizinhos.",
            ["Coimbra = 0 ✓. Vizinhos: Aveiro 58 (Co), Porto 117 (Co), Viseu 96 (Co). Restantes ∞.",
             "Menor temporária: Aveiro 58 ✓. A partir de Aveiro: Porto 58 + 68 = 126 > 117, fica 117; Vila Real 58 + 184 = 242 (Av); Viseu 58 + 95 = 153 > 96, fica 96.",
             "Menor temporária: Viseu 96 ✓. Porto 96 + 133 = 229 > 117, fica; Vila Real 96 + 110 = 206 < 242, passa a 206 (Vis).",
             "Menor temporária: Porto 117 ✓. Braga 117 + 53 = 170 (Po); Viana 117 + 71 = 188 (Po); Vila Real 117 + 116 = 233 > 206, fica.",
             "Menor temporária: Braga 170 ✓. Viana 170 + 48 = 218 > 188, fica 188; Vila Real 170 + 106 = 276 > 206, fica.",
             "Menor temporária: Viana 188 ✓. É o destino: parar.",
             "Percurso pelos antecessores, de trás para a frente: Viana ← Porto ← Coimbra."],
            "Trata-se de um problema de percurso mínimo; aplica-se o algoritmo de Dijkstra (etiquetas custo (antecessor), ✓ = permanente):\n" + dtab +
            "Percurso mais curto: Coimbra → Porto → Viana do Castelo, com 117 + 71 = 188 km."))]))
    # ---- Teresa 2025/26 Q3 e Q4
    VT = ["I1", "I2", "I3", "I4", "I5"]; AT = [("I1", "I2"), ("I1", "I5"), ("I2", "I4"), ("I3", "I1"), ("I4", "I3"), ("I4", "I5"), ("I5", "I2")]
    oT, iT = digraph_maps(VT, AT)
    out.append(dict(id="r-ter25-3", grupo=G2, tipo="aberta", tema="Digrafo", fonte="Teste real · Teresa Abreu · 18/11/2025",
        enunciado=("Túneis entre Câmara (I1), Hospital (I2), Bombeiros (I3), Polícia (I4) e Centro de Saúde (I5). Linha = origem, coluna = destino:\n" +
                   table([""] + VT, [[a] + [1 if (a, b) in AT else "" for b in VT] for a in VT])),
        alineas=[
        dict(enunciado="Pretende-se uma rota que percorra todos os túneis exatamente uma vez e volte ao ponto de partida. Identifique o problema e diga se é possível.", cotacao=16,
             resolucao=(table(["v", "deg⁺", "deg⁻"], [[v, len(oT[v]), len(iT[v])] for v in VT]) +
                        "É o problema do circuito euleriano. Exige digrafo conexo com $\\deg^+(v) = \\deg^-(v)$ em todos os vértices.\n"
                        "Falha em I1 (2 ≠ 1), I2 (1 ≠ 2), I4 (2 ≠ 1), I5 (1 ≠ 2) ⇒ a rota não é possível.")),
        dict(enunciado="Indique o número máximo de túneis que pode ser fechado sem que nenhum edifício fique sem ligações.", cotacao=8,
             resolucao=("Para tudo continuar ligado basta uma árvore geradora do grafo subjacente, que tem n − 1 = 4 arestas. Há 7 túneis ⇒ podem fechar-se no máximo 7 − 4 = 3.\n"
                        "(Se a pergunta for lida só como \"nenhum edifício isolado\", bastariam 3 túneis a cobrir os 5 edifícios, por exemplo {I3,I1}, {I2,I4}, {I4,I5}, e fechavam-se 4. A leitura habitual nesta UC é a da árvore.)")),
        dict(enunciado="O Sr. João chegou ao Hospital. Indique os lugares de onde pode ter vindo.", cotacao=14,
             resolucao=f"Fecho transitivo inverso de I2: $\\Gamma^{{-1}}_{{I2}} = {S(reach(iT, 'I2'), VT)}$ ⇒ pode ter vindo de qualquer edifício (todos chegam ao Hospital)."),
        dict(enunciado="A Joana quer ir dos Bombeiros (I3) à Polícia (I4). No mínimo por quantos túneis tem de passar?", cotacao=14,
             resolucao="I3 → I1 → I2 → I4: 3 túneis (I3 só tem saída para I1; de I1 só se vai a I2 ou I5, e só I2 liga a I4)."),
        dict(enunciado="Indique se o digrafo é simples e conexo.", cotacao=10,
             resolucao=("Simples: não tem lacetes nem arcos repetidos com o mesmo sentido. Conexo: o grafo subjacente é conexo.\n"
                        f"Mais ainda, é fortemente conexo: $\\Gamma_{{I1}} = {S(reach(oT, 'I1'), VT)}$ = V e $\\Gamma^{{-1}}_{{I1}}$ = V."))]))
    VR = list("ABCDEFG")
    WR = {("A", "B"): 12, ("A", "E"): 9, ("B", "C"): 5, ("B", "G"): 21, ("C", "A"): 7, ("C", "E"): 6, ("C", "G"): 16, ("D", "A"): 14, ("D", "G"): 4,
          ("E", "D"): 4, ("F", "B"): 2, ("F", "C"): 4, ("G", "F"): 3}
    WRu = {}
    for (a, b), w in WR.items():
        k = norm_edge(a, b, VR); WRu[k] = min(w, WRu.get(k, w))
    st, tot, ptab = prim_html(VR, WRu, "A")
    path, cost, dtab = dijkstra_html(VR, WR, "F", "G", True)
    out.append(dict(id="r-ter25-4", grupo=G4, tipo="aberta", tema="Redes", fonte="Teste real · Teresa Abreu · 18/11/2025",
        enunciado="Considere a rede com a seguinte matriz de adjacência (linha = origem, coluna = destino):\n" + matrix_table(VR, WR, True),
        alineas=[
        dict(enunciado="Usando um algoritmo a partir da matriz, determine a árvore geradora mínima e o valor obtido.", cotacao=20,
             resolucao="Para a árvore geradora ignoram-se as orientações. Prim a partir de A:\n" + ptab + f"Valor: {tot}"),
        dict(enunciado="Usando o algoritmo de Dijkstra, determine o percurso mínimo entre F e G.", cotacao=20,
             resolucao="Respeitando o sentido dos arcos:\n" + dtab + f"Percurso: {' → '.join(path)}, custo {cost}")]))
    out.append(dict(id="r-ter25-2", grupo=G3, tipo="aberta", tema="Planaridade", fonte="Teste real · Teresa Abreu · 18/11/2025",
        enunciado="Numa escola, 9 alunos formam um grupo onde cada aluno é amigo de alguns outros.", alineas=[
        dict(enunciado="É possível que cada aluno seja amigo exatamente de outros três?", cotacao=14,
             resolucao="Seria um grafo com 9 vértices todos de grau 3: $\\sum \\deg = 27$, ímpar. Mas $\\sum \\deg = 2|E|$ é sempre par (equivalente: o nº de vértices de grau ímpar é par). Impossível."),
        dict(enunciado="Se a rede de amizades for um grafo planar, qual é o número máximo de amizades?", cotacao=16,
             resolucao="Grafo simples planar com n = 9 ≥ 3: $m \\le 3n - 6 = 21$. Máximo: 21 amizades.")]))
    # ---- Anabela Silva 2025/26 (2º teste, PL turno 2, 04/12/2025)
    VA = list("abcde")
    EA = [norm_edge(a, b, VA) for a, b in ["ab", "ac", "ae", "ad", "bc", "bd", "ce", "cd", "ed"]]
    adjA = adj_from_edges(VA, EA); dA = {v: len(adjA[v]) for v in VA}
    CA = ["a", "b", "c", "e", "d", "a"]
    okA, metA = metodo_ciclico(VA, EA, CA)
    assert okA and dA == {"a": 4, "b": 3, "c": 4, "d": 4, "e": 3}
    hamA = ["a", "b", "c", "e", "d", "a"]
    assert all(y in adjA[x] for x, y in zip(hamA, hamA[1:]))
    boolA = table([""] + VA, [[x] + [1 if y in adjA[x] else 0 for y in VA] for x in VA])
    out.append(dict(id="r-ana25-1", grupo=G1, tipo="aberta", tema="Grafo não orientado", fonte="Teste real · Anabela Silva · 04/12/2025",
        enunciado="Seja G = (V, E) o grafo representado na figura:", imagem="/estudo/img/md/ana25-g1.png", alineas=[
        dict(enunciado="Indique o grau de cada um dos vértices.", cotacao=10,
             resolucao="deg(a) = 4, deg(b) = 3, deg(c) = 4, deg(d) = 4, deg(e) = 3.\nConfirmação: Σ deg = 18 = 2 × 9 arestas ✓"),
        dict(enunciado="Determine os vizinhos dos vértices c, d e f.", cotacao=10,
             resolucao="Γ(c) = {a, b, d, e} e Γ(d) = {a, b, c, e}.\nO vértice f não existe no grafo (gralha no enunciado): escreve isso na prova em vez de inventar."),
        dict(enunciado="O grafo é planar? Apresente a sua representação planar.", cotacao=15,
             resolucao=("Sim. G é o K5 sem a aresta {b,e} (o único par não adjacente é b e e).\n"
                        "O desenho dado tem cruzamentos, mas isso não prova nada: é preciso redesenhar. Pelo método cíclico:\n" + metA)),
        dict(enunciado="A fórmula de Euler é verificada? Justifique.", cotacao=9,
             resolucao="G é planar (representação da alínea anterior) e conexo, por isso aplica-se.\nV = 5, A = 9, F = 6 (5 interiores + a exterior).\nV − A + F = 5 − 9 + 6 = 2: verifica-se."),
        dict(enunciado="Indique, se existir, uma cadeia elementar que não seja simples.", cotacao=6,
             resolucao=("Não existe (é uma armadilha). Elementar = não repete vértices. Se uma cadeia não repete vértices, também não pode repetir arestas (repetir uma aresta obriga a repetir as pontas).\n"
                        "Logo toda a cadeia elementar é simples. O contrário é que pode acontecer: simples mas não elementar, por exemplo [a, b, c, a, d].")),
        dict(enunciado="Indique, se existir, um ciclo com comprimento 4.", cotacao=6,
             resolucao="[a, b, c, d, a]: 4 arestas ({a,b}, {b,c}, {c,d}, {d,a}), não repete arestas e volta ao início."),
        dict(enunciado="O que pode dizer sobre a veracidade do Teorema de Ore?", cotacao=10,
             resolucao=("G é simples, conexo e V = 5 ≥ 3. O único par NÃO adjacente é b e e: deg(b) + deg(e) = 3 + 3 = 6 ≥ 5.\n"
                        "A condição de Ore verifica-se, logo G tem ciclo hamiltoniano, por exemplo [a, b, c, e, d, a].")),
        dict(enunciado="Construa a matriz booleana para G.", cotacao=10,
             resolucao=boolA + "Simétrica (grafo não orientado), diagonal a 0 (sem lacetes). A soma de cada linha é o grau do vértice."),
        dict(enunciado="Como classificaria o grafo quanto à conexidade?", cotacao=6,
             resolucao="Conexo: há cadeia entre quaisquer dois vértices (por exemplo [a, b, c, e, d] passa por todos). Não é completo: falta a aresta {b,e}.")]))
    VD = list("123456")
    AD = [("3", "6"), ("2", "6"), ("2", "5"), ("1", "5"), ("2", "1"), ("2", "4"), ("4", "3"), ("4", "4"), ("2", "3"), ("3", "2")]
    oD, iD = digraph_maps(VD, AD)
    assert reach(oD, "3") == set(VD) and reach(iD, "3") == {"2", "3", "4"}
    out.append(dict(id="r-ana25-2", grupo=G2, tipo="aberta", tema="Digrafo", fonte="Teste real · Anabela Silva · 04/12/2025",
        enunciado="Considere a representação do seguinte digrafo D (o vértice 4 tem um lacete; entre 2 e 3 há um arco em cada sentido):", imagem="/estudo/img/md/ana25-d2.png", alineas=[
        dict(enunciado="Indique os antecessores do vértice 1 e os sucessores do vértice 4.", cotacao=10,
             resolucao="Antecessores de 1: Γ⁻(1) = {2} (só o arco 2→1 chega a 1).\nSucessores de 4: Γ⁺(4) = {3, 4} (arco 4→3 e o lacete 4→4: com lacete, o vértice é sucessor de si próprio)."),
        dict(enunciado="Apresente o fecho transitivo direto e o fecho transitivo inverso do vértice 3. D é fortemente conexo?", cotacao=20,
             resolucao=("Γ3: 3→6, 3→2; de 2: 2→1, 2→4, 2→5, 2→6; de 1: 1→5 ⇒ Γ3 = {1, 2, 3, 4, 5, 6}.\n"
                        "Γ⁻¹3: 2→3, 4→3; quem chega a 2: 3; quem chega a 4: 2 e 4 ⇒ Γ⁻¹3 = {2, 3, 4}.\n"
                        "Γ3 ∩ Γ⁻¹3 = {2, 3, 4} ≠ V, logo D NÃO é fortemente conexo (por exemplo, de 5 e de 6 não sai nenhum arco).")),
        dict(enunciado="Verifique se D tem um circuito euleriano.", cotacao=15,
             resolucao=(table(["v", "deg⁺", "deg⁻"], [[v, len(oD[v]), len(iD[v])] for v in VD]) +
                        "Para haver circuito euleriano é preciso deg⁺(v) = deg⁻(v) em todos. Falha, por exemplo, em 2 (5 ≠ 1), 5 (0 ≠ 2) e 6 (0 ≠ 2). Não tem circuito euleriano (nem caminho: há mais de 2 vértices desequilibrados).\n"
                        "O lacete em 4 conta 1 a sair e 1 a entrar."))]))
    VI = ["I1", "I2", "I3", "I4", "I5", "I6", "I7"]
    WI = {("I1", "I2"): 15, ("I1", "I3"): 8, ("I1", "I6"): 10, ("I1", "I7"): 100, ("I2", "I3"): 25, ("I3", "I4"): 5, ("I3", "I7"): 80,
          ("I4", "I5"): 15, ("I5", "I6"): 20, ("I5", "I7"): 10}
    stI, totI, ptabI = prim_html(VI, WI, "I1")
    pathI, costI, dtabI = dijkstra_html(VI, WI, "I4", "I2", False)
    posI = {"I1": (.3, .3), "I2": (.05, .05), "I3": (.1, .6), "I4": (.35, .95), "I5": (.75, .8), "I6": (.65, .25), "I7": (.95, .5)}
    out.append(dict(id="r-ana25-3", grupo=G4, tipo="aberta", tema="Redes", fonte="Teste real · Anabela Silva · 04/12/2025",
        enunciado="Custos de transporte (€ por unidade) entre armazéns; em branco, não há transporte:\n" + matrix_table(VI, WI, False),
        alineas=[
        dict(enunciado="Desenhe o grafo capaz de representar a situação descrita.", cotacao=15,
             resolucao="Rede não orientada (a tabela é simétrica), com 7 vértices e 10 arestas com os custos:\n" + svg(VI, posI, list(WI), weights=WI, w=360, h=280)),
        dict(enunciado="Através de um algoritmo adequado, apresente o valor mínimo do comprimento de fio de luzes que permite ligar todos os armazéns.", cotacao=20,
             resolucao=("Ligar todos com o mínimo: árvore geradora mínima. Prim a partir de I1:\n" + ptabI +
                        svg(VI, posI, list(WI), weights=WI, highlight=[(a, b) for a, b, _ in stI], w=360, h=280) + f"Valor mínimo: {totI}")),
        dict(enunciado="Determine o custo mínimo do envio de uma encomenda entre o armazém I4 e o I2. Utilize um algoritmo adequado.", cotacao=25,
             resolucao="Percurso mínimo entre dois pontos: Dijkstra.\n" + dtabI + f"Percurso: {' → '.join(pathI)}, custo {costI} €")]))
    out.append(dict(id="r-ana25-4", grupo=G1, tipo="aberta", tema="Contagem de arestas", fonte="Teste real · Anabela Silva · 04/12/2025",
        enunciado="Numa empresa existem 6 routers. Cada router deve estar ligado diretamente a todos os outros, exceto a um router específico de cada par, por questões de segurança. Cada ligação é um cabo físico.",
        alineas=[
        dict(enunciado="Quantas ligações físicas existem ao todo?", cotacao=8,
             resolucao=("Cada router liga a todos menos a 1: grau 6 − 2 = 4 (não liga a si próprio nem ao seu par).\n"
                        "Σ deg = 6 × 4 = 24 = 2A ⇒ A = 12 ligações.\nOutra forma: K6 teria 6 × 5 / 2 = 15 arestas; tiram-se as 3 dos pares proibidos: 15 − 3 = 12.")),
        dict(enunciado="Se cada cabo custa 50 €, qual é o custo total da instalação da rede?", cotacao=5,
             resolucao="12 × 50 € = 600 €.")]))
    # ---- José Castro 2023/24 Q6 (rede orientada)
    VJ = list("sabcdefgt")
    WJ = {("s", "a"): 7, ("s", "b"): 5, ("s", "c"): 8, ("a", "f"): 6, ("a", "g"): 5, ("b", "d"): 7, ("c", "d"): 5, ("c", "f"): 6, ("d", "e"): 11,
          ("e", "t"): 13, ("f", "d"): 5, ("f", "g"): 6, ("g", "t"): 9}
    oJ, iJ = digraph_maps(VJ, list(WJ))
    path, cost, dtab = dijkstra_html(VJ, WJ, "s", "t", True)
    out.append(dict(id="r-jc23-6", grupo=G4, tipo="aberta", tema="Redes", fonte="Teste real · José Castro · 28/11/2023",
        enunciado="Considere a rede representada pela matriz de adjacência (linha = origem, coluna = destino):\n" + matrix_table(VJ, WJ, True),
        alineas=[
        dict(enunciado="Determine $\\Gamma^{-1}_e$ (fecho transitivo inverso do vértice e).", cotacao=12.5,
             resolucao=f"Andando para trás pelos arcos que entram: d → e; b, c, f → d; s → b, c; a, c → f; s → a.\n$\\Gamma^{{-1}}_e = {S(reach(iJ, 'e'), VJ)}$"),
        dict(enunciado="Use o algoritmo de Dijkstra para calcular o percurso de custo mínimo entre s e t, apresentando todas as iterações.", cotacao=25,
             resolucao=dtab + f"Percurso mínimo: {' → '.join(path)}, custo {cost}")]))
    out.append(dict(id="r-jc23-3", grupo=G3, tipo="aberta", tema="Planaridade", fonte="Teste real · José Castro · 28/11/2023",
        enunciado="Suponha que um grafo planar conexo tem 30 arestas e que uma sua representação planar divide o plano em 20 regiões.", alineas=[
        dict(enunciado="Quantos vértices tem o grafo? Justifique.", cotacao=15,
             resolucao="Fórmula de Euler: $n - m + f = 2 \\Rightarrow n = 2 + m - f = 2 + 30 - 20 = 12$ vértices.")]))
    # ================= Teste do diurno · José Castro / Paula Cheira · 25/11/2026
    FD = "Teste real · Diurno (José Castro / Paula Cheira) · 25/11/2026"
    Vg = list("12345678")
    Eg = [("1", "2"), ("3", "4"), ("3", "5"), ("4", "8"), ("5", "6"), ("5", "7"), ("6", "8"), ("7", "8")]
    adjg = adj_from_edges(Vg, Eg)
    assert reach(adjg, "4") == set("345678") and not connected(adjg)
    dg = bfs_dist(adjg, "4")
    dg = dg[0] if isinstance(dg, tuple) else dg
    def bij(u, v):
        return 1 if (v in adjg[u]) else 0
    Mrows = [[u] + [bij(u, v) for v in Vg] for u in Vg]
    Mtab = table(["", *Vg], Mrows)
    Mtab4 = table(["", *Vg, "d(4,·)"], [r + [dg.get(r[0], "∞") if r[0] in dg else "∞"] for r in Mrows])
    degg = {"1": 1, "2": 1, "3": 2, "4": 3, "5": 3, "6": 2, "7": 2, "8": 4}
    posP = {"4": (.02, .5), "8": (.25, .05), "7": (.7, .05), "5": (.7, .9), "3": (.25, .95), "6": (.45, .5), "2": (.95, .15), "1": (.95, .85)}
    out.append(dict(id="r-diu26-1", grupo=G1, tipo="aberta", tema="Grafo não orientado", fonte=FD,
        enunciado="Considere o grafo G da figura (arestas: {4,8}, {8,7}, {8,6}, {7,5}, {4,3} (a curva, que passa por cima de {8,6}), {3,5}, {6,5}, {2,1} (que cruza {6,5}); os cruzamentos não são vértices):",
        imagem="/estudo/img/md/diu26-g1.jpg", alineas=[
        dict(enunciado="O grafo G é simples ou multigrafo? Justifique.", cotacao=5, resolucao=R(
            "Classificar G como simples ou multigrafo, dizendo porquê.",
            ["Grafo simples: não tem lacetes nem arestas paralelas.",
             "Lacete: aresta que sai e volta ao mesmo vértice.",
             "Arestas paralelas (múltiplas): duas ou mais arestas a ligar o MESMO par de vértices.",
             "Multigrafo: grafo que tem arestas paralelas."],
            "Só as definições. Olha para o desenho à procura de duas linhas entre os mesmos dois vértices ou de um laço. Armadilha: perto do 4 saem duas linhas na mesma direção, mas uma vai para o 8 e a outra é a curva que vai para o 3.",
            ["Procura laços: nenhum vértice tem uma linha que volte a ele próprio.",
             "Procura linhas repetidas: segue cada linha até ao fim. Do 4 sai uma para o 8 e a curva para o 3, pares diferentes. Não há nenhum par de vértices com 2 arestas.",
             "Os sítios onde as linhas se cruzam (curva com {8,6}, {2,1} com {6,5}) não são vértices, só cruzamentos no papel.",
             "Sem laços e sem arestas paralelas: é simples."],
            "G é um grafo simples (não é multigrafo), porque não tem lacetes (nenhuma aresta liga um vértice a si próprio) nem arestas paralelas (cada par de vértices está ligado no máximo por uma aresta).")),
        dict(enunciado="Apresente um grafo parcial de G com 6 arestas.", cotacao=7.5, resolucao=R(
            "Desenhar um grafo parcial de G que tenha exatamente 6 arestas.",
            ["Grafo parcial de G: mantém TODOS os vértices de G e fica só com algumas das arestas (G' = (V, E') com E' ⊆ E).",
             "Não confundir com subgrafo gerado por vértices, em que se tiram vértices."],
            "A definição de grafo parcial. G tem 8 arestas; escolhes 6 quaisquer e manténs os 8 vértices, mesmo que alguns fiquem isolados.",
            ["Lista as 8 arestas: {4,8}, {8,7}, {8,6}, {7,5}, {4,3}, {3,5}, {6,5}, {2,1}.",
             "Escolhe 6, por exemplo {4,8}, {8,7}, {7,5}, {5,6}, {6,8}, {3,5}.",
             "Desenha os 8 vértices (1 e 2 ficam isolados, sem problema) e só essas 6 arestas."],
            "G' = (V, E') com V = {1, 2, 3, 4, 5, 6, 7, 8} e E' = {{4,8}, {8,7}, {7,5}, {5,6}, {6,8}, {3,5}} ⊆ E, |E'| = 6:\n" +
            svg(Vg, posP, [("4", "8"), ("8", "7"), ("7", "5"), ("5", "6"), ("6", "8"), ("3", "5")], w=300, h=220))),
        dict(enunciado="Determine a matriz booleana de G.", cotacao=10, resolucao=R(
            "A matriz booleana (só 0 e 1) do grafo G.",
            ["Matriz booleana B: linha i, coluna j tem 1 se vi e vj são adjacentes, 0 se não.",
             "Diferença para a matriz de adjacência: na de adjacência escreve-se o NÚMERO de arestas entre os dois; na booleana só 0 ou 1. Como G é simples, aqui as duas são iguais.",
             "Num grafo não orientado a matriz é simétrica (bij = bji)."],
            "A definição de matriz booleana. Vai vértice a vértice e marca 1 nos vizinhos.",
            ["Vizinhos: 1: {2}; 2: {1}; 3: {4, 5}; 4: {3, 8}; 5: {3, 6, 7}; 6: {5, 8}; 7: {5, 8}; 8: {4, 6, 7}.",
             "Preenche a linha de cada vértice com 1 nas colunas dos vizinhos.",
             "Confirma a simetria: a linha 5 tem 1 em 3, 6 e 7, e as colunas 5 das linhas 3, 6 e 7 também têm 1."],
            "Ordenando os vértices 1, 2, …, 8 (bij = 1 se {vi, vj} ∈ E, 0 caso contrário):\n" + Mtab)),
        dict(enunciado="Determine o fecho transitivo direto do vértice 4 e adicione a coluna correspondente do comprimento mínimo à matriz de 1.3.", cotacao=12.5, resolucao=R(
            "(a) Γ4, os vértices a que se chega a partir de 4; (b) acrescentar à matriz uma coluna com a distância mínima de 4 a cada vértice.",
            ["Fecho transitivo direto Γv: todos os vértices atingíveis a partir de v por cadeias de qualquer comprimento (inclui o próprio v, comprimento 0).",
             "Comprimento de uma cadeia: nº de arestas. Comprimento mínimo d(4, v): menor nº de arestas para ir de 4 a v.",
             "∞: não há cadeia nenhuma."],
            "O método do professor (expansão por camadas com a matriz): começa com 4 (comprimento 0), juntam-se os vizinhos (comprimento 1), depois os vizinhos desses (comprimento 2), até não aparecer ninguém novo. O nº da camada é o comprimento mínimo.",
            ["Comprimento 0: {4}.",
             "Comprimento 1: vizinhos de 4 (linha 4 da matriz): 3 e 8.",
             "Comprimento 2: vizinhos de 3 e 8 ainda não marcados: 5 (de 3), 6 e 7 (de 8).",
             "Comprimento 3: vizinhos de 5, 6, 7 ainda não marcados: nenhum. Pára.",
             "1 e 2 nunca aparecem: distância ∞.",
             "Γ4 = {3, 4, 5, 6, 7, 8}. Escreve a coluna d(4,·) ao lado da matriz."],
            "Γ4 = {4} ∪ {3, 8} ∪ {5, 6, 7} = {3, 4, 5, 6, 7, 8}.\nMatriz de 1.3 com a coluna dos comprimentos mínimos a partir de 4:\n" + Mtab4)),
        dict(enunciado="Justifique que o grafo não é conexo e apresente uma representação gráfica das suas componentes conexas.", cotacao=10, resolucao=R(
            "Mostrar que G não é conexo e desenhar cada componente conexa.",
            ["Conexo: entre quaisquer dois vértices existe uma cadeia.",
             "Componente conexa: um bocado do grafo que está todo ligado entre si e não está ligado ao resto.",
             "Atenção: o cruzamento de {2,1} com {6,5} no desenho NÃO é um vértice, as arestas só se cruzam no papel."],
            "Usa o resultado de 1.4: se Γ4 não tem todos os vértices, há vértices aos quais 4 não chega, logo não é conexo.",
            ["Γ4 = {3, 4, 5, 6, 7, 8} ≠ V: 1 e 2 não são atingíveis a partir de 4.",
             "Logo não existe cadeia entre 4 e 1: G não é conexo.",
             "Componentes: {1, 2} (só a aresta {1,2}) e {3, 4, 5, 6, 7, 8} (as outras 7 arestas).",
             "Desenha-as separadas, sem cruzamentos."],
            "Pela alínea 1.4, Γ4 = {3, 4, 5, 6, 7, 8} ≠ V, ou seja, não existe nenhuma cadeia entre 4 e 1 (nem entre 4 e 2). Logo G não é conexo.\n"
            "G tem 2 componentes conexas: G1 com vértices {3, 4, 5, 6, 7, 8} e G2 com vértices {1, 2}:\n" +
            svg(Vg, posP, [("4", "8"), ("8", "7"), ("7", "5"), ("5", "3"), ("3", "4"), ("8", "6"), ("6", "5"), ("1", "2")], w=300, h=220)))]))
    out.append(dict(id="r-diu26-2", grupo=G1, tipo="aberta", tema="Definições", fonte=FD, enunciado="Teoria:", alineas=[
        dict(enunciado="Defina, com rigor, uma rede.", cotacao=10, resolucao=R(
            "A definição formal de rede.",
            ["Rede: grafo (ou digrafo) em que cada aresta (ou arco) tem um número associado, o peso.",
             "Peso: custo, distância, tempo, capacidade…"],
            "A definição dos slides TG_5. \"Com rigor\" quer dizer: escrever com símbolos, G, V, E e a função peso.",
            ["Diz o que é o grafo: G = (V, E).", "Diz que há uma função que dá um número real a cada aresta: w: E → ℝ.", "Junta os dois: a rede é o par (G, w)."],
            "Uma rede é um grafo (ou digrafo) G = (V, E) ao qual está associada uma função w: E → ℝ (ponderação) que atribui a cada aresta (arco) e ∈ E um número real w(e), chamado peso (custo, distância, capacidade, …). Representa-se por R = (V, E, w).")),
        dict(enunciado="Considere o grafo bipartido completo Kn,m. Em que condições tal grafo é hamiltoniano?", cotacao=10, resolucao=R(
            "Para que valores de n e m o Kn,m tem ciclo hamiltoniano.",
            ["Kn,m: dois grupos, um com n vértices e outro com m; cada vértice de um grupo liga a TODOS os do outro; dentro do mesmo grupo não há arestas.",
             "Ciclo hamiltoniano: volta que passa uma vez por cada vértice."],
            "Raciocínio sobre a alternância: num bipartido qualquer aresta muda de grupo, por isso um ciclo alterna V1, V2, V1, V2… e tem tantos vértices de um lado como do outro.",
            ["Um ciclo hamiltoniano passa por todos os n + m vértices alternando os grupos.",
             "Alternar e voltar ao início obriga a usar o mesmo nº de vértices de cada grupo: n = m.",
             "Um ciclo num grafo simples precisa de pelo menos 3 vértices, logo n + m ≥ 4, isto é, n = m ≥ 2.",
             "Se n = m ≥ 2, o ciclo existe: a1, b1, a2, b2, …, an, bn, a1 (todas estas arestas existem porque é completo).",
             "Exemplo: K2,2 é um quadrado (hamiltoniano); K2,3 não é."],
            "Kn,m é hamiltoniano se e só se n = m ≥ 2.\nJustificação: em Kn,m todas as arestas ligam V1 (n vértices) a V2 (m vértices), pelo que um ciclo alterna entre V1 e V2 e usa tantos vértices de V1 como de V2; para passar por todos é preciso n = m. Reciprocamente, se n = m ≥ 2, [a1, b1, a2, b2, …, an, bn, a1] é um ciclo hamiltoniano, pois Kn,m é completo."))]))
    # ---- Q3 digrafo
    Vd3 = list("ABCDEF"); Ad3 = [("E", "C"), ("C", "A"), ("E", "F"), ("F", "D"), ("D", "E"), ("D", "C"), ("C", "B"), ("A", "B"), ("B", "D")]
    o3, i3 = digraph_maps(Vd3, Ad3)
    assert all(reach(o3, v) == set(Vd3) for v in Vd3)
    eul3 = ["E", "C", "A", "B", "D", "E", "F", "D", "C", "B"]
    assert sorted(zip(eul3, eul3[1:])) == sorted(Ad3)
    tab3 = table(["v", "deg⁺ (saem)", "deg⁻ (entram)"], [[v, len(o3[v]), len(i3[v])] for v in Vd3])
    out.append(dict(id="r-diu26-3", grupo=G2, tipo="aberta", tema="Digrafo", fonte=FD,
        enunciado="Considere o grafo orientado D (arcos: E→C, C→A, E→F, F→D, D→E, D→C, C→B, A→B, B→D):", imagem="/estudo/img/md/diu26-d3.jpg", alineas=[
        dict(enunciado="Indique Γ⁻(E) e deg⁻(B).", cotacao=10, resolucao=R(
            "Os antecessores de E e o grau de entrada de B.",
            ["Γ⁻(v) (antecessores): vértices de onde sai uma seta que chega DIRETAMENTE a v. Não confundir com Γ⁻¹v (fecho inverso, caminhos de qualquer tamanho).",
             "deg⁻(v) (semigrau interior): nº de setas que ENTRAM em v."],
            "Só as definições: olha para as pontas das setas.",
            ["Setas que acabam em E: só D→E. Logo Γ⁻(E) = {D}.",
             "Setas que acabam em B: C→B e A→B. Logo deg⁻(B) = 2."],
            "Γ⁻(E) = {D}, porque (D, E) é o único arco que chega a E.\ndeg⁻(B) = |Γ⁻(B)| = |{A, C}| = 2.")),
        dict(enunciado="Justifique que D não tem um circuito euleriano mas tem um caminho euleriano. Não apresente tal caminho para o justificar.", cotacao=12.5, resolucao=R(
            "Usar o teorema (e não um exemplo) para mostrar: não há circuito euleriano, mas há caminho euleriano.",
            ["Circuito euleriano: caminho fechado que usa todos os arcos uma vez.",
             "Caminho euleriano: o mesmo, mas acaba num vértice diferente do início.",
             "deg⁺: setas que saem; deg⁻: setas que entram."],
            "Os teoremas para digrafos conexos: circuito euleriano ⇔ deg⁺(v) = deg⁻(v) em todos os vértices. Caminho euleriano de v0 para v1 ⇔ deg⁺(v0) = deg⁻(v0) + 1, deg⁻(v1) = deg⁺(v1) + 1 e os restantes equilibrados. \"Não apresente o caminho\" = a justificação TEM de ser pela tabela de graus.",
            ["Confirma que é conexo (ignorando as setas, está tudo ligado).",
             "Faz a tabela de deg⁺ e deg⁻.",
             "E: sai 2, entra 1. B: sai 1, entra 2. Os outros 4: iguais.",
             "Como E e B não estão equilibrados: não há circuito euleriano.",
             "E tem uma seta a sair a mais (início), B uma a entrar a mais (fim), resto equilibrado: há caminho euleriano de E para B."],
            tab3 + "D é conexo. Como deg⁺(E) = 2 ≠ 1 = deg⁻(E), não se verifica deg⁺(v) = deg⁻(v) para todo o v, logo D não tem circuito euleriano.\n"
            "No entanto, deg⁺(E) = deg⁻(E) + 1, deg⁻(B) = deg⁺(B) + 1 e deg⁺(v) = deg⁻(v) para v ∈ {A, C, D, F}, logo D tem um caminho euleriano, que começa em E e termina em B.")),
        dict(enunciado="Apresente um caminho euleriano de D.", cotacao=10, resolucao=R(
            "Escrever um caminho que use os 9 arcos, cada um uma vez.",
            ["Caminho euleriano: segue as setas e usa todos os arcos exatamente uma vez."],
            "Pela 3.2 sabes que começa em E e acaba em B. Constrói riscando as setas usadas; se ficares preso antes do fim, volta atrás e escolhe outra seta (algoritmo de Hierholzer).",
            ["Começa em E: E→C, C→A, A→B, B→D, D→E (5 setas usadas).",
             "De E ainda sai E→F: F→D, D→C, C→B.",
             "Contas: 9 setas usadas, acabou em B ✓"],
            "[E, C, A, B, D, E, F, D, C, B] é um caminho euleriano: usa os 9 arcos de D, cada um uma única vez, de E até B.")),
        dict(enunciado="O grafo D é fortemente conexo? Justifique.", cotacao=12.5, resolucao=R(
            "Dizer se de qualquer vértice se chega a qualquer outro, respeitando as setas.",
            ["Fortemente conexo: para quaisquer u e v existe caminho de u para v E de v para u.",
             "Γv: vértices atingíveis a partir de v. Γ⁻¹v: vértices que atingem v."],
            "Basta um circuito que passe por todos os vértices (ou mostrar ΓE = Γ⁻¹E = V). Também se pode usar: um vértice é atingível de todos e atinge todos ⇒ fortemente conexo.",
            ["Procura um caminho fechado que passe por todos: E→F→D→C→A→B→D→E. Passa por E, F, D, C, A, B: todos os 6.",
             "Num caminho fechado, cada vértice chega a qualquer outro seguindo o caminho às voltas.",
             "Logo é fortemente conexo. (Cuidado: os digrafos de outros testes tinham um vértice sem setas a sair; aqui todos têm deg⁺ ≥ 1, mas isso sozinho não prova nada.)"],
            "Sim. O caminho fechado [E, F, D, C, A, B, D, E] passa por todos os vértices de D, pelo que, para quaisquer u, v ∈ V, existe um caminho de u para v (seguindo este caminho fechado). Equivalentemente, ΓE = Γ⁻¹E = {A, B, C, D, E, F} = V. Logo D é fortemente conexo (tem uma única componente fortemente conexa)."))]))
    # ---- Q4 rede R
    VR = list("ABCDEFGH")
    WR = {("G", "H"): 14, ("C", "H"): 21, ("A", "G"): 26, ("C", "G"): 13, ("B", "H"): 8, ("A", "B"): 7, ("F", "G"): 15, ("E", "G"): 14,
          ("C", "E"): 12, ("E", "F"): 12, ("D", "E"): 10, ("B", "D"): 14, ("B", "F"): 33}
    adjR = adj_from_edges(VR, list(WR))
    assert ham_cycle(adjR, VR) is None
    stR, totR, ptR = prim_html(VR, WR, "A")
    assert totR == 76
    posR = {"H": (.6, 0), "A": (.95, .12), "G": (.2, .35), "C": (.6, .35), "B": (.92, .65), "F": (0, .85), "E": (.5, .85), "D": (.75, .85)}
    out.append(dict(id="r-diu26-4", grupo=G4, tipo="aberta", tema="Redes", fonte=FD,
        enunciado="Seja R a rede da figura (pesos: GH 14, CH 21, GA 26, GC 13, HB 8, AB 7, GF 15, GE 14, CE 12, FE 12, ED 10, DB 14, FB 33). "
                  "Confirma os pesos na tua folha: na foto alguns estão meio tapados.", imagem="/estudo/img/md/diu26-r4.jpg", alineas=[
        dict(enunciado="Verifique se R é hamiltoniano.", cotacao=17.5, resolucao=R(
            "Ver se existe um ciclo que passe uma vez por cada uma das 8 plantas (vértices) e volte ao início.",
            ["Ciclo hamiltoniano: passa por TODOS os vértices uma única vez e fecha.",
             "Regra 1: se um vértice tem grau 2, as suas 2 arestas estão obrigatoriamente no ciclo (é a única forma de entrar e sair).",
             "Regra 2: num ciclo, cada vértice usa exatamente 2 arestas; se já tem 2 obrigatórias, as outras saem (Regra 3)."],
            "Dirac não serve (deg(A) = 2 < 8/2 = 4, e falhar Dirac não prova nada). Usa-se o método das regras dos vértices de grau 2 até chegar a uma contradição.",
            ["Graus: A 2 (G, B); D 2 (E, B); H 3 (G, C, B); B 4; C 3; E 4; F 3; G 5.",
             "A tem grau 2: {G,A} e {A,B} entram no ciclo.",
             "D tem grau 2: {E,D} e {D,B} entram no ciclo.",
             "B já tem 2 arestas ({A,B} e {D,B}): apagam-se {H,B} e {F,B}.",
             "Agora H fica com grau 2 (G, C): {G,H} e {H,C} entram. F fica com grau 2 (G, E): {G,F} e {F,E} entram.",
             "G teria 3 arestas obrigatórias: {G,A}, {G,H}, {G,F}. Num ciclo só pode ter 2. Contradição.",
             "Logo não existe ciclo hamiltoniano."],
            "Aplicando as regras para ciclos hamiltonianos: deg(A) = 2 ⇒ {G,A}, {A,B} ∈ ciclo; deg(D) = 2 ⇒ {E,D}, {D,B} ∈ ciclo. B já tem duas arestas no ciclo, logo eliminam-se {H,B} e {F,B}. "
            "Então deg(H) = 2 ⇒ {G,H}, {H,C} ∈ ciclo e deg(F) = 2 ⇒ {G,F}, {F,E} ∈ ciclo. Mas assim G teria três arestas no ciclo ({G,A}, {G,H}, {G,F}), o que é impossível.\nLogo R não é hamiltoniano.")),
        dict(enunciado="Represente a rede R através da sua matriz de adjacência.", cotacao=10, resolucao=R(
            "A matriz da rede (com os pesos).",
            ["Matriz de adjacência de uma rede: na linha i, coluna j, escreve-se o PESO da aresta {vi, vj}; se não há aresta, fica vazio (ou 0/∞, conforme o professor).",
             "Rede não orientada ⇒ matriz simétrica."],
            "A definição. Ordena os vértices (A, B, …, H) e percorre a lista de arestas, escrevendo cada peso duas vezes (em ij e em ji).",
            ["Ordem: A, B, C, D, E, F, G, H.", "Para cada aresta, escreve o peso nas duas posições simétricas (por exemplo AB = 7 em (A,B) e (B,A)).",
             "Confirma: 13 arestas ⇒ 26 números na matriz."],
            matrix_table(VR, WR, False) + "(em branco: não há ligação)")),
        dict(enunciado="Utilize o algoritmo de Prim para encontrar as ligações entre as raízes das plantas que minimiza a distância total e garanta ainda que todas as plantas estão ligadas entre si. Indique a distância mínima e as ligações obtidas.", cotacao=15, resolucao=R(
            "A árvore geradora mínima (pelo Prim): quais as ligações e a soma.",
            ["Árvore geradora mínima: liga TODOS os vértices, sem ciclos, com a menor soma de pesos. Tem V − 1 = 7 arestas.",
             "Prim: começa num vértice e, em cada passo, junta o vértice novo mais barato de ligar à árvore que já tens."],
            "O enunciado pede Prim explicitamente. Podes começar em qualquer vértice (a soma final é sempre a mesma); aqui começa-se em A.",
            ["Árvore {A}. Ligações a sair: AB 7, AG 26. Escolhe AB 7.",
             "Árvore {A, B}. Candidatas: BH 8, BD 14, BF 33, AG 26. Escolhe BH 8.",
             "Árvore {A, B, H}. Candidatas: GH 14, BD 14, CH 21, AG 26, BF 33. Empate a 14: escolhe BD (podias escolher GH; dá o mesmo total). Escreve que há empate.",
             "Árvore {A, B, H, D}. Candidatas: DE 10, GH 14, CH 21… Escolhe DE 10.",
             "Árvore {A, B, H, D, E}. Candidatas: CE 12, FE 12, GE 14, GH 14… Empate a 12: escolhe CE.",
             "Juntam-se FE 12 e depois GC 13 (menor ligação a G).",
             "7 arestas para 8 vértices ✓. Soma: 7 + 8 + 14 + 10 + 12 + 12 + 13 = 76."],
            "Algoritmo de Prim com início em A:\n" + ptR + svg(VR, posR, list(WR), weights=WR, highlight=[(a, b) for a, b, _ in stR], w=360, h=260) +
            "Ligações: {A,B}, {B,H}, {B,D}, {D,E}, {E,C}, {E,F}, {C,G}. Distância mínima: 76.\n(No 3º passo há empate entre {B,D} e {H,G}, ambos com 14; escolhendo {H,G} obtém-se outra árvore com o mesmo total 76.)"))]))
    # ---- Q5 planaridade
    V5 = list("ABCDEFGH")
    E5 = [norm_edge(a, b, V5) for a, b in ["AH", "AF", "AD", "HF", "HD", "HE", "HC", "GF", "GD", "GB", "FB", "FC", "DE", "EB", "BC"]]
    C5 = ["A", "H", "C", "B", "E", "D", "G", "F", "A"]
    adj5 = adj_from_edges(V5, E5)
    assert all(b in adj5[a] for a, b in zip(C5, C5[1:]))
    ok5, txt5 = metodo_ciclico(V5, E5, C5)
    assert ok5
    out.append(dict(id="r-diu26-5", grupo=G3, tipo="aberta", tema="Planaridade", fonte=FD,
        enunciado="A figura mostra uma representação de um grafo planar (arestas: AH, AF (arco), AD, HF (arco), HD, HE, HC, GF, GD, GB, FB, FC, DE, EB, BC; H e G não estão ligados).",
        imagem="/estudo/img/md/diu26-p5.jpg", alineas=[
        dict(enunciado="Utilize o método cíclico para encontrar uma representação planar do grafo.", cotacao=17.5, resolucao=R(
            "Redesenhar o grafo sem cruzamentos usando o método cíclico.",
            ["Representação planar: desenho sem arestas a cruzar.",
             "Ciclo hamiltoniano: volta por todos os vértices; vai ser desenhado como um polígono.",
             "Cordas (L): arestas que não estão no ciclo. A: cordas desenhadas dentro; B: cordas desenhadas fora.",
             "Incompatíveis: duas cordas cujas pontas alternam no ciclo (a, c, b, d); se ficarem do mesmo lado, cruzam-se."],
            "O método cíclico (TG_3): (1) ciclo hamiltoniano; (2) lista das cordas; (3) pares incompatíveis; (4) distribuir por A e B sem pôr duas incompatíveis do mesmo lado; (5) desenhar.",
            ["Encontra um ciclo hamiltoniano: A→H→C→B→E→D→G→F→A (todas estas arestas existem).",
             "Escreve os 8 vértices nesta ordem à volta de um círculo.",
             "Cordas: as 15 − 8 = 7 arestas que sobram.",
             "Testa os pares: duas cordas são incompatíveis se as pontas alternam na ordem A, H, C, B, E, D, G, F.",
             "Põe a primeira em A, e cada incompatível com ela em B, e assim sucessivamente.",
             "Se tudo couber, desenha: polígono + cordas de A por dentro + cordas de B por fora (em curva)."],
            txt5)),
        dict(enunciado="Indique o maior grau das faces da sua representação planar.", cotacao=10, resolucao=R(
            "Das faces do desenho planar de 5.1, qual tem mais arestas à volta, e quantas.",
            ["Face: região fechada por arestas (incluindo a exterior).",
             "Grau de uma face: nº de arestas na sua fronteira."],
            "Contar as faces no desenho e confirmar com Euler: F = 2 − V + A, e Σ deg(faces) = 2A.",
            ["V = 8, A = 15 ⇒ F = 2 − 8 + 15 = 9 faces.",
             "Percorre cada face no desenho: [A,F,H] 3, [A,H,D] 3, [H,F,C] 3, [H,E,D] 3, [F,G,B] 3, [F,B,C] 3, [A,D,G,F] 4, [H,C,B,E] 4, [D,E,B,G] 4.",
             "Confirma: 6 × 3 + 3 × 4 = 30 = 2 × 15 ✓",
             "O maior grau é 4. (Este grafo é 3-conexo, por isso qualquer representação planar tem estas mesmas faces.)"],
            "V − A + F = 2 ⇒ F = 2 − 8 + 15 = 9 faces: [A,F,H], [A,H,D], [H,F,C], [H,E,D], [F,G,B], [F,B,C] de grau 3 e [A,D,G,F], [H,C,B,E], [D,E,B,G] de grau 4.\n"
            "Confirmação: Σ deg(fi) = 6 × 3 + 3 × 4 = 30 = 2A.\nO maior grau das faces é 4."))]))
    # ---- Q6 Dijkstra
    V6 = list("ABCDEFGHI")
    W6 = {("A", "C"): 6, ("A", "B"): 5, ("B", "C"): 8, ("B", "F"): 9, ("B", "D"): 3, ("C", "E"): 1, ("C", "F"): 10, ("E", "G"): 7, ("E", "F"): 1,
          ("E", "H"): 8, ("F", "H"): 5, ("D", "F"): 6, ("D", "H"): 4, ("G", "H"): 7, ("G", "I"): 11, ("H", "I"): 7}
    p6, c6, t6 = dijkstra_html(V6, W6, "A", "I", True)
    assert c6 == 19 and p6 == list("ABDHI")
    out.append(dict(id="r-diu26-6", grupo=G4, tipo="aberta", tema="Redes", fonte=FD,
        enunciado="Utilize o algoritmo de Dijkstra para determinar o caminho mais curto entre os vértices A e I. Apresente esse caminho e o respetivo custo.\n"
                  "Arcos (lidos da foto; confirma A→B, C→E, E→H e D→H na tua folha): A→C 6, A→B 5, B→C 8, B→F 9, B→D 3, C→E 1, C→F 10, E→G 7, E→F 1, E→H 8, F→H 5, D→F 6, D→H 4, G→H 7, G→I 11, H→I 7.",
        imagem="/estudo/img/md/diu26-d6.jpg", alineas=[
        dict(enunciado="Caminho mais curto de A para I e custo.", cotacao=20, resolucao=R(
            "O caminho de menor custo de A até I, com as iterações do Dijkstra.",
            ["Rede orientada: só se anda no sentido das setas.",
             "Etiqueta: custo (antecessor), a menor distância conhecida até esse vértice.",
             "Temporária: ainda pode baixar. Permanente (✓): já é a mínima."],
            "Caminho mais curto entre dois vértices ⇒ Dijkstra. Em cada iteração, a menor etiqueta temporária fica permanente e, a partir dela, tenta-se baixar as etiquetas dos vértices para onde há seta.",
            ["A = 0 ✓. Setas de A: B 5 (A), C 6 (A).",
             "B 5 ✓. De B: C 5+8 = 13 > 6 (fica 6); D 5+3 = 8 (B); F 5+9 = 14 (B).",
             "C 6 ✓. De C: E 6+1 = 7 (C); F 6+10 = 16 > 14 (fica).",
             "E 7 ✓. De E: F 7+1 = 8 < 14 ⇒ 8 (E); G 7+7 = 14 (E); H 7+8 = 15 (E).",
             "D 8 ✓ (empate com F 8, escolhe um). De D: F 8+6 = 14 > 8 (fica); H 8+4 = 12 < 15 ⇒ 12 (D).",
             "F 8 ✓. De F: H 8+5 = 13 > 12 (fica 12).",
             "H 12 ✓. De H: I 12+7 = 19 (H).",
             "G 14 ✓. De G: I 14+11 = 25 > 19 (fica). I 19 ✓: chegou ao destino.",
             "Volta pelos antecessores: I ← H ← D ← B ← A."],
            "Algoritmo de Dijkstra (etiquetas custo (antecessor); ✓ = etiqueta permanente):\n" + t6 +
            "Caminho mais curto: A → B → D → H → I, com custo 5 + 3 + 4 + 7 = 19."))]))
    return out

# ============================================================ ESCOLHA MÚLTIPLA
def mc(enun, opts, correta, expl, tema):
    return dict(grupo=MC, tipo="escolha", tema=tema, enunciado=enun, opcoes=opts, correta=correta, explicacao=expl)

def conceitos():
    q = [
        mc("Num grafo, o número de vértices de grau ímpar é sempre:", ["par", "ímpar", "igual ao nº de arestas", "zero"], 0, "Como $\\sum \\deg(v) = 2|E|$ é par, os graus ímpares têm de aparecer em número par.", "Graus"),
        mc("Um grafo tem graus 3, 3, 2, 2, 2. Quantas arestas tem?", ["5", "6", "12", "4"], 1, "$|E| = \\frac{\\sum \\deg}{2} = \\frac{12}{2} = 6$.", "Graus"),
        mc("Quantas arestas tem $K_6$?", ["12", "15", "30", "36"], 1, "$K_n$ tem $\\frac{n(n-1)}{2} = \\frac{6\\cdot5}{2} = 15$.", "Completos"),
        mc("Quantas arestas tem $K_{3,4}$?", ["7", "12", "21", "6"], 1, "$K_{m,n}$ tem $m \\cdot n = 12$ arestas.", "Bipartidos"),
        mc("Um grafo é bipartido se e só se:", ["não tem ciclos de comprimento ímpar", "é conexo", "todos os graus são pares", "não tem ciclos"], 0, "Caracterização dos bipartidos: não existem ciclos ímpares.", "Bipartidos"),
        mc("$K_3$ (triângulo) é bipartido?", ["Não, tem um ciclo de comprimento 3", "Sim", "Só se for conexo", "Depende da orientação"], 0, "O triângulo é um ciclo ímpar.", "Bipartidos"),
        mc("O subgrafo de G gerado por V' contém:", ["os vértices de V' e todas as arestas de G com as duas extremidades em V'", "todos os vértices de G e as arestas de V'", "só os vértices de V' sem arestas", "as arestas incidentes a V'"], 0, "Definição de subgrafo gerado por um conjunto de vértices.", "Subgrafos"),
        mc("O grafo parcial de G gerado por E' contém:", ["todos os vértices de G e só as arestas de E'", "só os vértices extremos de E'", "todas as arestas de G", "os vértices de E' e todas as arestas entre eles"], 0, "Grafo parcial: G' = (V, E'), mantém V.", "Subgrafos"),
        mc("Uma cadeia elementar:", ["não passa duas vezes pelo mesmo vértice", "não passa duas vezes pela mesma aresta mas pode repetir vértices", "é sempre fechada", "passa por todas as arestas"], 0, "Elementar ⇒ não repete vértices. Simples ⇒ não repete arestas.", "Cadeias"),
        mc("Uma cadeia simples:", ["não repete arestas", "não repete vértices", "é fechada", "tem comprimento 1"], 0, "Simples = sem arestas repetidas (pode repetir vértices).", "Cadeias"),
        mc("Um ciclo é:", ["uma cadeia simples fechada", "uma cadeia qualquer", "um caminho num digrafo", "uma cadeia aberta"], 0, "Definição dos slides: ciclo = cadeia simples fechada.", "Cadeias"),
        mc("Num digrafo, um circuito é:", ["um caminho simples fechado", "uma cadeia fechada", "um caminho elementar aberto", "um arco"], 0, "Nos digrafos fala-se de caminhos; circuito = caminho simples fechado.", "Digrafos"),
        mc("Um grafo conexo tem ciclo euleriano se e só se:", ["todos os vértices têm grau par", "tem exatamente 2 vértices de grau ímpar", "todos os graus são ≥ n/2", "é bipartido"], 0, "Teorema de Euler (2).", "Eulerianos"),
        mc("Um grafo conexo tem cadeia euleriana (não fechada) se e só se:", ["tem exatamente 2 vértices de grau ímpar", "todos os graus são pares", "não tem vértices de grau ímpar", "tem 4 vértices de grau ímpar"], 0, "Teorema de Euler (1): a cadeia começa num dos ímpares e acaba no outro.", "Eulerianos"),
        mc("Um grafo conexo tem 4 vértices de grau ímpar. Então:", ["não tem cadeia nem ciclo euleriano", "tem ciclo euleriano", "tem cadeia euleriana", "é hamiltoniano"], 0, "Só 0 (ciclo) ou 2 (cadeia) vértices ímpares permitem.", "Eulerianos"),
        mc("Um digrafo conexo tem circuito euleriano se e só se:", ["$\\deg^+(v) = \\deg^-(v)$ para todo o v", "todos os graus são pares", "é fortemente conexo e simples", "$\\deg^+(v) > \\deg^-(v)$ num vértice"], 0, "Condição dos digrafos.", "Eulerianos"),
        mc("Num digrafo conexo com caminho euleriano de $v_0$ para $v_1$:", ["$\\deg^+(v_0) = \\deg^-(v_0) + 1$ e $\\deg^-(v_1) = \\deg^+(v_1) + 1$", "$\\deg^+(v_0) = \\deg^-(v_0)$", "$v_0$ e $v_1$ têm grau par", "$\\deg^-(v_0) = \\deg^+(v_0) + 1$"], 0, "O início tem um arco a sair a mais, o fim um a entrar a mais.", "Eulerianos"),
        mc("Teorema de Dirac: G simples, conexo, n ≥ 3. Se ... então G tem ciclo hamiltoniano.", ["$\\deg(v) \\ge n/2$ para todo o v", "$\\deg(u) + \\deg(v) \\ge n$ para u, v adjacentes", "todos os graus são pares", "$m \\le 3n - 6$"], 0, "Dirac (1952).", "Hamiltonianos"),
        mc("Teorema de Ore: a condição $\\deg(u) + \\deg(v) \\ge n$ é exigida para:", ["quaisquer u, v NÃO adjacentes", "quaisquer u, v adjacentes", "todos os pares", "os vértices de grau ímpar"], 0, "Ore (1961): pares não adjacentes.", "Hamiltonianos"),
        mc("Um grafo não cumpre Dirac. Pode-se concluir que:", ["nada; Dirac é condição suficiente, não necessária", "não é hamiltoniano", "é euleriano", "não é planar"], 0, "Erro clássico no teste: falhar a condição não prova que não é hamiltoniano.", "Hamiltonianos"),
        mc("Regra 1 da procura de ciclos hamiltonianos: se v tem grau 2...", ["as duas arestas de v têm de estar no ciclo", "v pode ser ignorado", "nenhuma aresta de v entra no ciclo", "o grafo não é hamiltoniano"], 0, "Para entrar e sair de v só há aquelas duas arestas.", "Hamiltonianos"),
        mc("Regra 3: se duas arestas incidentes em v já estão no ciclo, então:", ["as restantes arestas de v podem ser apagadas", "acrescenta-se mais uma", "o ciclo está completo", "v tem grau 2"], 0, "Num ciclo cada vértice usa exatamente 2 arestas.", "Hamiltonianos"),
        mc("Fórmula de Euler (grafo planar conexo):", ["$n - m + f = 2$", "$n + m - f = 2$", "$m = 3n - 6$", "$n - m = f$"], 0, "n vértices, m arestas, f faces (incluindo a exterior).", "Planares"),
        mc("A soma dos graus das faces de um grafo planar é igual a:", ["2m", "m", "2n", "f"], 0, "Cada aresta é contada duas vezes (uma por cada lado).", "Planares"),
        mc("Se G é simples, conexo, n ≥ 3 e $m > 3n - 6$, então:", ["G não é planar", "G é planar", "G é bipartido", "nada se conclui"], 0, "Corolário 4'.", "Planares"),
        mc("G simples, conexo, 7 vértices e 14 arestas. Pelo corolário de Euler:", ["nada se conclui (14 ≤ 15)", "não é planar", "é planar", "é completo"], 0, "$3n - 6 = 15$ e $14 \\le 15$: o corolário só serve quando $m > 3n-6$.", "Planares"),
        mc("$K_5$ não é planar porque:", ["$m = 10 > 3\\cdot5 - 6 = 9$", "não tem ciclo hamiltoniano", "é bipartido", "tem vértices de grau ímpar"], 0, "Corolário com n = 5.", "Planares"),
        mc("$K_{3,3}$ não é planar porque:", ["não tem triângulos e $9 > 2\\cdot6 - 4 = 8$", "$9 > 3\\cdot6 - 6$", "tem grau 3", "não é conexo"], 0, "Lema 5' para grafos sem triângulos.", "Planares"),
        mc("No método cíclico, duas cordas são incompatíveis quando:", ["as suas extremidades alternam ao longo do ciclo", "partilham um vértice", "têm o mesmo peso", "são paralelas"], 0, "Se alternam, cruzam-se do mesmo lado do ciclo.", "Planares"),
        mc("No método cíclico, o grafo é planar se:", ["todas as cordas couberem em A (dentro) ou B (fora) sem conflitos", "o ciclo for euleriano", "L tiver mais de 3 arestas", "houver um triângulo de incompatibilidades"], 0, "L fica vazio ⇒ planar. Três cordas mutuamente incompatíveis ⇒ não planar.", "Planares"),
        mc("Um grafo planar conexo tem 12 vértices e 20 arestas. Quantas faces?", ["10", "8", "30", "6"], 0, "$f = 2 - n + m = 2 - 12 + 20 = 10$.", "Planares"),
        mc("$\\Gamma_v$ (fecho transitivo direto) é:", ["o conjunto dos vértices atingíveis a partir de v", "o conjunto dos vizinhos de v", "os vértices que chegam a v", "os sucessores imediatos de v"], 0, "Por caminhos de qualquer comprimento.", "Fecho transitivo"),
        mc("$\\Gamma^{-1}_v$ é:", ["o conjunto dos vértices a partir dos quais se atinge v", "os antecessores imediatos de v", "os vértices não ligados a v", "o complementar de $\\Gamma_v$"], 0, "Fecho transitivo inverso.", "Fecho transitivo"),
        mc("A componente fortemente conexa que contém v é:", ["$\\Gamma_v \\cap \\Gamma^{-1}_v$", "$\\Gamma_v \\cup \\Gamma^{-1}_v$", "$\\Gamma^+(v)$", "$\\Gamma_v \\setminus \\Gamma^{-1}_v$"], 0, "Vértices que v atinge E que atingem v.", "Fecho transitivo"),
        mc("Na matriz booleana de um digrafo, $\\deg^+(v_i)$ é:", ["a soma da linha i", "a soma da coluna i", "o elemento $b_{ii}$", "o total de 1s"], 0, "Linha = arcos que saem; coluna = arcos que entram.", "Matrizes"),
        mc("Numa matriz de adjacência de um grafo, um lacete em $v_i$ conta no grau:", ["2 vezes ($\\deg(v_i) = 2a_{ii} + \\sum_{j\\ne i} a_{ij}$)", "1 vez", "0 vezes", "depende"], 0, "Fórmula dos slides.", "Matrizes"),
        mc("Uma árvore com n vértices tem:", ["n − 1 arestas", "n arestas", "n + 1 arestas", "2n − 4 arestas"], 0, "Árvore = conexo sem ciclos ⇒ m = n − 1.", "Redes"),
        mc("O algoritmo de Prim:", ["junta à árvore, em cada passo, o vértice ligado pela aresta de menor peso", "ordena todas as arestas e aceita as que não formam ciclo", "calcula o caminho mais curto entre dois vértices", "procura ciclos eulerianos"], 0, "Prim cresce uma árvore; Kruskal ordena as arestas.", "Redes"),
        mc("O algoritmo de Kruskal rejeita uma aresta quando:", ["forma um ciclo com as já escolhidas", "tem peso maior que a anterior", "liga um vértice de grau 1", "já há n arestas"], 0, "Pára quando tem n − 1 arestas.", "Redes"),
        mc("Para 'ligar todas as cidades com o menor custo total' usa-se:", ["árvore geradora mínima (Prim/Kruskal)", "Dijkstra", "ciclo euleriano", "fecho transitivo"], 0, "Extensão mínima ≠ percurso mínimo.", "Redes"),
        mc("Para 'o caminho mais curto de A até B' usa-se:", ["Dijkstra", "Kruskal", "Prim", "método cíclico"], 0, "Problema de percurso mínimo.", "Redes"),
        mc("No algoritmo de Dijkstra, em cada iteração torna-se permanente:", ["a etiqueta temporária de menor valor", "a primeira por ordem alfabética", "a de maior valor", "todas as adjacentes"], 0, "Passo 3 do algoritmo.", "Redes"),
        mc("Uma rota que percorre todas as ruas uma única vez e volta ao início é um problema de:", ["ciclo euleriano", "ciclo hamiltoniano", "árvore geradora", "Dijkstra"], 0, "Todas as ARESTAS uma vez ⇒ Euler. Todos os VÉRTICES uma vez ⇒ Hamilton.", "Eulerianos"),
        mc("Visitar todas as localidades uma única vez e voltar ao início é um problema de:", ["ciclo hamiltoniano", "ciclo euleriano", "árvore geradora mínima", "planaridade"], 0, "Vértices ⇒ Hamilton.", "Hamiltonianos"),
    ]
    # numéricas geradas
    for _ in range(8):
        n = random.randint(5, 12)
        q.append(mc(f"Quantas arestas tem $K_{{{n}}}$?", sorted({str(n * (n - 1) // 2), str(n * (n - 1)), str(n * n), str(2 * n - 1)}, key=lambda x: random.random()),
                    None, f"$\\frac{{{n}({n}-1)}}{{2}} = {n * (n - 1) // 2}$.", "Completos"))
        q[-1]["correta"] = q[-1]["opcoes"].index(str(n * (n - 1) // 2))
    for _ in range(8):
        n = random.randint(5, 14); lim = 3 * n - 6
        q.append(mc(f"Um grafo simples planar com {n} vértices tem no máximo quantas arestas?", [str(lim), str(2 * n - 4), str(n * (n - 1) // 2), str(3 * n)], 0, f"$m \\le 3n - 6 = {lim}$.", "Planares"))
    for _ in range(8):
        m = random.randint(9, 40); f = random.randint(4, m - 3); n = 2 + m - f
        if n < 3: continue
        q.append(mc(f"Grafo planar conexo com {m} arestas e {f} faces. Quantos vértices?", [str(n), str(m - f), str(m + f - 2), str(n + 2)], 0, f"$n = 2 + m - f = 2 + {m} - {f} = {n}$.", "Planares"))
    for _ in range(6):
        k = random.choice([3, 5, 7]); n = random.choice([5, 7, 9, 11])
        q.append(mc(f"É possível um grafo com {n} vértices, todos de grau {k}?", ["Não: a soma dos graus seria ímpar", "Sim", "Só se for planar", "Só se for bipartido"], 0, f"$\\sum \\deg = {n}\\times{k} = {n * k}$, ímpar, mas tem de ser $2|E|$.", "Graus"))
    for _ in range(6):
        n = random.randint(6, 12); d = random.randint(2, n - 1)
        resp = "Sim" if d >= n / 2 else "Não se verifica"
        q.append(mc(f"G simples e conexo com {n} vértices e grau mínimo {d}. A condição de Dirac verifica-se?", ["Sim", "Não se verifica"], 0 if d >= n / 2 else 1,
                    f"É preciso $\\deg(v) \\ge n/2 = {n / 2:g}$. Grau mínimo {d} {'≥' if d >= n / 2 else '<'} {n / 2:g}.", "Hamiltonianos"))
    for i, x in enumerate(q):
        x["id"] = f"mc-{i}"
    return q

# ============================================================ MAIN
def main():
    perguntas = []
    perguntas += reais()
    for i in range(30): perguntas.append(ex_grupo1(i))
    for i in range(30): perguntas.append(ex_grupo2(i))
    for i in range(24): perguntas.append(ex_grupo3(i))
    for i in range(30): perguntas.append(ex_grupo4(i))
    import mc_md
    perguntas += mc_md.gerar(MC)
    # fichas de exercícios, arrumadas nos grupos do teste
    import gerar_md_fichas as gf
    para_grupo = {gf.T1: G1, gf.T2: G1, gf.T3: G3, gf.T4: G2, gf.T5: G4}
    fichas = gf.build()
    temas = {}
    for f in fichas:
        temas.setdefault(f["grupo"], []).append(f["id"])
        f["grupo"] = G2 if f["id"] in ("ex-2", "ex-17", "aula-2") else para_grupo[f["grupo"]]
    perguntas += fichas
    banco = dict(
        uc="MD", titulo="2º teste · Teoria de Grafos",
        descricao="Formato do teste do prof. Ricardo (2025/26). Os grafos e as resoluções são gerados e calculados automaticamente.",
        cabula="https://claude.ai/artifact/ShdbdPjQgkLmhrSpaJ9odP",
        estrutura=[dict(grupo=G1, n=1, cotacao=8), dict(grupo=G2, n=1, cotacao=4.5), dict(grupo=G3, n=1, cotacao=3.5), dict(grupo=G4, n=1, cotacao=4)],
        testesReais=[
            dict(titulo="🆕 Teste do diurno · 25/11/2026 (José Castro / Paula Cheira)", nota="Feito esta semana pelo diurno: o mais provável de se parecer com o teu.", ids=["r-diu26-1", "r-diu26-2", "r-diu26-3", "r-diu26-4", "r-diu26-5", "r-diu26-6"]),
            dict(titulo="Teste do Ricardo · 21/11/2025", nota="O mais parecido com o teu: faz este primeiro, com 1h30.", ids=["r-ric25-1", "r-ric25-2", "r-ric25-3", "r-ric25-4"]),
            dict(titulo="Teste da Anabela Silva · 04/12/2025 (2º teste, PL)", nota="Pede uma representação planar: treina redesenhar.", ids=["r-ana25-1", "r-ana25-2", "r-ana25-3", "r-ana25-4"]),
            dict(titulo="Teste da Teresa Abreu · 18/11/2025 (partes sem figura)", ids=["r-ter25-2", "r-ter25-3", "r-ter25-4"]),
            dict(titulo="Teste do José Castro · 28/11/2023 (partes sem figura)", ids=["r-jc23-3", "r-jc23-6"]),
        ],
        fichas=[dict(titulo=t, ids=temas[t]) for t in ("Conceitos e graus", "Euler e Hamilton", "Planares", "Matrizes e fecho", "Redes") if t in temas],
        perguntas=perguntas)
    import re
    def latex(t):
        t = t[1:-1]
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", t)
        for a, b in [("\\Rightarrow", "⇒"), ("\\Gamma", "Γ"), ("\\deg", "deg"), ("\\sum", "Σ"), ("\\le", "≤"), ("\\ge", "≥"), ("\\times", "×"), ("\\neq", "≠"),
                     ("\\cap", "∩"), ("\\cup", "∪"), ("\\emptyset", "∅"), ("\\notin", "∉"), ("\\leftrightarrow", "↔"), ("\\to", "→"),
                     ("\\neg", "¬"), ("\\land", "∧"), ("\\lor", "∨"), ("\\setminus", "\\"), ("\\{", "{"), ("\\}", "}"), ("\\,", " "), ("\\dots", "…"), ("\\mu", "μ")]:
            t = t.replace(a, b)
        t = re.sub(r"\\text\{([^{}]*)\}", r"\1", t)
        t = re.sub(r"\\mathcal\{([^{}]*)\}", r"\1", t)
        t = t.replace("^{-1}", "⁻¹").replace("^+", "⁺").replace("^-", "⁻").replace("^n", "ⁿ").replace("^3", "³").replace("^2", "²")
        t = re.sub(r"_\{([^{}]*)\}", r"\1", t)
        t = re.sub(r"_(\w)", r"\1", t)
        t = re.sub(r"\^\{([^{}]*)\}", r"^\1", t)
        return t.replace("{", "{").replace("\\", "")
    def limpa(x):
        if isinstance(x, str):
            partes = re.split(r"(\$[^$]*\$)", x)
            return "".join(latex(p) if p.startswith("$") and len(p) > 1 else p.replace("\\{", "{").replace("\\}", "}") for p in partes)
        if isinstance(x, list): return [limpa(y) for y in x]
        if isinstance(x, dict): return {k: limpa(v) for k, v in x.items()}
        return x
    banco = limpa(banco)
    with open(OUT, "w", encoding="utf8") as fh:
        json.dump(banco, fh, ensure_ascii=False, indent=1)
    print("ok", len(perguntas), "perguntas", os.path.getsize(OUT) // 1024, "KB")

if __name__ == "__main__":
    main()
