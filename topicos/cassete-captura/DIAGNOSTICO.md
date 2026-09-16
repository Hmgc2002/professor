# Diagnóstico — Digitalizar cassetes a sério

**Data:** 2026-09-16 · **Slug:** `cassete-captura` · **Curso:** [docs/cassete-captura/](../../docs/cassete-captura/index.html)

> 🔴 Este ficheiro é público. Tem só o ponto de partida técnico, o material e o ritmo.
> Não se perguntou o que está gravado nas fitas nem de quem são, e não é preciso para ensinar isto.
> Se um dia for, vai para `topicos/cassete-captura/PRIVADO.md`, que está no `.gitignore`.

---

## O pedido

> Digitalização e restauro: alinhar o azimute, escolher a cadeia de captura, medir o wow e o flutter de
> uma máquina real. É o único caminho que transformaria os limites que mediste no simulador em limites
> medidos numa cassete a sério.

É a continuação declarada de [`cassete-dados`](../cassete-dados/DIAGNOSTICO.md). Esse curso assumiu
**«não tens leitor nem cassetes»** e gerou todo o áudio (D-024). Este curso existe porque esse pressuposto
caiu: há fitas, e algumas precisam de ser digitalizadas.

---

## As perguntas e as respostas

### 1. Para quê?

**As duas coisas**: fitas de **dados** (para o descodificador) e fitas de **áudio** (para guardar).

**O que isso decide:** as duas querem uma captura diferente, e o curso tem de ensinar a diferença em vez de
escolher uma. Para dados, o que importa é **onde estão as arestas no tempo**: a lição 6 do
`cassete-dados` mediu que o descodificador aguenta um passa-baixo a 800 Hz e só parte a 700 Hz. Para áudio, importa **tudo o que a
fita ainda tem**, com os agudos à cabeça, e o que se perde na captura já não se recupera. Por isso a lição
do azimute é a mesma para as duas, mas o critério para dar a captura por boa não é.

### 2. Que material?

| Perguntei | Resposta | O que decide |
|---|---|---|
| Leitor | **Nenhum.** «Recomenda-me o melhor» | O curso tem uma lição sobre **como escolher e verificar** uma máquina, com critérios medíveis, e não um modelo e pronto (ver abaixo) |
| Entrada no computador | **Placa de som interna do Mac mini**, e um HomePod | 🔴 **Isto não chega, se o Mac mini for de 2018 ou mais recente.** As fichas técnicas da Apple para o Mac mini de 2018 e de 2024 listam só uma tomada de **auscultadores** de 3,5 mm, que é uma saída: nenhum dos dois tem entrada de linha nem de microfone. O Mac mini (Late 2014) ainda tinha entrada de linha. ⚠️ As fichas dos modelos de 2020 e 2023 não as abri. O HomePod é um altifalante: serve para ouvir, não para gravar. **É preciso uma interface de áudio USB com entrada de linha**, e a lição 2 existe por causa disto |
| Ferramentas | **Só uma chave de fendas fina** | Nada de osciloscópio, multímetro nem fita de teste. As medições do curso fazem-se **com o próprio computador**, e o azimute alinha-se **sem fita de teste**, pelo método que a norma de arquivo (IASA-TC 04 §5.4.12) aceita: pelos agudos da própria fita |

**Porque não recomendo «o melhor» sem mais nada.** A resposta curta existe: um *Nakamichi Dragon* corrige o
azimute sozinho, fita a fita (sistema NAAC). A Wikipédia descreve-o como o primeiro gravador de série a fazê-lo,
e Hoyt (lição 1) põe-no em segundo lugar na lista dele. Mas foi vendido entre 1982 e 1994, precisa de
manutenção, e Hoyt avisa que pode andar à procura do azimute em fitas difíceis. E sobretudo **esconde o mecanismo que este curso quer que aprendas**: o critério de
sucesso pede que expliques os limites, e uma máquina que alinha sozinha não te obriga a percebê-los. A
recomendação do curso é uma **lista de verificação**, feita com os números da IASA para um leitor de
arquivo:

