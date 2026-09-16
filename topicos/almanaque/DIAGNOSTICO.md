# Diagnóstico — O almanaque

**Data:** 2026-09-16 · **Slug:** `almanaque` · **Curso:** [docs/almanaque/](../../docs/almanaque/index.html)

> 🔴 Este ficheiro é público. Tem só o ponto de partida técnico e o ritmo.
> Não se perguntou onde estudas nem de onde observas. O curso precisa de **uma** posição para os
> exemplos, e por isso usa uma posição pública e arbitrária — o Observatório Astronómico de Lisboa,
> na Tapada da Ajuda (38° 42,5′ N, 9° 11,2′ W), que é um sítio publicado num mapa e não onde vives.
> (⚠️ A frase anterior dizia «não a tua m·o·r·a·d·a» e fazia o passo 5 do `validar.sh` disparar,
> com razão: ele procura a palavra e pede confirmação humana, e não sabe que ela estava ali a negar.
> Reescrevi a frase em vez de acrescentar uma exceção ao validador — a exceção enfraquecia-o para
> sempre e a frase não perde nada.)
> Se um dia quiseres o curso calibrado para onde observas de facto, isso vai para
> `topicos/almanaque/PRIVADO.md`, que está no `.gitignore`.

---

## O pedido

> <https://en.wikipedia.org/wiki/Almanac>

Um artigo, não uma pergunta. A primeira coisa que o diagnóstico teve de fazer foi descobrir **qual dos
almanaques** é que interessa, porque a palavra cobre pelo menos três objetos diferentes: a tabela de
efemérides, o livro de bordo do navegador, e o almanaque popular de agricultura e provérbios.

---

## As perguntas e as respostas

### 1. Para quê?

**As três coisas**, por esta ordem de peso:

| Objetivo | O que decide no curso |
|---|---|
| **Usar um almanaque náutico a sério** | Entra a redução de altura (Marcq St Hilaire) e a leitura das páginas diárias com os incrementos e as correções `v` e `d`. É o objetivo que fixa a **tolerância**: décimas de minuto de arco, não graus |
| **Perceber o objeto histórico** | Entra a lição 1 inteira: de onde vem a palavra, porque é que o almanaque nasce separado das tábuas astronómicas, e porque é que o formato sobreviveu ao computador |
| **Calcular eu próprio** | Todas as lições têm código que corre. O projeto produz um almanaque gerado por ti |

⚠️ **A tensão que isto cria, dita antes de ela morder.** «Calcular eu próprio» e «usar um almanaque náutico
a sério» não são o mesmo exercício e quase se contradizem. As fórmulas de baixa precisão que cabem numa
lição dão o Sol a cerca de 1°; uma página do *Nautical Almanac* dá-o a 0,1′, que é **600 vezes melhor**. Um curso
que não dissesse isto produzia um aluno convencido de que o código dele substitui o livro. A resolução está
escrita na lição 3 e é o eixo do curso: **orçamento de erro**. Cada lição declara o que a sua aproximação
custa em minutos de arco e em milhas náuticas no fim.

### 2. De onde partes?

Respondido sem amaciar:

| Perguntei | Resposta |
|---|---|
| Astronomia esférica (declinação, ascensão reta, ângulo horário, azimute) | **Nenhuma.** São palavras novas |
| Coordenadas celestes, mesmo informalmente | Não |
| Aritmética de calendários, UTC contra hora local, segundos intercalares | Não |
| Bibliotecas de efemérides (`skyfield`, PyEphem, SPICE) | Não |

É programador full-stack: terminal, Git, Python e ler código não se explicam. O que falta é **a geometria**,
e falta toda.

🔴 **Consequência imediata:** o pré-requisito em falta é a esfera celeste, e por isso é a **lição 0**, com
onze secções como qualquer outra — não uma caixa «recorda que a declinação é…» no início da lição 3.
Uma segunda coisa que também falta — as escalas de tempo — tem lição própria (a 2), porque se pode ensinar
depois de haver para quê.

