# Registo de alterações

O formato é uma entrada por sessão de trabalho, com data. O que muda o que eu
consigo aprender fica no topo da entrada; o que muda só a mecânica fica no fim.

## 2026-09-16 (5) — «O almanaque»: um curso que mede o seu próprio erro contra o livro oficial

Tópico novo, **`almanaque`**, 10 lições, a partir de <https://en.wikipedia.org/wiki/Almanac>.
Passou as quatro fases.

**O que o curso ensina, e porque é diferente dos outros**

- O eixo não é «como se calcula a posição do Sol» — é **orçamento de erro**. Cada lição declara o que a sua
  aproximação custa em minutos de arco e em milhas náuticas, e a lição 9 junta tudo numa tabela.
- O resultado, medido contra a página diária de 20 de março de 2026 do *Nautical Almanac*: das seis colunas
  tabeladas, **duas passam** os 0,1′ do livro (GHA de Áries a 0,053′, paralaxe da Lua a 0,077′) e **quatro
  falham** (Dec do Sol 0,195′, GHA do Sol 0,415′, Dec da Lua 2,1′, GHA da Lua 5,7′). As duas colunas de
  *eventos* — nascer/pôr/crepúsculos e nascer/ocaso da Lua — batem **ao minuto**, nas seis colunas.
- Isso é o produto do curso, não o seu fracasso: responde com números à pergunta com que a lição 1 abre, que é
  porque é que o livro continua a ser publicado.

**O que se descobriu a correr, e que não teria aparecido a reler**

- 🔴 **`gha()` usava o tempo sidéreo MÉDIO.** O almanaque publica o **aparente**. Erro sistemático de −0,09′ no
  GHA de Áries; com o GAST desce para +0,004′, que é o arredondamento do próprio livro.
- O ensaio do dia sidéreo media a taxa com passo de **1 segundo** e dava meio segundo a mais — cancelamento
  catastrófico. Não era da fórmula.
- A equação dos equinócios vale **0,263′**, não os 0,29′ que eu tinha escrito de estimativa. Corrigido em quatro
  sítios, dois deles *docstrings*.
- «A tabela pesa centenas de vezes mais do que o código» — medido: **30 vezes**.
- O detetor de luas novas dava um mês sinódico de **30,48 dias**, fora do intervalo publicado. Bug do detetor.
- O intercepto do exemplo trabalhado dava **178 milhas náuticas**, porque inventei a altura do sextante. Passou
  a ser obtida por inversão a partir de uma posição real: 18,4 milhas.
- A fixação de posição recupera a posição verdadeira a **0,264 milhas**, não «a menos de um milésimo». O resíduo
  virou a melhor parte do exercício: Marcq St Hilaire é uma linearização e comporta-se como um passo de Newton —
  0,00001 milhas à segunda iteração.
- O `round()` do Python arredonda **ao par** e o livro não. A reconstrução da tabela de incrementos dava 0,1 onde
  a página imprime 0,2.
- Um exercício media uma **tautologia** (confirmava a definição de *v*, não a qualidade da interpolação).
  Reescrito para medir a curvatura desprezada dentro da hora: 0,006′, dezasseis vezes abaixo do passo de impressão.
- O gerador etiquetava **25 dias do ano em Lisboa como «sempre-acima»**. A Lua ali não é circumpolar — eram dias
  em que ela saltou o nascer. `SemEvento` passou a distinguir **três** causas.
- No equador **não existe equilux**: o dia é sempre mais longo do que a noite. E a 60° N o atraso do nascer da Lua
  chega a ser **negativo** (a «lua da colheita»). Nenhuma das duas coisas eu esperava.
- 🔴 O `ensaio.py` rebentou com `UnicodeEncodeError` na primeira execução, por um «Δ» numa consola `cp1252` — a
  mesma falha que este `PROCESSO.md` já registava para o `validar.py`, repetida.

**As figuras, e o que a captura a 400 px apanhou que o axe não apanha**

- O mapa do curso tinha o `viewBox` escrito à mão e **as lições 6 a 9 ficavam fora dele**.
- A figura da reta de altura precisou de **três versões**: a primeira com rótulos sobrepostos, a segunda com
  geometria cortada pelo topo. A correção que ficou: `viewBox` calculado do envelope da geometria, e rótulos numa
  coluna fixa ordenados pela altura do alvo.
