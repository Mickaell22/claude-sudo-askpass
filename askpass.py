"""Ventana de sudo con efectos: corre dentro de kitty, lanzada por sudo-askpass.

Uso: askpass.py <frase> <archivo-salida> [--demo N]
Al aceptar escribe la contraseña en <archivo-salida> y crea <archivo-salida>.ok;
al cancelar crea <archivo-salida>.cancel. Solo stdlib.
"""
from __future__ import annotations

import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import termios
import time
import tty
import wave

ESC = "\033["
RATE = 22050


# ---------- color ----------
def acento() -> tuple[int, int, int]:
    try:
        css = open(os.path.expanduser("~/.config/waybar/accent.css")).read()
        h = re.search(r"accent #([0-9a-fA-F]{6})", css).group(1)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except (OSError, AttributeError):
        return (203, 166, 247)  # mauve


def fg(r, g, b):
    return f"{ESC}38;2;{r};{g};{b}m"


def bg(r, g, b):
    return f"{ESC}48;2;{r};{g};{b}m"


RESET = f"{ESC}0m"
BASE = (30, 30, 46)
TEXTO = (205, 214, 244)
PALETA = [(243, 139, 168), (250, 179, 135), (249, 226, 175), (166, 227, 161),
          (148, 226, 213), (137, 180, 250), (203, 166, 247), (245, 194, 231)]


