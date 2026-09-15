# professor

Um repositório que me ensina coisas. Dou-lhe um tópico; ele devolve um **curso** — mecanismo,
exemplos trabalhados, exercícios graduados, quiz que se corrige sozinho, teste de domínio e um
calendário de revisão espaçada. Depois **fica**: eu respondo, ele corrige, e o plano adapta-se ao
que eu errei.

O site: **https://hmgc2002.github.io/professor/**

## Estado declarado

| | |
|---|---|
| Tópicos | **1** — [Índices B-tree em SQL](docs/indices-btree-sql/index.html) |
| Em que fase | Passou as **quatro** fases (verificar · criar · aprofundar · validar) |
| Lições | 7 (4 de núcleo, 3 de extensão) · 29 exercícios · 37 perguntas de quiz · 46 flashcards · 17 perguntas no teste |
| Entregas em `respostas/` | **0** |
| Última validação | 2026-09-15 — `validar.sh` limpo nos **cinco** passos, acessibilidade incluída |

A penúltima linha é a que conta. Ver o **teste de honestidade**, no fim.

## Como se usa

```bash
/aprender <tópico>              # diagnóstico, depois as fases 0 a 3 até o curso estar publicado
/corrigir <tópico>              # lê a última entrega em respostas/, corrige, e ajusta o curso
/rever                          # o que está em atraso + uma sessão intercalada de recuperação
/aprofundar <tópico> <lição>    # Fase 2 dirigida a uma lição que ficou rasa
```

**As respostas chegam por ficheiro, não por formulário.** O site não tem backend e nenhuma sessão
lê o `localStorage` do browser. No fim de cada lição, o botão **«Copiar as minhas respostas»** gera
Markdown para colar em `topicos/<slug>/respostas/AAAA-MM-DD.md`. Efeito lateral bem-vindo: a
entrega fica versionada em Git, com data, e a correção fica ao lado dela.

## Antes de cada commit que toca em `docs/`

```bash
./validar.sh
```

Verifica âncoras e ligações, HTML bem formado (`tidy`), acessibilidade WCAG AA nos dois temas e a
400 px (`axe-core`), soluções fechadas por defeito, quiz com explicação em cada opção, e regenera
o `INDICE.md`.

**O passo do `axe-core` precisa de um Chrome instalado no sistema.** O que o puppeteer descarrega
vem sem assinatura e o kernel do macOS ARM mata-o; assiná-lo com `codesign --deep` *não* resolve
(«main executable failed strict validation»). A correção é `brew install --cask google-chrome` — o
`validar_a11y.mjs` encontra-o sozinho, ou aponta-se com `CHROME_PARA_VALIDAR=…`.

Resultado a 2026-09-15, com os cinco passos a correr: **15 páginas × 2 temas × 2 larguras = 60
combinações, zero violações WCAG A/AA** e zero transbordo horizontal a 400 px. O `validar.sh`
**deixa de dizer «tudo limpo» quando um passo não corre** — foi preciso ensiná-lo a isso depois de
ele o ter dito com a acessibilidade por validar.

## Estrutura

```
CLAUDE.md      instruções para qualquer sessão: o ciclo, as fases, as regras
PROCESSO.md    as quatro fases · as regras de casa · o registo de falhas
DECISOES.md    uma linha por decisão: data · o quê · com que informação · onde vive
INDICE.md      gerado — uma linha por cabeçalho com id, em todas as páginas
modelo/        licao.html · topico.html · folha.html · base.css · base.js
topicos/<slug>/  DIAGNOSTICO.md · PROGRESSO.md · respostas/ · correcoes/
docs/          o site (fonte do GitHub Pages)
```

As páginas são **HTML autocontido**: abrem do disco, sem build, sem rede, sem CDN. O CSS e o JS
inline são gerados a partir de `modelo/base.css` e `modelo/base.js` por `sincronizar.py` — a fonte
é um ficheiro só, o resultado publicado continua autónomo (`DECISOES.md` D-003 e D-005).

## A pedagogia é evidência, não gosto

Prática de recuperação, repetição espaçada, intercalação, exemplo trabalhado e o seu
desvanecimento, dificuldades desejáveis, elaboração — cada uma com a fonte primária citada em
[docs/metodo.html](docs/metodo.html). O que não tem evidência fica de fora, e diz-se porquê:
**«estilos de aprendizagem» não aparece aqui.** O que é convenção e não resultado experimental
(os intervalos do `.ics`, a ordem das secções) está marcado como convenção.

---

## O teste de honestidade

> **A 27 de outubro de 2026:** quantos tópicos foram criados, e em quantos existe pelo menos uma
> entrega em `respostas/`?
>
> Se houver cursos publicados que nunca foram estudados, este repositório está a produzir páginas
> e não aprendizagem — e a resposta honesta é dizê-lo aqui e fazer **menos** tópicos, não mais.

**Resposta a 2026-10-27:** _(por preencher)_

| | Criados | Com ≥1 entrega |
|---|---|---|
| Tópicos | 1 | 0 |

Hoje, a segunda coluna é zero — o que é normal num repositório com um dia. Se ainda for zero a
27 de outubro, o problema não é falta de tópicos.

**O produto não é o site. É eu saber a matéria.**
