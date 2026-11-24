"""Escolhas múltiplas de MD (Teoria de Grafos) com explicação para cada opção errada.
Formato de cada pergunta: (enunciado, [(opção, porque_errada | None se for a certa)], explicação da certa, tema)."""
import random

C = None  # marca a opção certa

BASE = [
    ("Num grafo, o número de vértices de grau ímpar é sempre:", [
        ("par", C),
        ("ímpar", "Se fosse ímpar, a soma dos graus seria ímpar, mas Σ deg(v) = 2A é sempre par."),
        ("igual ao número de arestas", "Não há relação: um ciclo tem A arestas e nenhum vértice de grau ímpar."),
        ("zero", "Pode haver vértices de grau ímpar (ex.: K4 tem 4 vértices de grau 3); só têm de ser em número par."),
     ], "Σ deg(v) = 2A é par, por isso os graus ímpares têm de aparecer em número par.", "Graus"),
    ("Um grafo tem graus 3, 3, 2, 2, 2. Quantas arestas tem?", [
        ("5", "Contaste vértices, não arestas."),
        ("6", C),
        ("12", "12 é a soma dos graus; cada aresta conta 2 vezes nessa soma, falta dividir por 2."),
        ("4", "Não vem de nenhuma regra: A = Σ deg / 2 = 12 / 2."),
     ], "A = Σ deg(v) / 2 = 12 / 2 = 6.", "Graus"),
    ("Quantas arestas tem K6?", [
        ("12", "12 seria 2 × 6, não tem a ver com Kn."),
        ("15", C),
        ("30", "30 = 6 × 5 conta cada aresta duas vezes (de cada ponta); falta dividir por 2."),
        ("36", "36 = 6 × 6 incluiria lacetes e contagens duplas."),
     ], "Kn tem n(n − 1)/2 = 6 × 5 / 2 = 15 arestas (apertos de mão).", "Completos"),
    ("Quantas arestas tem K3,4?", [
        ("7", "7 = 3 + 4 é o número de vértices."),
        ("12", C),
        ("21", "21 seria K7 (7 × 6 / 2), que liga também vértices do mesmo lado."),
        ("6", "6 seria K3,2 ou K2,3."),
     ], "Km,n tem m × n arestas: cada um dos 3 liga aos 4 do outro lado.", "Bipartidos"),
    ("Um grafo é bipartido se e só se:", [
        ("não tem ciclos de comprimento ímpar", C),
        ("é conexo", "Ser conexo não tem a ver: um triângulo é conexo e não é bipartido."),
        ("todos os graus são pares", "Essa é a condição de ciclo euleriano, não de bipartido."),
        ("não tem ciclos", "Não ter ciclos chega (árvores são bipartidas) mas não é necessário: um quadrado tem ciclo e é bipartido."),
     ], "Num bipartido alterna-se sempre entre V1 e V2, por isso todos os ciclos são pares.", "Bipartidos"),
    ("K3 (triângulo) é bipartido?", [
        ("Não, tem um ciclo de comprimento 3", C),
        ("Sim", "Com 3 vértices todos ligados, dois deles ficam sempre no mesmo lado e estão ligados."),
        ("Só se for conexo", "Já é conexo e mesmo assim não é bipartido."),
        ("Depende da orientação", "Bipartido é sobre grafos não orientados; não há orientação aqui."),
     ], "O triângulo é um ciclo ímpar.", "Bipartidos"),
    ("O subgrafo de G gerado por V' contém:", [
        ("os vértices de V' e todas as arestas de G com as duas extremidades em V'", C),
        ("todos os vértices de G e as arestas de V'", "Isso é a ideia do grafo PARCIAL (mantém todos os vértices)."),
        ("só os vértices de V' sem arestas", "As arestas entre vértices de V' vêm todas incluídas."),
        ("as arestas incidentes a V'", "Uma aresta com só uma ponta em V' não entra: precisa das duas."),
     ], "Subgrafo gerado: escolhes vértices, vêm todas as arestas entre eles.", "Subgrafos"),
    ("O grafo parcial de G gerado por E' contém:", [
        ("todos os vértices de G e só as arestas de E'", C),
        ("só os vértices extremos de E'", "Isso seria o SUBGRAFO parcial; o grafo parcial mantém todos os vértices."),
        ("todas as arestas de G", "Então seria o próprio G."),
        ("os vértices de E' e todas as arestas entre eles", "Isso é o subgrafo gerado por esses vértices."),
     ], "Grafo parcial G' = (V, E'): escolhes arestas, ficam todos os vértices (alguns podem ficar isolados).", "Subgrafos"),
    ("Uma cadeia elementar:", [
        ("não passa duas vezes pelo mesmo vértice", C),
        ("não passa duas vezes pela mesma aresta mas pode repetir vértices", "Isso é a definição de cadeia SIMPLES."),
        ("é sempre fechada", "Pode ser aberta; fechada e simples é um ciclo."),
        ("passa por todas as arestas", "Isso seria euleriana."),
     ], "Elementar = não repete vÉrtices. Simples = não repete arestas.", "Cadeias"),
    ("Uma cadeia simples:", [
        ("não repete arestas", C),
        ("não repete vértices", "Isso é elementar."),
        ("é fechada", "Pode ser aberta ou fechada."),
        ("tem comprimento 1", "Pode ter qualquer comprimento."),
     ], "Simples = sem arestas repetidas (pode repetir vértices).", "Cadeias"),
    ("Um ciclo é:", [
        ("uma cadeia simples fechada", C),
        ("uma cadeia qualquer", "Tem de ser fechada e não repetir arestas."),
        ("um caminho num digrafo", "Num digrafo fala-se de circuito, não de ciclo."),
        ("uma cadeia aberta", "Um ciclo é fechado: acaba onde começa."),
     ], "Definição dos slides: ciclo = cadeia simples fechada.", "Cadeias"),
    ("Num digrafo, um circuito é:", [
        ("um caminho simples fechado", C),
        ("uma cadeia fechada", "Cadeia é vocabulário de grafos não orientados."),
        ("um caminho elementar aberto", "Um circuito é fechado."),
        ("um arco", "Um arco é só uma ligação."),
     ], "Nos digrafos: caminho, circuito, arco. Nos grafos: cadeia, ciclo, aresta.", "Digrafos"),
    ("O comprimento (tamanho) de uma cadeia [a, b, c, a, d] é:", [
        ("4", C),
        ("5", "5 é o número de vértices escritos; o comprimento conta arestas."),
        ("3", "3 seria o número de vértices diferentes menos 1; conta-se cada aresta percorrida."),
        ("2", "Não corresponde a nenhuma contagem da sequência."),
     ], "Comprimento = número de arestas = vértices da sequência − 1 = 4.", "Cadeias"),
    ("Um grafo conexo tem ciclo euleriano se e só se:", [
        ("todos os vértices têm grau par", C),
        ("tem exatamente 2 vértices de grau ímpar", "Isso dá cadeia euleriana, não ciclo."),
        ("todos os graus são ≥ V/2", "Isso é Dirac (hamiltoniano)."),
        ("é bipartido", "Ser bipartido não tem a ver com Euler."),
     ], "Teorema de Euler: em cada passagem entra-se e sai-se, por isso todos os graus são pares.", "Eulerianos"),
    ("Um grafo conexo tem cadeia euleriana (não fechada) se e só se:", [
        ("tem exatamente 2 vértices de grau ímpar", C),
        ("todos os graus são pares", "Assim tem ciclo (fechado)."),
        ("não tem vértices de grau ímpar", "É o mesmo que todos pares: ciclo."),
        ("tem 4 vértices de grau ímpar", "Com 4 ímpares não há cadeia nem ciclo."),
     ], "Começa num ímpar e acaba no outro.", "Eulerianos"),
    ("Um grafo conexo tem 4 vértices de grau ímpar. Então:", [
        ("não tem cadeia nem ciclo euleriano", C),
        ("tem ciclo euleriano", "O ciclo exige 0 vértices ímpares."),
        ("tem cadeia euleriana", "A cadeia exige exatamente 2 ímpares."),
        ("é hamiltoniano", "Graus ímpares não dizem nada sobre Hamilton."),
     ], "Só 0 (ciclo) ou 2 (cadeia) vértices ímpares permitem Euler.", "Eulerianos"),
    ("Um digrafo conexo tem circuito euleriano se e só se:", [
        ("deg⁺(v) = deg⁻(v) para todo o v", C),
        ("todos os graus são pares", "Num digrafo conta-se entradas e saídas, não o grau total."),
        ("é fortemente conexo e simples", "Não chega: as entradas têm de igualar as saídas em cada vértice."),
        ("deg⁺(v) > deg⁻(v) num vértice", "Isso indica o início de um caminho, não um circuito."),
     ], "Cada vez que entras num vértice tens de sair: entradas = saídas.", "Eulerianos"),
    ("Num digrafo conexo com caminho euleriano de v0 para v1:", [
        ("deg⁺(v0) = deg⁻(v0) + 1 e deg⁻(v1) = deg⁺(v1) + 1", C),
        ("deg⁺(v0) = deg⁻(v0)", "No início sai-se uma vez a mais do que se entra."),
        ("v0 e v1 têm grau par", "Num digrafo olha-se para deg⁺ e deg⁻, não para a paridade."),
        ("deg⁻(v0) = deg⁺(v0) + 1", "Está trocado: isso é o vértice final."),
     ], "O início tem uma seta a sair a mais, o fim uma a entrar a mais.", "Eulerianos"),
    ("Teorema de Dirac: G simples, conexo, V ≥ 3. Se ... então G tem ciclo hamiltoniano.", [
        ("deg(v) ≥ V/2 para todo o v", C),
        ("deg(u) + deg(v) ≥ V para u, v adjacentes", "Parecido com Ore, mas Ore é para pares NÃO adjacentes."),
        ("todos os graus são pares", "Isso é Euler."),
        ("A ≤ 3V − 6", "Isso é planaridade."),
     ], "Dirac Divide: todos com grau pelo menos metade de V.", "Hamiltonianos"),
    ("Teorema de Ore: a condição deg(u) + deg(v) ≥ V é exigida para:", [
        ("quaisquer u, v NÃO adjacentes", C),
        ("quaisquer u, v adjacentes", "É precisamente o contrário: os que NÃO se tocam."),
        ("todos os pares", "Só os não adjacentes."),
        ("os vértices de grau ímpar", "Os graus ímpares interessam a Euler, não a Ore."),
     ], "Ore sOma os que não se tocam.", "Hamiltonianos"),
    ("Um grafo não cumpre Dirac. Pode-se concluir que:", [
        ("nada; Dirac é condição suficiente, não necessária", C),
        ("não é hamiltoniano", "Erro clássico: há grafos hamiltonianos que falham Dirac (ex.: um ciclo C6 tem graus 2 < 3)."),
        ("é euleriano", "Dirac não diz nada sobre Euler."),
        ("não é planar", "Dirac não diz nada sobre planaridade."),
     ], "Condição suficiente: se cumpre, é hamiltoniano; se falha, não se sabe.", "Hamiltonianos"),
    ("Num grafo com V = 15, a condição de Dirac exige grau mínimo:", [
        ("8", C),
        ("7", "7 < 7,5: não chega. Não se arredonda para baixo."),
        ("15", "Seria impossível num grafo simples (máximo V − 1 = 14)."),
        ("14", "Isso seria o grafo completo; Dirac pede só metade."),
     ], "V/2 = 7,5 e o grau é inteiro, por isso tem de ser ≥ 8.", "Hamiltonianos"),
    ("Regra 1 da procura de ciclos hamiltonianos: se v tem grau 2...", [
        ("as duas arestas de v têm de estar no ciclo", C),
        ("v pode ser ignorado", "O ciclo tem de passar por todos os vértices, incluindo v."),
        ("nenhuma aresta de v entra no ciclo", "Então nunca se visitaria v."),
        ("o grafo não é hamiltoniano", "Ter grau 2 não impede (um ciclo simples tem todos de grau 2)."),
     ], "Para entrar e sair de v só há aquelas duas arestas.", "Hamiltonianos"),
    ("Regra 3: se duas arestas incidentes em v já estão no ciclo, então:", [
        ("as restantes arestas de v podem ser apagadas", C),
        ("acrescenta-se mais uma", "Num ciclo cada vértice usa exatamente 2 arestas."),
        ("o ciclo está completo", "Só v está resolvido; faltam os outros vértices."),
        ("v tem grau 2", "v pode ter mais arestas; essas é que deixam de servir."),
     ], "Num ciclo hamiltoniano cada vértice usa exatamente 2 arestas.", "Hamiltonianos"),
    ("Um grafo bipartido com |V1| = 7 e |V2| = 8:", [
        ("não tem ciclo hamiltoniano", C),
        ("tem sempre ciclo hamiltoniano", "Um ciclo alterna V1, V2, V1… e precisa de tantos de um lado como do outro."),
        ("tem ciclo euleriano", "A paridade dos graus não depende disso."),
        ("não é planar", "Pode perfeitamente ser planar (o G1 do Ricardo é assim)."),
     ], "Num ciclo hamiltoniano de um bipartido os lados alternam, logo |V1| = |V2|.", "Hamiltonianos"),
    ("Fórmula de Euler (grafo planar conexo):", [
        ("V − A + F = 2", C),
        ("V + A − F = 2", "Sinais trocados. Confirma com um triângulo: 3 − 3 + 2 = 2."),
        ("A = 3V − 6", "Isso é o máximo de arestas, não a fórmula de Euler."),
        ("V − A = F", "Falta o 2: no triângulo 3 − 3 = 0 ≠ 2 faces."),
     ], "Truque: triângulo, 3 vértices − 3 arestas + 2 faces = 2.", "Planares"),
    ("Antes de usar V − A + F = 2 tens de garantir que o grafo é:", [
        ("planar e conexo", C),
        ("completo", "K5 é completo e nem sequer é planar."),
        ("bipartido", "Não é condição da fórmula."),
        ("euleriano", "Não é condição da fórmula."),
     ], "Sem desenho plano não há faces; sem ser conexo a fórmula muda (1 + nº de componentes).", "Planares"),
    ("A soma dos graus das faces de um grafo planar é igual a:", [
        ("2A", C),
        ("A", "Cada aresta tem dois lados e é contada em cada um."),
        ("2V", "Isso não é nenhuma regra; Σ deg(v) é que dá 2A."),
        ("F", "Seria só se cada face tivesse grau 1."),
     ], "Cada aresta separa 2 faces (ou a mesma dos dois lados): conta 2.", "Planares"),
    ("Na fórmula de Euler, a face exterior:", [
        ("conta como uma face", C),
        ("não conta", "Erro clássico. No triângulo só dá 2 contando a de fora."),
        ("conta duas vezes", "Conta uma vez."),
        ("só conta se o grafo for completo", "Conta sempre."),
     ], "F inclui sempre a região de fora do desenho.", "Planares"),
    ("Se G é simples, conexo, V ≥ 3 e A > 3V − 6, então:", [
        ("G não é planar", C),
        ("G é planar", "É o contrário: ultrapassou o máximo de arestas de um planar."),
        ("G é bipartido", "Não tem relação."),
        ("nada se conclui", "Aqui conclui-se: um planar teria A ≤ 3V − 6."),
     ], "Corolário 4'.", "Planares"),
    ("G simples, conexo, 7 vértices e 14 arestas. Pelo corolário de Euler:", [
        ("nada se conclui (14 ≤ 15)", C),
        ("não é planar", "14 não ultrapassa 3V − 6 = 15."),
        ("é planar", "Cumprir A ≤ 3V − 6 não prova que é planar."),
        ("é completo", "K7 teria 21 arestas."),
     ], "O corolário só serve quando A > 3V − 6.", "Planares"),
    ("K5 não é planar porque:", [
        ("A = 10 > 3 × 5 − 6 = 9", C),
        ("não tem ciclo hamiltoniano", "K5 tem ciclo hamiltoniano, e isso nada tem a ver com planaridade."),
        ("é bipartido", "K5 tem triângulos, logo não é bipartido."),
        ("tem vértices de grau ímpar", "Todos os vértices de K5 têm grau 4 (par)."),
     ], "Corolário com V = 5.", "Planares"),
    ("K3,3 não é planar porque:", [
        ("não tem triângulos e 9 > 2 × 6 − 4 = 8", C),
        ("9 > 3 × 6 − 6", "3 × 6 − 6 = 12 e 9 não é maior: por aí não se conclui."),
        ("tem grau 3", "Há grafos planares 3-regulares (ex.: o cubo)."),
        ("não é conexo", "K3,3 é conexo."),
     ], "Lema 5' para grafos sem triângulos.", "Planares"),
    ("Um desenho de G tem duas arestas a cruzar-se. Então:", [
        ("nada se conclui: pode existir outro desenho sem cruzamentos", C),
        ("G não é planar", "Planar é ADMITIR um desenho sem cruzamentos; este pode ser só um mau desenho (ex.: K4)."),
        ("G é planar", "Também não se sabe."),
        ("G não é conexo", "Não tem relação."),
     ], "K4 desenhado como quadrado com diagonais cruza, mas é planar.", "Planares"),
    ("No método cíclico, duas cordas são incompatíveis quando:", [
        ("as suas extremidades alternam ao longo do ciclo", C),
        ("partilham um vértice", "Cordas que partilham um vértice nunca se cruzam."),
        ("têm o mesmo peso", "Não há pesos no método cíclico."),
        ("são paralelas", "Paralelas no desenho não se cruzam."),
     ], "Se alternam (a, c, b, d), cruzam-se se ficarem do mesmo lado.", "Planares"),
    ("No método cíclico, o grafo é planar se:", [
        ("todas as cordas couberem em A (dentro) ou B (fora) sem conflitos", C),
        ("o ciclo for euleriano", "O método usa um ciclo hamiltoniano, e a conclusão vem das cordas."),
        ("L tiver mais de 3 arestas", "O número de cordas não decide."),
        ("houver um triângulo de incompatibilidades", "Isso prova o contrário: NÃO é planar."),
     ], "L fica vazio ⇒ planar. Três cordas mutuamente incompatíveis ⇒ não planar.", "Planares"),
    ("Γ(v) (com parênteses), num grafo, é:", [
        ("o conjunto dos vizinhos de v", C),
        ("o fecho transitivo de v", "O fecho escreve-se Γv, com índice."),
        ("o grau de v", "O grau é deg(v), um número; Γ(v) é um conjunto."),
        ("o conjunto das arestas de v", "São vértices, não arestas."),
     ], "Γ(3) = {2, 4, 8} são os vizinhos de 3.", "Fecho transitivo"),
    ("Γv (fecho transitivo direto) é:", [
        ("o conjunto dos vértices atingíveis a partir de v, incluindo v", C),
        ("o conjunto dos vizinhos de v", "Esses são só os do 1º passo; o fecho vai até ao fim."),
        ("os vértices que chegam a v", "Isso é Γ⁻¹v (fecho inverso)."),
        ("os sucessores imediatos de v", "Isso é Γ⁺(v)."),
     ], "Por caminhos de qualquer comprimento, seguindo as setas.", "Fecho transitivo"),
    ("Γ⁻¹v é:", [
        ("o conjunto dos vértices a partir dos quais se atinge v", C),
        ("os antecessores imediatos de v", "Esses são Γ⁻(v), só o 1º passo."),
        ("os vértices não ligados a v", "Não é um complementar."),
        ("o complementar de Γv", "Pode haver vértices nos dois (a componente de v)."),
     ], "Fecho transitivo inverso: anda-se contra as setas.", "Fecho transitivo"),
    ("A componente fortemente conexa que contém v é:", [
        ("Γv ∩ Γ⁻¹v", C),
        ("Γv ∪ Γ⁻¹v", "A união inclui vértices que só vão (ou só vêm) num sentido."),
        ("Γ⁺(v)", "São só os sucessores diretos."),
        ("Γv \\ Γ⁻¹v", "Retira exatamente os que interessam."),
     ], "Vértices que v atinge E que atingem v.", "Fecho transitivo"),
    ("Um digrafo tem um vértice com deg⁺ = 0. Então:", [
        ("não é fortemente conexo", C),
        ("é fortemente conexo", "Desse vértice não se chega a lado nenhum."),
        ("não é conexo", "Pode ser conexo (o grafo subjacente ligar tudo)."),
        ("tem circuito euleriano", "Nesse vértice deg⁺ ≠ deg⁻ (se tiver entradas)."),
     ], "Para ser fortemente conexo é preciso sair de todos os vértices.", "Digrafos"),
    ("\"O Sr. João chegou ao Hospital. De onde pode ter vindo?\" pede:", [
        ("Γ⁻¹ do Hospital", C),
        ("Γ do Hospital", "Γ diz para onde se pode ir A PARTIR do Hospital."),
        ("Γ⁻(Hospital) apenas", "Só dá o último passo; ele pode ter vindo de mais longe."),
        ("Dijkstra", "Não se pede um percurso mínimo."),
     ], "De onde se chega a v = fecho transitivo inverso.", "Digrafos"),
    ("Na matriz booleana de um digrafo, deg⁺(vᵢ) é:", [
        ("a soma da linha i", C),
        ("a soma da coluna i", "A coluna conta as entradas: deg⁻."),
        ("o elemento bᵢᵢ", "bᵢᵢ só indica um lacete."),
        ("o total de 1s", "O total dá o número de arcos."),
     ], "Linha = arcos que saem; coluna = arcos que entram.", "Matrizes"),
    ("Numa matriz de adjacência de um grafo, um lacete em vᵢ conta no grau:", [
        ("2 vezes (deg(vᵢ) = 2aᵢᵢ + Σ aᵢⱼ)", C),
        ("1 vez", "O lacete tem as duas pontas em vᵢ."),
        ("0 vezes", "Conta, e conta a dobrar."),
        ("depende", "Há regra fixa: 2 vezes."),
     ], "Fórmula dos slides.", "Matrizes"),
    ("Uma árvore com V vértices tem:", [
        ("V − 1 arestas", C),
        ("V arestas", "Com V arestas já haveria um ciclo."),
        ("V + 1 arestas", "Ainda mais arestas: ciclos."),
        ("2V − 4 arestas", "Isso é o limite de planares sem triângulos."),
     ], "Árvore = conexo e sem ciclos ⇒ A = V − 1.", "Redes"),
    ("O algoritmo de Prim:", [
        ("junta à árvore, em cada passo, o vértice ligado pela aresta de menor peso", C),
        ("ordena todas as arestas e aceita as que não formam ciclo", "Isso é Kruskal."),
        ("calcula o caminho mais curto entre dois vértices", "Isso é Dijkstra."),
        ("procura ciclos eulerianos", "Não tem a ver."),
     ], "Prim cresce a partir de uma raiz, como uma planta.", "Redes"),
    ("O algoritmo de Kruskal rejeita uma aresta quando:", [
        ("forma um ciclo com as já escolhidas", C),
        ("tem peso maior que a anterior", "As arestas já vêm ordenadas por peso; isso é normal."),
        ("liga um vértice de grau 1", "Não é critério."),
        ("já há V arestas", "Pára-se com V − 1, e o critério de rejeição é o ciclo."),
     ], "Uma árvore não tem ciclos.", "Redes"),
    ("\"Ligar todas as cidades com o menor custo total\" resolve-se com:", [
        ("árvore geradora mínima (Prim/Kruskal)", C),
        ("Dijkstra", "Dijkstra liga só DOIS pontos (origem e destino)."),
        ("ciclo euleriano", "Isso percorre todas as estradas, não minimiza a rede."),
        ("fecho transitivo", "Isso diz quem se alcança, não custos."),
     ], "Extensão mínima ≠ percurso mínimo.", "Redes"),
    ("\"O caminho mais curto de A até B\" resolve-se com:", [
        ("Dijkstra", C),
        ("Kruskal", "Kruskal liga todos os vértices, não procura um caminho."),
        ("Prim", "Prim também é árvore geradora."),
        ("método cíclico", "Isso é planaridade."),
     ], "Problema de percurso mínimo.", "Redes"),
    ("\"Número mínimo de ligações (túneis) de X para Y\" resolve-se:", [
        ("contando arestas por camadas, sem olhar aos pesos", C),
        ("com Dijkstra pelos pesos", "Os pesos medem distância ou custo, não o número de ligações."),
        ("com a árvore geradora mínima", "A árvore liga todos, não responde a X → Y."),
        ("com a fórmula de Euler", "Não tem a ver."),
     ], "Pergunta-se o número de arestas, não a distância.", "Redes"),
    ("No algoritmo de Dijkstra, em cada iteração torna-se permanente:", [
        ("a etiqueta temporária de menor valor", C),
        ("a primeira por ordem alfabética", "A ordem só serve para desempatar."),
        ("a de maior valor", "É a menor."),
        ("todas as adjacentes", "Só uma por iteração."),
     ], "Passo 3 do algoritmo.", "Redes"),
    ("Uma rota que percorre todas as ruas uma única vez e volta ao início é um problema de:", [
        ("ciclo euleriano", C),
        ("ciclo hamiltoniano", "Hamilton é sobre vértices (cruzamentos), não sobre ruas."),
        ("árvore geradora", "Não se trata de minimizar uma rede."),
        ("Dijkstra", "Não há origem e destino diferentes."),
     ], "Todas as ARESTAS uma vez ⇒ Euler (Estradas).", "Eulerianos"),
    ("Visitar todas as localidades uma única vez e voltar ao início é um problema de:", [
        ("ciclo hamiltoniano", C),
        ("ciclo euleriano", "Euler é sobre as ligações, não sobre as localidades."),
        ("árvore geradora mínima", "Uma árvore não volta ao início (não tem ciclos)."),
        ("planaridade", "Não tem a ver."),
     ], "Todos os VÉRTICES uma vez ⇒ Hamilton (Hotéis).", "Hamiltonianos"),
]


