#!/usr/bin/env python3
"""ensaio.py — uma «captura» de fita de ZX Spectrum para ensaiar a lição 5 sem máquina.

⚠️ NÃO é uma fita real. Cada defeito abaixo foi escolhido por mim para se
parecer com o que a lição 3 e a lição 4 descrevem, e os valores são
inventados para o ensaio. O que medires aqui mede o ensaio, não a cassete.

Uso:  python ensaio.py [ensaio.wav]      ->  ensaio.wav (48 kHz, 24 bits, estéreo) e ensaio.tap
"""
import sys

import numpy as np

import captura as C
import fita as F

ALTA = 192_000                     # taxa interna: 4× a da captura, para as arestas não saltarem

DEFEITOS = dict(
    erro_velocidade=+0.015,        # o gravador de 1985 e o deck de hoje, somados
    wow=[(0.0020, 0.55), (0.0006, 11.0)],   # (amplitude de pico, Hz)
    azimute_minutos=12.0,          # a cabeça de hoje contra a do gravador
    corte_agudos_hz=7000.0,        # perdas de fenda, afastamento e espessura, em bruto
    corte_graves_hz=40.0,          # a cabeça não grava corrente contínua
    snr_db=32.0,                   # chiado em relação ao piloto
    zumbido_dbfs=-58.0,            # 50 Hz da corrente, e harmónicas
    buraco=None,                   # ou (segundo, duração, amplitude que sobra): um dropout (lição 5, E4)
    semente=7,
)


def arestas_no_tempo(blocos, d):
    """Instantes (s) de cada mudança de nível, já com a velocidade a variar."""
    tempos, t = [], 0.4
    for b in blocos:
        for T in F.pulsos(b):
            v = 1 + d["erro_velocidade"] + sum(a * np.sin(2 * np.pi * hz * t) for a, hz in d["wow"])
            t += T / F.RELOGIO / v
            tempos.append(t)
        t += 0.8                                   # silêncio entre blocos
    return np.array(tempos), t + 0.4


def muro(x, taxa, fc):
    """Corte abrupto: é o filtro anti-aliasing que qualquer interface tem antes do conversor."""
    X = np.fft.rfft(x)
    X[np.fft.rfftfreq(len(x), 1 / taxa) > fc] = 0
    return np.fft.irfft(X, len(x))


def passa(x, taxa, fc, tipo):
    """Um polo, no domínio da frequência (sem desfasar é mais simples de ler;
    a fita a sério desfasa, e o descodificador não se importa)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / taxa)
    H = 1 / np.sqrt(1 + (f / fc) ** 2) if tipo == "baixo" else (f / fc) / np.sqrt(1 + (f / fc) ** 2)
    return np.fft.irfft(X * H, len(x))


def gerar(caminho="ensaio.wav", d=DEFEITOS):
    rng = np.random.default_rng(d["semente"])
    corpo = bytes((i * 37 + 11) % 256 for i in range(256))
    blocos = [F.cabecalho(3, "ENSAIO", len(corpo), 32768, 32768), F.bloco(0xFF, corpo)]
    with open(caminho.replace(".wav", ".tap"), "wb") as f:
        f.write(F.tap(blocos))

    tempos, dur = arestas_no_tempo(blocos, d)
    n = int(dur * ALTA)
    degraus = np.zeros(n)
    idx = np.searchsorted(np.arange(n) / ALTA, tempos)
    np.add.at(degraus, idx[idx < n], 1)
    nivel = np.cumsum(degraus) % 2                    # 0/1 que troca em cada aresta
    x = np.where(nivel > 0, -1.0, 1.0)
    # A aresta cai entre duas amostras. Sem isto ficava arrumada na grelha de
    # 192 kHz, e esse arredondamento (até 0,4 % de uma meia onda do piloto)
    # aparecia na lição 4 como flutter que ninguém tinha gravado.
    pos = tempos * ALTA
    k = np.ceil(pos).astype(int)
    k = k[k < n]
    fr = (k - pos[: len(k)])                          # parte do intervalo já com o nível novo
    x[k] = x[k] * fr + (-x[k]) * (1 - fr)
    antes = int(tempos[0] * ALTA) - int(0.02 * ALTA)  # silêncio antes do primeiro piloto
    x[:antes] = 0.0
    fim = int(tempos[-1] * ALTA) + 50
    x[fim:] = 0.0
    for a, b in zip(tempos[:-1], tempos[1:]):         # silêncios entre blocos
        if b - a > 0.3:
            x[int(a * ALTA) + 50:int(b * ALTA) - int(0.02 * ALTA)] = 0.0

    x = passa(passa(x, ALTA, d["corte_agudos_hz"], "baixo"), ALTA, d["corte_graves_hz"], "alto")
    esq, dir_ = C.simular_azimute(x, ALTA, d["azimute_minutos"])

    g = np.ones(n)
    if d["buraco"]:
        s0, dt, resto = d["buraco"]
        g[int(s0 * ALTA):int((s0 + dt) * ALTA)] = resto
    ref = np.sqrt(np.mean(x[int(tempos[0] * ALTA):int(tempos[8000] * ALTA)] ** 2))
    sigma = ref / 10 ** (d["snr_db"] / 20)
    t = np.arange(n) / ALTA
    zumbido = sum(10 ** (d["zumbido_dbfs"] / 20) / k * np.sin(2 * np.pi * 50 * k * t) for k in (1, 2, 3))
    canais = []
    for c in (esq, dir_):
        canais.append(c * g + rng.normal(0, sigma, n))
    y = np.stack(canais, 1)
    y = np.stack([muro(c, ALTA, 20_000) for c in y.T], 1)[::4]   # 192 -> 48 kHz sem dobrar agudos
    y = y / np.max(np.abs(y)) * 10 ** (-6 / 20)       # picos a -6 dBFS
    y += zumbido[::4, None] + 0.002                   # zumbido e um desvio de zero da interface
    C.escrever_wav(caminho, y, 48_000, 24)
    return blocos


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "ensaio.wav"
    b = gerar(nome)
    print(f"{nome}: 48000 Hz, 24 bits, estéreo — blocos de {[len(x) for x in b]} bytes")