- Um rótulo do mapa saía truncado («O que é um almanaq»), porque era cortado com uma fatia.
- A figura da soma de uma consulta dizia 8° 59,6′ e o valor é **8° 59,7′** — uma décima, que fazia a figura
  discordar do bloco de código da mesma lição.

**Infraestrutura: a verificação das figuras deixou de ser manual**

- 🔴 O registo de falhas do `PROCESSO.md` pedia isto **três vezes**, e três vezes ficou escrito
  «continua a ser um passo manual». Passa a haver `validar_figuras.mjs`, dentro do `validar.sh`
  (passo 4 de 6): a 400 px, nos dois temas, mede **texto fora do `viewBox`**, **texto por cima de
  texto**, **figuras vazias** e **marcadores de substituição por substituir** — as quatro classes de
  erro que aparecem no registo e que o axe deixa passar, porque o axe mede contraste e não geometria.
- Apanhou quatro erros reais neste tópico, todos em figuras que o axe aprovou.
- O limiar de sobreposição exige cruzamento **vertical e horizontal**. Com um critério só de área,
  acusava rótulos empilhados — que estão bem — e um validador com falsos positivos não se volta a
  correr.
- ⚠️ **Não substitui olhar.** Três figuras deste tópico passaram o passo automático e estavam
  visualmente más. Com `CAPTURAS=<pasta> ./validar.sh` os PNG ficam gravados, e o `PROCESSO.md`
  passa a dizer, na Fase 3, que é preciso vê-los.
- 🔴 **E apanhou dois erros antigos, em tópicos que já estavam dados como prontos:**
  em `cassete-dados/04-bits-em-som.html` o topo do rótulo «1 · por nível…» ficava 2 px acima do
  `viewBox` e era cortado; em `indices-btree-sql/02-do-indice-a-linha.html` o rótulo «estiver
  marcada → Heap Fetches» passava 4 px da margem direita e perdia o fim. Corrigidos, alargando o
  `viewBox` de cada um — nada se moveu em relação a nada.
  ⚠️ **Não levaram marca de correção na página**, e a razão fica escrita aqui em vez de ficar por
  dizer: a regra das «correções à vista» existe para quem leu uma afirmação errada, e aqui nenhuma
  afirmação estava errada — só alguns píxeis de um rótulo estavam cortados. Se algum dia uma destas
  figuras estiver a dizer outra coisa, aí leva a marca.
- Estado final: **62 páginas, 36 figuras, 0 problemas**, nos dois temas.

**Mecânica**

- `docs/almanaque/codigo/`: `almanaque.py` (motor), `ensaio.py` (8 secções de verificação contra fontes
  exteriores), `gerar.py` (o projeto) e `comparar.py` (lê o PDF oficial e mede). Todos **só biblioteca padrão**.
- `comparar.py` extrai as colunas do PDF do *Nautical Almanac* com `zlib` e `re`. 🔴 O PDF **não entra no
  repositório**: tem direitos de autor.
- `modelo/base.css`: classes novas `.destaque`, `.svg-traco-fino`, `.svg-traco-grosso`, `.svg-realce-traco`,
  `.svg-ponto`, `.svg-ponto-forte`, `.svg-texto-pequeno`.
- O passo 5 do `validar.sh` (termos sensíveis) disparou com razão numa frase do diagnóstico que dizia «não a tua
  m·o·r·a·d·a». **Reescrevi a frase em vez de acrescentar uma exceção ao validador** — a exceção enfraquecia-o
  para sempre e a frase não perdia nada.

## 2026-09-16 (4) — Os outros dois cursos também ganharam secção «Em vídeo»

- `docs/indices-btree-sql/bibliografia.html`: a cadeira **CMU 15-445/645, Intro to Database Systems** (Andy Pavlo),
  com as aulas #08, #09 (índices e filtros) e #10 (concorrência em índices) — a parte que este curso deixa de fora
  por opção. A secção «O que não está aqui» foi reescrita em vez de contradita: cursos em vídeo a ensinar a afinar
  queries continuam fora, porque não os vi; o que entrou é uma cadeira universitária com proveniência verificável,
  marcada como **não vista**, como percurso e não como recomendação de conteúdo.
