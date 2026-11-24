"""Gera src/estudo/bancos/md-fichas.json: fichas de exercícios de grafos com a correção da professora (imagens)
e, quando dá para verificar com segurança, uma resposta curta calculada."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from grafos import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "estudo", "bancos", "md-fichas.json")
IMG = "/estudo/img/md/fichas/"

T1, T2, T3, T4, T5 = "Conceitos e graus", "Euler e Hamilton", "Planares", "Matrizes e fecho", "Redes"

def prof(*pags, pre="prof"):
    return "".join(f"<img src='{IMG}{pre}-{p}.jpg' alt='correção, pág. {p}' loading='lazy' style='width:100%;background:#fff;border-radius:10px;margin:6px 0'>" for p in pags)

def q(id, grupo, tema, enun, res, pags=(), pre="prof", imagem=None):
    nome = "Ficha grafos_v3.pdf" if pre == "prof" else "Ficha extra 25_10.pdf"
    corr = (f"\n\n<b>Correção da professora:</b> no PDF \"{nome}\" (pasta Resoluções), pág. {', '.join(map(str, pags))}. Procura o número do exercício." if pags else "")
    if not res:
        res = "Resolve no papel e compara com a correção da professora indicada abaixo."
    d = dict(id=id, grupo=grupo, tipo="aberta", tema=tema, fonte="Ficha de exercícios", enunciado=enun, resolucao=(res or "") + corr)
    if imagem:
        d["imagem"] = imagem
    return d

def main():
    P = []
    # ---------------- Ficha de aula 25/10 (Anabela Silva), enunciados em texto
    a = "Ficha de aula 25/10 · "
    V = list("12345"); E = [("1", "2"), ("1", "3"), ("2", "3"), ("2", "4"), ("4", "5")]
    P.append(q("aula-1", T1, "Graus", a + "Exercício 1. Grafo G com V = {1,2,3,4,5} e arestas {1,2}, {1,3}, {2,3}, {2,4}, {4,5}.\na) Desenha o grafo. b) Calcula o grau de cada vértice. c) Quantas arestas tem G? Verifica que 2 × arestas = soma dos graus.",
                svg(V, {"1": (.1, .4), "2": (.45, .1), "3": (.85, .4), "4": (.45, .7), "5": (.9, .95)}, E, w=260, h=200) +
                "b) deg(1) = 2, deg(2) = 3, deg(3) = 2, deg(4) = 2, deg(5) = 1.\nc) A = 5. Σ deg = 2 + 3 + 2 + 2 + 1 = 10 = 2 × 5 ✓", (1,), "aula"))
    P.append(q("aula-2", T4, "Digrafo", a + "Exercício 2. Digrafo com V = {A,B,C,D,E} e arcos (A,B), (A,C), (B,D), (C,D), (D,E), (E,B).\na) Desenha o digrafo. b) Tabela de antecessores e sucessores. c) d⁻ e d⁺ de cada vértice.",
                svg(list("ABCDE"), {"A": (.05, .5), "B": (.35, .15), "C": (.35, .85), "D": (.65, .5), "E": (.95, .15)}, [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("E", "B")], directed=True, w=280, h=200) +
                table(["v", "Γ⁻ (antecessores)", "Γ⁺ (sucessores)", "d⁻", "d⁺"],
                      [["A", "∅", "{B, C}", 0, 2], ["B", "{A, E}", "{D}", 2, 1], ["C", "{A}", "{D}", 1, 1], ["D", "{B, C}", "{E}", 2, 1], ["E", "{D}", "{B}", 1, 1]]) +
                "Confirmação: Σ d⁻ = Σ d⁺ = 6 = número de arcos.", (1, 2), "aula"))
    P.append(q("aula-3", T1, "Cadeias", a + "Exercício 3. G com vértices A, B, C, D, E, F e arestas AB, AC, AE, BC, BD, CF, DE, DF, EF.\na) Desenha o grafo. b) Grau e vizinhos. c) Verifica se a cadeia [AB, BC, AC, AE, ED, DB] é simples e se é elementar. d) G é conexo?",
                "b) Todos os vértices têm grau 3. Γ(A) = {B,C,E}, Γ(B) = {A,C,D}, Γ(C) = {A,B,F}, Γ(D) = {B,E,F}, Γ(E) = {A,D,F}, Γ(F) = {C,D,E}.\n"
                "c) A cadeia é A → B → C → A → E → D → B. É simples: as 6 arestas são todas diferentes. Não é elementar: passa duas vezes por A e por B.\n"
                "d) Conexo: de qualquer vértice chega-se a qualquer outro.", (2,), "aula"))
    P.append(q("aula-4", T1, "Completos", a + "Exercício 4. a) Desenha K4. Quantas arestas tem? b) Quantas arestas tem Kn em geral?",
                "a) K4 tem 6 arestas (4 vértices, cada um liga aos outros 3: 4 × 3 / 2 = 6).\nb) Kn tem n(n − 1)/2 arestas.", (3,), "aula"))
    P.append(q("aula-5", T1, "Bipartidos", a + "Exercício 5. Grafo com vértices {a,b,c,d} e arestas {a,b}, {b,c}, {c,d}, {d,a}. É bipartido?",
                "Sim: é um ciclo de comprimento 4 (par). Partição V1 = {a, c}, V2 = {b, d}: todas as arestas ligam V1 a V2.", (3,), "aula"))
    P.append(q("aula-6", T1, "Cadeias", a + "Exercício 6. Grafo com vértices {A,B,C,D} e arestas A–B, B–C, C–A, C–D.\na) Exemplo de um ciclo elementar. b) Exemplo de uma cadeia que não é elementar. c) O grafo é conexo?",
                "a) [A, B, C, A].\nb) [D, C, A, B, C]: não repete arestas mas passa duas vezes por C (simples, não elementar). A professora deu [A,B,C,A,B,C,D], que também não é elementar (e nem é simples, porque repete arestas).\nc) Sim, é conexo.", (3, 4), "aula"))

    # ---------------- Ficha "Exercícios - Grafos e Redes" (enunciado em imagem)
    def ex(n, grupo, tema, pags, res=""):
        P.append(q(f"ex-{n}", grupo, tema, f"Ficha de exercícios · Exercício {n}", res, pags, imagem=f"{IMG}ex{n}.jpg"))
    ex(1, T1, "Graus e digrafo associado", (1,))
    ex(2, T1, "Antecessores e sucessores", (2,))
    ex(3, T1, "Representação", (2,))
    ex(4, T1, "Completos", (3,), "deg num Kn = n − 1. Arestas: K1 = 0, K2 = 1, K3 = 3, K4 = 6, K5 = 10, em geral n(n − 1)/2.")
    ex(6, T1, "Bipartidos", (4, 5))
    ex(14, T2, "Eulerianos", (5, 6, 7))
    ex(15, T2, "Eulerianos", (7,))
    ex(16, T2, "Eulerianos e hamiltonianos", (7, 8))
    ex(17, T2, "Eulerianos em digrafos", (9, 10))
    ex(19, T2, "Eulerianos e hamiltonianos", (11, 12))
    ex(20, T2, "Dirac e Ore", (12, 13), "Um exemplo que cumpre Ore e não cumpre Dirac precisa de um vértice com grau < n/2, mas com todos os pares não adjacentes a somar ≥ n.")
    ex(22, T2, "Hamiltonianos", (13, 14))
    ex(26, T3, "Fórmula de Euler", (14,),
       "Usa V − A + F = 2 (planar conexo) e confirma A ≤ 3V − 6.\n26.1: 7 − 10 + 6 = 3 ≠ 2, logo não existe (planar conexo).\n26.2: 8 − 10 + 4 = 2 e 10 ≤ 18, logo pode existir.\n26.3: 7 − 11 + 6 = 2 e 11 ≤ 15, logo pode existir.")
    ex(28, T3, "Representação planar", (15,))
    ex(29, T3, "K3,3 sem uma aresta", (15, 16), "K3,3 sem uma aresta: V = 6, A = 8. Desenha-se sem cruzamentos (a professora mostra o desenho) e confirma-se com Euler: F = 2 − 6 + 8 = 4.")
    ex(34, T4, "Matriz booleana e fecho", (16, 17, 18))

    # redes: resposta calculada
    V45 = ["Évora", "Faro", "Setúbal", "Braga", "Coimbra", "Leiria", "Porto"]
    W45 = {("Évora", "Faro"): 7, ("Évora", "Setúbal"): 8, ("Évora", "Coimbra"): 39, ("Évora", "Porto"): 95, ("Faro", "Setúbal"): 17, ("Faro", "Braga"): 85,
           ("Faro", "Leiria"): 22, ("Faro", "Porto"): 36, ("Setúbal", "Braga"): 85, ("Setúbal", "Leiria"): 14, ("Setúbal", "Porto"): 36, ("Braga", "Coimbra"): 31,
           ("Braga", "Leiria"): 19, ("Coimbra", "Leiria"): 13, ("Coimbra", "Porto"): 20, ("Leiria", "Porto"): 15}
    st, tot = prim(V45, W45, "Évora")
    rows, path, cost = dijkstra(V45, W45, "Évora", "Leiria", False)
    ex(36, T5, "Árvore geradora mínima", (18, 19, 20), "Valor da árvore geradora mínima (correção da professora): 760.")
    ex(40, T5, "Árvore geradora mínima", (20, 21), "Árvore da professora: {a,c} 13, {c,e} 3, {e,b} 6, {b,d} 5, {e,f} 10. Total 37.")
    ex(45, T5, "Árvore e Dijkstra", (21, 22),
       f"45.1 Conexa (há caminho entre todos) e não completa (por exemplo, Évora e Braga não estão ligadas).\n45.2 Árvore geradora mínima (Prim a partir de Évora): " +
       ", ".join(f"{a}–{b} {w}" for a, b, w in st) + f". Total {tot} €.\n45.3 Dijkstra Évora → Leiria: {' → '.join(path)}, custo {cost} €.")
    ex(43, T5, "Dijkstra", (22, 23), "Percurso mínimo de a para g (correção da professora): a – c – d – b – e – g, custo 16.")
    V46 = list("ABCDEF")
    W46 = {("A", "B"): 18, ("A", "D"): 32, ("B", "C"): 12, ("B", "D"): 28, ("C", "D"): 17, ("C", "F"): 32, ("D", "E"): 4, ("D", "F"): 17, ("E", "F"): 11}
    r46, p46, c46 = dijkstra(V46, W46, "A", "F", False)
    st46, t46 = prim(V46, W46, "A")
    ex(46, T5, "Dijkstra e árvore", (23, 24),
       f"46.2 Percurso mínimo de A para F: problema de caminho mais curto (Dijkstra).\n46.3 {' → '.join(p46)}, {c46} minutos (igual à correção da professora).\n"
       f"46.4 Itinerário sem ciclos que passa por todas: árvore geradora mínima. Prim a partir de A: " + ", ".join(f"{a}–{b} {w}" for a, b, w in st46) + f". Total {t46} minutos.")
    assert (c46, p46) == (47, ["A", "D", "E", "F"])

    banco = dict(uc="MD", titulo="Fichas de exercícios resolvidas · Teoria de Grafos",
                 descricao="Exercícios das fichas, com a resposta calculada quando possível e a página da correção da professora nos teus PDFs.",
                 estrutura=[dict(grupo=g, n=1) for g in (T1, T2, T3, T4, T5)], perguntas=P)
    json.dump(banco, open(OUT, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("ok", len(P), "exercícios", "45:", tot, path, cost, "46 MST:", t46)

if __name__ == "__main__":
    main()
