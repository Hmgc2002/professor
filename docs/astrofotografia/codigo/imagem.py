#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imagem.py — ler e escrever ficheiros de imagem, de raiz.

Três formatos, e nenhuma dependência para além do `numpy` e da biblioteca padrão:

* **PGM P5 de 16 bits** — o que sai de um conversor de RAW (`dcraw -D -4 -j -t 0`).
  Cabeçalho em texto, dados em *big-endian*. Vinte linhas de código.
* **FITS** — o formato em que a astronomia guarda imagens desde 1981. Blocos de
  2880 bytes, cartões de 80 caracteres, também *big-endian*.
* **PNG de 8 bits** — só para *olhar*. Escrito com `zlib`, que está na biblioteca padrão.

🔴 Porque é que isto não usa uma biblioteca: um formato de ficheiro que é caixa preta
transforma «o meu píxel vale 4096» numa pergunta sem resposta. Depois de leres o
cabeçalho à mão uma vez, sabes o que é um nível de zero, o que é *big-endian* e porque
é que a tua imagem apareceu com as cores trocadas.
"""

import struct
import sys
import zlib

import numpy as np

# O registo de falhas do PROCESSO.md tem duas linhas sobre isto: um script que só
# rebenta no caminho do sucesso (ao imprimir «✓» numa consola cp1252) é
# indistinguível de um script partido. Força-se UTF-8 à saída, sempre.
for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ----------------------------------------------------------------- PGM (P5)

def ler_pgm(caminho):
    """Devolve (array 2-D de inteiros, maximo). Aceita 8 e 16 bits.

    O cabeçalho do P5 é: «P5», largura, altura, valor máximo — separados por
    espaço em branco, com comentários «# …» pelo meio. A seguir, os dados em
    binário, *big-endian* se o máximo for maior do que 255.
    """
    with open(caminho, "rb") as f:
        dados = f.read()

    campos, i = [], 2                      # salta o «P5»
    if dados[:2] != b"P5":
        raise ValueError("%s não começa por P5 (não é um PGM binário)" % caminho)
    while len(campos) < 3:
        while i < len(dados) and dados[i:i + 1].isspace():
            i += 1
        if dados[i:i + 1] == b"#":         # comentário até ao fim da linha
            while i < len(dados) and dados[i:i + 1] not in (b"\n", b"\r"):
                i += 1
            continue
        j = i
        while j < len(dados) and not dados[j:j + 1].isspace():
            j += 1
        campos.append(int(dados[i:j]))
        i = j
    i += 1                                  # um (e só um) separador antes dos dados

    larg, alt, maximo = campos
    tipo = ">u2" if maximo > 255 else "u1"
    pix = np.frombuffer(dados, dtype=tipo, count=larg * alt, offset=i)
    return pix.reshape(alt, larg).astype(np.float64), maximo


def escrever_pgm(caminho, imagem, maximo=65535):
    """Escreve um P5. Os valores são cortados a [0, maximo] e arredondados."""
    a = np.clip(np.rint(imagem), 0, maximo).astype(">u2" if maximo > 255 else "u1")
    alt, larg = a.shape
    with open(caminho, "wb") as f:
        f.write(b"P5\n%d %d\n%d\n" % (larg, alt, maximo))
        f.write(a.tobytes())


# ----------------------------------------------------------------- FITS

def _cartao(chave, valor, comentario=""):
    """Um cartão FITS: 80 caracteres ASCII, sem fim de linha. Nunca 79 nem 81."""
    if isinstance(valor, bool):
        v = "T" if valor else "F"
    elif isinstance(valor, str):
        v = "'%-8s'" % valor
    else:
        v = str(valor)
    corpo = "%-8s= %20s" % (chave.upper(), v)
    if comentario:
        corpo = "%s / %s" % (corpo, comentario)
    return ("%-80s" % corpo)[:80]


def escrever_fits(caminho, imagem, extra=()):
    """Escreve um FITS de 16 bits com a convenção BZERO=32768 dos inteiros sem sinal.

    O FITS só conhece inteiros **com** sinal. Um sensor dá valores de 0 a 65535.
    A norma resolve isto com uma transformação afim declarada no cabeçalho:
    o disco guarda `valor - 32768`, e quem lê aplica `BSCALE·disco + BZERO`.
    """
    a = np.clip(np.rint(imagem), 0, 65535).astype(np.int32) - 32768
    alt, larg = a.shape
    cartoes = [_cartao("SIMPLE", True, "norma FITS 4.0"),
               _cartao("BITPIX", 16, "16 bits com sinal"),
               _cartao("NAXIS", 2),
               _cartao("NAXIS1", larg),
               _cartao("NAXIS2", alt),
               _cartao("BZERO", 32768, "desloca para inteiros sem sinal"),
               _cartao("BSCALE", 1)]
    cartoes += [_cartao(k, v, c) for k, v, c in extra]
    cartoes.append("%-80s" % "END")

    cab = "".join(cartoes)
    cab += " " * ((2880 - len(cab) % 2880) % 2880)
    corpo = a.astype(">i2").tobytes()
    corpo += b"\0" * ((2880 - len(corpo) % 2880) % 2880)
    with open(caminho, "wb") as f:
        f.write(cab.encode("ascii"))
        f.write(corpo)


def ler_fits(caminho):
    """Devolve (array 2-D, dicionário do cabeçalho). Só o essencial: uma imagem, sem extensões."""
    with open(caminho, "rb") as f:
        bruto = f.read()

    cab, i = {}, 0
    while True:
        cartao = bruto[i:i + 80].decode("ascii")
        i += 80
        chave = cartao[:8].strip()
        if chave == "END":
            break
        if cartao[8:10] == "= ":
            v = cartao[10:].split("/")[0].strip()
            if v in ("T", "F"):
                cab[chave] = (v == "T")
            elif v.startswith("'"):
                cab[chave] = v.strip("'").strip()
            else:
                cab[chave] = float(v) if ("." in v or "E" in v.upper()) else int(v)
    i = ((i + 2879) // 2880) * 2880          # os dados começam no bloco seguinte

    n = cab["NAXIS1"] * cab["NAXIS2"]
    tipos = {8: "u1", 16: ">i2", 32: ">i4", -32: ">f4", -64: ">f8"}
    a = np.frombuffer(bruto, dtype=tipos[cab["BITPIX"]], count=n, offset=i)
    a = a.reshape(cab["NAXIS2"], cab["NAXIS1"]).astype(np.float64)
    return a * cab.get("BSCALE", 1) + cab.get("BZERO", 0), cab


# ----------------------------------------------------------------- PNG (só para ver)

def escrever_png(caminho, imagem8):
    """PNG de 8 bits em tons de cinzento, escrito com `zlib`.

    Um PNG é uma assinatura seguida de blocos (comprimento, tipo, dados, CRC32).
    Cada linha dos dados leva à frente um byte de filtro — aqui, sempre 0.
    """
    a = np.clip(np.rint(imagem8), 0, 255).astype(np.uint8)
    alt, larg = a.shape
    cru = b"".join(b"\0" + a[y].tobytes() for y in range(alt))

    def bloco(tipo, dados):
        return (struct.pack(">I", len(dados)) + tipo + dados
                + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF))

    cabecalho = struct.pack(">IIBBBBB", larg, alt, 8, 0, 0, 0, 0)
    with open(caminho, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(bloco(b"IHDR", cabecalho))
        f.write(bloco(b"IDAT", zlib.compress(cru, 9)))
        f.write(bloco(b"IEND", b""))


if __name__ == "__main__":
    # Ida e volta pelos três formatos, com dados que têm extremos e um gradiente.
    # Valores inteiros de propósito: uma ida e volta só é «igual» se não houver
    # arredondamento pelo meio, e um teste que confunde as duas coisas não testa nada.
    teste = np.zeros((7, 11))
    teste[0, 0], teste[6, 10] = 0, 65535
    teste[3, :] = np.rint(np.linspace(0, 65535, 11))
    escrever_pgm("_t.pgm", teste)
    escrever_fits("_t.fits", teste, extra=[("EXPTIME", 30, "segundos")])
    p, mx = ler_pgm("_t.pgm")
    fi, cab = ler_fits("_t.fits")
    print("PGM  máximo declarado:", mx, "· igual ao original:", np.allclose(p, teste))
    print("FITS EXPTIME:", cab["EXPTIME"], "· igual ao original:", np.allclose(fi, teste))
    print("FITS tamanho em bytes:", len(open("_t.fits", "rb").read()),
          "(tem de ser múltiplo de 2880)")
    escrever_png("_t.png", teste / 65535 * 255)
    print("PNG escrito:", len(open("_t.png", "rb").read()), "bytes")
