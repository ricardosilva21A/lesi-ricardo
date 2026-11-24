"""Gera src/estudo/bancos/setr-t.json (SETR, teste de 9 dez. 2026) e as figuras dos circuitos.
Baseado nos slides SETR_00 a SETR_08 (Pedro Cunha), nos objetivos para o teste e nas fotos de dois testes
(Moodle, perguntas 3 a 9, e papel, página 2). As resoluções são minhas, a partir dos slides.
Correr:  python3 tools/gerar_setr.py
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from setr_afirmacoes import INSTRUCOES_CPUS, PERFORMANCE_MULTI, CONCECAO, VF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "estudo", "bancos", "setr-t.json")
IMG = os.path.join(ROOT, "src", "estudo", "img", "setr")
random.seed(912)

G1, G2, G3, G4, G5 = ("Grupo 1 · Circuitos", "Grupo 2 · Escolha as corretas", "Grupo 3 · Verdadeiro ou falso",
                      "Grupo 4 · Assembly ARM", "Grupo 5 · Cálculos")
PERG = []


def fmt(x, nd=3):
    x = round(x, nd)
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.{nd}f}".rstrip("0").rstrip(".").replace(".", ",")


def pct(h):
    return fmt(h * 100) + "%"


def mono(code):
    linhas = []
    for l in code.strip("\n").split("\n"):
        if ";" in l and not l.lstrip().startswith(";"):
            a, c = l.split(";", 1)
            l = a.rstrip().ljust(24) + "; " + c.strip()
        linhas.append(l)
    code = "\n".join(linhas)
    return f'<div style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px">{code}</div>'


# ---------------------------------------------------------------- figuras (SVG)
os.makedirs(IMG, exist_ok=True)


def svg_doc(body, w=360, h=230, esq=95, dir=20):
    W = w + esq + dir
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="14">'
            f'<rect width="{W}" height="{h}" fill="#fff"/>'
            f'<g transform="translate({esq - 40},0)" stroke="#111" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


def line(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def text(x, y, t, anchor="middle", size=14, bold=False):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" stroke="none" fill="#111"'
            f'{" font-weight=\"700\"" if bold else ""}>{t}</text>')


def res_h(x1, x2, y, lab):
    cx = (x1 + x2) / 2
    a, b = cx - 22, cx + 22
    pts = [(a, y)] + [(a + 4 + 6 * i, y + (-7 if i % 2 == 0 else 7)) for i in range(6)] + [(b, y)]
    pts[-2] = (b - 4, pts[-2][1])
    poly = " ".join(f"{px:.0f},{py:.0f}" for px, py in pts)
    return line(x1, y, a, y) + f'<polyline points="{poly}"/>' + line(b, y, x2, y) + text(cx, y - 14, lab)


def res_v(x, y1, y2, lab, side=1):
    cy = (y1 + y2) / 2
    a, b = cy - 22, cy + 22
    pts = [(x, a)] + [(x + (-7 if i % 2 == 0 else 7), a + 4 + 6 * i) for i in range(6)] + [(x, b)]
    poly = " ".join(f"{px:.0f},{py:.0f}" for px, py in pts)
    return (line(x, y1, x, a) + f'<polyline points="{poly}"/>' + line(x, b, x, y2)
            + text(x + 14 * side, cy + 5, lab, "start" if side > 0 else "end"))


def bat_v(x, y1, y2, lab, side=-1):
    cy = (y1 + y2) / 2
    return (line(x, y1, x, cy - 5) + line(x, cy + 5, x, y2)
            + f'<line x1="{x-16}" y1="{cy-5}" x2="{x+16}" y2="{cy-5}"/>'
            + f'<line x1="{x-8}" y1="{cy+5}" x2="{x+8}" y2="{cy+5}" stroke-width="5"/>'
            + text(x + 20 * (1 if side > 0 else -1) * 0 + (24 if side > 0 else -24), cy - 10, "+", "middle", 13)
            + text(x + (30 if side > 0 else -30), cy + 10, lab, "start" if side > 0 else "end"))


def arrow_h(x, y, right=True, lab=""):
    d = 1 if right else -1
    return (f'<path d="M{x-10*d},{y} L{x+8*d},{y} M{x+2*d},{y-5} L{x+8*d},{y} L{x+2*d},{y+5}" stroke="#c0392b"/>'
            + (text(x, y + 18, lab) if lab else ""))


def arrow_v(x, y, down=True, lab=""):
    d = 1 if down else -1
    return (f'<path d="M{x},{y-10*d} L{x},{y+8*d} M{x-5},{y+2*d} L{x},{y+8*d} L{x+5},{y+2*d}" stroke="#c0392b"/>'
            + (text(x - 10, y + 5, lab, "end") if lab else ""))


def dot(x, y, lab=None, dy=-8):
    return f'<circle cx="{x}" cy="{y}" r="3.5" fill="#111"/>' + (text(x + 10, y + dy, lab, "start", 13, True) if lab else "")


def guarda(nome, svg):
    with open(os.path.join(IMG, nome), "w", encoding="utf-8") as f:
        f.write(svg)
    return f"/estudo/img/setr/{nome}"


# ---------------------------------------------------------------- definições (Grupo 1)
DEFS = [
    ("Enuncie a lei de Ohm e indique a unidade de cada grandeza.",
     "E = R × I (tensão = resistência × corrente).\nE em volts (V), I em amperes (A), R em ohms (Ω).\nConhecendo duas grandezas calcula-se a terceira: I = E/R, R = E/I."),
    ("Enuncie a 1ª lei de Kirchhoff (lei dos nós) e o princípio em que se baseia.",
     "Num nó, a soma das correntes que chegam é igual à soma das correntes que saem (Σ I = 0 no nó).\nResulta do princípio da conservação da carga elétrica."),
    ("Enuncie a 2ª lei de Kirchhoff (lei das malhas) e o princípio em que se baseia.",
     "A soma dos potenciais elétricos (tensões) ao longo de uma malha fechada é zero (Σ V = 0).\nResulta da conservação da energia: toda a energia fornecida à malha é consumida pelos elementos dessa malha."),
    ("Defina nó, ramo e malha de um circuito elétrico.",
     "Nó: ponto onde o circuito ramifica (há mais do que um caminho para a corrente).\nRamo: trecho entre dois nós consecutivos; ao longo de um ramo a corrente é constante.\nMalha: caminho fechado que começa num nó e volta ao mesmo nó; a soma dos potenciais numa malha é zero."),
    ("O que é um circuito RLC? Qual o efeito da resistência no circuito?",
     "Circuito com uma resistência (R), uma bobine/indutor (L) e um condensador (C), ligados em série ou em paralelo.\nForma um oscilador harmónico para a corrente e ressoa como um circuito LC.\nA resistência aumenta o amortecimento (declínio das oscilações) e reduz a frequência de ressonância de pico. Na prática há sempre alguma resistência."),
    ("Indique como se identificam geradores e recetores ao aplicar a 2ª lei de Kirchhoff.",
     "No símbolo, a barra comprida é o polo positivo e a curta o negativo.\nGerador: a corrente entra pelo terminal negativo e sai pelo positivo (ganha energia).\nRecetor: a corrente entra pelo terminal positivo e sai pelo negativo (perde energia).\nAo percorrer a malha, se se encontra primeiro o terminal negativo, a tensão entra com sinal negativo."),
]


def pick_def():
    return random.choice(DEFS)


# ---------------------------------------------------------------- Grupo 1 · circuitos
def circ_serie(idx):
    n = random.choice([2, 3, 3])
    Rs = random.sample([1, 2, 3, 4, 5, 6, 8, 10], n)
    I = random.choice([0.5, 1, 1.5, 2, 2.5, 3])
    Req = sum(Rs)
    E = Req * I
    if abs(E - round(E)) > 1e-9:
        I = 2; E = Req * I
    body = bat_v(40, 40, 190, f"E = {fmt(E)} V")
    if n == 2:
        body += res_h(40, 320, 40, f"R1 = {Rs[0]} Ω") + res_v(320, 40, 190, f"R2 = {Rs[1]} Ω", -1)
    else:
        body += res_h(40, 180, 40, f"R1 = {Rs[0]} Ω") + res_h(180, 320, 40, f"R2 = {Rs[1]} Ω") + res_v(320, 40, 190, f"R3 = {Rs[2]} Ω", -1)
    body += line(40, 190, 320, 190) + arrow_h(110, 190, False, "I")
    img = guarda(f"serie-{idx}.svg", svg_doc(body))
    k = random.randrange(n)
    d = pick_def()
    tensoes = [r * I for r in Rs]
    somaR = " + ".join(str(r) for r in Rs)
    res_b = f"Em série a corrente é a mesma em todo o circuito.\nReq = {somaR} = {Req} Ω\nI = E / Req = {fmt(E)} / {Req} = {fmt(I)} A"
    res_c = "\n".join(f"V{i+1} = R{i+1} × I = {Rs[i]} × {fmt(I)} = {fmt(tensoes[i])} V" for i in range(n))
    res_c += f"\nVerificação (2ª lei de Kirchhoff): {fmt(E)} − " + " − ".join(fmt(t) for t in tensoes) + " = 0 ✓"
    P = Rs[k] * I ** 2
    PERG.append({
        "id": f"c-serie-{idx}", "grupo": G1, "tipo": "aberta", "tema": "Circuito em série",
        "enunciado": "Considere o circuito da figura, alimentado por uma fonte ideal.", "imagem": img,
        "alineas": [
            {"enunciado": d[0], "cotacao": 10, "resolucao": d[1]},
            {"enunciado": "Calcule a resistência equivalente e a corrente I no circuito.", "cotacao": 10, "resolucao": res_b},
            {"enunciado": "Calcule a tensão aos terminais de cada resistência e verifique a 2ª lei de Kirchhoff.", "cotacao": 10, "resolucao": res_c},
            {"enunciado": f"Calcule a potência dissipada em R{k+1}.", "cotacao": 10,
             "resolucao": f"Lei de Joule: P = R × I² = {Rs[k]} × {fmt(I)}² = {fmt(P)} W\n(ou P = V × I = {fmt(tensoes[k])} × {fmt(I)} = {fmt(P)} W)"},
        ],
    })


def circ_paralelo(idx):
    n = random.choice([2, 3])
    E = random.choice([6, 12, 24, 12, 30])
    divs = [r for r in [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20] if E / r * 2 == int(E / r * 2)]
    Rs = random.sample(divs, n)
    xs = [170, 300] if n == 2 else [150, 270, 390]
    body = bat_v(40, 40, 190, f"E = {E} V") + line(40, 40, xs[-1], 40) + line(40, 190, xs[-1], 190)
    for i, x in enumerate(xs):
        body += res_v(x, 40, 190, f"R{i+1} = {Rs[i]} Ω", 1)
        if i < len(xs) - 1:
            body += dot(x, 40) + dot(x, 190)
    body += arrow_h(90, 40, True, "") + text(90, 30, "It")
    img = guarda(f"paralelo-{idx}.svg", svg_doc(body, xs[-1] + 40, dir=80))
    Is = [E / r for r in Rs]
    It = sum(Is)
    Req = E / It
    d = pick_def()
    PERG.append({
        "id": f"c-paralelo-{idx}", "grupo": G1, "tipo": "aberta", "tema": "Circuito em paralelo",
        "enunciado": "Considere o circuito da figura, alimentado por uma fonte ideal.", "imagem": img,
        "alineas": [
            {"enunciado": d[0], "cotacao": 10, "resolucao": d[1]},
            {"enunciado": "Calcule a corrente em cada uma das resistências.", "cotacao": 10,
             "resolucao": "Em paralelo todas as resistências têm a tensão da fonte (E).\n" + "\n".join(
                 f"I{i+1} = E / R{i+1} = {E} / {Rs[i]} = {fmt(Is[i])} A" for i in range(n))},
            {"enunciado": "Usando a 1ª lei de Kirchhoff, calcule a corrente total It fornecida pela fonte.", "cotacao": 10,
             "resolucao": "Lei dos nós: a corrente que chega ao nó é igual à soma das que saem.\nIt = " + " + ".join(fmt(x) for x in Is) + f" = {fmt(It)} A"},
            {"enunciado": "Calcule a resistência equivalente do circuito.", "cotacao": 10,
             "resolucao": f"Req = E / It = {E} / {fmt(It)} = {fmt(Req)} Ω\n(ou 1/Req = " + " + ".join(f"1/{r}" for r in Rs) + ")"},
        ],
    })


def circ_malhas(idx):
    while True:
        R1, R2, R3 = random.choice([2, 3, 4, 5, 6, 8]), random.choice([1, 2, 3, 4, 6]), random.choice([1, 2, 3, 4, 5])
        i1, i2 = random.choice([1, 2, 3]), random.choice([1, 2, 3, 4])
        i3 = i1 + i2
        E1, E2 = R1 * i1 + R3 * i3, R2 * i2 + R3 * i3
        if E1 <= 60 and E2 <= 60 and E1 != E2:
            break
    body = (bat_v(40, 40, 190, f"E1 = {E1} V") + bat_v(320, 40, 190, f"E2 = {E2} V", 1)
            + res_h(40, 180, 40, f"R1 = {R1} Ω") + res_h(180, 320, 40, f"R2 = {R2} Ω")
            + res_v(180, 40, 190, f"R3 = {R3} Ω") + line(40, 190, 320, 190)
            + dot(180, 40, "A") + dot(180, 190, "B", 18)
            + arrow_h(78, 40, True) + text(78, 62, "i1") + arrow_h(282, 40, False) + text(282, 62, "i2")
            + arrow_v(180, 158, True) + text(196, 165, "i3", "start"))
    img = guarda(f"malhas-{idx}.svg", svg_doc(body, 360, dir=95))
    a, b, c, dd = R1 + R3, R3, R3, R2 + R3
    det = a * dd - b * c
    PtR = R3 * i3 ** 2
    alinea_a = random.choice([
        ("Indique quantos nós, ramos e malhas tem o circuito.",
         "Nós: 2 (A e B), onde o circuito ramifica.\nRamos: 3 (esquerdo com E1 e R1, central com R3, direito com E2 e R2).\nMalhas: 3 (a da esquerda, a da direita e a exterior)."),
        pick_def(),
    ])
    PERG.append({
        "id": f"c-malhas-{idx}", "grupo": G1, "tipo": "aberta", "tema": "Leis de Kirchhoff",
        "enunciado": "Considere o circuito da figura, com dois geradores ideais. Os sentidos das correntes estão arbitrados na figura.",
        "imagem": img,
        "alineas": [
            {"enunciado": alinea_a[0], "cotacao": 10, "resolucao": alinea_a[1]},
            {"enunciado": "Aplicando as leis de Kirchhoff, calcule i1, i2 e i3.", "cotacao": 20,
             "resolucao": (
                 f"1ª lei no nó A: i3 = i1 + i2\n"
                 f"2ª lei, malha da esquerda (sentido horário): −E1 + R1·i1 + R3·i3 = 0 → {E1} = {R1}·i1 + {R3}·(i1 + i2) → {E1} = {a}·i1 + {b}·i2\n"
                 f"2ª lei, malha da direita (sentido anti-horário): −E2 + R2·i2 + R3·i3 = 0 → {E2} = {R2}·i2 + {R3}·(i1 + i2) → {E2} = {c}·i1 + {dd}·i2\n"
                 f"Resolvendo o sistema (por exemplo pela regra de Cramer, det = {a}·{dd} − {b}·{c} = {det}):\n"
                 f"i1 = ({E1}·{dd} − {b}·{E2}) / {det} = {fmt(i1)} A\n"
                 f"i2 = ({a}·{E2} − {c}·{E1}) / {det} = {fmt(i2)} A\n"
                 f"i3 = i1 + i2 = {fmt(i3)} A\n"
                 f"Valores positivos: os sentidos arbitrados estão certos (um valor negativo indicaria o sentido contrário).")},
            {"enunciado": "Calcule a potência dissipada em R3.", "cotacao": 10,
             "resolucao": f"P = R3 × i3² = {R3} × {fmt(i3)}² = {fmt(PtR)} W"},
        ],
    })


for i in range(8):
    circ_serie(i)
for i in range(6):
    circ_paralelo(i)
for i in range(10):
    circ_malhas(i)

# ---------------------------------------------------------------- Grupo 2 · escolha as corretas (pools)
INSTR_TESTE = "Escolha as respostas corretas. Cada resposta correta vale 1 valor e cada resposta incorreta desconta 0,5 valores. Selecionar todas implica a anulação da questão."


def afirm(lst):
    return [{"v": v, "texto": t, "porque": p} for v, t, p in lst]


for pid, tema, lst in [("a-instr", "Conjunto de instruções e CPUs", INSTRUCOES_CPUS),
                       ("a-perf", "Análise da performance de programas e multiprocessadores", PERFORMANCE_MULTI),
                       ("a-concecao", "Conceitos e técnicas de conceção de SETR", CONCECAO)]:
    PERG.append({"id": pid, "grupo": G2, "tipo": "afirmacoes", "tema": tema, "enunciado": tema + ".",
                 "instrucao": INSTR_TESTE, "mostrar": 5, "certas": 2, "afirmacoes": afirm(lst)})

# ---------------------------------------------------------------- Grupo 3 · V/F e classificação
def limpa(porque, rot):
    for r in rot:
        for sep in (": ", ". ", "."):
            if porque.startswith(r + sep):
                porque = porque[len(r + sep):]
    porque = porque.strip()
    return porque[:1].upper() + porque[1:]


for q in VF:
    PERG.append({"id": q["id"], "grupo": G3, "tipo": "vf", "tema": q["tema"], "enunciado": q["enunciado"],
                 "rotulos": q["rotulos"], "mostrar": q["mostrar"],
                 "itens": [{"texto": t, "r": r, "porque": limpa(p, q["rotulos"])} for t, r, p in q["itens"]]})

# ---------------------------------------------------------------- Grupo 4 · assembly ARM
LD = lambda v, r: f"ADR r4,{v}      ; endereço de {v}\nLDR {r},[r4]    ; {r} = {v}\n"
ST = lambda v, r: f"ADR r4,{v}      ; endereço de {v}\nSTR {r},[r4]    ; {v} = {r}"
ASM = [
    ("x = (a * b) + c;", LD("a", "r0") + LD("b", "r1") + "MUL r2,r0,r1    ; r2 = a*b\n" + LD("c", "r3") + "ADD r2,r2,r3    ; r2 = a*b + c\n" + ST("x", "r2"), "Exercício dos slides"),
    ("y = (a | 14) & (1 >> b);", LD("a", "r0") + "ORR r0,r0,#14   ; r0 = a | 14\n" + LD("b", "r1") + "MOV r2,#1       ; r2 = 1\nMOV r2,r2,LSR r1 ; r2 = 1 >> b\nAND r0,r0,r2    ; r0 = (a|14) & (1>>b)\n" + ST("y", "r0"), "Exercício dos slides"),
    ("if (a < b) z = 3; else z = 2;", LD("a", "r0") + LD("b", "r1") + "CMP r0,r1       ; compara a com b\nBGE senao       ; se a >= b salta para o else\nMOV r2,#3       ; bloco verdadeiro: z = 3\nB fim           ; salta por cima do else\nsenao MOV r2,#2 ; bloco falso: z = 2\nfim " + ST("z", "r2") + "\n\nAlternativa com execução condicional (todas as instruções ARM podem ser condicionais):\nCMP r0,r1\nMOVLT r2,#3     ; se a < b\nMOVGE r2,#2     ; se a >= b", "Exercício dos slides"),
    ("X = (a << 2) & (b * c);", LD("a", "r0") + "MOV r0,r0,LSL #2 ; r0 = a << 2\n" + LD("b", "r1") + LD("c", "r2") + "MUL r3,r1,r2    ; r3 = b*c\nAND r0,r0,r3    ; r0 = (a<<2) & (b*c)\n" + ST("x", "r0"), "Teste (Moodle)"),
    ("x = (a + b) - c;", LD("a", "r0") + LD("b", "r1") + "ADD r3,r0,r1    ; r3 = a+b\n" + LD("c", "r2") + "SUB r3,r3,r2    ; r3 = (a+b) - c\n" + ST("x", "r3"), "Exemplo dos slides"),
    ("y = a * (b + c);", LD("b", "r0") + LD("c", "r1") + "ADD r2,r0,r1    ; r2 = b+c\n" + LD("a", "r0") + "MUL r2,r2,r0    ; r2 = (b+c)*a\n" + ST("y", "r2"), "Exemplo dos slides"),
    ("z = (a << 2) | (b & 15);", LD("a", "r0") + "MOV r0,r0,LSL #2 ; r0 = a << 2\n" + LD("b", "r1") + "AND r1,r1,#15   ; r1 = b & 15\nORR r1,r0,r1    ; r1 = (a<<2) | (b&15)\n" + ST("z", "r1"), "Exemplo dos slides"),
    ("x = (a - b) * c;", LD("a", "r0") + LD("b", "r1") + "SUB r2,r0,r1    ; r2 = a-b\n" + LD("c", "r3") + "MUL r2,r2,r3    ; r2 = (a-b)*c\n" + ST("x", "r2"), ""),
    ("y = (a >> 1) + (b & 7);", LD("a", "r0") + "MOV r0,r0,LSR #1 ; r0 = a >> 1 (ASR se a for com sinal)\n" + LD("b", "r1") + "AND r1,r1,#7    ; r1 = b & 7\nADD r0,r0,r1    ; r0 = (a>>1) + (b&7)\n" + ST("y", "r0"), ""),
    ("z = (a | b) ^ c;", LD("a", "r0") + LD("b", "r1") + "ORR r0,r0,r1    ; r0 = a | b\n" + LD("c", "r2") + "EOR r0,r0,r2    ; r0 = (a|b) ^ c  (EOR = ou exclusivo)\n" + ST("z", "r0"), ""),
    ("if (a == b) x = a + 1; else x = b - 1;", LD("a", "r0") + LD("b", "r1") + "CMP r0,r1       ; compara a com b\nBNE senao       ; se a != b vai para o else\nADD r2,r0,#1    ; x = a + 1\nB fim\nsenao SUB r2,r1,#1 ; x = b - 1\nfim " + ST("x", "r2"), ""),
    ("if (a > b) y = a - b; else y = b - a;", LD("a", "r0") + LD("b", "r1") + "CMP r0,r1       ; compara a com b\nBLE senao       ; se a <= b vai para o else\nSUB r2,r0,r1    ; y = a - b\nB fim\nsenao SUB r2,r1,r0 ; y = b - a\nfim " + ST("y", "r2"), ""),
    ("x = (a * 4) + (b * c);", LD("a", "r0") + "MOV r0,r0,LSL #2 ; r0 = a*4 (redução de força: *4 = <<2)\n" + LD("b", "r1") + LD("c", "r2") + "MUL r3,r1,r2    ; r3 = b*c\nADD r0,r0,r3    ; r0 = a*4 + b*c\n" + ST("x", "r0"), ""),
    ("z = ~a & b;", LD("a", "r0") + "MVN r0,r0       ; r0 = ~a (move negado)\n" + LD("b", "r1") + "AND r0,r0,r1    ; r0 = ~a & b\n" + ST("z", "r0") + "\n\nAlternativa: BIC r0,r1,r0 ; bit clear: r0 = b AND NOT a", ""),
    ("for (i = 0, s = 0; i < 10; i++) s = s + i;", "MOV r0,#0       ; r0 = i = 0\nMOV r1,#0       ; r1 = s = 0\nciclo CMP r0,#10 ; teste do loop: i < 10?\nBGE fim         ; se i >= 10 sai\nADD r1,r1,r0    ; s = s + i\nADD r0,r0,#1    ; i++\nB ciclo         ; volta ao teste\nfim " + ST("s", "r1"), ""),
    ("y = (a & 255) | (b << 8);", LD("a", "r0") + "AND r0,r0,#255  ; r0 = a & 0xFF\n" + LD("b", "r1") + "ORR r0,r0,r1,LSL #8 ; r0 = r0 | (b << 8), deslocamento no 2º operando\n" + ST("y", "r0"), ""),
    ("x = a - (b << 1) + c;", LD("a", "r0") + LD("b", "r1") + "SUB r0,r0,r1,LSL #1 ; r0 = a - (b<<1)\n" + LD("c", "r2") + "ADD r0,r0,r2    ; r0 = a - (b<<1) + c\n" + ST("x", "r0"), ""),
    ("if (a != 0) x = b; else x = c;", LD("a", "r0") + "CMP r0,#0       ; a == 0?\nBEQ senao       ; se a == 0 vai para o else\n" + LD("b", "r1") + "B fim\nsenao " + LD("c", "r1") + "fim " + ST("x", "r1"), ""),
]
for i, (c, sol, fonte) in enumerate(ASM):
    q = {"id": f"asm-{i}", "grupo": G4, "tipo": "aberta", "tema": "Assembly ARM",
         "enunciado": f"Considerando a arquitetura das instruções do ARM, escreva em código assembly comentado a seguinte atribuição em C:\n\n<b>{c}</b>",
         "resolucao": mono(sol) + "\nCritérios: carregar cada variável (ADR + LDR), fazer as operações nos registos, guardar o resultado (ADR + STR) e comentar cada linha com «;». Outros registos também servem."}
    PERG.append(q)

# ---------------------------------------------------------------- Grupo 5 · cálculos
def calc_cache(idx):
    h = random.choice([0.35, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
    tc, tm = random.choice([2, 3, 4, 5, 10]), random.choice([20, 50, 60, 70, 80, 100, 120])
    tav = h * tc + (1 - h) * tm
    h1 = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
    h2 = random.choice([x for x in [0.2, 0.3, 0.4, 0.5] if h1 + x < 0.95])
    t1, t2, tm2 = random.choice([2, 3, 4]), random.choice([10, 12, 15, 20]), random.choice([20, 60, 70, 100, 110])
    tav2 = h1 * t1 + h2 * t2 + (1 - h1 - h2) * tm2
    PERG.append({
        "id": f"k-cache-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Performance do sistema de memória",
        "enunciado": "Responda às seguintes questões sobre o tempo médio de acesso à memória. Apresente as fórmulas.",
        "alineas": [
            {"enunciado": f"Determine o tempo médio de acesso à memória (tav em ns), com uma taxa de cache hit de {pct(h)}, tcache = {tc} ns e tmain = {tm} ns.",
             "cotacao": 12, "resolucao": f"tav = h·tcache + (1 − h)·tmain\ntav = {fmt(h)} × {tc} + (1 − {fmt(h)}) × {tm}\n    = {fmt(h*tc)} + {fmt((1-h)*tm)} = {fmt(tav)} ns"},
            {"enunciado": f"Calcule o tempo médio de acesso a uma memória multinível com taxa de cache hit L1 de {pct(h1)}, taxa de cache hit L2 de {pct(h2)}, tcache L1 = {t1} ns, tcache L2 = {t2} ns e tmain = {tm2} ns.",
             "cotacao": 13, "resolucao": f"tav = h1·tL1 + h2·tL2 + (1 − h1 − h2)·tmain\ntav = {fmt(h1)} × {t1} + {fmt(h2)} × {t2} + (1 − {fmt(h1)} − {fmt(h2)}) × {tm2}\n    = {fmt(h1*t1)} + {fmt(h2*t2)} + {fmt(1-h1-h2)} × {tm2}\n    = {fmt(tav2)} ns"},
        ],
    })


def calc_cache_miss(idx):
    h1 = random.choice([0.1, 0.2, 0.3])
    miss = random.choice([x for x in [0.4, 0.5, 0.6, 0.7] if x > h1 + 0.05])
    h2 = 1 - miss
    t1, t2, tm = random.choice([2, 3, 4]), random.choice([10, 15, 20]), random.choice([60, 70, 80, 110, 120])
    tav = h1 * t1 + h2 * t2 + (1 - h1 - h2) * tm
    tipo = random.choice([
        ("Indique e explique os três tipos de cache miss.",
         "Compulsório (cold): a localização nunca foi acedida; o primeiro acesso falha sempre.\nCapacidade: o working set é maior do que a cache; reduz-se com caches maiores.\nConflito (collision): várias localizações do working set mapeiam para a mesma entrada da cache."),
        ("Defina cache hit, cache miss e working set.",
         "Cache hit: a localização requerida está na cache.\nCache miss: a localização requerida não está na cache.\nWorking set: conjunto de localizações usadas por um programa num intervalo de tempo."),
    ])
    PERG.append({
        "id": f"k-miss-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Caches multinível",
        "enunciado": f"Calcule o tempo médio (tav em nanossegundos) de acesso a uma memória multinível, com:\nTaxa de cache hit L1 de {pct(h1)};\nTaxa de cache miss {pct(miss)};\ntcache L1 = {t1} ns; tcache L2 = {t2} ns; tmain = {tm} ns.",
        "alineas": [
            {"enunciado": "Tav = ?", "cotacao": 15, "resolucao": (
                f"Como no exercício resolvido nos slides (cache miss L2 de 60% → h2 = 40%): h2 = 1 − {fmt(miss)} = {fmt(h2)}.\n"
                f"tav = h1·tL1 + h2·tL2 + (1 − h1 − h2)·tmain\n"
                f"tav = {fmt(h1)} × {t1} + {fmt(h2)} × {t2} + (1 − {fmt(h1)} − {fmt(h2)}) × {tm}\n"
                f"    = {fmt(h1*t1)} + {fmt(h2*t2)} + {fmt((1-h1-h2)*tm)} = {fmt(tav)} ns\n"
                f"Atenção: se o enunciado der diretamente a taxa de hit L2, usa-se esse valor como h2.")},
            {"enunciado": tipo[0], "cotacao": 10, "resolucao": tipo[1]},
        ],
    })


def calc_latencia(idx):
    variantes = [
        ("Qual a diferença entre FIQ e IRQ no ARM7?",
         "FIQ (fast interrupt request): para eventos que têm de ser tratados à medida que ocorrem; tratamento rápido e de baixa latência.\nIRQ (interrupt request): interrupções mais gerais; pausa o programa e corre o handler.\nA FIQ tem prioridade sobre a IRQ."),
        ("Descreva o procedimento de interrupção do ARM: ações do CPU e responsabilidades do handler.",
         "CPU: salva o PC, copia o CPSR para o SPSR, força os bits do CPSR para registar a interrupção e força o PC para o vetor.\nHandler: restaura o PC correto, restaura o CPSR a partir do SPSR e limpa as flags de interrupt disable."),
        ("Descreva a sequência de interrupção.",
         "1. O CPU reconhece o pedido (ACK).\n2. O dispositivo envia o vetor.\n3. O CPU chama o handler.\n4. O software processa o pedido.\n5. O CPU restaura o estado do programa foreground."),
        ("Indique as fontes de sobrecarga (overhead) de uma interrupção.",
         "Tempo de execução do handler; sobrecarga do próprio mecanismo de interrupção; save e restore dos registos; penalizações do pipeline; penalizações da cache."),
    ]
    v = variantes[idx % len(variantes)]
    PERG.append({
        "id": f"k-lat-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Interrupções do ARM",
        "enunciado": "No que concerne à latência das interrupções do ARM, no pior caso de latência, existe um número mínimo de ciclos do relógio necessário para dar resposta a um pedido de interrupção:",
        "alineas": [
            {"enunciado": "Número de ciclos para sincronizar o pedido externo; para completar a instrução em curso; para abortar dados; para entrar no estado de handling da interrupção; total no pior caso.",
             "cotacao": 15, "resolucao": "Sincronizar o pedido externo: 2 ciclos\nCompletar a instrução em curso: até 20 ciclos\nAbortar dados: 3 ciclos\nEntrar no estado de handling: 2 ciclos\nTotal no pior caso: 2 + 20 + 3 + 2 = 27 ciclos"},
            {"enunciado": v[0], "cotacao": 10, "resolucao": v[1]},
        ],
    })


def calc_acel(idx):
    n = random.choice([100, 200, 500, 1000, 2000])
    tin, tx, tout = random.choice([1, 2]), random.choice([1, 2, 3]), random.choice([1, 2, 3])
    ta = tin + tx + tout
    tcpu = ta + random.choice([-1.5, -1, -0.5, 0.5, 1, 1.5, 2])
    if tcpu <= 0:
        tcpu = ta + 1
    S = n * (tcpu - ta)
    total_cpu = tcpu * n
    forma = random.choice(["total", "ciclo"])
    cpu_txt = (f"o tempo de execução do CPU foi de {fmt(total_cpu)} ns" if forma == "total"
               else f"o tempo normal de execução do CPU foi de {fmt(tcpu)} ns por ciclo")
    vant = S > 0
    PERG.append({
        "id": f"k-acel-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Sistemas aceleradores",
        "enunciado": f"Numa dada função com um loop de {n} ciclos, {cpu_txt}. O sistema acelerado teve um tempo de execução de {tx} ns, de leitura de {tin} ns e de escrita de {tout} ns por ciclo.",
        "alineas": [
            {"enunciado": "Calcule o tempo de execução do acelerador (por ciclo e total).", "cotacao": 10,
             "resolucao": f"taccel = tin + tx + tout = {tin} + {tx} + {tout} = {ta} ns por ciclo\nTotal: {n} × {ta} = {fmt(n*ta)} ns"
                          + (f"\nCPU por ciclo: {fmt(total_cpu)} / {n} = {fmt(tcpu)} ns" if forma == "total" else f"\nCPU total: {n} × {fmt(tcpu)} = {fmt(total_cpu)} ns")},
            {"enunciado": "Calcule o speedup S do acelerador.", "cotacao": 8,
             "resolucao": f"S = n·(tCPU − taccel) = {n} × ({fmt(tcpu)} − {ta}) = {fmt(S)} ns"},
            {"enunciado": "A aceleração foi vantajosa? Que outros fatores devem ser considerados?", "cotacao": 7,
             "resolucao": ("Sim: " if vant else "Não: ") + (f"o acelerador ({fmt(n*ta)} ns) é mais rápido do que o CPU ({fmt(total_cpu)} ns), S > 0." if vant else f"o acelerador ({fmt(n*ta)} ns) demora mais do que o CPU ({fmt(total_cpu)} ns), S < 0.")
                          + "\nMesmo com vantagem, ela pode ser relativa: é preciso considerar o custo de implementação do acelerador, o consumo energético, o tempo de transferência de dados e a sincronização com o CPU mestre."},
        ],
    })


def calc_fir(idx):
    N = random.choice([5, 8, 12, 15, 20, 25, 50, 100])
    pior = 7 + 6 * N + 4 * (N - 1) + 2
    melhor = 7 + 6 * N + 2 * (N - 1) + 2
    f = random.choice([10, 20, 25, 50, 100])
    PERG.append({
        "id": f"k-fir-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Tempo de execução (filtro FIR)",
        "enunciado": (f"Considere o código ARM do filtro FIR, for (i=0; i&lt;N; i++) f = f + c[i]*x[i];, com N = {N}.\n"
                      "Blocos: inicialização 7 instruções / 7 ciclos; corpo 4 / 4; atualização 2 / 2; teste 2 instruções / 2 a 4 ciclos (BLT ocupa 1 ciclo no melhor caso e 3 no pior)."),
        "alineas": [
            {"enunciado": "Escreva a expressão de tloop e calcule o número de ciclos no pior caso.", "cotacao": 15,
             "resolucao": f"tloop = tinit + N·(tbody + tupdate) + (N − 1)·ttest,worst + ttest,best\ntloop = 7 + {N}×(4 + 2) + ({N} − 1)×4 + 2\n      = 7 + {6*N} + {4*(N-1)} + 2 = {pior} ciclos"},
            {"enunciado": f"Com um relógio de {f} MHz, quanto tempo demora o loop nesse caso?", "cotacao": 10,
             "resolucao": f"Período = 1 / {f} MHz = {fmt(1000/f)} ns\nt = {pior} × {fmt(1000/f)} = {fmt(pior*1000/f)} ns\n(No melhor caso, com o teste sempre em 2 ciclos: 7 + {6*N} + {2*(N-1)} + 2 = {melhor} ciclos.)"},
        ],
    })


def nzcv(a, b):
    r = (a + b) & 0xFFFFFFFF
    N = r >> 31
    Z = int(r == 0)
    C = int(a + b > 0xFFFFFFFF)
    sa, sb, sr = a >> 31, b >> 31, r >> 31
    V = int(sa == sb and sr != sa)
    return r, f"{N}{Z}{C}{V}"


def s32(x):
    return x - (1 << 32) if x >> 31 else x


SOMAS = [(0xFFFFFFFF, 1), (0x7FFFFFFF, 1), (5, 3), (0x80000000, 0x80000000), (0xFFFFFFFF, 0xFFFFFFFF),
         (10, 0xFFFFFFFD), (0xFFFFFFFB, 2), (0x40000000, 0x40000000), (0x80000000, 0xFFFFFFFF)]


def calc_flags(idx):
    escolhidas = random.sample(SOMAS, 3)
    als = []
    for a, b in escolhidas:
        r, f = nzcv(a, b)
        als.append({"enunciado": f"ADDS r0,r1,r2 com r1 = 0x{a:08X} ({s32(a)}) e r2 = 0x{b:08X} ({s32(b)}). Indique o resultado e as flags NZCV.",
                    "cotacao": 8 if len(als) < 2 else 9,
                    "resolucao": f"r0 = 0x{r:08X} ({s32(r)})\nN = {f[0]} (bit 31 do resultado), Z = {f[1]} (resultado é zero?), C = {f[2]} (transporte para fora do bit 31), V = {f[3]} (overflow com sinal: duas parcelas com o mesmo sinal e resultado com sinal diferente)\nNZCV = {f}"})
    PERG.append({"id": f"k-flags-{idx}", "grupo": G5, "tipo": "aberta", "tema": "Flags NZCV do CPSR",
                 "enunciado": "Todas as operações aritméticas, lógicas e de deslocamento do ARM definem os bits N, Z, C e V do CPSR. Considere registos de 32 bits.",
                 "alineas": als})


for i in range(8):
    calc_cache(i)
for i in range(5):
    calc_cache_miss(i)
for i in range(4):
    calc_latencia(i)
for i in range(8):
    calc_acel(i)
for i in range(5):
    calc_fir(i)
for i in range(4):
    calc_flags(i)

# ---------------------------------------------------------------- Conceitos (escolha simples)
MC = "Conceitos"
ESC = [
    ("Um resistor óhmico de 10 Ω é atravessado por uma corrente de 1,0 A. Qual a tensão aos seus terminais?", ["10 V", "5 V", "20 V", "0,1 V"], "E = R × I = 10 × 1 = 10 V."),
    ("A diferença de potencial num resistor óhmico é 1,5 V quando passa 1,5 mA. Qual a resistência?", ["1×10³ Ω", "1×10⁻³ Ω", "1 Ω", "2,25×10³ Ω"], "R = E / I = 1,5 / 1,5×10⁻³ = 1000 Ω. Atenção ao mA = 10⁻³ A."),
    ("Numa lâmpada ligada a 12 V com resistência de 6 Ω, qual a corrente?", ["2 A", "72 A", "0,5 A", "18 A"], "I = E / R = 12 / 6 = 2 A."),
    ("Uma corrente de 5 A atravessa uma resistência de 8 Ω. Qual a tensão?", ["40 V", "1,6 V", "13 V", "0,625 V"], "E = I × R = 5 × 8 = 40 V."),
    ("Se a corrente medida num circuito DC é mais baixa do que o normal, isso pode significar que...", ["a tensão diminuiu ou a resistência aumentou", "a tensão aumentou ou a resistência diminuiu", "a resistência e a tensão aumentaram na mesma proporção", "o circuito está em curto-circuito"], "I = E/R: menos tensão ou mais resistência (ligações soltas, corrosão)."),
    ("A 1ª lei de Kirchhoff (lei dos nós) resulta do princípio da conservação...", ["da carga elétrica", "da energia", "da massa", "da potência"], "A 2ª lei (malhas) resulta da conservação da energia."),
    ("A 2ª lei de Kirchhoff (lei das malhas) diz que...", ["a soma dos potenciais ao longo de uma malha fechada é zero", "a soma das correntes num nó é zero", "a corrente é igual em todos os ramos", "a resistência equivalente é a soma das resistências"], "Conservação da energia."),
    ("Ao longo de um ramo de um circuito, a corrente elétrica é...", ["sempre constante", "sempre nula", "igual à soma das correntes dos nós", "inversamente proporcional ao número de malhas"], "Ramo: trecho entre dois nós consecutivos."),
    ("Num circuito RLC, a introdução da resistência...", ["aumenta o amortecimento e reduz a frequência de ressonância de pico", "elimina as oscilações por completo", "aumenta a frequência de ressonância", "transforma o circuito num LC ideal"], "Slides de Circuitos RLC."),
    ("A indutância de uma bobine mede-se em...", ["henries (H)", "farads (F)", "ohms (Ω)", "webers (Wb)"], "Capacitância em farads; indutância em henries."),
    ("Qual a definição de sistema de computação embebido?", ["Dispositivo que inclui um computador programável mas que não é um computador de propósito geral", "Qualquer computador portátil", "Um computador de propósito geral com sistema operativo de tempo real", "Um circuito sem processador"], "Definição dos slides."),
    ("Um sistema multimédia que perde qualidade quando falha um deadline é um exemplo de...", ["soft real time", "hard real time", "sistema não embebido", "sistema multi-rate"], "Hard = falha da ação; soft = redução da performance."),
    ("Qual destes é um requisito não funcional?", ["Autonomia de 8 horas com 4 pilhas AA", "Apresentar a latitude e longitude atuais", "Mostrar estradas principais e marcos", "Calcular a rota"], "Energia, tempo, tamanho, peso, custo e fiabilidade são não funcionais."),
    ("Qual a ordem dos níveis de abstração na conceção?", ["Requisitos, especificação, arquitetura, design de componentes, integração", "Especificação, requisitos, arquitetura, integração, componentes", "Arquitetura, requisitos, componentes, especificação, integração", "Requisitos, arquitetura, especificação, integração, componentes"], "Do mais abstrato ao mais detalhado."),
    ("Qual arquitetura permite dois fetches de memória simultâneos?", ["Harvard", "von Neumann", "CISC", "Big-endian"], "Memórias de dados e de programa separadas."),
    ("Quantos registos de uso geral tem o modelo de programação do ARM?", ["16 (r0 a r15)", "32 (r0 a r31)", "8 (r0 a r7)", "4 (N, Z, C, V)"], "r15 é o PC; o CPSR é à parte."),
    ("Que flags tem o CPSR do ARM?", ["N, Z, C, V", "PC, IR, SP, LR", "S, Z, P, C", "FIQ, IRQ"], "Negativo, Zero, Carry, oVerflow."),
    ("Qual o pipeline do ARM7?", ["3 estágios: fetch, decode, execute", "3 estágios: fetch, run, idle", "5 estágios: fetch, decode, execute, memory, write-back", "2 estágios: fetch, execute"], "Run e idle são modos de potência."),
    ("Qual é a latência de interrupção do ARM no pior caso?", ["27 ciclos", "20 ciclos", "7 ciclos", "33 ciclos"], "2 + 20 + 3 + 2."),
    ("Qual a interrupção de maior prioridade, que nunca é mascarada?", ["NMI", "IRQ", "SWI", "Trap"], "Non-maskable interrupt, muitas vezes para power-down."),
    ("No ARM, uma trap (interrupção de software) é feita com a instrução...", ["SWI", "BL", "MOV r15,r14", "CMP"], "SWI entra no modo supervisor."),
    ("Que tipo de cache miss se reduz aumentando o tamanho da cache?", ["Capacidade", "Compulsório", "Conflito", "Nenhum"], "O working set deixa de ser maior do que a cache."),
    ("Com h = 0,70, tcache = 4 ns e tmain = 20 ns, qual é o tav?", ["8,8 ns", "6,8 ns", "17,2 ns", "12 ns"], "0,7×4 + 0,3×20 = 2,8 + 6 = 8,8 ns."),
    ("Com h = 35%, tcache = 10 ns e tmain = 120 ns, qual é o tav?", ["81,5 ns", "45,5 ns", "3,5 ns", "78 ns"], "0,35×10 + 0,65×120 = 3,5 + 78 = 81,5 ns."),
    ("O pipelining...", ["aumenta o throughput sem reduzir a latência", "reduz a latência sem alterar o throughput", "reduz a latência e o throughput", "só funciona em CISC"], "Medidas da performance."),
    ("Para satisfazer as restrições temporais deve analisar-se o tempo de execução...", ["no pior caso", "no melhor caso", "no caso médio", "de uma só instrução"], "O pior caso garante o deadline."),
    ("A fórmula básica do tempo de execução de um programa é...", ["program path + instruction timing", "tempo de ciclo × número de registos", "latência + throughput", "tcache + tmain"], "Slides de Análise de performance."),
    ("Trocar x*2 por x<<1 é um exemplo de...", ["redução da strength", "movimento de código", "eliminação de variáveis de indução", "array padding"], "Operação cara trocada por uma barata."),
    ("O teste que examina o código fonte é o...", ["clear box (white box)", "black box", "random", "de regressão"], "Black box não analisa o código."),
    ("A injeção de erros serve para...", ["medir a qualidade dos testes", "aumentar a performance", "reduzir o consumo de energia", "corrigir bugs automaticamente"], "Vê-se a % de bugs injetados que os testes detetam."),
    ("O tempo total de execução de um acelerador é...", ["taccel = tin + tx + tout", "taccel = tCPU − tx", "taccel = n·tCPU", "taccel = tin × tout"], "Entrada + computação + saída."),
    ("O speedup de um acelerador num loop de n iterações é...", ["S = n(tCPU − taccel)", "S = n(taccel − tCPU)", "S = tCPU / n", "S = taccel + tCPU"], "Positivo = compensa."),
    ("CPU: 450 ns para 100 ciclos. Acelerador: 2 ns de execução, 1 ns de leitura e 2 ns de escrita por ciclo. A aceleração foi vantajosa?", ["Não: o acelerador demora 500 ns", "Sim: o acelerador demora 50 ns", "Sim: o acelerador demora 5 ns", "Não: o acelerador demora 4500 ns"], "5 ns × 100 = 500 ns > 450 ns (exercício 1 dos slides)."),
    ("Qual a solução indicada para os problemas de caching com aceleradores?", ["Atualização da cache", "Aumentar a cache", "Desligar a cache", "Usar arquitetura de von Neumann"], "O CPU pode ler um valor desatualizado da cache."),
    ("O que gasta mais energia por operação?", ["Transferência de memória", "Soma", "Multiplicação", "Leitura na SRAM"], "33 ciclos contra 1 da soma."),
    ("Num sistema multithreaded (non-blocking) com acelerador...", ["o CPU continua a trabalhar enquanto o acelerador computa", "o CPU espera pelo acelerador", "não pode haver acelerador", "o acelerador espera pelo CPU"], "No single-threaded o CPU espera."),
]
for i, (e, ops, ex) in enumerate(ESC):
    PERG.append({"id": f"mc-{i}", "grupo": MC, "tipo": "escolha", "tema": "Conceitos", "enunciado": e, "opcoes": ops, "correta": 0, "explicacao": ex})

# ---------------------------------------------------------------- testes reais (enunciados das fotos, resoluções minhas)
FM, FP = "Teste real · Moodle", "Teste real · papel"
INSTR_MOODLE = "Escolha até 2 respostas corretas. Cada resposta correta valerá 1 valor e cada resposta errada será descontado 0,5 valor."
INSTR_PAPEL = "Escolha as respostas corretas (circulando-as). Cada resposta correta valerá 1 valor e cada resposta incorreta descontará 0,5 valores. A seleção de todas como corretas implica a anulação da questão."
REAIS = [
    {"id": "r-m3", "grupo": G2, "tipo": "afirmacoes", "fonte": FM, "tema": "Pergunta 3", "valores": 2, "instrucao": INSTR_MOODLE,
     "enunciado": "Conjunto de instruções e CPUs.",
     "afirmacoes": [
         {"v": True, "texto": "Na arquitetura de computador de Harvard são permitidos dois fetches de memória simultâneos uma vez que a memória de dados e a memória de instruções são separadas.", "porque": "Memórias e barramentos separados."},
         {"v": False, "texto": "O modelo de programação do ARM contém 16 registos (r0-r15), adicionalmente existe um registo especial de 32 bits designado por NZCV, que é automaticamente colocado durante todas as operações aritméticas, lógicas e deslocamento para o registo de estado do programa em curso.", "porque": "O registo chama-se CPSR; NZCV são as flags dentro dele."},
         {"v": False, "texto": "Ao nível de prioridades de interrupções, Non-maskable interrupt (NMI) é um tipo de interrupção com prioridade inferior à interrupção em curso e não é reconhecida pelo CPU enquanto a interrupção corrente não estiver completa.", "porque": "A NMI tem a prioridade mais alta e nunca é mascarada."},
         {"v": True, "texto": "Nas operações de cache, dizemos que houve um cache hit quando a localização requerida está na memória cache. Quando a localização não se encontra em cache, então dizemos que aconteceu um cache miss. Um cache miss pode ocorrer de modo compulsório (se o endereço ainda não foi acedido anteriormente).", "porque": "Definições certas; o miss compulsório é o primeiro acesso."},
         {"v": False, "texto": "O pipeline do ARM7 possui um pipe de 3 estágios, fetch, run e idle. Permitindo que várias instruções sejam tratadas simultaneamente em diferentes estágios do ciclo.", "porque": "São fetch, decode e execute."},
     ]},
    {"id": "r-m4", "grupo": G3, "tipo": "vf", "fonte": FM, "tema": "Pergunta 4", "valores": 2, "rotulos": ["Verdadeiro", "Falso"],
     "enunciado": "A engenharia concorrente mostra que a operação em diferentes tarefas simultaneamente permite reduzir o tempo de conceção dos sistemas embebidos. Escolha se as seguintes técnicas de engenharia concorrentes são Verdadeiras ou Falsas.",
     "itens": [
         {"texto": "Cruzar equipas funcionais (multidisciplinares)", "r": 0, "porque": "Cross-functional teams."},
         {"texto": "Realização do produto de forma concorrente (vários componentes de uma só vez)", "r": 0, "porque": "Concurrent product realization: projetar vários subsistemas ao mesmo tempo é o centro da técnica."},
         {"texto": "Envolvimento dos fornecedores (maior capacidade de resposta)", "r": 0, "porque": "Early and continual supplier involvement."},
         {"texto": "Gestão integrada do produto (todos os elementos são independentes, não tem de haver um responsável)", "r": 1, "porque": "Na gestão integrada há alguém responsável pelo projeto todo."},
         {"texto": "Focalização na concorrência (ir ao encontro das necessidades)", "r": 0, "porque": "Pela descrição corresponde ao foco no cliente (ir ao encontro das necessidades). A palavra «concorrência» é estranha: confirma com o professor."},
         {"texto": "Manter a informação em sigilo (sem partilha de informação)", "r": 1, "porque": "É o oposto da partilha incremental de informação."},
     ]},
    {"id": "r-m5", "grupo": G4, "tipo": "aberta", "fonte": FM, "tema": "Pergunta 5", "valores": 3,
     "enunciado": "Considerando a arquitetura das instruções do ARM, escreva em código assembly comentado, a seguinte atribuição em C:\n\n<b>X = (a << 2) & (b * c)</b>",
     "resolucao": mono(ASM[3][1]) + "\n\nCarregar a, deslocar 2 bits para a esquerda (LSL #2), carregar b e c, multiplicar, fazer o AND e guardar em x."},
    {"id": "r-m6", "grupo": G2, "tipo": "afirmacoes", "fonte": FM, "tema": "Pergunta 6", "valores": 2, "instrucao": INSTR_MOODLE,
     "enunciado": "Conceitos e técnicas de conceção de SETR.",
     "afirmacoes": [
         {"v": False, "texto": "Em Sistemas Embebidos em Tempo Real (SETR), as operações com restrições temporais podem classificar-se como, Soft real time, quando o não cumprimento das restrições causa a falha da ação do sistema.", "porque": "Falha da ação é hard real time."},
         {"v": False, "texto": "Os projetos de SETR normalmente são desenvolvidos por equipas multidisciplinares complexas formadas por muitos elementos, com janelas de mercado até 1 ano e sem grande margem para falhas.", "porque": "Slides: equipas de poucos elementos, janela de mercado de 6 meses."},
         {"v": True, "texto": "A utilização de lógica customizada na conceção de projetos de SETR (ex: FPGAs), requer menos energia que os microprocessadores, contudo, os microprocessadores são mais rápidos e mais eficientes, uma vez que são fortemente pipelined e utilizam tecnologia VLSI agressiva.", "porque": "Paradoxo da performance + slide de energia."},
         {"v": False, "texto": "Os requisitos funcionais indicam o que o sistema deve realmente fazer, definem as suas iterações de tarefas e serviços para input/output. O tempo necessário para processar um input e a fiabilidade do sistema são 2 exemplos de requisitos deste tipo.", "porque": "Tempo de processamento e fiabilidade são não funcionais."},
         {"v": True, "texto": "O ambiente de desenvolvimento de SETR é normalmente diferente da arquitetura da plataforma de destino/target do sistema. Um compilador cruzado permite gerar código para essa arquitetura específica (target) a partir de um ambiente de desenvolvimento genérico (host).", "porque": "Host e target diferentes, daí o cross-compiler."},
     ]},
    {"id": "r-m7", "grupo": G2, "tipo": "afirmacoes", "fonte": FM, "tema": "Pergunta 7", "valores": 2, "instrucao": INSTR_MOODLE,
     "enunciado": "Análise da performance de programas e multi-processadores.",
     "afirmacoes": [
         {"v": False, "texto": "Para medição da performance de programas de sistemas em tempo real, é imperativo considerar o tempo de execução no melhor caso, uma vez que é uma métrica para satisfação das restrições temporais.", "porque": "É o pior caso."},
         {"v": False, "texto": "O cálculo do tempo de execução de um programa consiste no path do programa + o tempo de execução de cada instrução. As instruções condicionais \"IF\" são bons alvos para otimização do tempo de execução dos programas.", "porque": "Os bons alvos de otimização são os loops."},
         {"v": False, "texto": "Duas das estratégias estudadas para validação e teste do programa são: Black box que consiste em examinar o código fonte para determinar se este funciona e Clear box, técnica esta que considera testes random e testes de regressão.", "porque": "Estão trocadas."},
         {"v": True, "texto": "Na conceção de SETR, a utilização de sistemas multiprocessadores melhora o desempenho no processamento de I/O em tempo-real, podem consumir menos energia e melhorar o desempenho no streaming de dados (multimédia). Normalmente a partilha da computação supera o desempenho da computação singular.", "porque": "Texto dos slides de multiprocessadores."},
         {"v": True, "texto": "Um acelerador é um elemento de processamento (PE) que surge no barramento do CPU, nas operações de acesso à memória principal durante o processo de aceleração, este pode provocar problemas de caching com o CPU. Normalmente, a solução para resolver este tipo de problema é considerar a atualização da cache.", "porque": "Solução dos slides: atualização da cache."},
     ]},
    {"id": "r-m8", "grupo": G5, "tipo": "aberta", "fonte": FM, "tema": "Pergunta 8", "valores": 2,
     "enunciado": "No que concerne à latência das interrupções do ARM, no pior caso de latência, existe um número mínimo de ciclos do relógio necessário para dar resposta a um pedido de interrupção:",
     "alineas": [
         {"enunciado": "Número de ciclos para sincronizar o pedido externo", "cotacao": 4, "resolucao": "2 ciclos"},
         {"enunciado": "Número de ciclos para completar a instrução em curso", "cotacao": 4, "resolucao": "20 ciclos (no máximo)"},
         {"enunciado": "Número de ciclos para abortar dados", "cotacao": 4, "resolucao": "3 ciclos"},
         {"enunciado": "Número de ciclos para entrar no estado de handling da interrupção", "cotacao": 4, "resolucao": "2 ciclos"},
         {"enunciado": "Total de ciclos para dar resposta a uma interrupção (no pior caso)", "cotacao": 4, "resolucao": "2 + 20 + 3 + 2 = 27 ciclos"},
     ]},
    {"id": "r-m9", "grupo": G5, "tipo": "aberta", "fonte": FM, "tema": "Pergunta 9", "valores": 2,
     "enunciado": "Calcule o tempo médio (Tav em nanossegundos) de acesso a uma memória multinível, com:\nTaxa de cache hit L1 de 20%;\nTaxa de cache miss 50%;\ntcache L1 = 4 ns; tcache L2 = 10 ns; tmain = 70 ns;\nTav = ?\n\nDeve dar uma resposta numérica, ex: 73.8ns",
     "resolucao": ("Seguindo o exercício resolvido nos slides (cache miss L2 de 60% → h2 = 40%), h2 = 1 − 0,5 = 0,5:\n"
                   "Tav = h1·tL1 + h2·tL2 + (1 − h1 − h2)·tmain\n"
                   "Tav = 0,2×4 + 0,5×10 + (1 − 0,2 − 0,5)×70 = 0,8 + 5 + 21 = 26,8 ns\n\n"
                   "Nota: se se interpretar o miss de 50% como a fração que vai à memória principal (h2 = 1 − 0,2 − 0,5 = 0,3), dá 0,8 + 3 + 35 = 38,8 ns. "
                   "Como o enunciado é ambíguo, escreve a fórmula e diz que h2 usaste.")},
    {"id": "r-p21", "grupo": G2, "tipo": "afirmacoes", "fonte": FP, "tema": "2.1", "valores": 2, "instrucao": INSTR_PAPEL,
     "enunciado": "2.1 Conjunto de instruções e CPUs",
     "afirmacoes": [
         {"v": False, "texto": "Na arquitetura de computador de Von Neumann são permitidos dois fetches de memória simultâneos uma vez que a memória de dados e a memória de instruções são separadas.", "porque": "É Harvard."},
         {"v": False, "texto": "O modelo de programação do ARM contem 32 registos (r0-r31), existe um registo especial, o CPSR (Current Program Status Register), que é automaticamente colocado durante todas as operações aritméticas, lógicas e deslocamento para o registo de estado do programa em curso.", "porque": "São 16 registos (r0-r15). O resto está certo."},
         {"v": True, "texto": "ARM7 suporta 2 tipos de interrupções, Fast interrupt requests (FIQs) e Interrupt requests (IRQs). As FIQs são mais rápidas, permitem atalhar algumas etapas do handler.", "porque": "FIQ = tratamento rápido e de baixa latência (tem registos próprios, o handler guarda menos coisas)."},
         {"v": False, "texto": "Nas operações de cache, dizemos que houve um cache miss quando a localização requerida está na memória cache. Quando a localização não se encontra na cache, então dizemos que aconteceu um cache hit. Um cache hit pode ocorrer compulsoriamente (se o endereço ainda não foi acedido anteriormente).", "porque": "Hit e miss estão trocados."},
         {"v": True, "texto": "O pipeline do ARM7 possui um pipe de 3 estágios, fetch, decode e execute. Permitindo que várias instruções sejam tratadas simultaneamente em diferentes estágios do ciclo.", "porque": "Certo."},
     ]},
    {"id": "r-p22", "grupo": G2, "tipo": "afirmacoes", "fonte": FP, "tema": "2.2", "valores": 2, "instrucao": INSTR_PAPEL,
     "enunciado": "2.2 Análise da performance de programas e multiprocessadores",
     "afirmacoes": [
         {"v": False, "texto": "Para medição da performance de programas de sistemas em tempo real, é imperativo considerar o tempo de execução no melhor caso, uma vez que é uma métrica para satisfação das restrições temporais.", "porque": "É o pior caso."},
         {"v": True, "texto": "O cálculo do tempo de execução de um programa consiste no path do programa + o tempo de execução de cada instrução. Os loops são bons alvos para otimização.", "porque": "Certo."},
         {"v": False, "texto": "Duas das estratégias estudadas para validação e teste do programa são: Black box que consiste em examinar o código fonte para determinar se este funciona e Clear box, técnica esta que considera testes random e testes de regressão.", "porque": "Estão trocadas."},
         {"v": True, "texto": "Na conceção de SETR, a utilização de sistemas multiprocessadores melhora o desempenho no processamento de I/O em tempo-real, podem consumir menos energia e melhorar o desempenho no streaming de dados (multimédia). Normalmente a partilha da computação supera o desempenho da computação singular.", "porque": "Certo."},
         {"v": False, "texto": "Um acelerador é um elemento de processamento (PE) que surge no barramento do CPU, contudo este pode provocar problemas de caching na sincronia com o CPU. Normalmente, se aumentar a capacidade da cache soluciona este problema.", "porque": "A solução é a atualização da cache."},
     ]},
    {"id": "r-p23", "grupo": G2, "tipo": "afirmacoes", "fonte": FP, "tema": "2.3", "valores": 2, "instrucao": INSTR_PAPEL,
     "enunciado": "2.3 Técnicas de Design de Sistemas Embebidos",
     "explicacao": "Esta parte (modelos de desenvolvimento e engenharia concorrente) não está nos objetivos deste ano. As respostas são a minha leitura do livro de Wolf: confirma com o professor se aparecer.",
     "afirmacoes": [
         {"v": False, "texto": "Dos vários modelos de desenvolvimento de projetos estudados, o modelo de refinamento sucessivo assume que o sistema é construído em várias etapas, cada uma das etapas é composta por 3 fases sendo elas, requisitos, conceção e teste.", "porque": "Voltas com requisitos, construção e teste descrevem o modelo em espiral."},
         {"v": False, "texto": "A junção de equipas funcionais da mesma área disciplinar e a partilha incremental de informação entre equipas, são duas técnicas fulcrais de engenharia concorrente no desenvolvimento de Sistemas Embebidos em Tempo Real.", "porque": "As equipas são multidisciplinares (cross-functional)."},
         {"v": False, "texto": "A metodologia co-design consiste em arquitetar o hardware e o software paralelamente para permitir implementar módulos independentes para uma maior facilidade de integração.", "porque": "No co-design o hardware e o software são concebidos em conjunto, tendo em conta a interação entre eles, não como módulos independentes."},
         {"v": True, "texto": "No fluxo de conceção hierárquico, os sistemas embebidos devem ser desenvolvidos sobre múltiplos níveis de abstração, nomeadamente, Arquitetura do sistema; Sistemas de hardware e software e Componentes de hardware e software.", "porque": "Certo."},
         {"v": True, "texto": "Os requisitos são uma descrição formal das necessidades do cliente, a sua consistência para que não se contradigam entre si e permitir que sejam modificados facilmente durante o processo de desenvolvimento são dois exemplos de bons requisitos a seguir para SETR.", "porque": "Consistência e modificabilidade são qualidades de bons requisitos. Atenção que nos slides os requisitos são descritos em linguagem corrente."},
     ]},
]
for q in REAIS:
    q["tituloReal"] = (q["tema"] if q["tema"].startswith("Pergunta") else "Questão " + q["tema"]) + f" ({q['valores']} val.)"
PERG.extend(REAIS)

banco = {
    "uc": "SETR",
    "titulo": "Teste · 9 dez. 2026",
    "descricao": "Matéria dos objetivos para o teste (circuitos, conceitos de SETR, instruction set, CPUs, análise de performance, multiprocessadores). A estrutura do teste modelo é um palpite a partir de dois testes anteriores. Resoluções feitas a partir dos slides.",
    "cabula": "/estudo/paginas/setr.html",
    "estrutura": [
        {"grupo": G1, "n": 1, "cotacao": 4},
        {"grupo": G2, "n": 3, "cotacao": 6},
        {"grupo": G3, "n": 1, "cotacao": 2},
        {"grupo": G4, "n": 1, "cotacao": 3},
        {"grupo": G5, "n": 2, "cotacao": 5},
    ],
    "testesReais": [
        {"titulo": "Teste em Moodle (perguntas 3 a 9)", "nota": "As perguntas 1 e 2 não estão nas fotos. Faz com 1h.",
         "ids": ["r-m3", "r-m4", "r-m5", "r-m6", "r-m7", "r-m8", "r-m9"]},
        {"titulo": "Teste em papel (página 2, grupo 2)", "nota": "Só a página 2 está na foto.",
         "ids": ["r-p21", "r-p22", "r-p23"]},
    ],
    "perguntas": PERG,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(banco, f, ensure_ascii=False, indent=1)
from collections import Counter
print("OK", len(PERG), "perguntas", Counter(q["grupo"] for q in PERG))
print("afirmações:", sum(len(q.get("afirmacoes", [])) for q in PERG), "itens V/F:", sum(len(q.get("itens", [])) for q in PERG))
