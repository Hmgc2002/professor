# Diagnóstico — Abstracts e resumos técnicos

**Data:** 2026-09-15 · **Slug:** `abstracts-e-resumos` · **Curso:** [docs/abstracts-e-resumos/](../../docs/abstracts-e-resumos/index.html)
**Ponto de partida pedido:** <https://en.wikipedia.org/wiki/Abstract_(summary)> — fonte **terciária**; o curso assenta
nas primárias que ela cita e noutras que ela não cita (lista em `docs/abstracts-e-resumos/index.html#fases`).

> 🔴 Este ficheiro é público. Só tem o ponto de partida técnico e o ritmo. O tópico não precisa de contexto
> pessoal para ser bem ensinado, por isso não há `PRIVADO.md`. **Mas** há um risco próprio deste tópico,
> tratado mais abaixo: os exercícios pedem textos de trabalho, e textos de trabalho não podem vir parar aqui.

---

## As perguntas e as respostas

### 1. Para que precisas disto?

**b) + c) + d)** — escrever resumos técnicos no trabalho (descrição de PR, RFC/design doc, post-mortem,
abertura de README); ler abstracts depressa para decidir que artigos abrir; perceber o mecanismo de um resumo.

**Não escolheste a)** (escrever o abstract de um artigo científico).

**O que isso decide:**

- O abstract científico entra, mas como **modelo de estudo**, não como destino: é o género onde as regras de um
  bom resumo estão mais escritas, testadas e normalizadas (ANSI/NISO Z39.14, CONSORT, IMRaD). Aprende-se lá o
  mecanismo e transporta-se para o PR, o RFC e o post-mortem.
- Do lado científico, o que se pratica é **ler** (triagem), não escrever.
- A lição central do mecanismo (d) é a **lição 0**, e é ela que liga os outros dois objetivos: resumir é decidir
  o que o leitor precisa para a decisão *dele* — e o leitor de um PR não decide o mesmo que o leitor de um artigo.

### 2. De onde partes?

- **Nunca escreveste um abstract, e leste poucos.**
- **Não conheces** estruturado/não estruturado, informativo/indicativo, nem IMRaD.
- **Nunca escreveste** estes textos, em nenhuma língua.

**O que isso decide:** 🔴 há **lição 0**, e parte de zero: o que é um resumo *enquanto operação* (o que se apaga,
o que se generaliza, o que se constrói), antes de qualquer género. Nenhum termo (informativo, IMRaD, «move»)
aparece antes de ser definido. Em contrapartida, não se explica o que é um PR, um commit ou um README — és
programador; o que falta é a escrita, não o objeto.

### 3. Quanto tempo por semana?

**«O que for necessário.»**

⚠️ Isto não é um número, e um plano precisa de um. **Assumi ~1h30 por semana, uma lição por semana.**

