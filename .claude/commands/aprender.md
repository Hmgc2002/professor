---
description: Cria um curso completo sobre um tópico — diagnóstico, depois as fases 0 a 3.
argument-hint: <tópico>
---

Vais criar um curso sobre: **$ARGUMENTS**

Lê `CLAUDE.md` e `PROCESSO.md` antes de começar. Escreves em **português europeu** e tratas o
aluno por **tu**. Ele é programador full-stack e aprende por mecanismos, não por listas.

O produto não é uma página bonita. É ele saber a matéria. Tudo o que se segue existe por isso.

---

## ① Diagnóstico — antes de escrever uma linha

Faz **até 5 perguntas**, todas de uma vez, e espera pela resposta:

1. **Para quê** — o que ele vai fazer com isto? (decide que exemplos escolhes)
2. **O que já sabe** — o ponto de partida real. Pede-lhe que seja duro: assumir a mais produz
   lições com saltos que ele não consegue transpor.
3. **Quanto tempo por semana.**
4. **Até quando** — ou se não há prazo.
5. **Como saberemos que aprendeu** — o critério de sucesso observável.

Se ele responder «avança», **assume** e **declara** por escrito o que assumiste.

Escreve tudo em `topicos/<slug>/DIAGNOSTICO.md`. 🔴 Esse ficheiro é **público** — nada de morada,
terra, idade, empregador, finanças ou saúde. Se o tópico precisar de contexto pessoal para ser
bem ensinado, **pergunta** se vai para `topicos/<slug>/PRIVADO.md` (que está no `.gitignore`).

Se as respostas forem contraditórias (por exemplo, «quero cobrir tudo» com «1h por semana»),
**di-lo e propõe uma resolução** — núcleo e extensão, tópico mais pequeno, ou menos objetivos.
Não escrevas 10 lições para quem tem tempo para 4 e não digas nada.

Cria também `topicos/<slug>/PROGRESSO.md` (tabela vazia com cabeçalho) e a pasta `respostas/`.

---

## ② Fase 0 — Verificar

🔴 **Nunca escrevas «não existe nada sobre isto» sem procurar.** Faz e **regista o que fizeste**:

```bash
grep -ri "<termo>" docs/ topicos/
grep -i "<termo>" INDICE.md
git log -S "<termo>" --oneline
```

Procura também **pelo que a coisa serve para fazer**, não só pelo nome: quem procura «B-tree» não
encontra uma lição chamada «porque é que a tua query está lenta». Procura por sintoma e por verbo.

Identifica **pré-requisitos**, **vizinhos** (onde vais ter de declarar fronteira) e **fontes primárias**
(documentação oficial, especificação, artigo original, código-fonte — um blogue é secundário e diz-se que é).

O resultado escreve-se na «nota das fases» do `index.html` do tópico. Se não encontraste nada,
escreve **o que procuraste** — «não existe» sem a lista de pesquisas é um palpite, não uma verificação.

---

## ③ Fase 1 — Criar

Parte de `modelo/topico.html` e `modelo/licao.html`. **Nunca copies a página de outro tópico**
(copia-se o erro junto). Segue `PROCESSO.md` §«O que um curso tem de ter», que manda:

- `docs/<slug>/index.html` com objetivos verificáveis, a fronteira, os pressupostos **com o que
  muda se estiverem errados**, o mapa em SVG, o plano no tempo e a nota das fases.
- `docs/<slug>/NN-<nome>.html` por lição, com as **11 secções pela ordem**.
- Um pré-requisito que ele não tem é **lição 0**, não nota de rodapé.
- Soluções dentro de `<details>` fechado. Quiz com explicação em **cada** opção, também nas erradas.
- Pelo menos um exercício com código que corre, se o tópico for técnico.
- Fontes com 🌐 *Verificado a AAAA-MM-DD*. **Não inventes fontes, DOIs, páginas nem citações** —
  abre cada uma. Se não conseguires verificar, escreve que não verificaste.

Depois das lições: `folha.html` (imprimível), `teste.html` (intercalado), `flashcards.csv`
(`frente;verso;etiqueta`) e `revisao.ics` (+1, +3, +7, +21, +60 dias, com `VALARM`, `DESCRIPTION`
com os passos e `UID` estável). Um **projeto** se o tópico o permitir.

Acrescenta o cartão em `docs/index.html` com a etiqueta **🚧 em construção**.

---

## ④ Fase 2 — Aprofundar

Relê **como aluno que não sabe a matéria**, não como autor que acabou de a escrever:

- Que lição explica *o quê* mas não o *porquê*?
- Que passo do exemplo trabalhado dá um salto que só faz sentido para quem já sabe?
- Que exercício se resolve por cópia do padrão do exemplo acima, sem perceber nada?
- Que «erro comum» é mesmo comum, e qual inventaste por simetria?
- Que afirmação escreveste de memória sem abrir a fonte?

Corrige, e **escreve na nota das fases a lista do que a Fase 1 errou**.
Uma Fase 2 que não encontrou nada não correu — volta a correr.

---

## ⑤ Fase 3 — Validar

🔴 **Correr o que está escrito, em vez de o julgar.** Ler um comando e concluir que está certo não
é verificar. No repositório de origem deste método, seis de sete erros de uma sessão só apareceram
a correr.

1. **Resolve todos os exercícios e o teste do zero**, sem olhar para as tuas soluções. Compara.
   Uma solução que não bate é um bug na solução até prova em contrário.
2. **Corre todo o código** — exemplos, exercícios, soluções, comandos. Todo.
3. **Confere cada afirmação factual** contra a fonte aberta nesse momento. Números redondos sem
   origem («cerca de 20%») são sinal de invenção: ou arranjas a fonte, ou substituis por uma
   explicação do mecanismo e uma medição que o aluno faz na máquina dele.
4. **Cruza com os outros tópicos**: contradições (uma cede, regista-se) e sobreposições (remissão
   com fronteira declarada).
5. `./validar.sh` até dar limpo.

Escreve o que a Fase 3 apanhou na nota das fases. Só agora a etiqueta passa de
🚧 em construção a **pronto** em `docs/index.html`.

---

## ⑥ Fechar

- `CHANGELOG.md`: entrada com data.
- `DECISOES.md`: uma linha por decisão tomada (data · o quê · com que informação · onde vive).
- Commit em português, com o título a dizer **o que se descobriu**, não o que se mexeu.
  Corpo com *Ficheiros novos* e *Ficheiros alterados*, uma linha cada.
- 🔴 **Não faças push nem mexas no Pages sem pedir.**

No fim, diz ao aluno em duas ou três frases: o que a Fase 2 e a Fase 3 apanharam. É isso que lhe
diz se o processo funcionou desta vez.
