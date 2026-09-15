#!/usr/bin/env python3
"""Procura números do resumo que não aparecem no texto completo.

Lição 6 de docs/abstracts-e-resumos/. Automatiza METADE da definição de
«abstract deficiente» de Pitkin, Branagan & Burmeister (JAMA 1999;281(12):1110-1111):
dados do abstract que são inconsistentes com o corpo do artigo OU que não se
encontram no corpo de todo. Este script só vê a segunda metade — e é por isso
que existe: para veres, a correr, o que uma verificação mecânica não apanha.

  - Falso negativo: o número existe no corpo mas refere-se a outra coisa
    («30%» do CPU no corpo, «30%» de erros no resumo) — passa sem aviso.
  - Falso positivo: o resumo faz uma conta honesta a partir do corpo
    («23 vezes mais rápido» a partir de 4,2 s e 180 ms) — é acusado.

Uso:
    python3 conferir_numeros.py resumo.txt corpo.txt
    python3 conferir_numeros.py --teste
"""
import re
import sys

NUMERO = re.compile(r"(?<![\w,.])\d+(?:[.,]\d+)?")


def numeros(texto):
    # 4,2 e 4.2 são o mesmo número; «9h» dá 9; «p95» não conta (colado a letras).
    return [m.group().replace(",", ".") for m in NUMERO.finditer(texto)]


def sem_correspondencia(resumo, corpo):
    no_corpo = set(numeros(corpo))
    vistos, falta = set(), []
    for n in numeros(resumo):
        if n not in no_corpo and n not in vistos:
            falta.append(n)
        vistos.add(n)
    return falta


def teste():
    corpo = "O CPU andava pelos 30%. O p95 desceu de 4,2 s para 180 ms."
    assert sem_correspondencia("A latência desceu de 4.2 s para 180 ms.", corpo) == []
    assert sem_correspondencia("Ficou 23 vezes mais rápido.", corpo) == ["23"]   # falso positivo
    assert sem_correspondencia("30% dos pedidos falharam.", corpo) == []          # falso negativo
    print("ok: vírgula e ponto decimais equivalem; o falso positivo e o falso negativo comportam-se como descrito")


def main():
    if "--teste" in sys.argv:
        teste()
        return
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    resumo = open(sys.argv[1], encoding="utf-8").read()
    corpo = open(sys.argv[2], encoding="utf-8").read()
    falta = sem_correspondencia(resumo, corpo)
    if not falta:
        print("todos os números do resumo aparecem no corpo — o que NÃO quer dizer que estejam certos")
        return
    for n in falta:
        print(f"no resumo mas não no corpo: {n}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
