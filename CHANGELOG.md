# Registo de alterações

O formato é uma entrada por sessão de trabalho, com data. O que muda o que eu
consigo aprender fica no topo da entrada; o que muda só a mecânica fica no fim.

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