- `docs/abstracts-e-resumos/bibliografia.html`: **Larry McEnerney**, *The Craft of Writing Effectively*
  (Universidade de Chicago, 2014) — a tese da lição 0 dita por quem dirigiu o programa de escrita da universidade
  durante quatro décadas; e **Simon Peyton Jones**, *How to Write a Great Research Paper*, com os diapositivos e a
  gravação de 34 minutos publicados pelo autor.
- Todas marcadas como **não vistas**, com a proveniência confirmada (página da cadeira, página do autor, verbete
  sobre o orador). No caso do McEnerney **não se escreve o endereço do vídeo**: o YouTube recusou a consulta, e um
  endereço que não abri não se cita — diz-se onde procurar.

## 2026-09-16 (3) — A bibliografia deixou de ser só leitura

**Processo**

- Regra alargada, a pedido do dono do repositório: «pelo menos uma fonte que não seja documentação» passa a
  incluir **qualquer media** — documentários, filmes, séries, palestras, vídeos, podcasts — e não só livros,
  artigos e cursos. A razão é a mesma de sempre: o que se procura é quem responda ao *porque é assim* em vez do
  *o que faz*, e isso tanto pode estar num livro como num documentário.
- Actualizados o `PROCESSO.md` (secção 11 e `bibliografia.html`) e os comandos `/aprender` e `/aprofundar`, que são
  quem executa a regra.

**Conteúdo**

- `docs/cassete-captura/bibliografia.html`: secção nova **«6. Em vídeo»**, com o documentário *Cassette: A
  Documentary Mixtape* (Smoot e Taylor, 2016) — marcado como **não visto**, porque não consigo ver vídeo, com a
  ficha confirmada e uma discrepância de duração entre fichas registada. E a declaração do que procurei e
  **não** recomendo: há dezenas de tutoriais de azimute no YouTube, não os vi nem sei avaliar a proveniência, e
  uma afinação mal explicada estraga fitas.
- `docs/cassete-dados/bibliografia.html`: o mesmo documentário na secção da história, onde Lou Ottens conta as
  escolhas do formato que a lição 7 explica.

## 2026-09-16 (2) — Digitalizar cassetes a sério: o curso que põe o simulador à prova de uma máquina real

**Novo**

- Tópico **Digitalizar cassetes a sério** (`docs/cassete-captura/`), continuação declarada do `cassete-dados`. O
  diagnóstico apanhou uma contradição — «sem prazo» com «há fitas que precisam de ser digitalizadas» — e resolveu-a com
  **dois percursos**: o das fitas (chega à primeira captura a sério em três semanas) e o do critério
  (`topicos/cassete-captura/DIAGNOSTICO.md`).
- Sete lições: ler um espetro · escolher, provar e não estragar a máquina · a cadeia de captura · o azimute · medir o wow
  e o flutter · o projeto com uma fita real · restaurar sem destruir. Com as normas de arquivo (IASA-TC 03 e TC-04) como
  fonte dos critérios numéricos.
- Três programas em `docs/cassete-captura/codigo/`: `captura.py` (espetro, relatório de captura, azimute, wow e flutter),
  `margens.py` (descodificar, provar e medir margens de uma fita real) e `ensaio.py` (uma fita de ensaio sintética, para
  praticar o projeto antes de haver máquina).
- Bibliografia, folha de consulta, teste intercalado, 37 flashcards e calendário de revisão.

**O que as fases apanharam** — por extenso na nota das fases do tópico. O essencial:

- 🔴 **O limite mais citado do curso anterior não é um limite.** «Parte a 1,5 amostras por meia onda» era propriedade do
  método de geração do simulador: reamostrando a mesma gravação pela FFT, falha a 8000 Hz, passa a 7000 e falha a 6500.
- 🔴 **O arnês de medição da lição 6 do `cassete-dados` não corria** — importava cinco funções que o `fita.py` publicado
  não tinha. Corrigido nesse tópico, com o ficheiro completo publicado e a correção à vista.
- 🔴 **Contradição entre tópicos:** a lição 3 do `cassete-dados` dizia que o azimute «mente sobre as horas». Não mente: o
  atraso é constante. Corrigida lá, com a marca de correção.
- 🔴 **42 de 42 respostas certas na opção «c»** — a rotação da posição usava `n · 3 % 3`, que é sempre zero. Apanhado pelo
  `validar.py`, que ganhou essa verificação depois da ocorrência anterior.
