#!/usr/bin/env node
/**
 * Acessibilidade com axe-core, nos DOIS temas.
 *
 * Porquê os dois: o contraste é a violação mais comum e depende inteiramente
 * das variáveis de cor, que mudam com o tema. Validar só um tema deixa metade
 * das páginas por validar e dá a sensação contrária.
 *
 * 🔴 Lê só `violations`. `incomplete` é o balde do «não consegui decidir»
 * (sobreposições, imagens de fundo, cor herdada de um ancestral que o axe não
 * resolve) e enche o ecrã de coisas que estão bem. Um validador que dá ruído
 * não se volta a correr.
 *
 * Também mede a 400 px, que é onde as páginas são mesmo lidas, e verifica que
 * a página não ganha barra horizontal nessa largura.
 */
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import puppeteer from "puppeteer";

const require = createRequire(import.meta.url);
const axeFonte = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

const ficheiros = process.argv.slice(2);
if (ficheiros.length === 0) {
  console.error("uso: node validar_a11y.mjs <ficheiro.html> [...]");
  process.exit(2);
}

const TEMAS = ["claro", "escuro"];
const LARGURAS = [400, 1280];
const cor = process.stdout.isTTY
  ? { v: "\x1b[31m", a: "\x1b[33m", ok: "\x1b[32m", f: "\x1b[90m", z: "\x1b[0m" }
  : { v: "", a: "", ok: "", f: "", z: "" };

let navegador;
try {
  navegador = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
} catch (e) {
  // Código 3 = "não cheguei a correr", distinto de 1 = "corri e encontrei violações".
  // Tratar os dois como o mesmo faz o relatório mentir em ambas as direções.
  console.error("BROWSER  o Chrome do puppeteer não arrancou: " + e.message);
  process.exit(3);
}
let totalViolacoes = 0;
let totalIncompletos = 0;
const larguraMa = [];

try {
  for (const ficheiro of ficheiros) {
    const url = "file://" + path.resolve(ficheiro);
    const pagina = await navegador.newPage();

    for (const largura of LARGURAS) {
      await pagina.setViewport({ width: largura, height: 900, deviceScaleFactor: 1 });

      for (const tema of TEMAS) {
        await pagina.goto(url, { waitUntil: "networkidle0" });
        await pagina.evaluate((t) => {
          document.documentElement.setAttribute("data-tema", t);
          try { localStorage.setItem("professor:tema", t); } catch (e) { /* sem armazenamento */ }
        }, tema);
        await pagina.evaluate(axeFonte);

        const r = await pagina.evaluate(async () => {
          // runOnly: as regras WCAG 2.1 A e AA. "best-practice" fica de fora de
          // propósito — são conselhos, e misturá-los com violações reais treina
          // a ignorar o relatório.
          return await window.axe.run(document, {
            runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
            resultTypes: ["violations"],
          });
        });

        totalIncompletos += r.incomplete.length;
        for (const v of r.violations) {
          totalViolacoes++;
          console.log(`${cor.v}A11Y${cor.z}  ${ficheiro} [${tema}, ${largura}px]  ${v.id}: ${v.help}`);
          for (const n of v.nodes.slice(0, 3)) {
            console.log(`${cor.f}        ${n.target.join(" ")}${cor.z}`);
            const detalhe = (n.any[0] || n.all[0] || {}).message;
            if (detalhe) console.log(`${cor.f}        → ${detalhe}${cor.z}`);
          }
          if (v.nodes.length > 3) console.log(`${cor.f}        (+${v.nodes.length - 3} outros)${cor.z}`);
          console.log(`${cor.f}        ${v.helpUrl}${cor.z}`);
        }

        if (largura === 400) {
          const estoura = await pagina.evaluate(() =>
            document.documentElement.scrollWidth - document.documentElement.clientWidth);
          if (estoura > 1) larguraMa.push(`${ficheiro} [${tema}]: transborda ${estoura}px a 400px`);
        }
      }
    }
    await pagina.close();
  }
} finally {
  await navegador.close();
}

for (const m of [...new Set(larguraMa)]) console.log(`${cor.v}400PX${cor.z} ${m}`);

if (totalViolacoes || larguraMa.length) {
  console.log(`\n${cor.v}${totalViolacoes} violação(ões) de acessibilidade${cor.z}` +
              (larguraMa.length ? ` e ${new Set(larguraMa).size} problema(s) a 400 px` : "") + ".");
  process.exit(1);
}
console.log(`${cor.ok}✓${cor.z} ${ficheiros.length} página(s) sem violações WCAG A/AA nos dois temas, a 400 e 1280 px` +
            `${cor.f} (${totalIncompletos} resultado(s) "incomplete" ignorados de propósito)${cor.z}`);
