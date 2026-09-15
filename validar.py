#!/usr/bin/env python3
"""Validador estrutural e pedagógico das páginas de docs/ e modelo/.

Só stdlib (DECISOES.md D-012): o macOS traz Python 3.9 e instalar dependências
para correr um validador é criar uma razão para o não correr.

🔴 Regra: um validador com falsos positivos não se volta a correr. Se este
acusar algo que está certo, corrige-se O VALIDADOR — nunca se acrescenta uma
exceção para calar um aviso verdadeiro.

A armadilha já paga: o validador do `compendio` acusou-se a si próprio três
vezes por procurar `href="#..."` com expressões regulares e apanhar texto que
vivia dentro de <pre> e <code>. Aqui a extração é feita com um parser de HTML,
que vê tags a sério e nunca vê texto escapado como se fosse uma ligação.
modelo/licao.html tem um caso desses lá dentro, de propósito, como sentinela.
"""
import html.parser
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

VERMELHO, AMARELO, VERDE, CINZA, FIM_COR = "\033[31m", "\033[33m", "\033[32m", "\033[90m", "\033[0m"
if not sys.stdout.isatty():
    VERMELHO = AMARELO = VERDE = CINZA = FIM_COR = ""


class No:
    __slots__ = ("tag", "attrs", "filhos", "pai", "linha", "texto")

    def __init__(self, tag, attrs, linha, pai=None):
        self.tag, self.attrs, self.linha, self.pai = tag, dict(attrs), linha, pai
        self.filhos, self.texto = [], []

    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def texto_todo(self):
        partes = list(self.texto)
        for f in self.filhos:
            partes.append(f.texto_todo())
        return "".join(partes)

    def descendentes(self):
        for f in self.filhos:
            yield f
            yield from f.descendentes()

    def dentro_de(self, *tags):
        p = self.pai
        while p is not None:
            if p.tag in tags:
                return True
            p = p.pai
        return False

    def dentro_de_classe(self, classe):
        p = self.pai
        while p is not None:
            if classe in p.classes():
                return True
            p = p.pai
        return False


