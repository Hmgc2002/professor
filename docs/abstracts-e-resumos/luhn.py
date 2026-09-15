#!/usr/bin/env python3
"""Resumo extrativo à maneira de Luhn (1958), só com a biblioteca-padrão.

Lição 0 de docs/abstracts-e-resumos/. Existe para veres o que um resumo
consegue fazer SEM perceber o texto: escolher frases, nunca escrever frases.

O que vem do artigo (H. P. Luhn, «The Automatic Creation of Literature
Abstracts», IBM Journal of Research and Development 2(2):159-165, 1958):
  - uma palavra é «significativa» por se repetir, depois de tirar as palavras
    comuns;
  - variantes da mesma palavra contam como a mesma palavra;
  - numa frase, palavras significativas separadas por no máximo «four or five»
    palavras não significativas formam um grupo (cluster);
  - o fator de significância de um grupo é (significativas no grupo)² a dividir
    pelo total de palavras do grupo — no exemplo da Fig. 2: 4² / 7 = 2,3;
  - a frase vale o melhor dos seus grupos.

O que é simplificação minha, e não do artigo:
  - «repete-se» = aparece 2 ou mais vezes (Luhn fala de cortes de frequência
    alta e baixa, a afinar com experiência; aqui não há corte alto além da lista
    de palavras comuns);
  - «variantes da mesma palavra» = mesmos 6 primeiros caracteres;
  - a lista de palavras comuns é curta e escrita à mão.

Uso:
    python3 luhn.py texto.txt [número de frases]
    python3 luhn.py --teste
"""
import collections
import re
import sys

INTERVALO_MAXIMO = 4  # palavras não significativas entre duas significativas

COMUNS = set("""
a à ao aos as às o os um uma uns umas de do da dos das em no na nos nas num numa por pelo pela pelos pelas
para com sem sob sobre entre até e ou mas que se como quando onde porque pois já não sim também só
é são era eram foi foram ser estar está estava estavam tem têm tinha tinham ter há havia
seu sua seus suas este esta estes estas esse essa isso isto aquele aquela ele ela eles elas
mais menos muito muita muitos muitas todo toda todos todas cada outro outra outros outras
the of and to in is was for on that with as by at from it be are were this which or an not
""".split())


def frases(texto):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f.strip()]


def palavras(frase):
    return re.findall(r"[0-9A-Za-zÀ-ÿ]+(?:,[0-9]+)?", frase.lower())


def raiz(palavra):
    return palavra[:6]


def significativas(texto, minimo=2):
    contagem = collections.Counter(
        raiz(p) for p in palavras(texto) if p not in COMUNS and len(p) > 2 and not p[0].isdigit()
    )
    return {r for r, n in contagem.items() if n >= minimo}


def fator(frase, sig):
    """Melhor fator de significância entre os grupos da frase (0 se não há grupo)."""
    ps = palavras(frase)
    posicoes = [i for i, p in enumerate(ps) if p not in COMUNS and raiz(p) in sig]
    if not posicoes:
        return 0.0
    grupos, actual = [], [posicoes[0]]
    for i in posicoes[1:]:
        if i - actual[-1] - 1 <= INTERVALO_MAXIMO:
            actual.append(i)
        else:
            grupos.append(actual)
            actual = [i]
    grupos.append(actual)
    return max(len(g) ** 2 / (g[-1] - g[0] + 1) for g in grupos)


def resumir(texto, n=2):
    fs = frases(texto)
    sig = significativas(texto)
    pontuadas = [(fator(f, sig), i, f) for i, f in enumerate(fs)]
    escolhidas = sorted(sorted(pontuadas, reverse=True)[:n], key=lambda t: t[1])
    return sig, pontuadas, escolhidas


def teste():
    # Fig. 2 do artigo: 4 significativas num grupo de 7 palavras -> 16/7 = 2,29.
    # S = significativa, x = não significativa; o grupo vai do 1.º ao último S.
    frase = "x x S x S S x x S x x x x x x x x"
    sig = {"s"}
    obtido = fator(frase.replace("x", "zz"), sig)
    esperado = 4 ** 2 / 7
    assert abs(obtido - esperado) < 1e-9, (obtido, esperado)
    # Um S a mais de 4 palavras de distância abre outro grupo, não alarga este.
    longe = "S x x x x x S"
    assert fator(longe.replace("x", "zz"), sig) == 1.0
    print(f"ok: Fig. 2 dá {obtido:.2f}; um S a 5 palavras de distância não entra no grupo")


def main():
    if "--teste" in sys.argv:
        teste()
        return
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    texto = open(sys.argv[1], encoding="utf-8").read()
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    sig, pontuadas, escolhidas = resumir(texto, n)
    print("palavras significativas:", " ".join(sorted(sig)))
    print()
    for f_, i, frase in pontuadas:
        print(f"{f_:5.2f}  [{i + 1:2d}] {frase}")
    print()
    print(f"auto-abstract ({n} frases, pela ordem do texto):")
    for f_, i, frase in escolhidas:
        print(f"  {frase}")


if __name__ == "__main__":
    main()