- Medições que mudaram o conteúdo: a soma dos canais **falha** onde cada canal sozinho lê (azimute ≥ 45′, pente a
  2021 Hz); um dropout que a captura ainda aguenta **gasta-lhe a margem toda**; o chiado põe um chão na medição do wow
  (0,115 % a 30 dB de SNR); a ida e volta de uma mudança de velocidade pela FFT dá −240 dB de erro, o que desmente, para
  métodos corretos, o aviso de Hoyt contra mudar a velocidade no digital.
- ⚠️ **Sem hardware:** não há deck nem cassetes. Todas as medições do curso são sobre sinais gerados, e isso está dito em
  cada sítio onde aparecem.

**Mecânica**

- `validar.py`: força UTF-8 na saída. Numa consola de Windows com a saída redirecionada, imprimir o «✓» final atirava
  `UnicodeEncodeError` — ou seja, o validador rebentava exactamente no caminho do sucesso.
- `modelo/base.css`: links dentro de `<figcaption>` passam a usar a cor de acento. Sem isso, ficavam com a cor por
  omissão do browser e falhavam o contraste WCAG AA no tema claro (2,33:1), apanhado pelo axe.
- `docs/index.html`: cartão do tópico novo, com a ressalva de que nenhuma medição foi feita em máquina real.

## 2026-09-16 — A cassete como memória de computador: um curso que acaba num descodificador que corre

**Novo**

- Tópico **A cassete como memória de computador** (`docs/cassete-dados/`), a partir do pedido com a página da Wikipédia
  «Cassette tape». O diagnóstico escolheu a porta «armazenamento de dados», com partida em zero em magnetismo e em sinal,
  e critério de sucesso «código que corre» (`topicos/cassete-dados/DIAGNOSTICO.md`).
- Oito lições, duas delas lição 0 de facto (amostragem e magnetismo): bias, os limites da fita, porque é que só o tempo
  sobrevive a uma fita, o formato do ZX Spectrum, o descodificador, e porque é que a cassete falhava e morreu — com a
  fronteira declarada contra o curso de índices B-tree (numa fita o acesso aleatório não é lento: não existe).
- Um gerador de fita e um descodificador em Python só com biblioteca padrão, com os limites medidos (taxa, ruído,
  corte de agudos, velocidade). Kansas City implementado de ponta a ponta, por contraste.
- Bibliografia, folha, teste intercalado, 53 flashcards, calendário de revisão.

**O que as fases apanharam** — está por extenso na nota das fases do tópico. O essencial: **todas** as saídas de código
que eu tinha escrito de cabeça estavam erradas; a lição do bias afirmava uma curva de distorção que era artefacto do
modelo; o descodificador perdia sempre o byte de paridade; cinco de nove figuras estavam mal a 400 px, uma delas a
contradizer o texto; e 42 de 48 respostas certas estavam na opção b.

**Mecânica**

- `validar.py`: caminhos com `as_posix()`. No Windows, `str(Path)` dava barras invertidas — oito erros falsos em
  `modelo/` e, pior, o `INDICE.md` regenerado **vazio** sem aviso.
- `validar.py`: novo `ver_posicoes_certas`, aviso quando mais de metade das respostas certas de um tópico está na mesma
  posição. Dispara hoje em `indices-btree-sql` (34 de 37 na b) — por corrigir, fora do âmbito desta sessão.
- `validar.sh`: `TIDY_PARA_VALIDAR` para apontar para um tidy-html5 5.x fora do Homebrew.

## 2026-09-15 — Abstracts e resumos técnicos: um curso sobre resumir para quem decide

**Novo**

- Tópico **Abstracts e resumos técnicos** (`docs/abstracts-e-resumos/`), a partir do pedido com a página da Wikipédia
  «Abstract (summary)» e do diagnóstico em `topicos/abstracts-e-resumos/DIAGNOSTICO.md`.
- Sete lições: o mecanismo de qualquer resumo (apagar, generalizar, construir — Kintsch & van Dijk) contra o método de
  Luhn a correr; informativo e indicativo; triagem de artigos; descrição de PR e título de commit; RFC, PEP e README;
  post-mortem; e diagnóstico intercalado de resumos maus.
- Folha imprimível, teste de domínio intercalado, 40 flashcards, calendário de revisão, projeto.
- Dois scripts com teste embutido: `luhn.py` (resumo extrativo de 1958) e `conferir_numeros.py` (a metade automatizável
  da definição de abstract deficiente de Pitkin et al.), e três textos para os exercícios.

