#!/usr/bin/env python3
"""margens.py — da captura real ao critério de sucesso (lição 5).

    python margens.py ler     captura.wav [canal]    # descodifica e prova
    python margens.py piloto  captura.wav            # velocidade e wow da cadeia inteira
    python margens.py margens captura.wav [segundos] # quanto estrago esta captura aguenta
    python margens.py comparar a.tap b.tap           # duas capturas, os mesmos bytes?

Usa o ler_fita.py do cassete-dados (lição 6) sem lhe mexer: só lhe dá as
amostras já em números, por isso as capturas de 24 bits também servem.
"""
import struct
import sys

import numpy as np

import captura as C
import ler_fita as L

PILOTO_HZ = 3_500_000 / (2 * 2168)          # 807,2 Hz: um período são DUAS meias ondas


def canal(x, qual):
    if qual == "soma":
        return x[:, 0] + x[:, 1] if x.shape[1] > 1 else x[:, 0]
    return x[:, int(qual)]


def ler(s, taxa):
    """As amostras -> os blocos. O descodificador é o da lição 6, tal e qual."""
    return L.descodificar(L.comprimentos(L.arestas(L.centrar(list(s), taxa), taxa)), taxa)


def provas(blocos):
    """O que substitui «igual ao original» quando não há original.
    Devolve uma lista de (prova, passou?, detalhe)."""
    r = []
    for n, b in enumerate(blocos):
        r.append((f"bloco {n}: paridade", L.paridade_ok(b), f"{len(b)} bytes, bandeira {b[0]:#04x}"))
    for n, (a, b) in enumerate(zip(blocos, blocos[1:])):
        if a[0] == 0x00 and len(a) == 19:
            comp = struct.unpack_from("<H", a, 12)[0]      # bandeira, tipo, 10 do nome -> 12
            r.append((f"cabeçalho {n} anuncia {comp} bytes", len(b) == comp + 2 and b[0] == 0xFF,
                      f"o bloco seguinte tem {len(b)} (= {comp} + bandeira + paridade?)"))
    return r


def tap(blocos):
    return b"".join(struct.pack("<H", len(b)) + b for b in blocos)


def trecho_piloto(s, taxa, segundos=4.0):
    """O primeiro tom-piloto: a primeira janela longa em que o espetro tem o pico
    perto de 807 Hz. Devolve o índice de início."""
    passo = taxa // 4
    for i in range(0, len(s) - int(segundos * taxa), passo):
        f, m = C.espetro(s[i:i + passo], taxa)
        fp, _ = C.pico(f, m, 400, 1600)
        if abs(fp / PILOTO_HZ - 1) < 0.2 and np.std(s[i:i + passo]) > 0.1 * np.max(np.abs(s)):
            return i + passo                       # salta o arranque
    raise SystemExit("não encontrei um tom-piloto de 4 s")


def medir_piloto(s, taxa):
    i = trecho_piloto(s, taxa)
    return C.medir_wow(s[i:i + int(4.0 * taxa)], taxa, PILOTO_HZ)


