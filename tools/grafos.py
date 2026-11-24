"""Algoritmos e desenho de grafos usados pelo gerador do banco de MD (Teoria de Grafos).
Tudo determinístico e verificável: as resoluções do banco saem daqui."""
import itertools, math, random, heapq
from collections import deque

# ---------------------------------------------------------------- utilidades
def fmt_set(xs, order=None):
    xs = list(xs)
    if order:
        xs.sort(key=order.index)
    return "\\{" + ", ".join(map(str, xs)) + "\\}"

def adj_from_edges(V, E):
    adj = {v: set() for v in V}
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def norm_edge(u, v, order):
    return (u, v) if order.index(u) < order.index(v) else (v, u)

def connected(adj, nodes=None):
    nodes = set(adj) if nodes is None else set(nodes)
    if not nodes:
        return True
    s = next(iter(nodes)); seen = {s}; q = [s]
    while q:
        x = q.pop()
        for y in adj[x]:
            if y in nodes and y not in seen:
                seen.add(y); q.append(y)
    return seen == nodes

def bfs_dist(adj, s):
    d = {s: 0}; par = {s: None}; q = deque([s])
    while q:
        x = q.popleft()
        for y in sorted(adj[x], key=str):
            if y not in d:
                d[y] = d[x] + 1; par[y] = x; q.append(y)
    return d, par

def path_to(par, t):
    p = []
    while t is not None:
        p.append(t); t = par[t]
    return p[::-1]

# ---------------------------------------------------------------- bipartido
def bipartite(adj, order):
    color = {}
    par = {}
    for s in order:
        if s in color:
            continue
        color[s] = 0; par[s] = None; q = deque([s])
        while q:
            x = q.popleft()
            for y in sorted(adj[x], key=order.index):
                if y not in color:
                    color[y] = 1 - color[x]; par[y] = x; q.append(y)
                elif color[y] == color[x]:
                    # ciclo ímpar: caminhos até ao antepassado comum
                    px = path_to(par, x); py = path_to(par, y)
                    i = 0
                    while i < min(len(px), len(py)) and px[i] == py[i]:
                        i += 1
                    cyc = px[i - 1:] + py[i:][::-1] + [px[i - 1]]
                    return False, cyc
    A = [v for v in order if color[v] == 0]; B = [v for v in order if color[v] == 1]
    return True, (A, B)

# ---------------------------------------------------------------- hamiltonianos
def ham_cycle(adj, order, need_cycle=True, start=None):
    n = len(order)
    starts = [start] if start else (order[:1] if need_cycle else order)
    for s in starts:
        path = [s]; used = {s}
        def rec():
            if len(path) == n:
                return (not need_cycle) or (s in adj[path[-1]])
            for y in sorted(adj[path[-1]], key=order.index):
                if y not in used:
                    used.add(y); path.append(y)
                    if rec():
                        return True
                    used.discard(y); path.pop()
            return False
        if rec():
            return path + ([s] if need_cycle else [])
    return None

# ---------------------------------------------------------------- eulerianos
def odd_vertices(adj, order):
    return [v for v in order if len(adj[v]) % 2 == 1]

def hierholzer(edges, start, directed=False):
    """edges: lista de pares (multiconjunto). devolve sequência de vértices."""
    from collections import defaultdict
    g = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        g[u].append((v, i))
        if not directed:
            g[v].append((u, i))
    for k in g:
        g[k].sort(key=lambda t: str(t[0]), reverse=True)
    used = set(); stack = [start]; out = []
    while stack:
        x = stack[-1]
        while g[x] and g[x][-1][1] in used:
            g[x].pop()
        if g[x]:
            y, i = g[x].pop(); used.add(i); stack.append(y)
        else:
            out.append(stack.pop())
    return out[::-1]

def eulerize(adj, order):
    odd = odd_vertices(adj, order)
    dist = {}; par = {}
    for v in odd:
        dist[v], par[v] = bfs_dist(adj, v)
    best = [math.inf, None]
    def rec(rest, acc, pairs):
        if acc >= best[0]:
            return
        if not rest:
            best[0] = acc; best[1] = list(pairs); return
        a = rest[0]
        for b in rest[1:]:
            r2 = [x for x in rest if x not in (a, b)]
            pairs.append((a, b)); rec(r2, acc + dist[a][b], pairs); pairs.pop()
    rec(odd, 0, [])
    dup = []
    for a, b in best[1]:
        p = path_to(par[a], b)
        for x, y in zip(p, p[1:]):
            dup.append(norm_edge(x, y, order))
    return odd, best[1], dup

