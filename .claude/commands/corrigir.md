---
description: Corrige a última entrega de respostas de um tópico e ajusta o curso ao que falhou.
argument-hint: <tópico>
---

Vais corrigir a última entrega de: **$ARGUMENTS**

Lê `CLAUDE.md` primeiro. Português europeu, tratamento por **tu**.

---

## 1. Encontra a entrega

O ficheiro mais recente em `topicos/<slug>/respostas/AAAA-MM-DD.md`.

```bash
ls -1 topicos/<slug>/respostas/ | sort | tail -3
```

🔴 **Não perguntes ao aluno o que ele respondeu.** As respostas estão no ficheiro — é esse o ponto
de todo o mecanismo de entrega. Se não houver ficheiro nenhum, diz-lho e explica que o botão
«Copiar as minhas respostas» no fim da lição gera o Markdown para colar ali.

Lê também `topicos/<slug>/PROGRESSO.md` e as correções anteriores em `topicos/<slug>/correcoes/`:
um erro que se repete é informação diferente de um erro novo.

## 2. Corrige uma a uma

Para **cada** resposta, aberta ou de quiz:

- **Certo / errado / parcial** — e não arredondes para cima. Um «quase» corrigido como certo é uma
  lacuna que volta no teste de domínio.
- 🔴 **Que conceção errada é que o erro revela.** Isto é o mais importante da correção e o que
  distingue isto de um corretor automático. Não escrevas «errado, o correto é X»: escreve o que a
  resposta dele deixa ver sobre o modelo mental que ele construiu, e onde é que esse modelo até
  funciona (as conceções erradas sobrevivem porque acertam em muitos casos).
- **O que fazer a seguir** — que secção reler, que exercício repetir.

Nas respostas abertas (a pergunta de Feynman), procura sobretudo:
jargão a tapar um buraco · uma analogia que funciona no exemplo dado mas parte noutro caso ·
o *quê* correto com o *porquê* ausente.

Dá crédito explícito ao que está bem, e diz **porque** está bem. Corrigir só o que falha dá uma
imagem falsa da sessão.

Escreve em `topicos/<slug>/correcoes/AAAA-MM-DD.md`.

## 3. Decide de quem é a culpa

Para cada erro, a pergunta que mais importa:

> **Isto é uma lacuna dele, ou uma lacuna do curso?**

Se duas ou mais respostas falham no mesmo sítio, ou se a resposta errada é a leitura mais natural
do que está escrito, **o curso é que está mal**. Nesse caso:

- **Reescreve ou acrescenta a lição.** Se a lição publicada estava errada, a correção fica
  **à vista**, nunca apagada em silêncio:
  `⚠️ Corrigido a AAAA-MM-DD — dizia X, está Y, porque Z.`
- Se faltava um passo, acrescenta-o ao exemplo trabalhado.
- Se o exercício era ambíguo, reescreve o enunciado e di-lo.
- **Corrigir num sítio é corrigir em todos**: `grep -ri` no repositório, mais os flashcards e a folha.

## 4. Ajusta o que vem a seguir

- Acrescenta 2–3 perguntas sobre o que falhou à secção **Recuperar** da lição seguinte.
- Se o erro for de base, acrescenta uma revisão extra ao `revisao.ics` a +2 dias.
- Se um flashcard cobria exatamente isto e ele falhou na mesma, o flashcard está mal escrito
  (provavelmente pede reconhecimento em vez de recuperação). Reescreve-o.

## 5. Regista

`topicos/<slug>/PROGRESSO.md`, uma linha: **data · lição · resultado · o que falhou · o que muda no plano**.

Se mexeste em `docs/`, corre `./validar.sh` antes do commit. Commit em português, com o título a
dizer o que se descobriu — por exemplo:
«A lição 3 dava a seletividade como resolvida e as respostas mostram que o exemplo escondia o caso
em que o índice não compensa».

## 6. Diz-lhe

Termina com um resumo curto e direto: quantas certas, **qual é o padrão** dos erros (não a lista),
o que muda no curso por causa disto, e o que fazer na próxima sessão. Se o resultado foi bom,
diz isso sem rodeios — e diz o que ainda não foi testado.
