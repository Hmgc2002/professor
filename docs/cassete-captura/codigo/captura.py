#!/usr/bin/env python3
"""captura.py — as medições do curso «Digitalizar cassetes a sério».

Uma dependência: NumPy (pip install numpy). Tudo o resto é biblioteca padrão.

Cada função mede UMA coisa e diz em que unidades. As lições constroem-nas
uma a uma; este ficheiro é o resultado final, para correres sobre as tuas
capturas:

    python captura.py relatorio  minha-fita.wav        # lição 2
    python captura.py azimute    minha-fita.wav        # lição 3
    python captura.py wow        tom-3150.wav [3150]   # lição 4
"""
import struct
import sys

import numpy as np

V_CASSETE = 0.047625        # m/s — 1 7/8 polegadas por segundo
LARGURA_MONO = 1.5e-3       # m — pista mono
LARGURA_CANAL = 0.6e-3      # m — cada canal de uma pista estéreo
ENTRE_CANAIS = 0.9e-3       # m — de centro a centro: 0,6 + 0,3 de separação


# ================================================================ ficheiros
def ler_wav(caminho):
    """Devolve (taxa, x) com x em float64 entre -1 e 1, forma (amostras, canais).

    Lê PCM de 16, 24 e 32 bits e float de 32 bits, incluindo o cabeçalho
    WAVE_FORMAT_EXTENSIBLE que muitos programas escrevem para 24 bits.
    """
    with open(caminho, "rb") as f:
        dados = f.read()
    if dados[:4] != b"RIFF" or dados[8:12] != b"WAVE":
        raise ValueError(f"{caminho}: não é um WAV")
    i, fmt, bruto = 12, None, None
    while i + 8 <= len(dados):
        nome, tam = dados[i:i + 4], struct.unpack_from("<I", dados, i + 4)[0]
        corpo = dados[i + 8:i + 8 + tam]
        if nome == b"fmt ":
            fmt = corpo
        elif nome == b"data":
            bruto = corpo
        i += 8 + tam + (tam & 1)            # os pedaços têm tamanho par
    etiqueta, canais, taxa = struct.unpack_from("<HHI", fmt, 0)
    bits = struct.unpack_from("<H", fmt, 14)[0]
    if etiqueta == 0xFFFE:                  # EXTENSIBLE: o formato real vem mais à frente
        etiqueta = struct.unpack_from("<H", fmt, 24)[0]
    largura = bits // 8
    bruto = bruto[:len(bruto) // (largura * canais) * largura * canais]
    if etiqueta == 3 and bits == 32:
        x = np.frombuffer(bruto, "<f4").astype(np.float64)
    elif etiqueta == 1 and bits == 16:
        x = np.frombuffer(bruto, "<i2") / 32768.0
    elif etiqueta == 1 and bits == 24:
        b = np.frombuffer(bruto, np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        v = np.where(v >= 1 << 23, v - (1 << 24), v)       # sinal em complemento para 2
        x = v / float(1 << 23)
    elif etiqueta == 1 and bits == 32:
        x = np.frombuffer(bruto, "<i4") / float(1 << 31)
    else:
        raise ValueError(f"{caminho}: formato {etiqueta} com {bits} bits não suportado")
    return taxa, x.reshape(-1, canais)


def escrever_wav(caminho, x, taxa, bits=24):
    """Escreve PCM inteiro. x em [-1, 1], forma (amostras,) ou (amostras, canais).
    O que passar de ±1 é cortado — e isso é clipping, que a lição 2 ensina a detetar."""
    x = np.atleast_2d(np.asarray(x, dtype=np.float64).T).T
    canais = x.shape[1]
    escala = float(1 << (bits - 1))
    v = np.clip(np.round(x * escala), -escala, escala - 1).astype(np.int64).ravel()
    if bits == 16:
        corpo = v.astype("<i2").tobytes()
    elif bits == 24:
        u = (v & 0xFFFFFF).astype(np.uint32)
        corpo = np.stack([u & 255, (u >> 8) & 255, (u >> 16) & 255], 1).astype(np.uint8).tobytes()
    else:
        raise ValueError("só escrevo 16 ou 24 bits")
    largura = bits // 8
    fmt = struct.pack("<HHIIHH", 1, canais, taxa, taxa * canais * largura, canais * largura, bits)
    with open(caminho, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 4 + 8 + len(fmt) + 8 + len(corpo)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<I", len(fmt)) + fmt)
        f.write(b"data" + struct.pack("<I", len(corpo)) + corpo)
        if len(corpo) & 1:
            f.write(b"\0")


# ================================================================ lição 0: espetro
def db(v):
    return 20 * np.log10(np.maximum(np.abs(v), 1e-12))


def espetro(x, taxa, n=None):
    """Amplitude de cada frequência, em dB relativos a um seno de amplitude 1.

    Janela de Hann: sem ela, um tom que não cabe um número inteiro de vezes na
    janela espalha-se por todo o espetro (fuga). A correção de 2/soma(janela)
    faz com que um seno de amplitude A apareça com altura A no seu bin."""
    x = np.asarray(x, dtype=np.float64)[:n]
    janela = np.hanning(len(x))
    X = np.fft.rfft(x * janela)
    f = np.fft.rfftfreq(len(x), 1 / taxa)
    return f, db(X * 2 / janela.sum())


def pico(f, mag_db, fmin=0.0, fmax=None):
    """Frequência e altura do pico, com interpolação parabólica entre bins.
    Sem interpolação, a resolução é taxa/N — 11,7 Hz com 4096 amostras a 48 kHz."""
    fmax = f[-1] if fmax is None else fmax
    idx = np.where((f >= fmin) & (f <= fmax))[0]
    k = idx[np.argmax(mag_db[idx])]
    a, b, c = mag_db[k - 1], mag_db[k], mag_db[k + 1]
    d = 0.5 * (a - c) / (a - 2 * b + c)
    return f[k] + d * (f[1] - f[0]), b - 0.25 * (a - c) * d


def tom(freq, taxa, segundos, amplitude=0.5):
    t = np.arange(int(taxa * segundos)) / taxa
    return amplitude * np.sin(2 * np.pi * freq * t)


# ================================================================ lição 2: a cadeia
def relatorio(x, taxa):
    """O que se confere numa captura antes de a dar por boa. Devolve um dict."""
    x = np.atleast_2d(np.asarray(x).T).T
    r = {"segundos": len(x) / taxa, "canais": x.shape[1]}
    for c in range(x.shape[1]):
        s = x[:, c]
        m = taxa // 20                                     # blocos de 50 ms
        blocos = s[: len(s) // m * m].reshape(-1, m)
        rms_blocos = np.sqrt(np.mean(blocos ** 2, axis=1))
        f, m = espetro(s[: min(len(s), 8 * taxa)], taxa)
        zumbido = max(m[np.argmin(np.abs(f - h))] for h in (50, 100, 150))
        r[c] = {
            "pico_dbfs": float(db(np.max(np.abs(s)))),
            "rms_dbfs": float(db(np.sqrt(np.mean(s ** 2)))),
            # «no teto»: amostras a menos de 0,01 dB do máximo possível
            "no_teto": int(np.sum(np.abs(s) >= 10 ** (-0.01 / 20))),
            "desvio_dc": float(np.mean(s)),
            "fundo_dbfs": float(db(np.percentile(rms_blocos, 5))),
            "zumbido_dbfs": float(zumbido),
        }
    return r


# ================================================================ lição 3: azimute
def perda_azimute_db(freq, minutos, largura=LARGURA_CANAL, v=V_CASSETE):
    """Perda de uma cabeça cuja fenda está rodada `minutos` de arco.

    Cada ponto da largura da pista lê o sinal com um atraso proporcional à sua
    posição; a cabeça devolve a MÉDIA desses atrasos. A média de uma fase que
    varia linearmente é sin(x)/x, com x = pi * largura * tan(ângulo) / λ."""
    lam = v / np.asarray(freq, dtype=np.float64)
    x = np.pi * largura * np.tan(np.radians(minutos / 60)) / lam
    return db(np.sinc(x / np.pi))           # np.sinc(u) = sin(pi u)/(pi u)


def simular_azimute(sinal, taxa, minutos, v=V_CASSETE):
    """Lê uma pista mono com uma cabeça estéreo rodada. Devolve (esq, dir).

    Exato no domínio da frequência. Cada canal é a média, sobre a sua faixa
    (0,6 mm centrada a -0,45 ou +0,45 mm), de cópias do sinal atrasadas por
    y*tan(ângulo)/v. A média de uma fase linear numa faixa é um atraso puro (o
    do centro da faixa) vezes sin(x)/x (a largura da faixa)."""
    X = np.fft.rfft(sinal)
    f = np.fft.rfftfreq(len(sinal), 1 / taxa)
    k = np.tan(np.radians(minutos / 60)) / v              # segundos por metro de altura
    saida = []
    for centro in (-ENTRE_CANAIS / 2, +ENTRE_CANAIS / 2):
        H = np.exp(-2j * np.pi * f * k * centro) * np.sinc(f * k * LARGURA_CANAL)
        saida.append(np.fft.irfft(X * H, len(sinal)))
    return saida[0], saida[1]


def atraso(a, b, taxa, maximo_s=0.002):
    """Quanto é que b vem atrasado em relação a a, em segundos (negativo = adiantado).

    Correlação cruzada pela FFT, pico procurado só dentro de ±maximo_s, e
    interpolação parabólica para ter frações de amostra: a 44,1 kHz um erro de
    azimute de 10' dá 2,4 amostras, e sem frações a medida saltava aos degraus."""
    n = len(a)
    A, B = np.fft.rfft(a - np.mean(a)), np.fft.rfft(b - np.mean(b))
    c = np.fft.irfft(np.conj(A) * B, n)
    m = int(maximo_s * taxa)
    janela = np.concatenate([c[-m:], c[:m + 1]])            # atrasos -m .. +m
    k = int(np.argmax(janela))
    y0, y1, y2 = janela[k - 1], janela[k], janela[k + 1]
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return (k - m + d) / taxa


def minutos_de_atraso(segundos, v=V_CASSETE, entre=ENTRE_CANAIS):
    """Ângulo da cabeça, em minutos de arco, a partir do atraso entre canais."""
    return np.degrees(np.arctan(segundos * v / entre)) * 60


def energia_agudos_db(x, taxa, de=6000.0, ate=16000.0):
    """Energia numa banda de agudos, em dB. É o critério da IASA e do Hoyt quando
    não há fita de teste: o azimute certo é o que maximiza isto."""
    X = np.fft.rfft(x - np.mean(x))
    f = np.fft.rfftfreq(len(x), 1 / taxa)
    banda = (f >= de) & (f <= ate)
    return float(10 * np.log10(np.sum(np.abs(X[banda]) ** 2) / len(x) ** 2 + 1e-30))


# ================================================================ lição 4: wow e flutter
def frequencia_instantanea(x, taxa, f0, taxa_saida=1000):
    """Frequência do tom ao longo do tempo, em Hz, a `taxa_saida` pontos por segundo.

    1. Sinal analítico pela FFT: apagar as frequências negativas e dobrar as
       positivas (Smith, «Mathematics of the DFT»). Fica-se com um número
       complexo que roda à frequência do tom.
    2. Só se guarda a banda f0/2 .. 1,5 f0: o resto é ruído que a derivada
       amplificava.
    3. Frequência = quanto roda a fase por amostra.
    4. Média em blocos até `taxa_saida`: a frequência de modulação que
       interessa acaba muito abaixo de 500 Hz."""
    x = np.asarray(x, dtype=np.float64)
    X = np.fft.fft(x)
    f = np.fft.fftfreq(len(x), 1 / taxa)
    Z = np.where((f > 0.5 * f0) & (f < 1.5 * f0), 2 * X, 0)
    z = np.fft.ifft(Z)
    fase = np.unwrap(np.angle(z))
    inst = np.diff(fase) * taxa / (2 * np.pi)
    passo = taxa // taxa_saida
    inst = inst[: len(inst) // passo * passo].reshape(-1, passo).mean(axis=1)
    corte = max(1, int(0.05 * taxa_saida))                  # bordos: a FFT supõe o sinal periódico
    return inst[corte:-corte]


def desvio_percent(inst):
    return (inst - np.mean(inst)) / np.mean(inst) * 100


def _ponderacao_polos():
    """Polos de um passa-banda de 1.ª ordem com ganho 0 dB a 4 Hz e -20 dB
    a 0,315 Hz e a 140 Hz — os três pontos da curva que encontrei publicados
    (Martin, 2021). ⚠️ NÃO é a tabela da IEC 60386, que é paga e não abri."""
    def H(fr, fa, fb):
        return np.abs((1j * fr / fa) / (1 + 1j * fr / fa) / (1 + 1j * fr / fb))
    melhor = None
    for fa in np.geomspace(0.05, 40, 160):                  # canto do passa-alto
        for fb in np.geomspace(0.5, 400, 160):               # canto do passa-baixo
            g = 1 / H(4.0, fa, fb)
            erro = (db(g * H(0.315, fa, fb)) + 20) ** 2 + (db(g * H(140.0, fa, fb)) + 20) ** 2
            if melhor is None or erro < melhor[0]:
                melhor = (erro, fa, fb, g)
    return melhor[1:]


def ponderar(desvio, taxa_d):
    """Aplica a ponderação aproximada no domínio da frequência (sem desfasar)."""
    fa, fb, g = _ponderacao_polos()
    D = np.fft.rfft(desvio)
    fr = np.fft.rfftfreq(len(desvio), 1 / taxa_d)
    H = g * (1j * fr / fa) / (1 + 1j * fr / fa) / (1 + 1j * fr / fb)
    return np.fft.irfft(D * np.abs(H), len(desvio))


def dois_sigma_desvio(d):
    """«2 sigma» como duas vezes o desvio-padrão (a leitura de Martin)."""
    return 2 * float(np.std(d))


def dois_sigma_5pct(d):
    """«2 sigma» como o valor que |d| só ultrapassa 5 % do tempo (a leitura da Virtins)."""
    return float(np.percentile(np.abs(d - np.mean(d)), 95))


def tom_com_wow(f0, taxa, segundos, componentes, amplitude=0.5, deriva=0.0):
    """Um tom gravado por uma máquina cuja velocidade varia.
    componentes: [(amplitude_relativa, hz), ...] — 0.001 é 0,1 % de pico.
    deriva: erro constante de velocidade (0.02 = 2 % mais depressa)."""
    t = np.arange(int(taxa * segundos)) / taxa
    v = np.full_like(t, 1 + deriva)          # sem componentes, sum([]) dava um escalar
    for a, hz in componentes:
        v += a * np.sin(2 * np.pi * hz * t)
    fase = 2 * np.pi * f0 * np.cumsum(v) / taxa
    return amplitude * np.sin(fase)


def medir_wow(x, taxa, f0):
    inst = frequencia_instantanea(x, taxa, f0)
    d = desvio_percent(inst)
    w = ponderar(d, 1000)
    f, m = espetro(d, 1000)
    return {
        "media_hz": float(np.mean(inst)),
        "erro_velocidade_pct": float((np.mean(inst) / f0 - 1) * 100),
        "nao_ponderado_2sd": dois_sigma_desvio(d),
        "nao_ponderado_5pct": dois_sigma_5pct(d),
        "ponderado_2sd": dois_sigma_desvio(w),
        "ponderado_5pct": dois_sigma_5pct(w),
        "rms_ponderado": float(np.std(w)),
        "pico_modulacao_hz": pico(f, m, 0.2, 200)[0],
    }


# ================================================================ linha de comandos
def _principal(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    acao, caminho = argv[1], argv[2]
    taxa, x = ler_wav(caminho)
    if acao == "relatorio":
        r = relatorio(x, taxa)
        print(f"{caminho}: {r['segundos']:.1f} s, {taxa} Hz, {r['canais']} canal(is)")
        for c in range(r["canais"]):
            v = r[c]
            print(f"  canal {c}: pico {v['pico_dbfs']:6.1f} dBFS  rms {v['rms_dbfs']:6.1f} dBFS  "
                  f"no teto {v['no_teto']:5d}  dc {v['desvio_dc']:+.4f}  "
                  f"fundo {v['fundo_dbfs']:6.1f} dBFS  zumbido {v['zumbido_dbfs']:6.1f} dBFS")
    elif acao == "azimute":
        if x.shape[1] < 2:
            print("preciso de uma captura estéreo")
            return 1
        tau = atraso(x[:, 0], x[:, 1], taxa)
        print(f"atraso D-E: {tau * 1e6:+.1f} µs = {tau * taxa:+.2f} amostras "
              f"-> cabeça a {minutos_de_atraso(tau):+.1f}' em relação à gravação")
        print(f"agudos (6-16 kHz), soma E+D: {energia_agudos_db(x[:, 0] + x[:, 1], taxa):.1f} dB")
    elif acao == "wow":
        f0 = float(argv[3]) if len(argv) > 3 else 3150.0
        r = medir_wow(x[:, 0], taxa, f0)
        for k, v in r.items():
            print(f"  {k:22s} {v:10.4f}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_principal(sys.argv))
