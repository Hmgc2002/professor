#!/usr/bin/env bash
# Corre antes de cada commit que toca em docs/. Falha = não se faz commit.
#
# 🔴 Um validador com falsos positivos não se volta a correr. Se algum destes
# passos acusar algo que está certo, corrige-se O PASSO — nunca se acrescenta
# uma exceção para calar um aviso verdadeiro. Cada filtro aqui tem de trazer
# escrito porque é que o que ele apaga é mesmo ruído.
set -uo pipefail
cd "$(dirname "$0")"

V=$'\033[31m'; A=$'\033[33m'; G=$'\033[32m'; C=$'\033[90m'; Z=$'\033[0m'
[ -t 1 ] || { V=""; A=""; G=""; C=""; Z=""; }

falhou=0
por_validar=""
passo() { printf '\n%s▸ %s%s\n' "$C" "$1" "$Z"; }

# ---------------------------------------------------------------- 0. sincronia
passo "0/5  CSS e JS inline em sincronia com modelo/ (DECISOES.md D-005)"
if ! python3 sincronizar.py --verificar; then
  echo "${V}corre: python3 sincronizar.py${Z}"
  falhou=1
fi

# ---------------------------------------------------------------- 1-2-5-6. estrutura
passo "1/5  âncoras, ligações, quiz, soluções fechadas, INDICE.md"
python3 validar.py || falhou=1

# ---------------------------------------------------------------- 3. HTML
passo "2/5  HTML bem formado (tidy do Homebrew — o /usr/bin/tidy é de 2006 e não conhece HTML5)"
TIDY=""
for c in /opt/homebrew/bin/tidy /usr/local/bin/tidy; do
  [ -x "$c" ] && TIDY="$c" && break
done
if [ -z "$TIDY" ]; then
  echo "${A}tidy do Homebrew não encontrado — instala com: brew install tidy-html5${Z}"
  echo "${A}(este passo ficou por correr; não conta como passado)${Z}"
  falhou=1
else
  "$TIDY" --version | head -1 | sed "s/^/${C}/;s/$/${Z}/"
  saida_tidy=""
  for f in docs/*.html docs/*/*.html modelo/*.html; do
    [ -e "$f" ] || continue
    # Filtro 1: <title id="…"> dentro de <svg> é SVG válido e obrigatório para
    # aria-labelledby; o tidy 5.8 não conhece SVG e trata-o como o <title> do <head>.
    # A verificação a sério do <title> do <head> está em validar.py (ver ver_basico).
    # Filtro 2: <ol type="…"> é HTML válido — a especificação WHATWG lista reversed, start e
    # type como atributos de <ol>, com os valores 1, a, A, i, I (conferido a 2026-09-15 em
    # html.spec.whatwg.org, «The ol element»). O tidy 5.8 diz que não é HTML5; está errado.
    linhas=$("$TIDY" -q -e "$f" 2>&1 | grep -v 'Warning: <title> proprietary attribute "id"' \
                                     | grep -v 'Warning: <ol> attribute "type" not allowed for HTML5')
    [ -n "$linhas" ] && saida_tidy+=$(printf '%s\n' "$linhas" | sed "s|^|$f |")$'\n'
  done
  if [ -n "$saida_tidy" ]; then
    printf '%s' "$saida_tidy" | sed "s/^/${V}HTML${Z}  /"
    falhou=1
  else
    echo "${G}✓${Z} HTML bem formado"
  fi
fi

# ---------------------------------------------------------------- 4. acessibilidade
passo "3/5  acessibilidade (axe-core, WCAG A/AA, nos dois temas, a 400 e 1280 px)"
if [ ! -d node_modules/axe-core ] || [ ! -d node_modules/puppeteer ]; then
  echo "${A}axe-core/puppeteer não instalados — corre: npm install${Z}"
  echo "${A}🔴 A acessibilidade FICOU POR VALIDAR. Não publiques um tópico novo sem correr isto.${Z}"
  por_validar="acessibilidade (axe-core não instalado)"
else
  node validar_a11y.mjs docs/*.html docs/*/*.html modelo/*.html
  estado=$?
  if [ $estado -eq 1 ]; then
    falhou=1
  elif [ $estado -ne 0 ]; then
    echo "${A}o axe não chegou a correr (código $estado).${Z}"
    echo "${A}Causa conhecida no macOS ARM: o Chrome que o puppeteer descarrega vem SEM assinatura,${Z}"
    echo "${A}e o kernel mata binários arm64 não assinados. Assiná-lo com 'codesign --deep' NÃO resolve${Z}"
    echo "${A}— dá 'main executable failed strict validation', porque o bundle tem frameworks aninhados.${Z}"
    echo "${A}A correção que funciona é usar um Chrome já assinado:${Z}"
    echo "${C}  brew install --cask google-chrome${Z}"
    echo "${A}O validar_a11y.mjs encontra-o sozinho. Para apontar para outro:${Z}"
    echo "${C}  CHROME_PARA_VALIDAR=/caminho/para/chrome ./validar.sh${Z}"
    echo "${A}🔴 A acessibilidade FICOU POR VALIDAR.${Z}"
    por_validar="acessibilidade (o browser não arrancou)"
  fi
fi

# ---------------------------------------------------------------- 5. ficheiros do tópico
passo "4/5  cada tópico com folha, teste, flashcards e calendário"
for d in docs/*/; do
  [ -e "$d/index.html" ] || continue
  nome=$(basename "$d")
  for f in folha.html teste.html flashcards.csv revisao.ics; do
    if [ ! -e "$d$f" ]; then
      if grep -q "em construção" "$d/index.html" 2>/dev/null; then
        echo "${A}aviso${Z}  $nome: falta $f (tópico marcado 🚧 em construção)"
      else
        echo "${V}ERRO${Z}   $nome: falta $f e o tópico não está marcado 🚧 em construção"
        falhou=1
      fi
    fi
  done