def w(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def tam():
    t = shutil.get_terminal_size((80, 22))
    return t.columns, t.lines


def limpiar():
    w(bg(*BASE) + f"{ESC}2J{ESC}H")


def en(x, y, s):
    w(f"{ESC}{y};{x}H{s}")


# ---------- sonido (sintetizado, cada vez distinto) ----------
def onda(notas, vol=0.25, tipo="sin"):
    datos = bytearray()
    for freq, dur in notas:
        n = int(RATE * dur)
        for i in range(n):
            t = i / RATE
            env = min(1.0, i / 300) * min(1.0, (n - i) / 600)
            if freq <= 0:
                v = 0.0
            elif tipo == "square":
                v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif tipo == "saw":
                v = 2 * ((freq * t) % 1) - 1
            else:
                v = math.sin(2 * math.pi * freq * t)
            datos += struct.pack("<h", int(v * env * vol * 32767))
    return bytes(datos)


def sonar(notas, vol=0.25, tipo="sin"):
    if not shutil.which("pw-play"):
        return
    fd, ruta = tempfile.mkstemp(suffix=".wav", dir=os.environ.get("XDG_RUNTIME_DIR"))
    with os.fdopen(fd, "wb") as f, wave.open(f, "wb") as wv:
        wv.setnchannels(1)
        wv.setsampwidth(2)
        wv.setframerate(RATE)
        wv.writeframes(onda(notas, vol, tipo))
    subprocess.Popen(["sh", "-c", f'pw-play "{ruta}"; rm -f "{ruta}"'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def melodia():
    escalas = {"mayor": [0, 2, 4, 7, 9, 12], "menor": [0, 3, 5, 7, 10, 12],
               "japo": [0, 1, 5, 7, 8, 12], "arabe": [0, 1, 4, 5, 7, 8, 11, 12]}
    esc = random.choice(list(escalas.values()))
    base = random.choice([220, 262, 294, 330, 392])
    pasos = [random.choice(esc) for _ in range(random.randint(3, 7))]
    if random.random() < 0.5:
        pasos.sort(reverse=random.random() < 0.5)
    dur = random.choice([0.07, 0.1, 0.14])
    return [(base * 2 ** (p / 12), dur) for p in pasos]


def sonido_random():
    r = random.random()
    if r < 0.15:
        sonar([(988, 0.08), (1319, 0.3)], 0.2, "square")      # moneda
    elif r < 0.25:
        sonar([(f, 0.03) for f in range(300, 1500, 60)], 0.15, "saw")  # power-up
    else:
        sonar(melodia(), 0.22, random.choice(["sin", "sin", "square", "saw"]))


# ---------- intros ----------
def matrix(seg=1.6):
    cols, filas = tam()
    gotas = [random.randint(-filas, 0) for _ in range(cols)]
    ch = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ01ﾀﾁﾂﾃﾄ$#@%&"
    fin = time.time() + seg
    while time.time() < fin:
        for x in range(0, cols, 2):
            y = gotas[x]
            if 1 <= y <= filas:
                en(x + 1, y, fg(166, 227, 161) + random.choice(ch))
            if 1 <= y - 6 <= filas:
                en(x + 1, y - 6, " ")
            gotas[x] = y + 1 if y < filas + 6 else random.randint(-8, 0)
        time.sleep(0.04)


def maquina(frase):
    cols, filas = tam()
    x, y = max(1, (cols - len(frase)) // 2), filas // 2
    for i, c in enumerate(frase):
        en(x + i, y, fg(*random.choice(PALETA)) + c)
        if c != " " and i % 2 == 0:
            sonar([(random.randint(1800, 2600), 0.012)], 0.08, "square")
        time.sleep(0.035)
    time.sleep(0.5)


def hackeo():
    cols, filas = tam()
    tareas = ["Descifrando el kernel", "Sobornando a systemd", "Convenciendo a Nix",
              "Calentando el /nix/store", "Pidiendo permiso a Linus", "Despertando al root",
              "Alineando los bits", "Hackeando la NASA (mentira)"]
    random.shuffle(tareas)
    y = max(2, filas // 2 - 3)
    for t in tareas[:4]:
        for p in range(0, 101, random.choice([5, 10, 20])):
            barra = "█" * (p // 5) + "░" * (20 - p // 5)
            en(4, y, fg(*TEXTO) + f"{t:<28}" + fg(*acento()) + f"[{barra}] {p:3}%")
            time.sleep(0.02)
        y += 1
    sonar([(523, 0.08), (659, 0.08), (784, 0.15)], 0.2)
    time.sleep(0.3)


def estrellas(seg=1.5):
    cols, filas = tam()
    st = [[random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.1, 1)] for _ in range(80)]
    fin = time.time() + seg
    while time.time() < fin:
        limpiar()
        for s in st:
            s[2] -= 0.04
            if s[2] <= 0.02:
                s[:] = [random.uniform(-1, 1), random.uniform(-1, 1), 1]
            x = int(cols / 2 + s[0] / s[2] * cols / 4)
            y = int(filas / 2 + s[1] / s[2] * filas / 4)
            if 1 <= x <= cols and 1 <= y <= filas:
                en(x, y, fg(*TEXTO) + ("*" if s[2] < 0.3 else "."))
        time.sleep(0.04)


def gatito():
    cols, filas = tam()
    cuadros = [r" /\_/\ ", r"( o.o )", r" > ^ < "]
    pasos = [r" /\_/\ ", r"( -.- )", r" > ^ < "]
    for x in range(1, cols - 8, 2):
        limpiar()
        arte = pasos if x % 8 == 0 else cuadros
        for i, l in enumerate(arte):
            en(x, filas // 2 - 1 + i, fg(250, 179, 135) + l)
        time.sleep(0.03)
    sonar([(880, 0.1), (660, 0.2)], 0.2)


def arcoiris(frase):
    cols, filas = tam()
    x, y = max(1, (cols - len(frase)) // 2), filas // 2
    for k in range(30):
        for i, c in enumerate(frase):
            en(x + i, y + int(math.sin((i + k) / 2) * 2), fg(*PALETA[(i + k) % len(PALETA)]) + c)
        time.sleep(0.05)
        for i in range(len(frase)):
            for d in (-2, -1, 0, 1, 2):
                en(x + i, y + d, " ")


def susto():
    cols, filas = tam()
    en(cols // 2 - 6, filas // 2, fg(*TEXTO) + "cargando...")
    time.sleep(random.uniform(1.0, 2.2))
    cara = [r"   _______   ", r"  /       \  ", r" |  X   X  | ", r" |    ^    | ",
            r" |  \___/  | ", r"  \_______/  ", r"  BUUUUUU!!  "]
    sonar([(random.choice([200, 233, 180]), 0.6)], 0.55, "saw")
    for k in range(6):
        w(bg(*((243, 139, 168) if k % 2 == 0 else (17, 17, 27))) + f"{ESC}2J")
        for i, l in enumerate(cara):
            en(cols // 2 - 6, filas // 2 - 3 + i, fg(17, 17, 27) if k % 2 == 0 else fg(243, 139, 168))
            w(l)
        time.sleep(0.09)
    time.sleep(0.3)


# ---------- prompt ----------
def caja(frase, mascara, error=""):
    cols, filas = tam()
    ac = acento()
    ancho = min(cols - 4, max(46, len(frase) + 6))
    x0, y0 = (cols - ancho) // 2 + 1, filas // 2 - 3
    limpiar()
    borde = fg(*ac)
    en(x0, y0, borde + "╭" + "─" * (ancho - 2) + "╮")
    for i in range(1, 6):
        en(x0, y0 + i, borde + "│" + " " * (ancho - 2) + "│")
    en(x0, y0 + 6, borde + "╰" + "─" * (ancho - 2) + "╯")
    f = frase[: ancho - 6]
    en(x0 + (ancho - len(f)) // 2, y0 + 1, fg(*ac) + f"{ESC}1m" + f + RESET + bg(*BASE))
    en(x0 + 3, y0 + 3, fg(*TEXTO) + "Contraseña: " + mascara)
    en(x0 + 3, y0 + 5, fg(108, 112, 134) + (error or "Enter = aceptar   Esc = cancelar"))
    en(x0 + 15 + len(mascara_visible(mascara)), y0 + 3, "")


def mascara_visible(m):
    return re.sub(r"\033\[[0-9;]*m", "", m)


def pedir(frase):
    simbolos = "✦★♥♦●◆✿❀☾☀⚡♪"
    clave, masc = [], ""
    fd = sys.stdin.fileno()
    viejo = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        caja(frase, masc)
        while True:
            c = os.read(fd, 1)
            if c in (b"\r", b"\n"):
                return "".join(clave) if clave else None
            if c in (b"\x1b", b"\x03", b"\x04"):
                return None
            if c in (b"\x7f", b"\x08"):
                if clave:
                    clave.pop()
                    masc = masc[: masc.rfind(ESC + "38")]
            elif c == b"\x15":
                clave, masc = [], ""
            else:
                # UTF-8: el primer byte dice cuantos siguen (ñ y tildes son 2 bytes)
                extra = 3 if c[0] >= 0xF0 else 2 if c[0] >= 0xE0 else 1 if c[0] >= 0xC0 else 0
                try:
                    ch = (c + (os.read(fd, extra) if extra else b"")).decode()
                except UnicodeDecodeError:
                    continue
                clave.append(ch)
                masc += fg(*random.choice(PALETA)) + random.choice(simbolos)
                if random.random() < 0.3:
                    sonar([(random.randint(1200, 2400), 0.015)], 0.06, "square")
            caja(frase, masc)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, viejo)


def main():
    frase, salida = sys.argv[1], sys.argv[2]
    w(f"{ESC}?25l")  # ocultar cursor
    limpiar()
    intros = [matrix, lambda: maquina(frase), hackeo, estrellas, gatito, lambda: arcoiris(frase)]
    if "--demo" in sys.argv:
        n = int(sys.argv[sys.argv.index("--demo") + 1])
        ([*intros, susto])[n]()
        return
    sonido_random()
    if random.random() < 0.08:  # ponytail: susto con 8% de probabilidad
        susto()
    else:
        random.choice(intros)()
    w(f"{ESC}?25h")
    clave = pedir(frase)
    viejo = os.umask(0o077)
    try:
        if clave is None:
            open(salida + ".cancel", "w").close()
        else:
            with open(salida, "w") as f:
                f.write(clave)
            open(salida + ".ok", "w").close()
            sonar([(784, 0.06), (1047, 0.12)], 0.15)
            time.sleep(0.2)
    finally:
        os.umask(viejo)


if __name__ == "__main__":
    main()