### 3. Quanto tempo por semana?

**6 horas ou mais.**

### 4. Até quando?

**Sem prazo.** O plano no tempo é indicativo e conta 10 semanas a cerca de 6 h; se forem 8 h, são 8 semanas.

### 5. Como saberemos que aprendeste?

> **Gerar um almanaque meu:** produzo um almanaque anual para uma posição dada, com números que batem
> com fonte oficial dentro de tolerância declarada.

**O que isto torna verificável, e é a razão de o critério ser bom:** existe uma fonte contra a qual comparar.
As páginas diárias do *Nautical Almanac* de 2000 a 2030 estão publicadas em PDF gratuito
(<https://thenauticalalmanac.com>, aberto a 2026-09-16), e a diferença entre o que o teu código diz e o que a
página diz é um número, não uma opinião.

⚠️ **A parte do critério que não é gratuita:** «dentro de tolerância declarada» obriga-te a declarar a
tolerância **antes** de comparar. Declarar depois é escolher o limiar que faz o resultado passar. A lição 9
faz-te escrever a tolerância primeiro, num ficheiro, e só depois correr a comparação.

---

## O que assumi, e o que muda se estiver errado

| Assumi que… | De onde veio | Se estiver errado… |
|---|---|---|
| Não há sextante nem horizonte do mar à mão | Não foi perguntado, e o material não foi mencionado | A lição 7 passa a ter uma segunda metade com observação real (horizonte artificial, altura do olho). Como está, a lição 7 reduz **alturas dadas** — o mecanismo é o mesmo, falta-lhe o instrumento |
| Python 3, e `pip install` disponível se for preciso | É programador full-stack | Nada muda no núcleo: 🔴 **todo o código do curso é biblioteca padrão**, de propósito, porque um almanaque construído sobre `skyfield` não ensina o que está lá dentro. O `skyfield` aparece **só** na lição 9, como padrão de comparação |
| A posição de exemplo pode ser pública e arbitrária | Decisão de privacidade (D-001) | Se quiseres o curso na tua posição, muda-se uma constante. Nenhum mecanismo depende do sítio |
| Interessa a época atual (1950–2050), não datas históricas | «Gerar um almanaque meu» lê-se como «para o ano que vem» | As séries de baixa precisão que o curso usa estão declaradas para 1950–2050. Fora disso, a lição 2 explica o que parte primeiro (o ΔT, que é medido e não calculado) e o curso passaria a precisar de uma lição sobre calendários históricos e a reforma gregoriana |
| Inglês técnico lê-se sem atrito | Todas as fontes primárias estão em inglês | Se não fosse assim, o curso tinha de traduzir as páginas do *Nautical Almanac* em vez de as usar |

---

## A fronteira que o diagnóstico já fixa

- **Não** é um curso de astronomia observacional nem de telescópios.
- **Não** é um curso de mecânica celeste: ninguém integra órbitas aqui. Usam-se séries ajustadas, publicadas,
  e diz-se de onde vêm e quanto erram.
- **Não** substitui o *Nautical Almanac* a bordo. O curso ensina a **lê-lo**, a **reproduzi-lo** com tolerância
  declarada, e a saber quando a reprodução não serve.

---

## Fase 0 — o que se procurou no repositório

| Procurei | Onde | Resultado |
|---|---|---|
| `almanaque`, `almanac`, `efeméride`, `astronom`, `juliano`, `sextante`, `latitude`, `longitude`, `declinação`, `tempo sidéreo`, `órbita`, `maré`, `navegação` | `grep -ri` em `docs/` e `topicos/` | **0 ficheiros** em todos |
| `calendário` | idem | 8 ficheiros — todos sobre o `revisao.ics` (calendário de revisão espaçada). Nada de calendários astronómicos |
| `lua` como palavra inteira | idem | 0. (O `grep -ril lua` sem fronteiras dá 3 ficheiros por acaso, dentro de outras palavras) |
| Por sintoma e por verbo: `tabela pré-calculada`, `pré-calcul`, `lookup`, `memoiz`, `consulta em tabela`, `data e hora`, `segundos intercalares`, `esfera`, `trigonom` | idem | 0 em todos |
| `interpolação` | idem | 7 ficheiros, **todos** em `cassete-captura/00-espetro.html`: interpolação parabólica de um pico de FFT. **Vizinho a declarar** — mecanismo diferente do da interpolação linear numa tábua horária |
| `fuso`, `UTC` | idem | 10 e 5 ficheiros, quase todos falsos: `fuso` apanha **parafuso** em `cassete-captura`. O único hit a sério é um exemplo de título de commit em `abstracts-e-resumos/03-pr-e-commit.html` («usa o fuso de Lisboa no relatório diário») — é exemplo de escrita, não conteúdo sobre tempo |
| `cache` | idem | 14 ficheiros, todos em sentido informático. ⭐ Não é sobreposição, mas é a **analogia** que a lição 1 usa |
| `git log -S` para `almanaque`, `efeméride`, `astronomia`, `sextante`, `dia juliano`, `latitude`, `Lua`, `maré`, `declinação` | histórico inteiro | **Nada.** Nunca existiu e nunca foi removido |
| `INDICE.md` | `grep -in "calend\|tempo\|interpol\|tabela\|precomput\|cache"` | Só cabeçalhos «O plano no tempo» e uma tabela de números do Postgres |

**Conclusão da Fase 0:** tópico novo. Sem pré-requisitos dentro do repositório, um vizinho a declarar
(a interpolação de `cassete-captura`) e uma analogia a aproveitar (o *cache*).

## Fontes primárias localizadas na Fase 0

| Fonte | Tipo | Estado |
|---|---|---|
| *Nautical Almanac*, páginas diárias 1911–2030 em PDF · <https://thenauticalalmanac.com> | Reprodução do livro oficial | ✅ aberto a 2026-09-16 |
| Fórmulas de baixa precisão do *Astronomical Almanac* (pág. C5) | Fonte primária impressa | ⚠️ O sítio do USNO (`aa.usno.navy.mil/faq/sun_approx`) **não respondeu** a 2026-09-16 (ligação recusada, e `docs/SunApprox.php` deu HTTP 500). As fórmulas foram conferidas contra uma reprodução que cita a edição de 2017 e contra a Wikipédia; ver a lição 3, que o diz na cara |
| NOAA Solar Calculator — detalhes do cálculo | Documentação oficial | ✅ aberto a 2026-09-16; declara-se baseado no Meeus e dá a exatidão («within a minute for locations between +/- 72°») |
| NOAA Tides & Currents — constituintes harmónicas | Documentação oficial | ⚠️ A tabela é desenhada por JavaScript e não veio no texto; a API também não respondeu daqui. Os valores de velocidade vieram da Wikipédia e **conferem-se por cálculo** na lição 8 |
| Jean Meeus, *Astronomical Algorithms* | **Livro** | ✅ confirmado como base declarada do NOAA Solar Calculator. ⚠️ Não tenho o exemplar: não se cita página nem ISBN |
| Dava Sobel, *Longitude* (1995) e a série *Longitude* (Channel 4 / A&E, 2000) | **Livro e série** | ✅ confirmados a 2026-09-16, com a ressalva sobre Maskelyne escrita na bibliografia |

---

## O plano que sai daqui

10 lições. **Núcleo:** 0 a 7 e 9 — é o percurso até ao critério de sucesso.
**Extensão:** 8 (marés), que serve o objetivo histórico e a definição de almanaque, mas não a fixação de posição.

Ver o mapa e o plano no tempo em [`docs/almanaque/index.html`](../../docs/almanaque/index.html).