**Porque não mais depressa, mesmo havendo tempo:** a evidência sobre espaçamento diz que o mesmo tempo de estudo
rende mais distribuído do que concentrado ([método](../../docs/metodo.html#espacamento)). Fazer as sete lições
num fim de semana dava a sensação de ter aprendido e retenção pior. **O tempo a mais vai para o projeto e para as
revisões, não para lições mais rápidas.**

### 4. Até quando?

**Sem prazo.**

**O que isso decide:** sem prazo e com «o que for necessário», o risco não é falta de tempo — é não haver dia
nenhum em que isto seja a coisa a fazer. O `revisao.ics` e uma hora fixa na semana substituem o prazo.

### 5. Como saberemos que aprendeste?

**Aceitaste o critério proposto**, que repito aqui:

> Dado um texto teu ou alheio, escreves-lhe um abstract dentro de um limite de palavras. Quem só lê o abstract
> fica a saber o problema, o método, o resultado principal com números e a implicação. Consegues também dizer o
> que falta a um abstract mau e porquê.

⚠️ **Adaptei-o, e declaro como.** O critério foi escrito a pensar em artigos científicos (a), e tu escolheste
b, c e d. Num PR ou num post-mortem não há «método» nem sempre há «resultado» no sentido de um artigo. A versão
que o `teste.html` usa é:

> Dado um texto (artigo, diff descrito, relato de incidente, proposta), escreves-lhe um resumo **dentro de um
> limite de palavras** que deixa o leitor-alvo saber **o problema, o que se fez ou propõe, o efeito — com
> números quando existem — e o que isso implica para ele**. E, dado um resumo mau, dizes **o que lhe falta, que
> operação de resumo falhou, e porquê** — e, para um abstract científico, se o que ele promete merece abrir o artigo.

Se esta adaptação não é o que querias, diz — muda o teste e os exercícios das lições 3, 5 e 6.

---

## A tensão que as respostas criam, e como a resolvi

Não há contradição de tempo (disseste «o que for necessário»). A tensão é outra: **três objetivos com públicos
diferentes** (o revisor de um PR, a equipa que lê um post-mortem, tu a fazer triagem de artigos) e **ponto de
partida zero**. Cobrir os três géneros de trabalho antes de ter o mecanismo produz três listas de regras soltas.

**Resolução — núcleo e extensão** (DECISOES.md D-016):

| | Lições | Semanas | O que tens no fim |
|---|---|---|---|
| **Núcleo** | 0 · 1 · 2 · 3 | ~4 | O mecanismo, a anatomia de um abstract, a triagem de artigos (c), e o género de trabalho que escreves mais vezes — a descrição de um PR e o título de um commit (b) |
| **Extensão** | 4 · 5 · 6 | ~3 | RFC/PEP/README, post-mortem, e o diagnóstico intercalado de resumos maus de todos os géneros — que é a segunda metade do critério |

Parar no núcleo deixa-te com os três objetivos tocados. A extensão é onde o critério fica inteiro.

---

## O que assumi (e o que muda se estiver errado)

| Assumi | Porquê | Se estiver errado |
|---|---|---|
| ~1h30/semana, uma lição por semana | «O que for necessário» não é um número | Com menos de 1h, cada lição parte-se em duas sessões (mecanismo+exemplos / prática+quiz); o plano passa a ~14 semanas |
| O critério adaptado da pergunta 5 | O original foi escrito para artigos científicos, que não escolheste | Muda o `teste.html` e os exercícios das lições 3, 5 e 6 |
| **Escreves em português** os textos de trabalho; **lês em inglês** os abstracts científicos | Não respondeste à língua («nunca escrevi»); os artigos que vais triar estão quase todos em inglês | Se escreves em inglês no trabalho, os exemplos das lições 3–5 precisam de versão inglesa — e há diferenças reais (voz ativa/passiva, imperativo no título do commit) |
| Usas Git e fazes PRs com revisão | Perfil: programador full-stack | Se não há revisão de código onde trabalhas, a lição 3 perde o leitor que dá sentido ao resumo — passa a ser sobre o *eu* de daqui a seis meses |
| Tens Python 3 à mão | Os dois exercícios com código usam só a biblioteca-padrão | Os scripts são curtos; reescrevê-los noutra linguagem é, em si, um bom exercício |
| Não precisas de abstracts gráficos, em vídeo, nem de resumos gerados por LLM | Não aparece em nenhuma resposta | Resumos por LLM seriam um tópico vizinho próprio, não uma lição: o mecanismo (lição 0) aplica-se, mas a verificação é outra conversa |

---

## 🔴 O risco específico deste tópico: textos de trabalho num repositório público

Os exercícios e o projeto pedem que resumas textos reais. **Uma descrição de PR, um post-mortem ou um design doc
do teu trabalho não podem ir para `topicos/abstracts-e-resumos/respostas/`** — esse diretório é público
(DECISOES.md D-001) e o `validar.sh` não apanha nomes de sistemas, clientes ou incidentes.

**Regra para as entregas:** usa textos **públicos** (PRs de projetos open source, post-mortems publicados,
PEPs, RFCs do IETF) ou **inventados**. Se quiseres praticar num texto do trabalho, pratica fora do repositório e
entrega só a reflexão sobre o que mudaste e porquê, sem o texto.

---

## Estado

| | |
|---|---|
| Diagnóstico | ✅ 2026-09-15 |
| Curso publicado | ✅ 2026-09-15 (passou a Fase 3) |
| Primeira entrega em `respostas/` | ⬜ ainda nenhuma |
