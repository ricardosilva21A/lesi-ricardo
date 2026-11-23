// Lógica partilhada das notas (página inicial e /notas/). Notas guardadas só no dispositivo.
(function () {
  const K = "notas";
  const load = () => { try { return JSON.parse(localStorage.getItem(K)) || {}; } catch { return {}; } };
  const save = n => { try { localStorage.setItem(K, JSON.stringify(n)); } catch {} };

  const tem = v => v !== undefined && v !== null && v !== "";

  // nó: { id, nome, peso, min?, filhos?, avaliacao? }. Valor = a + b·g (g = nota igual em tudo o que falta)
  function linear(node, notasUC) {
    if (!node.filhos) {
      const v = notasUC?.[node.id];
      return tem(v) ? { a: +v, b: 0, falta: [] } : { a: 0, b: 1, falta: [node] };
    }
    const tot = node.filhos.reduce((s, f) => s + f.peso, 0);
    let a = 0, b = 0, falta = [];
    node.filhos.forEach(f => { const r = linear(f, notasUC); a += r.a * f.peso / tot; b += r.b * f.peso / tot; falta.push(...r.falta); });
    return { a, b, falta };
  }

  function analisa(uc, notas) {
    const nUC = notas[uc.sigla] || {};
    const raiz = { id: "final", nome: "Nota final", filhos: uc.avaliacao };
    const fin = linear(raiz, nUC);
    let gMin = 0; const falhados = [];
    (function walk(n) {
      if (n.min !== undefined && n.min !== null) {
        const r = linear(n, nUC);
        if (r.b === 0) { if (r.a < n.min) falhados.push(`${n.nome}: ${fmt(r.a)} < mínimo ${n.min}`); }
        else gMin = Math.max(gMin, (n.min - r.a) / r.b);
      }
      (n.filhos || []).forEach(walk);
    })(raiz);
    const lancadas = Object.values(nUC).filter(tem).length;
    return { fin, gMin, falhados, lancadas };
  }

  const precisa = (r, alvo) => r.fin.b === 0 ? null : Math.max(r.gMin, (alvo - r.fin.a) / r.fin.b, 0);
  const fmt = x => (Math.round(x * 100) / 100).toLocaleString("pt-PT", { maximumFractionDigits: 2 });

  // avaliação do calendário → { uc, folha }
  function ligacoes(D) {
    const m = {};
    D.ucs.forEach(u => (function walk(ns) { (ns || []).forEach(n => { if (n.avaliacao) m[n.avaliacao] = { uc: u, folha: n }; walk(n.filhos); }); })(u.avaliacao));
    return m;
  }

  // Plano realista: cada avaliação em falta recebe max(g, piso), em que o piso garante as notas mínimas.
  // Devolve { possivel, itens: [{folha, nota}] } com o menor g que chega ao alvo.
  function plano(uc, notas, alvo) {
    const nUC = notas[uc.sigla] || {};
    const raiz = { id: "final", nome: "Nota final", filhos: uc.avaliacao };
    const folhas = [];
    (function w(n) { if (!n.filhos) { if (!tem(nUC[n.id])) folhas.push(n); } else n.filhos.forEach(w); })(raiz);
    if (!folhas.length) return null;
    const piso = Object.fromEntries(folhas.map(f => [f.id, f.min != null ? f.min : 0]));
    const valor = (n, g) => {
      if (!n.filhos) return tem(nUC[n.id]) ? +nUC[n.id] : Math.max(g, piso[n.id]);
      const tot = n.filhos.reduce((s, f) => s + f.peso, 0);
      return n.filhos.reduce((s, f) => s + valor(f, g) * f.peso / tot, 0);
    };
    const procura = (fn) => { // menor g em [0,20] com fn(g) verdadeiro
      if (!fn(20)) return null;
      let lo = 0, hi = 20;
      if (fn(0)) return 0;
      for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (fn(m)) hi = m; else lo = m; }
      return hi;
    };
    let ok = true;
    // pisos dos nós intermédios com mínimo (de baixo para cima)
    (function w(n) {
      (n.filhos || []).forEach(w);
      if (n.filhos && n.min != null) {
        const minhas = []; (function c(x) { if (!x.filhos) { if (piso[x.id] !== undefined) minhas.push(x.id); } else x.filhos.forEach(c); })(n);
        if (!minhas.length) return;
        const save = Object.fromEntries(minhas.map(id => [id, piso[id]]));
        const h = procura(g => { minhas.forEach(id => piso[id] = Math.max(save[id], g)); const v = valor(n, 0); minhas.forEach(id => piso[id] = save[id]); return v >= n.min - 1e-9; });
        if (h === null) { ok = false; return; }
        minhas.forEach(id => piso[id] = Math.max(save[id], h));
      }
    })(raiz);
    if (!ok || Object.values(piso).some(p => p > 20)) return { possivel: false, itens: [] };
    const g = procura(x => valor(raiz, x) >= alvo - 1e-9);
    if (g === null) return { possivel: false, itens: [] };
    return { possivel: true, itens: folhas.map(f => ({ folha: f, nota: Math.ceil(Math.max(g, piso[f.id]) * 100 - 1e-6) / 100 })) };
  }

  const planoTxt = p => !p ? "" : !p.possivel ? `<b class="bad">impossível</b>` : p.itens.map(i => `${i.folha.nome.toLowerCase()} <b>${fmt(i.nota)}</b>`).join(" · ");
  window.Notas = { planoTxt, load, save, tem, linear, analisa, precisa, plano, fmt, ligacoes };
})();
