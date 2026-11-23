// Gera a pasta public/ a partir de src/ e de avaliacoes.json.
// Corre no Vercel a cada push (node build.js). Sem dependências.
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const OUT = path.join(ROOT, "public");
const dados = JSON.parse(fs.readFileSync(path.join(ROOT, "avaliacoes.json"), "utf8"));

// ---------- validação simples ----------
const siglas = new Set(dados.ucs.map((u) => u.sigla));
const ids = new Set();
for (const a of dados.avaliacoes) {
  if (!siglas.has(a.uc)) throw new Error(`UC desconhecida "${a.uc}" em ${a.id}`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(a.data)) throw new Error(`Data inválida em ${a.id}: ${a.data} (usar AAAA-MM-DD)`);
  if (a.hora && !/^\d{2}:\d{2}$/.test(a.hora)) throw new Error(`Hora inválida em ${a.id}: ${a.hora} (usar HH:MM)`);
  if (!["teste", "trabalho"].includes(a.tipo)) throw new Error(`Tipo inválido em ${a.id}: usar "teste" ou "trabalho"`);
  if (ids.has(a.id)) throw new Error(`id repetido: ${a.id}`);
  ids.add(a.id);
}

// método de avaliação: pesos positivos, ids únicos dentro da UC
for (const u of dados.ucs) {
  if (!u.avaliacao) continue;
  const vistos = new Set();
  (function walk(nos, onde) {
    for (const n of nos) {
      if (!n.id || !(n.peso > 0)) throw new Error(`Avaliação de ${u.sigla}: cada componente precisa de "id" e "peso" > 0 (${onde})`);
      if (vistos.has(n.id)) throw new Error(`Avaliação de ${u.sigla}: id repetido "${n.id}"`);
      vistos.add(n.id);
      if (n.avaliacao && !ids.has(n.avaliacao)) throw new Error(`Avaliação de ${u.sigla}: "${n.avaliacao}" não existe nas avaliações`);
      if (n.filhos) walk(n.filhos, n.nome);
    }
  })(u.avaliacao, "raiz");
}

// ---------- copiar src/ ----------
fs.rmSync(OUT, { recursive: true, force: true });
fs.cpSync(path.join(ROOT, "src"), OUT, { recursive: true });
fs.copyFileSync(path.join(ROOT, "avaliacoes.json"), path.join(OUT, "avaliacoes.json"));

// ---------- lista de bancos de estudo ----------
const dirBancos = path.join(OUT, "estudo", "bancos");
const bancos = fs.existsSync(dirBancos)
  ? fs.readdirSync(dirBancos)
      .filter((f) => f.endsWith(".json") && f !== "index.json")
      .map((f) => {
        const b = JSON.parse(fs.readFileSync(path.join(dirBancos, f), "utf8"));
        return { id: f.replace(/\.json$/, ""), uc: b.uc || "", titulo: b.titulo || f, perguntas: (b.perguntas || []).length };
      })
  : [];
if (fs.existsSync(dirBancos)) fs.writeFileSync(path.join(dirBancos, "index.json"), JSON.stringify(bancos, null, 2));

// ---------- calendário .ics ----------
const esc = (s) => String(s || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
const fold = (l) => {
  const out = [];
  while (Buffer.byteLength(l) > 74) {
    let i = 74;
    while (Buffer.byteLength(l.slice(0, i)) > 74) i--;
    out.push(l.slice(0, i));
    l = " " + l.slice(i);
  }
  out.push(l);
  return out.join("\r\n");
};
const ymd = (d) => d.replace(/-/g, "");
const nextDay = (d) => {
  const t = new Date(d + "T00:00:00Z");
  t.setUTCDate(t.getUTCDate() + 1);
  return t.toISOString().slice(0, 10).replace(/-/g, "");
};
const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
const nomeUC = Object.fromEntries(dados.ucs.map((u) => [u.sigla, u.nome]));

const linhas = [
  "BEGIN:VCALENDAR",
  "VERSION:2.0",
  "PRODID:-//lesi-ricardo//avaliacoes//PT",
  "CALSCALE:GREGORIAN",
  "METHOD:PUBLISH",
  `X-WR-CALNAME:${esc(dados.titulo)}`,
  "X-WR-TIMEZONE:Europe/Lisbon",
  "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
  "X-PUBLISHED-TTL:PT6H",
  "BEGIN:VTIMEZONE",
  "TZID:Europe/Lisbon",
  "BEGIN:DAYLIGHT",
  "TZOFFSETFROM:+0000",
  "TZOFFSETTO:+0100",
  "TZNAME:WEST",
  "DTSTART:19700329T010000",
  "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU",
  "END:DAYLIGHT",
  "BEGIN:STANDARD",
  "TZOFFSETFROM:+0100",
  "TZOFFSETTO:+0000",
  "TZNAME:WET",
  "DTSTART:19701025T020000",
  "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU",
  "END:STANDARD",
  "END:VTIMEZONE",
];

for (const a of dados.avaliacoes) {
  const tipo = a.tipo === "teste" ? "Teste" : "Trabalho";
  const desc = [`${nomeUC[a.uc]} (${tipo})`, a.notas, a.estudo ? `Estudar: ${dados.url}/${a.estudo.endsWith(".html") ? a.estudo : "estudo/?banco=" + a.estudo}` : ""]
    .filter(Boolean)
    .join("\n");
  linhas.push("BEGIN:VEVENT", `UID:${a.id}@lesi-ricardo`, `DTSTAMP:${stamp}`);
  if (a.hora) {
    const [h, m] = a.hora.split(":").map(Number);
    const fim = `${String(h + 2).padStart(2, "0")}${String(m).padStart(2, "0")}00`;
    linhas.push(`DTSTART;TZID=Europe/Lisbon:${ymd(a.data)}T${a.hora.replace(":", "")}00`, `DTEND;TZID=Europe/Lisbon:${ymd(a.data)}T${fim}`);
  } else {
    linhas.push(`DTSTART;VALUE=DATE:${ymd(a.data)}`, `DTEND;VALUE=DATE:${nextDay(a.data)}`, "TRANSP:TRANSPARENT");
  }
  linhas.push(`SUMMARY:${esc(`${a.uc} · ${a.titulo}`)}`, `DESCRIPTION:${esc(desc)}`, `CATEGORIES:${tipo}`);
  if (a.local) linhas.push(`LOCATION:${esc(a.local)}`);
  linhas.push(
    "BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${esc(`${a.uc} · ${a.titulo}`)}`, "TRIGGER:-P2D", "END:VALARM",
    "END:VEVENT"
  );
}
linhas.push("END:VCALENDAR");
fs.writeFileSync(path.join(OUT, "calendario.ics"), linhas.map(fold).join("\r\n") + "\r\n");

console.log(`OK: ${dados.avaliacoes.length} avaliações, ${bancos.length} banco(s) de estudo.`);