- ajuste de azimute acessível;
- variação de velocidade melhor do que 0,3 %;
- wow e flutter ponderados melhor do que 0,1 %;
- resposta de 30 Hz a 20 kHz dentro de +2/−3 dB;
- leitura de fitas de tipo I, II e IV.

Hoyt, que escreveu o guia de transferências usado na lição 1, recomendava Nakamichi usados e dizia que modelos
topo de gama da Sony, da Denon e da Tascam também servem. Não dou um modelo único: ⚠️ **não verifiquei preços nem o
mercado de usados**, e não os escrevo.

### 3. De onde partes?

**Zero, e respondido sem amaciar:**

| Perguntei | Resposta |
|---|---|
| Fizeste as lições 0–4 de `cassete-dados`? | **Não** |
| Abriste um aparelho, ajustaste um parafuso de afinação, soldaste? | **Não** |
| Audacity, sox, numpy/scipy para ver um espetro (FFT)? | **Não** |
| Demodulação de FM, ponderação? | **Não** |

**O que isso decide:**

- 🔴 **O `cassete-dados` passa a ser pré-requisito, e não se repete aqui.** A física da fita (lição 1), os
  limites (lição 3) e o descodificador (lições 5 e 6) vivem lá. Copiá-los para cá era criar dois sítios para
  corrigir. O mapa deste curso mostra essas lições **como lições do percurso**, com a ordem em que as fazes,
  e não como notas de rodapé.
- **Há uma lição 0 própria**: *ver as frequências de um sinal* (o espetro, a FFT, o espetrograma no
  Audacity). Não existe em nenhum dos dois cursos (procurado; ver a nota das fases) e é pré-requisito de
  tudo o que aqui se mede.
- **A demodulação de frequência e a ponderação** entram na lição do wow e do flutter, construídas a partir
  do zero, porque é ali que servem.
- **Abrir aparelhos:** a lição 1 tem uma secção de segurança. O azimute ajusta-se com a máquina a tocar, e
  por isso a regra de onde se mete e onde não se mete a chave de fendas tem de estar escrita antes de haver
  uma máquina na mesa.

### 4. Tempo e prazo

**Até 1 h por dia, sem prazo, como no tópico anterior. Mas há fitas que precisam de ser digitalizadas.**

⚠️ **Estas duas respostas puxam em sentidos contrários**, e digo-o em vez de fingir que não. «Sem prazo»
com «há fitas que precisam» quer dizer: **o curso não tem prazo, as fitas têm**. Se o curso for feito pela
ordem natural (os dois tópicos, ~8 semanas), a primeira captura séria acontece no fim, e cada semana
de espera é uma semana a mais de fita guardada.

**Resolução: dois percursos com um ponto de encontro.**

| | O que é | Quando |
|---|---|---|
| **Percurso das fitas** | O mínimo para capturar **uma vez e bem**, e guardar o ficheiro bruto: lição 0, lição 1, lição 2, lição 3 deste curso, mais as lições 0 e 1 do `cassete-dados` | ~2–3 semanas, mais o tempo de arranjar a máquina e a interface |
| **Percurso do critério** | Tudo o resto: o wow e o flutter, as lições 2–6 do `cassete-dados`, a fita de dados real e o restauro | ~5 semanas depois |

A regra que torna isto seguro: **o restauro faz-se sobre o ficheiro, não sobre a fita.** Uma captura bem
feita e guardada sem processamento pode ser restaurada daqui a um ano, quando souberes mais. Uma captura
mal alinhada não se restaura: os agudos perdidos por azimute não voltam (IASA-TC 04 §5.4.12.3). Por isso
**o azimute está no percurso das fitas** e o restauro não está.

🔴 **Até lá, não toques as fitas que importam.** A máquina que chegar primeiro prova-se com uma fita que não
tenha valor nenhum. Uma máquina com correias ou rolete gastos pode estragar a fita que lá entrar.

⭐ Se alguma fita for insubstituível e estiver em mau estado (a desfazer-se, com bolor, partida), a resposta
honesta é que um serviço profissional de transferência é mais seguro do que a primeira tentativa de quem
está a aprender. O curso diz como reconhecer esses casos (lição 1).

