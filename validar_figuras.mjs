#!/usr/bin/env node
/**
 * Geometria das figuras SVG, a 400 px, nos dois temas.
 *
 * 🔴 PORQUE EXISTE. O registo de falhas do PROCESSO.md pede este passo três
 * vezes, e três vezes ficou escrito «continua a ser um passo manual»:
 *
 *   2026-09-15 · abstracts-e-resumos — «o axe passou a 400 px, mas quatro
 *     diagramas tinham texto cortado, sobreposto ou desatualizado»
 *   2026-09-16 · cassete-dados — «cinco de nove figuras estavam mal a 400 px»
 *   2026-09-16 · cassete-captura — «uma figura nova saiu VAZIA (chaves
 *     duplicadas numa f-string) e o axe passou na mesma»
 *
 * O axe mede contraste e nomes acessíveis. Não mede geometria: não sabe que um
 * `<text>` saiu fora do `viewBox`, que dois rótulos ficaram um por cima do
 * outro, ou que uma figura está vazia. Este passo mede isso.
 *
 * O que NÃO substitui: olhar para a imagem. Ao criar o tópico `almanaque`, três
 * figuras passaram todas as verificações automáticas e estavam visualmente más.
 * Este script apanha a classe de erros que é mecânica; o resto continua a exigir
 * uma captura e um par de olhos — e é por isso que ele grava os PNG.
 *
 * Uso:
 *   node validar_figuras.mjs docs/<slug>            # uma pasta
 *   node validar_figuras.mjs docs/*\/ modelo        # várias
 *   CAPTURAS=/caminho node validar_figuras.mjs ...  # e grava os PNG lá
 *
 * Sai 1 se encontrar problemas.
 */
import puppeteer from "puppeteer";
import path from "node:path";
import process from "node:process";
import { readdirSync, mkdirSync, statSync, existsSync } from "node:fs";

// O mesmo Chrome que o validar_a11y.mjs procura, pela mesma razão: o que o
// puppeteer descarrega vem sem assinatura e o macOS ARM mata-o.
function encontrarChrome() {
  if (process.env.CHROME_PARA_VALIDAR) return process.env.CHROME_PARA_VALIDAR;
  const c = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  ];
  for (const x of c) if (existsSync(x)) return x;
  return undefined;
}

const alvos = process.argv.slice(2);
if (!alvos.length) {
  console.error("uso: node validar_figuras.mjs <pasta> [<pasta>...]");
  process.exit(2);
}
const CAPTURAS = process.env.CAPTURAS || "";
if (CAPTURAS) mkdirSync(CAPTURAS, { recursive: true });

const paginas = [];
for (const alvo of alvos) {
  let st;
  try { st = statSync(alvo); } catch { continue; }
  if (st.isDirectory()) {
    for (const f of readdirSync(alvo)) {
      if (f.endsWith(".html")) paginas.push(path.join(alvo, f));
    }
  } else if (alvo.endsWith(".html")) {
    paginas.push(alvo);
  }
}

const exe = encontrarChrome();
const navegador = await puppeteer.launch(exe ? { executablePath: exe } : {});
let problemas = 0, figuras = 0;

for (const pag of paginas) {
  const url = "file:///" + path.resolve(pag).replace(/\\/g, "/");
  for (const tema of ["claro", "escuro"]) {
    const p = await navegador.newPage();
    await p.setViewport({ width: 400, height: 900, deviceScaleFactor: 2 });
    await p.goto(url, { waitUntil: "networkidle0" });
    await p.evaluate((t) => document.documentElement.setAttribute("data-tema", t), tema);

    const rel = await p.evaluate(() => {
      const fora = [];
      document.querySelectorAll("figure svg").forEach((svg, i) => {
        const vb = (svg.getAttribute("viewBox") || "0 0 0 0").split(/\s+/).map(Number);
        const [vx, vy, vw, vh] = vb;
        const caixas = [];
        for (const t of svg.querySelectorAll("text")) {
          const s = (t.textContent || "").trim();
          if (!s) continue;
          // Marcador de substituição que sobreviveu à geração — a falha de
          // 2026-09-16 (cassete-captura), em que o SVG saiu com "{x0}" escrito.
          if (/\{[a-z_0-9]+\}/i.test(s)) fora.push({ i, tipo: "chave-nao-substituida", texto: s });
          let bb;
          try { bb = t.getBBox(); } catch { continue; }
          if (bb.x < vx - 1 || bb.y < vy - 1 ||
              bb.x + bb.width > vx + vw + 1 || bb.y + bb.height > vy + vh + 1) {
            fora.push({ i, tipo: "texto-fora-do-viewBox", texto: s.slice(0, 40),
                        bb: [bb.x, bb.y, bb.width, bb.height].map(Math.round), vb });
          }
          caixas.push({ s, bb });
        }
        // Sobreposição: exige cruzamento nas DUAS direções. Rótulos empilhados
        // (título em cima, etiqueta em baixo) partilham quase toda a largura e
        // quase nenhuma altura; um critério só de área acusava-os como
        // sobrepostos, e um validador com falsos positivos não se volta a correr.
        for (let a = 0; a < caixas.length; a++) {
          for (let b = a + 1; b < caixas.length; b++) {
            const A = caixas[a].bb, B = caixas[b].bb;
            const ix = Math.max(0, Math.min(A.x + A.width, B.x + B.width) - Math.max(A.x, B.x));
            const iy = Math.max(0, Math.min(A.y + A.height, B.y + B.height) - Math.max(A.y, B.y));
            if (iy / Math.min(A.height, B.height) > 0.5 &&
                ix / Math.min(A.width, B.width) > 0.25) {
              fora.push({ i, tipo: "texto-sobreposto",
                          texto: caixas[a].s.slice(0, 25) + " // " + caixas[b].s.slice(0, 25) });
            }
          }
        }
        if (svg.querySelectorAll("path, rect, circle, line, polyline, polygon, text").length < 2) {
          fora.push({ i, tipo: "figura-vazia" });
        }
      });
      return { figuras: document.querySelectorAll("figure svg").length,
               larguraScroll: document.documentElement.scrollWidth,
               problemas: fora };
    });

    if (tema === "claro") figuras += rel.figuras;
    if (rel.larguraScroll > 401) {
      console.log(`SCROLL  ${pag} [${tema}]  scrollWidth=${rel.larguraScroll} (a página ganha barra horizontal a 400 px)`);
      problemas++;
    }
    for (const x of rel.problemas) {
      console.log(`FIGURA  ${pag} [${tema}] fig#${x.i}  ${x.tipo}  ${JSON.stringify(x).slice(0, 200)}`);
      problemas++;
    }
    if (CAPTURAS && rel.figuras) {
      const fs = await p.$$("figure");
      for (let i = 0; i < fs.length; i++) {
        const nome = path.basename(pag, ".html") + `-fig${i}-${tema}.png`;
        await fs[i].screenshot({ path: path.join(CAPTURAS, nome) }).catch(() => {});
      }
    }
    await p.close();
  }
}
await navegador.close();
console.log(`${paginas.length} página(s) · ${figuras} figura(s) · ${problemas} problema(s)`);
if (CAPTURAS) console.log(`capturas em ${CAPTURAS} — 🔴 olha para elas: isto mede geometria, não legibilidade`);
process.exit(problemas ? 1 : 0);