def reamostrar(s, taxa, nova):
    """Muda a taxa pela FFT (ideal para um sinal periódico; aqui chega)."""
    n = int(round(len(s) * nova / taxa))
    return np.fft.irfft(np.fft.rfft(s)[: n // 2 + 1] * (n / len(s)), n) if nova < taxa else \
        np.fft.irfft(np.concatenate([np.fft.rfft(s), np.zeros(n // 2 + 1 - (len(s) // 2 + 1))]) * (n / len(s)), n)


def um_polo(s, taxa, fc):
    """O mesmo passa-baixo de 1 polo do estragar() do cassete-dados."""
    a = 1 - np.exp(-2 * np.pi * fc / taxa)
    y, ant = np.empty_like(s), 0.0
    for i, v in enumerate(s):
        ant += a * (v - ant)
        y[i] = ant
    return y


def com_wow(s, taxa, wow, hz=3.0):
    """Lê a captura com a velocidade a oscilar, como o onda() do cassete-dados:
    a posição na fita avança v(t) amostras por amostra."""
    t = np.arange(len(s)) / taxa
    pos = np.cumsum(1 + wow * np.sin(2 * np.pi * hz * t))
    pos = pos[pos < len(s) - 1]
    return np.interp(pos, np.arange(len(s)), s)


def margens(s, taxa, certo):
    """Estraga a captura aos poucos, um ataque de cada vez, e diz onde deixa de dar `certo`.
    Os ataques são os quatro da lição 6 do cassete-dados, para as tabelas se compararem."""
    ok = lambda y, t=taxa: tap(ler(y, t)) == certo
    ruido_da_captura = np.std(s[: int(0.3 * taxa)])            # o silêncio do princípio
    i = trecho_piloto(s, taxa)
    sinal = np.std(s[i:i + taxa])
    print(f"  SNR desta captura: {C.db(sinal / ruido_da_captura):.1f} dB "
          f"(piloto contra o silêncio inicial)")

    print("  1. taxa de amostragem")
    for t in (22050, 11025, 8000, 6500, 6000, 5000):
        print(f"     {t:6d} Hz = {855 / 3.5e6 * t:4.2f} amostras/meia onda -> "
              f"{'ok' if ok(reamostrar(s, taxa, t), t) else 'FALHA'}")

    print("  2. ruído somado (4 sementes)")
    for snr in (20, 16, 12, 8, 6, 4):
        sigma = sinal / 10 ** (snr / 20)
        n = sum(ok(s + np.random.default_rng(k).normal(0, sigma, len(s))) for k in range(4))
        print(f"     SNR {snr:2d} dB acrescentado -> {n}/4")

    print("  3. corte de agudos (1 polo)")
    for fc in (2000, 1000, 800, 700, 600, 500, 400):
        print(f"     {fc:5d} Hz -> {'ok' if ok(um_polo(s, taxa, fc)) else 'FALHA'}")

    print("  4. erro de velocidade constante (a captura inteira mais depressa ou mais devagar)")
    for v in (0.70, 0.75, 0.80, 0.90, 1.10, 1.20, 1.25, 1.30):
        y = reamostrar(s, taxa, int(round(taxa / v)))      # menos amostras = fita mais depressa
        print(f"     x{v:.2f} -> {'ok' if ok(y) else 'FALHA'}")

    print("  5. wow a 3 Hz (o ataque 4 do simulador)")
    for w in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        print(f"     {w:4.0%} -> {'ok' if ok(com_wow(s, taxa, w)) else 'FALHA'}")


def principal(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    acao = argv[1]
    if acao == "comparar":
        a, b = (open(p, "rb").read() for p in argv[2:4])
        print("IGUAIS" if a == b else f"DIFERENTES ({len(a)} e {len(b)} bytes)")
        return 0 if a == b else 1
    taxa, x = C.ler_wav(argv[2])
    if acao == "ler":
        s = canal(x, argv[3] if len(argv) > 3 else "soma")
        blocos = ler(s, taxa)
        for nome, passou, det in provas(blocos):
            print(f"  {'ok   ' if passou else 'FALHA'}  {nome}  ({det})")
        saida = argv[2].replace(".wav", "-lido.tap")
        open(saida, "wb").write(tap(blocos))
        print(f"escrito {saida}")
    elif acao == "piloto":
        for c in range(x.shape[1]):
            r = medir_piloto(x[:, c], taxa)
            print(f"  canal {c}: " + "  ".join(f"{k}={v:.4f}" for k, v in r.items()))
    elif acao == "margens":
        seg = float(argv[3]) if len(argv) > 3 else None
        s = canal(x, "soma")
        if seg:
            s = s[: int(seg * taxa)]
        certo = tap(ler(s, taxa))
        if not certo or not all(p for _, p, _ in provas(ler(s, taxa))):
            raise SystemExit("esta captura não passa as provas: não há margens a medir")
        margens(s, taxa, certo)
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv))
