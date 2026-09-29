# ==================================================================
#  Práctica 1 - Segundo Parcial | Tópicos de IA
#  "¿Qué personalidad tienes?"  -  Test que funciona con LÓGICA DIFUSA
# ==================================================================

import sys


# ------------------------------------------------------------------
# 1. OPERADORES LÓGICOS DIFUSOS
# ------------------------------------------------------------------
def Y(*valores):
    return min(valores)


def O(*valores):
    return max(valores)


def NO(valor):
    return 1 - valor


# ------------------------------------------------------------------
# 2. FUNCIONES DE PERTENENCIA
# ------------------------------------------------------------------
def trapecio(x, a, b, c, d):
    if x < a or x > d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return 0.0 if b == a else (x - a) / (b - a)
    return 0.0 if d == c else (d - x) / (d - c)


def fuzzificar(puntaje):
    return {
        "bajo": trapecio(puntaje, 0, 0, 1, 2.5),
        "medio": trapecio(puntaje, 1, 2.5, 2.5, 4),
        "alto": trapecio(puntaje, 2.5, 4, 5, 5),
    }


# ------------------------------------------------------------------
# 3. LAS PREGUNTAS
# ------------------------------------------------------------------
PREGUNTAS = [
    ("sociable",   "En una fiesta me acerco a platicar con gente que no conozco.", False),
    ("sociable",   "Después de salir con amigos termino con MÁS energía.", False),
    ("organizado", "Mi cuarto o escritorio casi siempre está ordenado.", False),
    ("organizado", "Hago mis pendientes con tiempo, no a última hora.", False),
    ("creativo",   "Se me ocurren ideas diferentes para resolver problemas.", False),
    ("creativo",   "Me gusta dibujar, escribir, hacer música o crear cosas.", False),
    ("aventurero", "Me animo a probar comidas o actividades que nunca he hecho.", False),
    ("aventurero", "Prefiero un viaje improvisado a uno bien planeado.", False),
    ("tranquilo",  "Cuando algo sale mal, mantengo la calma.", False),
    ("tranquilo",  "Me preocupo mucho por cosas que todavía no pasan.", True),
]

RASGOS = ["sociable", "organizado", "creativo", "aventurero", "tranquilo"]


# ------------------------------------------------------------------
# 4. BASE DE REGLAS DIFUSAS
# ------------------------------------------------------------------
PERSONALIDADES = [
    ("El Líder", "👑", "Tomas la iniciativa y sabes organizar a los demás.",
     "SI sociable es ALTO  Y  organizado es ALTO",
     lambda g: Y(g["sociable"]["alto"], g["organizado"]["alto"])),

    ("El Artista", "🎨", "Tu mente vuela; creas cosas únicas a tu manera.",
     "SI creativo es ALTO  Y  NO organizado es ALTO",
     lambda g: Y(g["creativo"]["alto"], NO(g["organizado"]["alto"]))),

    ("El Explorador", "🧭", "Buscas experiencias nuevas y te gusta compartirlas.",
     "SI aventurero es ALTO  Y  (sociable es MEDIO  O  sociable es ALTO)",
     lambda g: Y(g["aventurero"]["alto"],
                 O(g["sociable"]["medio"], g["sociable"]["alto"]))),

    ("El Estratega", "🧠", "Planeas todo con cabeza fría y prefieres grupos pequeños.",
     "SI organizado es ALTO  Y  tranquilo es ALTO  Y  NO sociable es ALTO",
     lambda g: Y(g["organizado"]["alto"],
                 g["tranquilo"]["alto"],
                 NO(g["sociable"]["alto"]))),

    ("El Alma de la Fiesta", "🎉", "Donde llegas hay risas, energía y planes locos.",
     "SI sociable es ALTO  Y  aventurero es ALTO",
     lambda g: Y(g["sociable"]["alto"], g["aventurero"]["alto"])),

    ("El Sabio Zen", "🧘", "Nada te altera; eres el que calma a los demás.",
     "SI tranquilo es ALTO  Y  NO aventurero es ALTO",
     lambda g: Y(g["tranquilo"]["alto"], NO(g["aventurero"]["alto"]))),

    ("El Observador", "🌙", "Reservado y reflexivo; notas lo que otros no ven.",
     "SI sociable es BAJO  Y  (creativo es MEDIO  O  creativo es ALTO)",
     lambda g: Y(g["sociable"]["bajo"],
                 O(g["creativo"]["medio"], g["creativo"]["alto"]))),

    ("El Equilibrado", "⚖️", "Un poco de todo: te adaptas a cualquier situación.",
     "SI todos los rasgos son MEDIO",
     lambda g: Y(*(g[r]["medio"] for r in RASGOS))),
]