# ---------------------------------------------------------------- digrafos
def reach(out, v):
    seen = {v}; q = [v]
    while q:
        x = q.pop()
        for y in out[x]:
            if y not in seen:
                seen.add(y); q.append(y)
    return seen

def digraph_maps(V, A):
    out = {v: set() for v in V}; inn = {v: set() for v in V}
    for u, v in A:
        out[u].add(v); inn[v].add(u)
    return out, inn

def scc(V, A):
    out, inn = digraph_maps(V, A)
    comps = []; done = set()
    for v in V:
        if v in done:
            continue
        c = reach(out, v) & reach(inn, v)
        comps.append(sorted(c, key=V.index)); done |= c
    return comps

def non_elementary_circuit(V, A):
    """circuito (caminho simples fechado, sem repetir arcos) que repete um vértice."""
    out, _ = digraph_maps(V, A)
    best = None
    for s in V:
        path = [s]; used = set()
        def rec():
            nonlocal best
            x = path[-1]
            if len(path) > 1 and x == s:
                inner = path[1:-1]
                if len(set(inner)) < len(inner) or s in inner:
                    if best is None or len(path) < len(best):
                        best = list(path)
                    return
            if len(path) > 12:
                return
            for y in sorted(out[x], key=V.index):
                if (x, y) not in used:
                    used.add((x, y)); path.append(y); rec(); path.pop(); used.discard((x, y))
        rec()
    return best

def elementary_circuit(V, A):
    out, _ = digraph_maps(V, A)
    for s in V:
        st = [(s, [s])]
        while st:
            x, p = st.pop()
            for y in out[x]:
                if y == s and len(p) >= 2:
                    return p + [s]
                if y not in p and V.index(y) > V.index(s):
                    st.append((y, p + [y]))
    return None

# ---------------------------------------------------------------- planaridade
def faces_from_drawing(pos, adj):
    """faces de um desenho plano com arestas retas. devolve lista de faces (listas de vértices)
    e o índice da face exterior."""
    ang = {}
    for v in adj:
        ang[v] = sorted(adj[v], key=lambda w: math.atan2(pos[w][1] - pos[v][1], pos[w][0] - pos[v][0]))
    used = set(); faces = []
    for u in adj:
        for v in adj[u]:
            if (u, v) in used:
                continue
            f = []; a, b = u, v
            while (a, b) not in used:
                used.add((a, b)); f.append(a)
                lst = ang[b]; i = lst.index(a)
                c = lst[(i - 1) % len(lst)]  # próximo no sentido horário
                a, b = b, c
            faces.append(f)
    def area(f):
        return sum(pos[f[i]][0] * pos[f[(i + 1) % len(f)]][1] - pos[f[(i + 1) % len(f)]][0] * pos[f[i]][1] for i in range(len(f))) / 2
    # com y para baixo (svg) a orientação inverte-se; a exterior é a de maior |área| com sinal oposto
    areas = [area(f) for f in faces]
    sign_inner = 1 if sum(1 for a in areas if a > 0) > sum(1 for a in areas if a < 0) else -1
    ext = max(range(len(faces)), key=lambda i: (-(areas[i] * sign_inner), abs(areas[i])))
    return faces, ext