def numericas(rng):
    out = []
    for _ in range(8):
        n = rng.randint(5, 12); certo = n * (n - 1) // 2
        ops = [(str(certo), C), (str(n * (n - 1)), "Contaste cada aresta duas vezes (uma por cada ponta); falta dividir por 2."),
               (str(n * n), "n × n contaria lacetes e cada aresta duas vezes."), (str(2 * n - 1), "Não corresponde a nenhuma regra de Kn.")]
        out.append((f"Quantas arestas tem K{n}?", ops, f"n(n − 1)/2 = {n} × {n - 1} / 2 = {certo}.", "Completos"))
    for _ in range(8):
        n = rng.randint(5, 14); lim = 3 * n - 6
        ops = [(str(lim), C), (str(2 * n - 4), "2V − 4 é o limite só para grafos sem triângulos."),
               (str(n * (n - 1) // 2), "Esse é o número de arestas de K" + str(n) + ", que não é planar para V ≥ 5."), (str(3 * n), "Falta o − 6: 3V − 6.")]
        out.append((f"Um grafo simples planar com {n} vértices tem no máximo quantas arestas?", ops, f"A ≤ 3V − 6 = 3 × {n} − 6 = {lim}.", "Planares"))
    for _ in range(8):
        m = rng.randint(9, 40); f = rng.randint(4, m - 3); n = 2 + m - f
        if n < 3:
            continue
        ops = [(str(n), C), (str(m - f), "Esqueceste o + 2: V = 2 + A − F."), (str(m + f - 2), "Sinal da face trocado: V = 2 + A − F."), (str(n + 2), "Somaste o 2 duas vezes.")]
        out.append((f"Grafo planar conexo com {m} arestas e {f} faces. Quantos vértices?", ops, f"V − A + F = 2 ⇒ V = 2 + {m} − {f} = {n}.", "Planares"))
    for _ in range(6):
        k = rng.choice([3, 5, 7]); n = rng.choice([5, 7, 9, 11])
        ops = [("Não: a soma dos graus seria ímpar", C), ("Sim", f"Σ deg = {n} × {k} = {n * k} é ímpar, mas tem de ser 2A (par)."),
               ("Só se for planar", "A paridade da soma dos graus não depende de ser planar."), ("Só se for bipartido", "A paridade da soma dos graus não depende de ser bipartido.")]
        out.append((f"É possível um grafo com {n} vértices, todos de grau {k}?", ops, f"Σ deg = {n} × {k} = {n * k}, ímpar, mas Σ deg = 2A é sempre par.", "Graus"))
    for _ in range(6):
        n = rng.randint(6, 12); d = rng.randint(2, n - 1); ok = d >= n / 2
        ops = [("Sim", C if ok else f"Grau mínimo {d} < V/2 = {n / 2:g}: há pelo menos um vértice que falha."),
               ("Não se verifica", f"Grau mínimo {d} ≥ V/2 = {n / 2:g}: todos os vértices cumprem." if ok else C)]
        out.append((f"G simples e conexo com {n} vértices e grau mínimo {d}. A condição de Dirac verifica-se?", ops,
                    f"É preciso deg(v) ≥ V/2 = {n / 2:g} em todos. Grau mínimo {d} {'≥' if ok else '<'} {n / 2:g}.", "Hamiltonianos"))
    return out


def gerar(grupo, seed=2026):
    rng = random.Random(seed)
    qs = []
    for i, (enun, ops, expl, tema) in enumerate(BASE + numericas(rng)):
        assert sum(1 for _, p in ops if p is None) == 1, enun
        qs.append(dict(id=f"mc-{i}", grupo=grupo, tipo="escolha", tema=tema, enunciado=enun,
                       opcoes=[o for o, _ in ops], correta=next(j for j, (_, p) in enumerate(ops) if p is None),
                       porque=[p for _, p in ops], explicacao=expl))
    return qs