### 5. Como saberemos que aprendeste?

**(b)** Uma fita de dados real sai **byte a byte correta** do teu descodificador, e explicas quais dos
limites do simulador se confirmaram e quais não.

**O que isso decide:**

- O critério **depende da lição 6 do `cassete-dados`**: o descodificador é esse. O percurso do critério
  inclui-a obrigatoriamente.
- A lição 5 deste curso é o **projeto**: capturar uma fita de dados, descodificá-la e confrontar **cada um
  dos quatro limites** medidos no simulador (parte a 1,5 amostras por meia onda, a SNR ≈ 16 dB, a um corte
  de 700 Hz e a 25 % de wow) com o que a fita real mostra.
- «Byte a byte correta» numa fita real não tem original para comparar. O curso diz o que conta como prova:
  a paridade XOR de cada bloco, o cabeçalho coerente com o comprimento do bloco de dados, e **duas capturas
  independentes que dão os mesmos bytes**.

---

## O que assumi (e o que muda se estiver errado)

| Assumi | Porquê | Se estiver errado |
|---|---|---|
| **O Mac mini é de 2018 ou mais recente** (sem entrada de áudio) | Verifiquei-o nas fichas de 2018 e de 2024 (não nas de 2020 e 2023), e respondeste «placa de som interna» sem dizer o ano | Se for de 2014 ou anterior, tens entrada de linha de 3,5 mm e podes começar sem comprar a interface. A lição 2 ensina-te a **medir** se essa entrada é boa o suficiente |
| **As fitas de dados são de ZX Spectrum** | É o formato do descodificador que já existe (`cassete-dados`, D-025) | Se forem de outra máquina (C64, Amstrad, MSX), a captura e o azimute ficam iguais, mas o critério de sucesso precisa de um descodificador novo. A lição 4 do `cassete-dados` dá a base; o projeto cresce uma semana |
| **Tens pelo menos uma fita de dados que podes tocar várias vezes** | O critério pede duas capturas independentes | Se só houver fitas preciosas, o projeto faz-se com uma fita gravada por ti a partir de um `.tap` (precisa de uma máquina que grave). Os limites medidos passam a ser os da **tua** gravação, e isso diz-se |
| **A máquina vai ser um deck de secretária, comprado usado** | Recomendação da lição 1 | Com um leitor USB barato ou um walkman, o curso faz-se na mesma, e a lição 4 passa a medir **porque é que** a captura é pior. Não há ajuste de azimute acessível em muitos deles, e a lição 3 fica em teoria até haver outra máquina |
| **Python 3 e NumPy** — ⚠️ **muda em relação ao `cassete-dados`**, que era só biblioteca padrão | Uma FFT de minutos de áudio a 96 kHz em Python puro demora demasiado para ser um exercício. `pip install numpy` é uma dependência só, e é a biblioteca de referência para isto | Se não quiseres instalar nada, os exercícios da lição 0 correm na biblioteca padrão com sinais curtos. Os das lições 3 e 4 ficam lentos (minutos) mas corretos |
| **Capturas no Mac, estudas e corres o código em qualquer máquina** | O repositório está num Windows; a interface vai ligada ao Mac | Nada: o código é portável, e o Audacity existe nos dois sistemas. Os caminhos de menu são os da versão para macOS |
| **Não vais abrir a caixa de um aparelho ligado à corrente** | Nunca abriste nenhum | A lição 1 diz o que se faz com a caixa **fechada** e onde parar. Soldar e trocar correias ficam fora do curso, e diz-se a quem se pede |
| **Os limites medidos no simulador são os da lição 6 do `cassete-dados`**: parte a 1,5 amostras por meia onda, a SNR ≈ 16 dB, a um corte de 700 Hz e a 25 % de wow (3 Hz) | Estão escritos na nota das fases desse tópico | Se o descodificador mudar, a tabela da lição 5 muda com ele |

---

## Estado

| | |
|---|---|
| Diagnóstico | ✅ 2026-09-16 |
| Curso publicado | ⬜ |
| Máquina e interface | ⬜ por arranjar |
| Primeira entrega em `respostas/` | ⬜ ainda nenhuma |
