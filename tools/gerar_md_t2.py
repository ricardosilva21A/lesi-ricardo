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
    out.append(dict(id="r-ric25-1", grupo=G1, tipo="aberta", tema="Grafo não orientado", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o seguinte grafo $G_1$:", imagem="/estudo/img/md/ric25-g1.png", alineas=[
        dict(enunciado="Ilustre a fórmula de Euler para grafos planares.", cotacao=15,
             resolucao=("$G_1$ está desenhado sem cruzamentos (planar) e é conexo.\nn = 15 vértices, m = 20 arestas.\nFaces: "
                        "$f_1$ = [C,Q,P,D] (4), $f_2$ = [P,O,N,D] (4), $f_3$ = [C,D,F,E] (4), $f_4$ = [D,N,G,K,H,F] (6), $f_5$ = [G,I,J,K] (4), $f_6$ = [G,L,M,I] (4) e a face exterior $f_7$ (14) → f = 7.\n"
                        "$n - m + f = 15 - 20 + 7 = 2$ ✓   ( $\\sum \\deg(f_i) = 4+4+4+6+4+4+14 = 40 = 2m$ ✓ )")),
        dict(enunciado="Indique $\\deg(F_1)$, sendo $F_1$ o subgrafo de $G_1$ gerado por $\\{F, D, N, G, K, H\\}$.", cotacao=10,
             resolucao=("Arestas de $G_1$ com as duas extremidades no conjunto: {F,D}, {D,N}, {N,G}, {G,K}, {K,H}, {H,F}.\n"
                        "$F_1$ é o ciclo [F,D,N,G,K,H,F]: cada vértice tem grau 2 em $F_1$ (soma dos graus = 12 = 2 × 6 arestas).\n"
                        "Este ciclo é a fronteira da face $f_4$, que tem grau 6.")),
        dict(enunciado="Justifique que o grafo não é completo e investigue, justificando, se o grafo é bipartido.", cotacao=15,
             resolucao=(f"Não é completo: $K_{{15}}$ tem $\\frac{{15 \\times 14}}{{2}} = 105$ arestas e $G_1$ só tem 20 (por exemplo C e H não são adjacentes).\n"
                        f"É bipartido: $V_1 = {S(P1, V)}$ e $V_2 = {S(P2, V)}$; todas as arestas ligam $V_1$ a $V_2$. "
                        "(Confirma-se também porque todas as faces têm grau par, ou seja, não há ciclos ímpares.)")),
        dict(enunciado="Ilustre para o grafo a aplicação do teorema de Dirac.", cotacao=15,
             resolucao=("Dirac: G simples, conexo, n ≥ 3, $\\deg(v) \\ge n/2$ ∀v ⇒ hamiltoniano.\nn = 15, n/2 = 7,5. Mas, por exemplo, deg(E) = 2 < 7,5 (o grau máximo é 4).\n"
                        "A condição falha e, sendo Dirac uma condição suficiente, não se pode concluir se $G_1$ é ou não hamiltoniano.\n"
                        f"(Extra: na verdade $G_1$ não é hamiltoniano. É bipartido com partes de tamanhos {len(P1)} e {len(P2)}, e um ciclo hamiltoniano alterna entre as partes, por isso exigiria partes iguais.)")),
        dict(enunciado="Seja $\\mu = [D, F, E, C, Q, P, O, N, G, L, M, I, J, K, H]$. O que pode concluir deste resultado à luz da Teoria de Grafos?", cotacao=15,
             resolucao=("Todos os pares consecutivos são arestas de $G_1$, não há vértices repetidos e μ passa pelos 15 vértices: μ é uma CADEIA HAMILTONIANA.\n"
                        "Não é um ciclo hamiltoniano porque H e D não são adjacentes (não dá para fechar). Logo $G_1$ tem cadeia hamiltoniana (é semi-hamiltoniano).")),
        dict(enunciado="A eulerização consiste em transformar um grafo não euleriano num euleriano duplicando arestas já existentes. Indique o menor número de arestas necessárias e quais.", cotacao=10,
             resolucao=("Vértices de grau ímpar: " + ", ".join(f"{v}({deg[v]})" for v in odd) + " → 6 vértices.\n"
                        "Nenhum par de vértices ímpares é adjacente, por isso cada emparelhamento custa pelo menos 2 arestas: mínimo 3 × 2 = 6 arestas.\n"
                        "Uma solução: " + "; ".join(f"{a}–{b}" for a, b in pares) + f" duplicando {edges_txt(dup)}.\n"
                        "(Outras escolhas com 6 arestas também estão certas, por exemplo C–E–F, P–O–N, I–J–K.)"))]))
    # ---- Ricardo 2025/26 G2
    Vd = list("ABCDEF"); A = [("A", "B"), ("B", "E"), ("E", "C"), ("C", "A"), ("A", "D"), ("D", "C"), ("C", "F")]
    o, i = digraph_maps(Vd, A)
    assert reach(o, "C") == set(Vd) and reach(i, "C") == set("ABCDE")
    out.append(dict(id="r-ric25-2", grupo=G2, tipo="aberta", tema="Digrafo", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o digrafo:", imagem="/estudo/img/md/ric25-d2.png", alineas=[
        dict(enunciado="Investigue se o digrafo é fortemente conexo. Caso não seja, indique todas as componentes conexas.", cotacao=10,
             resolucao=("Não é fortemente conexo: F não tem arcos a sair ($\\deg^+(F) = 0$), logo de F não se chega a nenhum vértice.\n"
                        "$\\Gamma_A \\cap \\Gamma^{-1}_A = \\{A,B,C,D,E,F\\} \\cap \\{A,B,C,D,E\\} = \\{A,B,C,D,E\\}$\n"
                        "Componentes fortemente conexas: {A, B, C, D, E} e {F}. (O digrafo é conexo: o grafo subjacente é conexo.)")),
        dict(enunciado="Apresente um circuito não elementar.", cotacao=10,
             resolucao=("Circuitos elementares: [A,B,E,C,A] e [A,D,C,A]. Juntando os dois pelo vértice comum: [A,B,E,C,A,D,C,A] passa duas vezes por A e por C (não elementar).\n"
                        "⚠️ Atenção: este percurso usa o arco (C,A) duas vezes. Com a definição rigorosa (circuito = caminho simples fechado) este digrafo não tem circuito não elementar, porque (C,A) é o único arco que entra em A. "
                        "Na prova, apresenta o exemplo e, se tiveres tempo, comenta isto: mostra que dominas a definição.")),
        dict(enunciado="Justifique que o digrafo tem um caminho euleriano e indique-o.", cotacao=10,
             resolucao=(table(["v", "deg⁺", "deg⁻"], [["A", 2, 1], ["B", 1, 1], ["C", 2, 2], ["D", 1, 1], ["E", 1, 1], ["F", 0, 1]]) +
                        "Conexo; $\\deg^+(A) = \\deg^-(A) + 1$, $\\deg^-(F) = \\deg^+(F) + 1$ e nos outros $\\deg^+ = \\deg^-$ ⇒ caminho euleriano de A para F:\n[A, B, E, C, A, D, C, F]")),
        dict(enunciado="Determine $\\Gamma_C$ e $\\Gamma^{-1}_C$.", cotacao=15,
             resolucao=("$\\Gamma_C$ (atingíveis a partir de C): C→A, C→F, A→B, A→D, B→E ⇒ $\\Gamma_C = \\{A, B, C, D, E, F\\}$\n"
                        "$\\Gamma^{-1}_C$ (de onde se chega a C): D→C, E→C, B→E, A→B ⇒ $\\Gamma^{-1}_C = \\{A, B, C, D, E\\}$"))]))
    # ---- Ricardo 2025/26 G3
    V3 = list("123456"); E3 = [norm_edge(a, b, V3) for a, b in ["15", "14", "13", "25", "24", "23", "63", "65", "64", "35"]]
    adj3 = adj_from_edges(V3, E3)
    C3 = ["1", "3", "2", "4", "6", "5", "1"]
    assert all(b in adj3[a] for a, b in zip(C3, C3[1:]))
    out.append(dict(id="r-ric25-3", grupo=G3, tipo="aberta", tema="Planaridade", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere o seguinte grafo (numerei os vértices no sentido horário a partir do de cima à esquerda: 1 cima-esq., 2 cima-dir., 3 direita, 4 baixo-dir., 5 baixo-esq., 6 esquerda):",
        imagem="/estudo/img/md/ric25-g3.png", alineas=[
        dict(enunciado="Justifique que o grafo não é planar.", cotacao=15,
             resolucao=("n = 6, m = 10. $3n - 6 = 12$ e 10 ≤ 12, por isso o corolário não decide.\n"
                        "Mas com $V_1 = \\{1, 2, 6\\}$ e $V_2 = \\{3, 4, 5\\}$ existem as 9 arestas entre os dois conjuntos: G contém $K_{3,3}$ (só sobra a aresta {3,5}).\n"
                        "$K_{3,3}$ não tem triângulos e tem $9 > 2n - 4 = 8$ arestas ⇒ não é planar. Logo G também não é.")),
        dict(enunciado="Aplique o método cíclico para comprovar que o grafo não é planar.", cotacao=20,
             resolucao=metodo_ciclico(V3, E3, C3)[1]),
    ]))
    assert metodo_ciclico(V3, E3, C3)[0] is False
    # ---- Ricardo 2025/26 G4
    V4 = ["Aveiro", "Braga", "Coimbra", "Porto", "Viana", "Vila Real", "Viseu"]
    W4 = {("Aveiro", "Coimbra"): 58, ("Aveiro", "Porto"): 68, ("Aveiro", "Vila Real"): 184, ("Aveiro", "Viseu"): 95, ("Braga", "Porto"): 53,
          ("Braga", "Viana"): 48, ("Braga", "Vila Real"): 106, ("Coimbra", "Porto"): 117, ("Coimbra", "Viseu"): 96, ("Porto", "Viana"): 71,
          ("Porto", "Vila Real"): 116, ("Porto", "Viseu"): 133, ("Viana", "Vila Real"): 154, ("Vila Real", "Viseu"): 110}
    steps, total, ptab = prim_html(V4, W4, "Aveiro")
    path, cost, dtab = dijkstra_html(V4, W4, "Coimbra", "Viana", False)
    out.append(dict(id="r-ric25-4", grupo=G4, tipo="aberta", tema="Redes", fonte="Teste real · Ricardo Gonçalves · 21/11/2025",
        enunciado="Considere as seguintes distâncias, em km, entre algumas cidades portuguesas (em branco: sem ligação):\n" + matrix_table(V4, W4, False),
        alineas=[
        dict(enunciado="A empresa TIR pretende um percurso que permita a um camião recolher bens em todas as cidades, pelas ligações assinaladas. Por meio de um algoritmo adequado, represente e determine a menor distância possível.", cotacao=15,
             resolucao=("É um problema de árvore geradora mínima (ligar todas as cidades com a menor soma). Prim a partir de Aveiro:\n" + ptab +
                        svg(V4, {"Aveiro": (.25, .55), "Braga": (.5, .1), "Coimbra": (.2, .95), "Porto": (.3, .3), "Viana": (.15, .05), "Vila Real": (.85, .3), "Viseu": (.75, .75)},
                            list(W4), weights=W4, highlight=[(a, b) for a, b, _ in steps], w=360, h=280) + f"Total: {total} km")),
        dict(enunciado="Um funcionário está em Coimbra e tem de ir a Viana do Castelo. Determine, por um algoritmo adequado, o percurso mais curto e a distância.", cotacao=25,
             resolucao=("Percurso mínimo ⇒ algoritmo de Dijkstra. Etiquetas custo (antecessor):\n" + dtab + f"Percurso: {' → '.join(path)}, {cost} km"))]))
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
    banco = dict(
        uc="MD", titulo="2º teste · Teoria de Grafos",
        descricao="Formato do teste do prof. Ricardo (2025/26). Os grafos e as resoluções são gerados e calculados automaticamente.",
        cabula="https://claude.ai/artifact/ShdbdPjQgkLmhrSpaJ9odP",
        estrutura=[dict(grupo=G1, n=1, cotacao=8), dict(grupo=G2, n=1, cotacao=4.5), dict(grupo=G3, n=1, cotacao=3.5), dict(grupo=G4, n=1, cotacao=4)],
        testesReais=[
            dict(titulo="Teste do Ricardo · 21/11/2025", nota="O mais parecido com o teu: faz este primeiro, com 1h30.", ids=["r-ric25-1", "r-ric25-2", "r-ric25-3", "r-ric25-4"]),
            dict(titulo="Teste da Anabela Silva · 04/12/2025 (2º teste, PL)", nota="Pede uma representação planar: treina redesenhar.", ids=["r-ana25-1", "r-ana25-2", "r-ana25-3", "r-ana25-4"]),
            dict(titulo="Teste da Teresa Abreu · 18/11/2025 (partes sem figura)", ids=["r-ter25-2", "r-ter25-3", "r-ter25-4"]),
            dict(titulo="Teste do José Castro · 28/11/2023 (partes sem figura)", ids=["r-jc23-3", "r-jc23-6"]),
        ],
        perguntas=perguntas)
    import re
    def limpa(x):
        if isinstance(x, str):
            partes = re.split(r"(\$[^$]*\$)", x)  # fora de $...$ o KaTeX não atua
            return "".join(p if p.startswith("$") else p.replace("\\{", "{").replace("\\}", "}") for p in partes)
        if isinstance(x, list): return [limpa(y) for y in x]
        if isinstance(x, dict): return {k: limpa(v) for k, v in x.items()}
        return x
    banco = limpa(banco)
    with open(OUT, "w", encoding="utf8") as fh:
        json.dump(banco, fh, ensure_ascii=False, indent=1)
    print("ok", len(perguntas), "perguntas", os.path.getsize(OUT) // 1024, "KB")

if __name__ == "__main__":
    main()