done
# O separador dos flashcards é «;». Um «;» dentro do texto de um cartão parte-o em quatro
# colunas e o Anki importa-o torto, sem erro. Já aconteceu (abstracts-e-resumos, 2026-09-15).
for csv in docs/*/flashcards.csv; do
  [ -e "$csv" ] || continue
  tortos=$(python3 -c "import csv,sys; r=list(csv.reader(open(sys.argv[1],encoding='utf-8'),delimiter=';')); print(' '.join(str(i+1) for i,l in enumerate(r) if len(l)!=3))" "$csv")
  if [ -n "$tortos" ]; then
    echo "${V}ERRO${Z}   $csv: linhas sem exatamente 3 colunas (frente;verso;etiqueta): $tortos"
    falhou=1
  fi
done
echo "${G}✓${Z} ficheiros de fim de tópico verificados"

# ---------------------------------------------------------------- 6. nada de privado
passo "5/5  nada de pessoal no que vai para um repositório público (DECISOES.md D-001)"
# -w: palavra inteira. Sem isto, «nif» apanha «sig{nif}icam» — e um validador
# que grita por causa de «significam» é um validador que se deixa de correr.
if grep -rwniE 'morada|código postal|nif|iban|contribuinte|cartão de cidadão|palavra-passe|password|api[_-]?key|secret|token' \
     docs/ topicos/ --include='*.html' --include='*.md' --include='*.csv' 2>/dev/null \
     | grep -vE 'validar|palavra-passe do|exemplo:' ; then
  echo "${V}Há termos sensíveis nos ficheiros publicados. Confirma cada um antes do commit.${Z}"
  falhou=1
else
  echo "${G}✓${Z} sem termos sensíveis"
fi

# ----------------------------------------------------------------
echo
if [ "$falhou" -ne 0 ]; then
  echo "${V}✗ validação falhou — não se faz commit assim.${Z}"
  exit 1
fi
if [ -n "$por_validar" ]; then
  # Dizer "tudo limpo" quando um passo não chegou a correr é a forma mais fácil
  # de um validador mentir. O resumo tem de arrastar consigo o que ficou por fazer.
  echo "${A}✓ o que correu, correu limpo — MAS ficou por validar: ${por_validar}.${Z}"
  echo "${A}  Não publiques um tópico novo assim sem saberes que o estás a fazer.${Z}"
  exit 0
fi
echo "${G}✓ tudo limpo.${Z}"
