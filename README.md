# lesi-ricardo

Calendário de testes e trabalhos, com subscrição para o calendário do telemóvel e páginas de estudo.

Site: https://lesi-ricardo.vercel.app

## Adicionar ou mudar uma avaliação

Edita o ficheiro `avaliacoes.json` (dá para fazer no github.com, no lápis ✏️) e faz commit. O Vercel publica sozinho em cerca de 30 segundos, e o calendário subscrito atualiza a seguir.

```json
{ "id": "md-t2", "uc": "MD", "tipo": "teste", "titulo": "2º teste", "data": "2026-11-28", "hora": "18:30", "local": "Sala B204", "notas": "", "estudo": "md-t2" }
```

| Campo | O que é |
|---|---|
| `id` | Único, sem espaços. Não mudar depois de subscrito, senão o evento duplica. |
| `uc` | Sigla igual à da lista `ucs`. |
| `tipo` | `teste` ou `trabalho`. |
| `data` | `AAAA-MM-DD`. |
| `hora` | `HH:MM` ou vazio (fica como evento de dia inteiro). |
| `estudo` | Vazio, o nome de um banco (`md-t2` abre `/estudo/?banco=md-t2`) ou o caminho de um HTML próprio (`estudo/paginas/md.html`). |

Se algo estiver mal escrito (UC inexistente, data errada), o build falha e o site antigo mantém-se no ar.

## Método de avaliação (página /notas/)

Cada UC em `ucs` pode ter um campo `avaliacao` com as componentes. Os pesos são relativos dentro de cada nível, `min` é a nota mínima e `avaliacao` liga à data no calendário (opcional). As notas que escreves no site ficam só no teu dispositivo.

```json
"avaliacao": [
  { "id": "T", "nome": "Testes", "peso": 85, "filhos": [
    { "id": "t1", "nome": "1º teste", "peso": 35 },
    { "id": "t2", "nome": "2º teste", "peso": 30, "avaliacao": "md-t2" },
    { "id": "t3", "nome": "3º teste", "peso": 35, "min": 7, "avaliacao": "md-t3" } ] },
  { "id": "tg", "nome": "Trabalho de grupo", "peso": 15 }
]
```

A calculadora assume a mesma nota em todas as avaliações que faltam e respeita as notas mínimas.

## Bancos de estudo

Cada banco é um ficheiro em `src/estudo/bancos/<nome>.json`. Aparece sozinho na página `/estudo/`. O motor faz testes modelo aleatórios a partir da `estrutura`, treino uma a uma, repetição das erradas e histórico de notas (guardado no dispositivo).

```json
{
  "uc": "MD",
  "titulo": "2º teste",
  "estrutura": [
    { "grupo": "Grupo 1", "n": 10, "cotacao": 10 },
    { "grupo": "Grupo 2", "n": 2, "cotacao": 6 },
    { "grupo": "Grupo 3", "n": 1, "cotacao": 4 }
  ],
  "perguntas": [
    { "grupo": "Grupo 1", "tipo": "escolha", "tema": "Lógica", "enunciado": "…", "opcoes": ["…", "…", "…", "…"], "correta": 0, "explicacao": "…" },
    { "grupo": "Grupo 2", "tipo": "aberta", "tema": "Esquema", "enunciado": "…", "resolucao": "…", "imagem": "" }
  ]
}
```

- `correta` é o índice da opção certa, a contar do 0. As opções são baralhadas em cada tentativa.
- `aberta` serve para esquemas e desenhos: mostra o enunciado, depois a resolução, e autoavalias.
- `afirmacoes` é o formato «escolhe as corretas»: lista `afirmacoes` com `{ "v": true/false, "texto", "porque" }`. Cada certa escolhida vale 1, cada errada desconta 0,5, escolher todas anula. Com `mostrar` e `certas` (ex.: 5 e 2) o motor sorteia afirmações diferentes em cada tentativa.
- `vf` é uma lista de afirmações para classificar: `rotulos` (por omissão Verdadeiro/Falso, mas pode ser ex. RISC/CISC), `itens` com `{ "texto", "r": índice do rótulo certo, "porque" }` e `mostrar` opcional.
- As afirmações de `afirmacoes` e `vf` aparecem também no modo «Afirmações uma a uma».
- Fórmulas em LaTeX entre `$...$` (escrever `\\` no JSON). Pode-se usar HTML, tabelas e SVG.
- Põe mais perguntas do que o `n` de cada grupo para os testes modelo variarem.

Para uma página de estudo HTML feita à parte, mete-a em `src/estudo/paginas/` e aponta o campo `estudo` para ela.

Prompt para gerar um banco com o Claude:

> Com base nestes PowerPoints, gera um banco de perguntas em JSON no formato do README do repositório lesi-ricardo para a UC X, teste Y. Estrutura: grupo 1 com N escolhas múltiplas, grupo 2 com ... Quero pelo menos 3 vezes mais perguntas do que as de um teste, com explicação em todas.

## Estrutura

- `avaliacoes.json` · dados
- `src/` · páginas (index e estudo)
- `build.js` · gera `public/` e o `calendario.ics` (corre no Vercel)
