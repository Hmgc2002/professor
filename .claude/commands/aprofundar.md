---
description: Fase 2 dirigida a uma lição que ficou rasa — reescreve-a como aluno, não como autor.
argument-hint: <tópico> <lição>
---

Vais aprofundar: **$ARGUMENTS** (primeiro argumento é o slug do tópico, segundo é o número ou nome
da lição).

Lê `CLAUDE.md` e a secção da Fase 2 em `PROCESSO.md`. Português europeu, tratamento por **tu**.

---

## 1. Lê como aluno, não como autor

Abre `docs/<slug>/<lição>.html` e lê **do princípio ao fim** fingindo que não sabes a matéria.
Quem escreveu a lição não consegue ver os saltos, porque preenche-os sem dar por isso.

Lê também, antes de decidir o que mexer:

- `topicos/<slug>/correcoes/` — se ele já errou aqui, o erro diz-te onde está o buraco, e vale
  mais do que a tua leitura.
- `topicos/<slug>/DIAGNOSTICO.md` — o que foi assumido sobre ele. Uma lição pode estar rasa
  porque o pressuposto estava errado, e aí o que se corrige é o pressuposto.

## 2. Procura estas sete coisas

| # | A pergunta | O sintoma |
|---|---|---|
| 1 | Explica o **quê** sem explicar o **porquê**? | Dá-se a regra e não o mecanismo que a produz |
| 2 | Que **salto** há no exemplo trabalhado? | Um passo que só faz sentido para quem já sabe a resposta |
| 3 | Que exercício se resolve **por cópia** do padrão acima? | Muda-se o exemplo de contexto e ele deixa de se resolver |
| 4 | Que «erro comum» foi **inventado por simetria**? | Não aparece em lado nenhum a sério; ninguém o comete |
| 5 | Que afirmação foi escrita **de memória**? | Números redondos, «cerca de», «geralmente», sem fonte |
| 6 | O **diagrama** falta ou não mostra o que interessa? | A coisa tem partes que se movem e está descrita só em prosa |
| 7 | O quiz distingue **perceber** de **decorar**? | As distractoras são absurdas; acerta-se por eliminação |
| 8 | As **fontes** têm alguma coisa que não seja documentação? | Só links para o manual: diz o *que faz*, nunca o *porque é assim*. Falta o livro, o artigo original ou o curso — ou a declaração de que procuraste e não há |

## 3. Corrige

- Acrescenta o que falta: o passo em falta, o diagrama, o exercício num contexto novo,
  a distractora que corresponde a uma conceção errada real.
- Se a lição publicada **estava errada**, a correção fica **à vista**, nunca apagada em silêncio:
  `⚠️ Corrigido a AAAA-MM-DD — dizia X, está Y, porque Z.`
- **Corrigir num sítio é corrigir em todos**: se mudaste uma definição, `grep -ri` no repositório
  inteiro, mais `flashcards.csv` e `folha.html`.
- Se a lição cresceu demasiado, **parte-a em duas** e atualiza o mapa e o plano no `index.html`.
- Se o buraco é anterior a esta lição, o que falta é uma **lição nova antes** desta — e então o
  mapa muda, não só o texto.

## 4. Volta a validar

🔴 Uma lição mexida volta à **Fase 3**, não fica a meio caminho:

1. Resolve os exercícios novos **do zero**, sem olhar para as soluções.
2. **Corre** todo o código que acrescentaste.
3. Confere cada afirmação nova contra a fonte aberta nesse momento.
4. `./validar.sh` limpo.

## 5. Regista

- **Na nota das fases** do `docs/<slug>/index.html`: o que este aprofundamento encontrou, com data.
  É a lista do que estava mal — não «melhorou-se a lição 3».
- `CHANGELOG.md` e, se houve decisão, `DECISOES.md`.
- Commit em português com o título a dizer o que se descobriu.

Termina a dizer-lhe, em duas frases: **o que estava rasa e porquê passou despercebido da primeira
vez**. É esse padrão que evita repeti-lo na lição seguinte.