class Arvore(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = No("#raiz", [], 0)
        self.actual = self.raiz

    def handle_starttag(self, tag, attrs):
        no = No(tag, attrs, self.getpos()[0], self.actual)
        self.actual.filhos.append(no)
        if tag not in VOID:
            self.actual = no

    def handle_startendtag(self, tag, attrs):
        self.actual.filhos.append(No(tag, attrs, self.getpos()[0], self.actual))

    def handle_endtag(self, tag):
        no = self.actual
        while no is not self.raiz and no.tag != tag:
            no = no.pai
        if no is not self.raiz:
            self.actual = no.pai

    def handle_data(self, dados):
        self.actual.texto.append(dados)

    # handle_comment não faz nada: comentários nunca entram na árvore,
    # por isso uma âncora escrita dentro de um comentário não é procurada.


class Relatorio:
    def __init__(self):
        self.erros, self.avisos = [], []

    def erro(self, ficheiro, linha, msg):
        self.erros.append((ficheiro, linha, msg))

    def aviso(self, ficheiro, linha, msg):
        self.avisos.append((ficheiro, linha, msg))


def analisar(caminho):
    arv = Arvore()
    arv.feed(caminho.read_text(encoding="utf-8"))
    arv.close()
    return arv.raiz


# ---------------------------------------------------------------- verificações

def ver_ids_e_ancoras(rel, rp, raiz, ids_por_pagina):
    vistos = {}
    for no in raiz.descendentes():
        ident = no.attrs.get("id")
        if not ident:
            continue
        if ident in vistos:
            rel.erro(rp, no.linha, f"id duplicado «{ident}» (o outro está na linha {vistos[ident]})")
        else:
            vistos[ident] = no.linha
    ids_por_pagina[rp] = set(vistos)


def ver_ligacoes(rel, rp, raiz, ids_por_pagina, caminho):
    for no in raiz.descendentes():
        href = no.attrs.get("href") if no.tag == "a" else None
        if not href:
            continue
        # Espaço reservado: só faz sentido dentro de modelo/, onde os ficheiros
        # do tópico ainda não existem. Fora de modelo/ é erro (ver abaixo).
        reservado = "data-espaco-reservado" in no.attrs
        if reservado and not rp.startswith("modelo/"):
            rel.erro(rp, no.linha, f"data-espaco-reservado fora de modelo/ em «{href}» — ou a ligação é a sério, ou sai")
            continue
        if reservado or href.startswith(("http://", "https://", "mailto:", "data:", "tel:")):
            continue
        alvo, _, frag = href.partition("#")
        if not alvo:  # âncora na própria página
            if frag and frag not in ids_por_pagina[rp]:
                rel.erro(rp, no.linha, f"âncora órfã «#{frag}» — não há nenhum id com esse nome nesta página")
            continue
        destino = (caminho.parent / alvo).resolve()
        if not destino.exists():
            rel.erro(rp, no.linha, f"ligação quebrada «{href}» — {destino.relative_to(RAIZ) if RAIZ in destino.parents else destino} não existe")
            continue
        if frag and destino.suffix == ".html":
            drp = str(destino.relative_to(RAIZ))
            if drp not in ids_por_pagina:
                ids_por_pagina[drp] = {n.attrs["id"] for n in analisar(destino).descendentes() if n.attrs.get("id")}
            if frag not in ids_por_pagina[drp]:
                rel.erro(rp, no.linha, f"âncora órfã «{href}» — {alvo} existe mas não tem id «{frag}»")


def ver_solucoes(rel, rp, raiz):
    for no in raiz.descendentes():
        if no.tag != "details":
            continue
        sums = [f for f in no.filhos if f.tag == "summary"]
        if not sums:
            rel.erro(rp, no.linha, "<details> sem <summary>")
            continue
        for s in sums:
            if any(d.tag == "a" for d in s.descendentes()):
                rel.erro(rp, s.linha, "<summary> com <a> lá dentro — o clique fica ambíguo para teclado e leitor de ecrã")
        if "open" in no.attrs:
            rel.erro(rp, no.linha,
                     "<details> aberto por defeito — a solução visível antes da tentativa apaga a dificuldade desejável")


def ver_quiz(rel, rp, raiz):
    for quiz in raiz.descendentes():
        if "quiz" not in quiz.classes():
            continue
        if not quiz.attrs.get("data-quiz"):
            rel.aviso(rp, quiz.linha, ".quiz sem data-quiz — o estado guardado colide com o de outra página")
        perguntas = [n for n in quiz.descendentes() if "pergunta" in n.classes() and n.tag == "li"]
        if not perguntas:
            rel.erro(rp, quiz.linha, ".quiz sem nenhuma li.pergunta")
        for p in perguntas:
            if not any("enunciado" in n.classes() for n in p.descendentes()):
                rel.erro(rp, p.linha, "pergunta sem .enunciado")
            opcoes = [n for n in p.descendentes() if n.tag == "li" and "opcao" in n.classes()]
            if len(opcoes) < 2:
                rel.erro(rp, p.linha, f"pergunta com {len(opcoes)} opção(ões) — precisa de pelo menos 2")
            certas = 0
            nomes = set()
            for o in opcoes:
                entradas = [n for n in o.descendentes() if n.tag == "input"]
                if not entradas:
                    rel.erro(rp, o.linha, "li.opcao sem <input type=radio>")
                    continue
                e = entradas[0]
                nomes.add(e.attrs.get("name"))
                if not e.attrs.get("value"):
                    rel.erro(rp, o.linha, "opção sem value — o estado não se consegue guardar nem repor")
                certa = e.attrs.get("data-certa")
                if certa not in ("true", "false"):
                    rel.erro(rp, o.linha, f"opção com data-certa=«{certa}» — tem de ser \"true\" ou \"false\"")
                certas += certa == "true"
                if not any("rotulo" in n.classes() for n in o.descendentes()):
                    rel.erro(rp, o.linha, "opção sem .rotulo — a entrega em Markdown não consegue dizer o que foi escolhido")
                expl = [n for n in o.descendentes() if "explicacao" in n.classes()]
                if not expl:
                    rel.erro(rp, o.linha, "opção sem .explicacao — 🔴 cada opção explica-se, também as erradas")
                elif len(expl[0].texto_todo().strip()) < 25:
                    rel.erro(rp, o.linha, "explicação com menos de 25 caracteres — não explica, confirma")
                elif "hidden" not in expl[0].attrs:
                    rel.erro(rp, o.linha, ".explicacao sem hidden — fica à vista antes de responder")
            if certas != 1:
                rel.erro(rp, p.linha, f"pergunta com {certas} opções certas — tem de ser exatamente 1")
            if len(nomes) > 1:
                rel.erro(rp, p.linha, f"opções da mesma pergunta com names diferentes {sorted(nomes)} — dá para escolher várias")
        if not any("data-verificar" in n.attrs for n in quiz.descendentes()):
            rel.erro(rp, quiz.linha, "quiz sem botão [data-verificar] — não há correção imediata")


def ver_basico(rel, rp, raiz, texto):
    htmls = [n for n in raiz.descendentes() if n.tag == "html"]
    if not htmls or htmls[0].attrs.get("lang") != "pt-PT":
        rel.erro(rp, 1, '<html> sem lang="pt-PT" — o leitor de ecrã lê português com pronúncia inglesa')
    if not any(n.tag == "title" and n.texto_todo().strip() for n in raiz.descendentes()):
        rel.erro(rp, 1, "página sem <title> com texto")
    if not any(n.tag == "meta" and n.attrs.get("name") == "viewport" for n in raiz.descendentes()):
        rel.erro(rp, 1, "sem <meta name=viewport> — não funciona a 400 px")
    h1s = [n for n in raiz.descendentes() if n.tag == "h1"]
    if len(h1s) != 1:
        rel.erro(rp, 1, f"{len(h1s)} elementos <h1> — tem de ser exatamente 1")
    for n in raiz.descendentes():
        if n.tag == "title" and not n.dentro_de("svg") and "id" in n.attrs:
            # O tidy avisa de <title id> em qualquer sítio porque não conhece SVG;
            # dentro de <svg> é válido e necessário para aria-labelledby. A verificação
            # verdadeira vive aqui, e por isso o validar.sh pode filtrar esse aviso.
            rel.erro(rp, n.linha, "<title> do <head> com id — atributo não permitido aí")
        if n.tag == "img" and "alt" not in n.attrs:
            rel.erro(rp, n.linha, "<img> sem alt")
        if n.tag == "svg" and not (n.attrs.get("aria-labelledby") or n.attrs.get("aria-label") or n.attrs.get("aria-hidden")):
            rel.erro(rp, n.linha, "<svg> sem aria-labelledby/aria-label/aria-hidden")
        if n.tag == "table" and not n.dentro_de_classe("tabela-rolavel"):
            rel.aviso(rp, n.linha, "<table> fora de .tabela-rolavel — a 400 px estoura a página")
        if n.tag == "textarea":
            ident = n.attrs.get("id")
            rotulado = n.attrs.get("aria-label") or (ident and re.search(r'<label[^>]*\bfor="%s"' % re.escape(ident), texto))
            if not rotulado:
                rel.erro(rp, n.linha, "<textarea> sem <label for> nem aria-label")
    for marcador in ("/* INICIO ESTILO */", "/* INICIO COMPORTAMENTO */"):
        if marcador not in texto:
            rel.erro(rp, 1, f"sem o marcador {marcador} — sincronizar.py não consegue manter o estilo alinhado")


def ver_tabela_rolavel(rel, rp, raiz):
    for n in raiz.descendentes():
        if "tabela-rolavel" not in n.classes():
            continue
        if n.attrs.get("tabindex") != "0":
            rel.erro(rp, n.linha, '.tabela-rolavel sem tabindex="0" — não se rola com o teclado')
        if not (n.attrs.get("aria-label") or n.attrs.get("aria-labelledby")):
            rel.erro(rp, n.linha, ".tabela-rolavel com role=region sem nome acessível")


# ---------------------------------------------------------------- índice

def gerar_indice(paginas):
    linhas = ["# ÍNDICE",
              "",
              "Gerado por `validar.py`. **Não editar à mão.** Uma linha por cabeçalho com `id`, em todas as",
              "páginas publicadas — é por aqui que a Fase 0 procura o que já existe, antes de escrever outra vez",
              "o que já está escrito.",
              ""]
    for rp, raiz in paginas:
        titulo = next((n.texto_todo().strip() for n in raiz.descendentes() if n.tag == "title"), rp)
        linhas.append(f"## `{rp}` — {titulo}")
        linhas.append("")
        achou = False
        for n in raiz.descendentes():
            if n.tag in ("h1", "h2", "h3") and n.attrs.get("id"):
                nivel = int(n.tag[1])
                texto = " ".join(n.texto_todo().split())
                linhas.append(f"{'  ' * (nivel - 1)}- [{texto}]({rp}#{n.attrs['id']})")
                achou = True
        if not achou:
            linhas.append("_(sem cabeçalhos com id)_")
        linhas.append("")
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- principal

def main():
    so_verificar = "--verificar-indice" in sys.argv
    alvos = sorted(list((RAIZ / "docs").rglob("*.html")) + list((RAIZ / "modelo").rglob("*.html")))
    if not alvos:
        print(f"{AMARELO}nenhuma página encontrada em docs/ ou modelo/{FIM_COR}")
        return 0

    rel = Relatorio()
    ids_por_pagina, paginas = {}, []

    for caminho in alvos:
        rp = str(caminho.relative_to(RAIZ))
        texto = caminho.read_text(encoding="utf-8")
        raiz = analisar(caminho)
        paginas.append((rp, raiz))
        ver_ids_e_ancoras(rel, rp, raiz, ids_por_pagina)
        ver_basico(rel, rp, raiz, texto)
        ver_solucoes(rel, rp, raiz)
        ver_quiz(rel, rp, raiz)
        ver_tabela_rolavel(rel, rp, raiz)

    for caminho in alvos:
        rp = str(caminho.relative_to(RAIZ))
        ver_ligacoes(rel, rp, dict(paginas)[rp], ids_por_pagina, caminho)

    indice_novo = gerar_indice([(rp, r) for rp, r in paginas if rp.startswith("docs/")])
    fich_indice = RAIZ / "INDICE.md"
    antigo = fich_indice.read_text(encoding="utf-8") if fich_indice.exists() else ""
    if antigo != indice_novo:
        if so_verificar:
            rel.erro("INDICE.md", 1, "desactualizado — corre ./validar.sh")
        else:
            fich_indice.write_text(indice_novo, encoding="utf-8")
            print(f"{CINZA}INDICE.md regenerado{FIM_COR}")

    for f, l, m in rel.avisos:
        print(f"{AMARELO}aviso{FIM_COR}  {f}:{l}  {m}")
    for f, l, m in rel.erros:
        print(f"{VERMELHO}ERRO{FIM_COR}   {f}:{l}  {m}")

    n = len(alvos)
    if rel.erros:
        print(f"\n{VERMELHO}{len(rel.erros)} erro(s){FIM_COR} em {n} página(s). Nada se publica assim.")
        return 1
    print(f"{VERDE}✓{FIM_COR} {n} página(s) sem erros"
          + (f" ({len(rel.avisos)} aviso(s))" if rel.avisos else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
