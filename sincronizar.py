#!/usr/bin/env python3
"""Injeta modelo/base.css e modelo/base.js em cada página HTML.

Porque existe: DECISOES.md D-003 exige páginas autocontidas (abrem do disco,
sem build, sem rede). A regra «corrigir num sítio é corrigir em todos» torna
N cópias de CSS uma bomba-relógio. D-005 resolve a tensão: a FONTE é um
ficheiro só, o RESULTADO publicado continua inline. Quem lê a página não
precisa deste script — só quem edita o estilo precisa.

Uso:
    python3 sincronizar.py            # escreve
    python3 sincronizar.py --verificar  # só diz o que está dessincronizado (sai 1)
"""
import json
import re
import sys
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
PARES = [
    ("modelo/base.css", "/* INICIO ESTILO */", "/* FIM ESTILO */"),
    ("modelo/base.js", "/* INICIO COMPORTAMENTO */", "/* FIM COMPORTAMENTO */"),
]
INI_BUSCA, FIM_BUSCA = "/* INICIO INDICE-PESQUISA */", "/* FIM INDICE-PESQUISA */"

PALAVRA = re.compile(r"[0-9A-Za-zÀ-ÿ_]+")

# Palavras que aparecem em toda a parte e não distinguem nada. Cortá-las reduz
# o índice para metade sem tirar capacidade de procura. Não é uma lista de
# "stopwords" a sério, é o que apareceu mesmo com frequência inútil.
VAZIAS = set("""
a as o os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre entre
ate até e ou mas que se como quando onde porque porquê pois logo entao então
ser sou é são era eram foi foram seja sejam sendo sido estar esta está estao estão estava
ter tem têm tinha tendo tido haver ha há havia fazer faz fez feito
seu sua seus suas meu minha teu tua nosso nossa este esta esse essa aquele aquela isto isso aquilo
ele ela eles elas eu tu nos nós vos lhe lhes me te se si
mais menos muito muita muitos muitas pouco pouca todo toda todos todas algum alguma cada qualquer
outro outra outros outras mesmo mesma proprio própria tal tao tão ja já ainda sempre nunca
nao não sim tambem também so só apenas bem mal melhor pior grande pequeno
aqui ali la lá agora depois antes hoje ontem amanha amanhã
qual quais quanto quantos quem cujo cuja
""".split())


def indice_de_pesquisa():
    """Constrói o índice de pesquisa a partir do CONTEÚDO das páginas.

    Porque existe: a primeira versão da pesquisa filtrava os cartões do catálogo
    usando uma lista de palavras-chave escrita à mão. Metade dos conceitos do
    curso piloto — bitmap, vacuum, work_mem, visibility map — não aparecia lá, e
    portanto não se encontrava. Uma lista manual nasce incompleta e envelhece a
    cada lição nova; além disso contradiz a regra da Fase 0 («procurar o termo e
    o que a coisa serve para fazer»), que só funciona se houver o que procurar.

    O que se indexa, por secção <h2>: o título da secção, os <h3> lá dentro, e os
    termos em <code>, <strong> e <th>. Não se indexa a prosa toda — isso daria
    centenas de kB inline e a página tem de continuar a abrir do disco (D-003).
    """
    import validar  # o parser já existe ali; duplicá-lo era garantir que divergiam

    saida = []
    for caminho in sorted((RAIZ / "docs").rglob("*.html")):
        rp = caminho.relative_to(RAIZ / "docs").as_posix()
        if rp == "index.html":
            continue
        raiz = validar.analisar(caminho)
        titulo = next((n.texto_todo().strip() for n in raiz.descendentes() if n.tag == "title"), rp)
        titulo = titulo.split(" — ")[0].strip()

        # Duas gavetas por secção: o que está DESTACADO (h3, code, strong, th) e o
        # que é prosa. Sem esta separação, procurar "bitmap" devolve a lição toda
        # por ordem alfabética — encontra tudo e não serve para nada.
        seccoes, actual = [], None
        DESTAQUE = ("h3", "h4", "code", "strong", "th", "dfn", "summary")
        for no in raiz.descendentes():
            if no.tag == "h2" and no.attrs.get("id"):
                actual = {"id": no.attrs["id"], "h": " ".join(no.texto_todo().split()),
                          "destaque": set(), "prosa": set()}
                seccoes.append(actual)
            elif actual is not None and no.tag not in ("script", "style", "nav"):
                # Só o texto PRÓPRIO do nó: os filhos são visitados por si, e sem
                # isto o texto de cada parágrafo entrava uma vez por antepassado.
                proprio = PALAVRA.findall("".join(no.texto))
                destacado = no.tag in DESTAQUE or no.dentro_de(*DESTAQUE)
                for palavra in proprio:
                    palavra = palavra.lower()
                    if len(palavra) >= 3 and palavra not in VAZIAS:
                        actual["destaque" if destacado else "prosa"].add(palavra)

        for s in seccoes:
            s["prosa"] -= s["destaque"]          # nada entra duas vezes

        saida.append({
            "p": rp,
            "t": titulo,
            "s": [{"id": s["id"], "h": s["h"],
                   "d": " ".join(sorted(s["destaque"])),
                   "k": " ".join(sorted(s["prosa"]))}
                  for s in seccoes if s["h"]],
        })
    return saida


