---
description: Percorre todos os tópicos, diz o que está em atraso de revisão e gera uma sessão intercalada.
---

Lê `CLAUDE.md` primeiro. Português europeu, tratamento por **tu**.

Isto não é um resumo de progresso: é a peça que decide se o que foi estudado fica sabido. A
repetição espaçada e a intercalação são as duas técnicas de maior utilidade e as mais fáceis de
não fazer, porque não produzem páginas novas.

---

## 1. Levanta o estado

Para **cada** `topicos/*/PROGRESSO.md`:

- Data da última sessão e qual foi a lição.
- O que ficou marcado como falhado nas correções (`topicos/*/correcoes/`).
- As datas de revisão de `docs/<slug>/revisao.ics` (+1, +3, +7, +21, +60 da conclusão).

Compara com a data de hoje. Classifica cada tópico:

| Estado | Critério |
|---|---|
| **em atraso** | Passou uma data de revisão do `.ics` sem sessão registada no `PROGRESSO.md` |
| **a chegar** | Data de revisão nos próximos 3 dias |
| **em dia** | Nem uma coisa nem outra |
| **nunca estudado** | Curso publicado sem nenhuma entrega em `respostas/` |

🔴 A última linha é a que interessa dizer em voz alta. Um repositório com cursos publicados e
nenhuma entrega está a produzir páginas e não aprendizagem — e a resposta honesta é dizê-lo, não
sugerir mais um tópico.

## 2. Gera a sessão de recuperação

**Intercalada**, e a intercalação é o ponto todo: perguntas de tópicos **diferentes**, baralhadas,
sem dizer de que lição vem cada uma. Praticar em blocos treina a reconhecer o capítulo; misturar
treina a reconhecer o problema — que é o que acontece na vida real.

Monta 10 a 15 perguntas, por esta ordem de prioridade:

1. O que ele **falhou** em correções anteriores (é o que mais precisa de voltar).
2. O que está **há mais tempo** sem ser revisto.
3. Uma ou duas de tópicos em dia, para não deixar cair.

Formato: escreve-as **no chat**, numeradas, sem as respostas. Ele responde no chat, tu corriges
uma a uma como em `/corrigir` — dizendo **que conceção errada** cada erro revela, não só
«errado, era X».

Se ele responder mal a algo de um tópico dado como dominado, isso não é falha dele: é sinal de que
o espaçamento do `.ics` daquele tópico é curto demais. Ajusta-o e di-lo.

## 3. Regista

Uma linha no `PROGRESSO.md` de **cada** tópico tocado: data · «revisão intercalada» · resultado ·
o que falhou · o que muda.

Se alguma coisa mudou nas páginas, `./validar.sh` antes do commit.

## 4. Diz-lhe

- O que está em atraso e **há quanto tempo**.
- O que ele falhou hoje e que já tinha falhado antes — o padrão, não a lista.
- Se houver cursos publicados nunca estudados: diz o número, sem embrulho, e sugere **fechar um
  antes de abrir outro**.