# ------------------------------------------------------------------
# 5. FUNCIONES DE APOYO
# ------------------------------------------------------------------
def barra(grado, ancho=20):
    llenos = round(grado * ancho)
    return "█" * llenos + "░" * (ancho - llenos)


def preguntar_0_a_5():
    while True:
        r = input("   Tu respuesta (0-5): ").strip()
        if r in ("0", "1", "2", "3", "4", "5"):
            return int(r)
        print("   ⚠ Escribe solo un número del 0 al 5.")


# ------------------------------------------------------------------
# 6. PROGRAMA PRINCIPAL
# ------------------------------------------------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("   🔮  ¿QUÉ PERSONALIDAD TIENES?  (test con lógica difusa)")
    print("=" * 60)
    print("Qué tanto te identificas con cada situación:")
    print("   0 = nada que ver conmigo   ...   5 = ¡totalmente yo!\n")
    print("10 Preguntas\n")

    # ---- Paso A: respuestas ----
    suma = {r: 0 for r in RASGOS}

    for i, (rasgo, texto, invertida) in enumerate(PREGUNTAS, 1):
        print(f"{i:2d}. {texto}")
        valor = preguntar_0_a_5()

        if invertida:
            valor = 5 - valor

        suma[rasgo] += valor
        print()

    # Promedio de cada rasgo
    puntaje = {
        r: suma[r] / sum(1 for p in PREGUNTAS if p[0] == r)
        for r in RASGOS
    }

    # ---- Paso B: FUZZIFICACIÓN ----
    grados = {r: fuzzificar(puntaje[r]) for r in RASGOS}

    print("=" * 60)
    print("   📊  TUS RASGOS (grado de pertenencia difusa)")
    print("=" * 60)

    for r in RASGOS:
        g = grados[r]
        etiqueta = max(g, key=g.get).upper()

        print(f"  {r.capitalize():11s} {puntaje[r]:.1f}/5 → {etiqueta}")

        for conjunto in ("bajo", "medio", "alto"):
            print(f"      {conjunto:5s} {barra(g[conjunto])} {g[conjunto]:.2f}")

    # ---- Paso C: INFERENCIA DIFUSA ----
    resultados = []

    for nombre, emoji, desc, regla_txt, regla in PERSONALIDADES:
        grado = regla(grados)
        resultados.append((grado, nombre, emoji, desc, regla_txt))

    resultados.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "=" * 60)
    print("   🧩  QUÉ TANTO TE PARECES A CADA PERSONALIDAD")
    print("=" * 60)

    for grado, nombre, emoji, _, _ in resultados:
        print(f"  {emoji} {nombre:22s} {barra(grado)} {grado * 100:5.1f}%")

    # ---- Paso D: RESULTADO FINAL ----
    grado, nombre, emoji, desc, regla_txt = resultados[0]

    print("\n" + "=" * 60)

    if grado == 0:
        print("  ✨ Eres difícil de clasificar: ¡tu personalidad es única!")
    else:
        print(f"  {emoji}  ERES: {nombre.upper()}  ({grado * 100:.0f}%)")
        print(f"      {desc}")
        print(f"      Regla que lo decidió: {regla_txt}")

        segundo = resultados[1]

        if segundo[0] == grado:
            print(f"      ¡También coincides con {segundo[2]} {segundo[1]}!")
        elif segundo[0] > 0:
            print(f"      Con un toque de {segundo[2]} {segundo[1]} "
                  f"({segundo[0] * 100:.0f}%)")

    print("=" * 60)
    print("  En lógica difusa no eres 100% una sola cosa: ¡eres una mezcla!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n¡Hasta luego!")