def escrever_indice_pesquisa(verificar):
    alvo = RAIZ / "docs" / "index.html"
    if not alvo.exists():
        return False
    texto = alvo.read_text(encoding="utf-8")
    a, b = texto.find(INI_BUSCA), texto.find(FIM_BUSCA)
    if a == -1 or b == -1:
        print(f"AVISO docs/index.html sem os marcadores {INI_BUSCA} — pesquisa não gerada")
        return False
    corpo = "\nwindow.INDICE_PESQUISA = " + json.dumps(
        indice_de_pesquisa(), ensure_ascii=False, separators=(",", ":")) + ";\n"
    novo = texto[: a + len(INI_BUSCA)] + corpo + texto[b:]
    if novo == texto:
        return False
    if not verificar:
        alvo.write_text(novo, encoding="utf-8")
    return True


def paginas():
    for base in ("docs", "modelo"):
        yield from sorted((RAIZ / base).rglob("*.html"))


def main() -> int:
    verificar = "--verificar" in sys.argv
    fontes = [(RAIZ / f).read_text(encoding="utf-8").strip() for f, _, _ in PARES]

    mudadas, dessincronizadas = [], []
    for pagina in paginas():
        texto = original = pagina.read_text(encoding="utf-8")
        for (caminho, ini, fim), corpo in zip(PARES, fontes):
            a = texto.find(ini)
            b = texto.find(fim)
            if a == -1 or b == -1:
                continue
            if b < a:
                print(f"ERRO {pagina.relative_to(RAIZ)}: marcador «{fim}» antes de «{ini}»")
                return 2
            texto = texto[: a + len(ini)] + "\n" + corpo + "\n" + texto[b:]
        if texto != original:
            (dessincronizadas if verificar else mudadas).append(pagina)
            if not verificar:
                pagina.write_text(texto, encoding="utf-8")

    if escrever_indice_pesquisa(verificar):
        (dessincronizadas if verificar else mudadas).append(RAIZ / "docs" / "index.html.indice-pesquisa")

    if verificar:
        for p in dessincronizadas:
            print(f"dessincronizado: {p.relative_to(RAIZ)}")
        if dessincronizadas:
            print(f"\n{len(dessincronizadas)} página(s) fora de sincronia. Corre: python3 sincronizar.py")
            return 1
        print("todas as páginas em sincronia com modelo/base.css e modelo/base.js")
        return 0

    for p in mudadas:
        print(f"actualizada: {p.relative_to(RAIZ)}")
    print(f"{len(mudadas)} página(s) actualizada(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
