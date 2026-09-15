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
import sys
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
PARES = [
    ("modelo/base.css", "/* INICIO ESTILO */", "/* FIM ESTILO */"),
    ("modelo/base.js", "/* INICIO COMPORTAMENTO */", "/* FIM COMPORTAMENTO */"),
]


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