def segments_cross(p1, p2, p3, p4):
    def o(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if len({p1, p2, p3, p4}) < 4:
        return False
    return (o(p1, p2, p3) * o(p1, p2, p4) < 0) and (o(p3, p4, p1) * o(p3, p4, p2) < 0)

def chord_conflicts(cycle, chords):
    pos = {v: i for i, v in enumerate(cycle)}
    def inter(c1, c2):
        a, b = sorted((pos[c1[0]], pos[c1[1]])); c, d = pos[c2[0]], pos[c2[1]]
        if len({a, b, c, d}) < 4:
            return False
        return (a < c < b) != (a < d < b)
    conf = {c: set() for c in chords}
    for c1, c2 in itertools.combinations(chords, 2):
        if inter(c1, c2):
            conf[c1].add(c2); conf[c2].add(c1)
    return conf

def split_chords(chords, conf):
    """2-coloração do grafo de incompatibilidades: devolve (True, A, B) ou (False, ciclo ímpar)."""
    color = {}; par = {}
    for s in chords:
        if s in color:
            continue
        color[s] = 0; par[s] = None; q = deque([s])
        while q:
            x = q.popleft()
            for y in sorted(conf[x], key=chords.index):
                if y not in color:
                    color[y] = 1 - color[x]; par[y] = x; q.append(y)
                elif color[y] == color[x]:
                    px = path_to(par, x); py = path_to(par, y)
                    i = 0
                    while i < min(len(px), len(py)) and px[i] == py[i]:
                        i += 1
                    return False, px[i - 1:] + py[i:][::-1]
    return True, ([c for c in chords if color[c] == 0], [c for c in chords if color[c] == 1])

def find_k33(adj, order):
    for six in itertools.combinations(order, 6):
        for P in itertools.combinations(six, 3):
            if six[0] not in P:
                continue
            Q = [v for v in six if v not in P]
            if all(q in adj[p] for p in P for q in Q):
                return list(P), Q
    return None

def find_k5(adj, order):
    for five in itertools.combinations(order, 5):
        if all(b in adj[a] for a, b in itertools.combinations(five, 2)):
            return list(five)
    return None

def has_triangle(adj):
    return any(adj[a] & adj[b] for a in adj for b in adj[a])

# ---------------------------------------------------------------- redes
def prim(V, W, start):
    """W: dict {(u,v): peso} não orientado (chaves normalizadas)."""
    def w(a, b):
        return W.get((a, b), W.get((b, a)))
    T = [start]; steps = []; total = 0
    while len(T) < len(V):
        cand = [(w(a, b), V.index(a), V.index(b), a, b) for a in T for b in V if b not in T and w(a, b) is not None]
        if not cand:
            return None
        c = min(cand); total += c[0]
        steps.append((c[3], c[4], c[0])); T.append(c[4])
    return steps, total

def kruskal(V, W):
    parent = {v: v for v in V}
    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    es = sorted(W.items(), key=lambda kv: (kv[1], V.index(kv[0][0]), V.index(kv[0][1])))
    log = []; total = 0; tree = []
    for (a, b), w in es:
        ra, rb = f(a), f(b)
        if ra != rb:
            parent[ra] = rb; total += w; tree.append((a, b, w)); log.append((a, b, w, True))
        else:
            log.append((a, b, w, False))
        if len(tree) == len(V) - 1:
            break
    return log, tree, total

def dijkstra(V, W, s, t, directed):
    nb = {v: [] for v in V}
    for (a, b), w in W.items():
        nb[a].append((b, w))
        if not directed:
            nb[b].append((a, w))
    INF = math.inf
    lab = {v: (INF, None) for v in V}; lab[s] = (0, None)
    perm = []; rows = []
    p = s
    while True:
        perm.append(p)
        for (y, w) in nb[p]:
            if y not in perm and lab[p][0] + w < lab[y][0]:
                lab[y] = (lab[p][0] + w, p)
        rows.append((p, {v: lab[v] for v in V}, list(perm)))
        if p == t:
            break
        temp = [v for v in V if v not in perm and lab[v][0] < INF]
        if not temp:
            return None
        p = min(temp, key=lambda v: (lab[v][0], V.index(v)))
    path = [t]
    while path[-1] != s:
        path.append(lab[path[-1]][1])
    return rows, path[::-1], lab[t][0]

# ---------------------------------------------------------------- desenho SVG
_uid = [0]
def svg(V, pos, edges, directed=False, weights=None, highlight=None, w=330, h=250, label_pos=None, curve=None):
    """pos: coords em [0,1]. weights: {(u,v): peso}. highlight: conjunto de arestas a destacar."""
    _uid[0] += 1; mid = f"ar{_uid[0]}"
    pad = 26
    P = {v: (pad + pos[v][0] * (w - 2 * pad), pad + pos[v][1] * (h - 2 * pad)) for v in V}
    r = 11
    s = [f"<svg viewBox='0 0 {w} {h}' width='{w}' style='max-width:100%;display:block;margin:6px auto' font-family='system-ui,sans-serif'>"]
    if directed:
        s.append(f"<defs><marker id='{mid}' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='currentColor'/></marker></defs>")
    hl = set(highlight or [])
    for (a, b) in edges:
        (x1, y1), (x2, y2) = P[a], P[b]
        d = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        sx, sy = x1 + ux * r, y1 + uy * r
        ex, ey = x2 - ux * (r + (2 if directed else 0)), y2 - uy * (r + (2 if directed else 0))
        on = (a, b) in hl or (b, a) in hl
        stroke = "#e5484d" if on else "currentColor"
        sw = 3.2 if on else 1.4
        op = "1" if on or not hl else ".35"
        mk = f" marker-end='url(#{mid})'" if directed else ""
        s.append(f"<line x1='{sx:.1f}' y1='{sy:.1f}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='{stroke}' stroke-width='{sw}' opacity='{op}'{mk}/>")
        if weights is not None:
            wt = weights.get((a, b), weights.get((b, a)))
            if wt is not None:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                t = str(wt); tw = 7 * len(t) + 6
                s.append(f"<rect x='{mx - tw / 2:.1f}' y='{my - 8:.1f}' width='{tw}' height='15' rx='4' fill='var(--card)' opacity='.92'/><text x='{mx:.1f}' y='{my + 3.5:.1f}' font-size='11' text-anchor='middle' fill='{stroke}' font-weight='600'>{t}</text>")
    for v in V:
        x, y = P[v]
        s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='var(--card)' stroke='currentColor' stroke-width='1.6'/><text x='{x:.1f}' y='{y + 4:.1f}' font-size='11' text-anchor='middle' fill='currentColor' font-weight='700'>{v}</text>")
    s.append("</svg>")
    return "".join(s)

def table(header, rows, first_bold=True):
    th = "".join(f"<th style='padding:4px 7px;border:1px solid var(--line)'>{h}</th>" for h in header)
    trs = []
    for r in rows:
        tds = "".join(f"<td style='padding:4px 7px;border:1px solid var(--line);text-align:center{';font-weight:700' if (i == 0 and first_bold) else ''}'>{c}</td>" for i, c in enumerate(r))
        trs.append(f"<tr>{tds}</tr>")
    return f"<div style='overflow-x:auto'><table style='border-collapse:collapse;font-size:13px;margin:6px 0'><tr>{th}</tr>{''.join(trs)}</table></div>"

def matrix_table(V, W, directed, blank=""):
    rows = []
    for a in V:
        r = [a]
        for b in V:
            val = W.get((a, b))
            if val is None and not directed:
                val = W.get((b, a))
            r.append(blank if val is None else val)
        rows.append(r)
    return table([""] + V, rows)

def planar_svg(cyc, A_, B_, w=300, h=300):
    """Desenho plano a partir do método cíclico: ciclo como polígono, A dentro (retas), B por fora (curvas)."""
    n = len(cyc); cx, cy, R = w / 2, h / 2, min(w, h) * 0.27
    ang = {v: -math.pi / 2 + 2 * math.pi * i / n for i, v in enumerate(cyc)}
    P = {v: (cx + R * math.cos(ang[v]), cy + R * math.sin(ang[v])) for v in cyc}
    idx = {v: i for i, v in enumerate(cyc)}
    s = [f"<svg viewBox='0 0 {w} {h}' width='{w}' style='max-width:100%;display:block;margin:6px auto' font-family='system-ui,sans-serif'>"]
    def seg(a, b, col, sw):
        (x1, y1), (x2, y2) = P[a], P[b]
        s.append(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{col}' stroke-width='{sw}'/>")
    for i in range(n):
        seg(cyc[i], cyc[(i + 1) % n], "currentColor", 1.6)
    for a, b in A_:
        seg(a, b, "#2f7dff", 2)
    for a, b in B_:
        i, j = sorted((idx[a], idx[b]))
        span = j - i
        if span > n / 2:  # contornar pelo arco mais curto
            i, j = j, i + n; span = n - span
        mid = -math.pi / 2 + 2 * math.pi * ((i + j) / 2) / n
        r2 = R * (1.25 + 0.22 * span)
        qx, qy = cx + r2 * math.cos(mid), cy + r2 * math.sin(mid)
        (x1, y1), (x2, y2) = P[a], P[b]
        s.append(f"<path d='M{x1:.1f},{y1:.1f} Q{qx:.1f},{qy:.1f} {x2:.1f},{y2:.1f}' fill='none' stroke='#e5484d' stroke-width='2'/>")
    for v in cyc:
        x, y = P[v]
        s.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='11' fill='var(--card)' stroke='currentColor' stroke-width='1.6'/><text x='{x:.1f}' y='{y + 4:.1f}' font-size='11' text-anchor='middle' fill='currentColor' font-weight='700'>{v}</text>")
    s.append(f"<text x='8' y='{h - 8}' font-size='11' fill='currentColor'>preto: ciclo C · azul: A dentro · vermelho: B fora</text></svg>")
    return "".join(s)