**O que as fases apanharam** — está por extenso na nota das fases do tópico: nove erros da Fase 1 encontrados a reler
como aluno (afirmações sem fonte, uma paráfrase com um acrescento meu, termos por definir), e na Fase 3 cinco contagens
erradas, dois flashcards partidos, quatro diagramas ilegíveis a 400 px e respostas certas concentradas na opção b.

**Mecânica**

- `validar.py`: novo `ver_amostras`, que confere as contagens de palavras e caracteres que as páginas afirmam.
- `validar.sh`: filtro justificado para um falso positivo do tidy (`<ol type>`) e verificação das colunas dos flashcards.

## 2026-09-15 — Bibliografia

**Novo**

- O tópico **abstracts e resumos** ganhou quatro fontes que não vinham das lições, verificadas contra a
  página do editor: Schimel, *Writing Science* (OUP, 2012); Pinker, *The Sense of Style* (Viking, 2014),
  cap. 3; Williams, *Style* (com o aviso sobre as várias edições em circulação); e o curso gratuito de
  escrita técnica da Google — este último com a nota de que **não cobre resumos**, o que confirmei na
  página do curso.

- `bibliografia.html` em cada tópico: percurso de leitura ordenado por **por onde começar**, com o
  porquê e o que saltar em cada entrada.
- O tópico de índices ganhou os dois **artigos originais** das B-trees (Bayer & McCreight 1972;
  Comer 1979) e quatro livros — Winand, Rogov, Petrov, Kleppmann — cada um ligado à lição que continua.

**Corrigido**

- O curso de índices tinha sido publicado com **zero livros e zero artigos** nas fontes, contra o que
  o `PROCESSO.md` exige. A Fase 2 não apanhou porque só olhava para o conteúdo, nunca para o processo.
- A Fase 2 do `/aprender` passou a ter uma **lista de verificação contra o `PROCESSO.md`**, e o
  `/aprofundar` uma oitava pergunta sobre as fontes.
- O `validar.sh` passou a exigir `bibliografia.html` — se o processo exige e o validador não verifica,
  a exigência é decorativa.

## 2026-09-15 — A pesquisa passou a procurar dentro das lições

**Corrigido**

- A pesquisa do catálogo filtrava cartões com uma lista de palavras-chave escrita à mão.
  Testada com 21 termos reais, falhava em **8**: `bitmap`, `vacuum`, `heap fetches`,
  `work_mem`, `visibility map`, `prefixo`, `correlação`, `estatísticas`.
- Passa a usar um índice **gerado do conteúdo** das páginas pelo `sincronizar.py`
  (111 secções, ~85 kB inline), com relevância por **onde** o termo aparece e resultados
  agrupados por página, com ligação direta à secção.
- Limite declarado em D-015: acima de ~40 páginas indexadas, o índice inline deixa de caber
  e a decisão tem de ser revista.

## 2026-09-15 — Repositório criado e publicado

**No ar:** <https://hmgc2002.github.io/professor/> (GitHub Pages, `main:/docs`)

Confirmado, não assumido: as 15 páginas e ficheiros respondem 200, com os tipos certos
(`text/calendar` para o `.ics`, `text/csv` para os flashcards). O quiz corrige no site publicado,
as soluções estão fechadas, e a página não carrega **nenhum** recurso externo — zero pedidos fora
da própria origem, que é o que a decisão D-003 exige.

**Novo**

- Esqueleto completo: `CLAUDE.md`, `PROCESSO.md`, `DECISOES.md`, `INDICE.md`.
- `modelo/` com as três páginas-modelo (tópico, lição, folha), tema claro/escuro,
  barra lateral colapsável e quiz funcional sem rede.
- Validadores: `validar.py` (âncoras, ligações, `<details>`, quiz, índice),
  `validar_a11y.mjs` (axe-core nos dois temas), `validar.sh` (orquestra e inclui `tidy`).
- Quatro comandos em `.claude/commands/`: `aprender`, `corrigir`, `rever`, `aprofundar`.
- Tópico piloto **Índices B-tree em SQL**: diagnóstico, 7 lições, folha imprimível,
  teste de domínio, 40 flashcards e calendário de revisão espaçada.
