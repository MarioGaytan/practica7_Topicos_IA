# ==================================================================
#  Práctica 1 - Segundo Parcial | Tópicos de IA
#  "¿Qué personalidad tienes?"  -  Test que funciona con LÓGICA DIFUSA
# ------------------------------------------------------------------
#  El jugador responde 10 situaciones del 0 al 5.
#  Por dentro el programa:
#    1) Calcula 5 rasgos (sociable, organizado, creativo, aventurero, tranquilo).
#    2) FUZZIFICA cada rasgo: lo convierte en grados de BAJO / MEDIO / ALTO.
#    3) Evalúa REGLAS DIFUSAS con los operadores Y (min), O (max), NO (1-x).
#    4) Cada regla da un % de parecido con una personalidad; gana la mayor.
# ==================================================================

import sys  # se usa solo para que la consola de Windows muestre acentos y emojis


# ------------------------------------------------------------------
# 1. OPERADORES LÓGICOS DIFUSOS  (aquí vive la lógica difusa)
# ------------------------------------------------------------------
def Y(*valores):                # Y difuso (AND): recibe varios grados entre 0 y 1
    return min(valores)         # el resultado es el MENOR: la cadena es tan fuerte como su eslabón más débil


def O(*valores):                # O difuso (OR): recibe varios grados entre 0 y 1
    return max(valores)         # el resultado es el MAYOR: basta con que una condición se cumpla bien


def NO(valor):                  # NO difuso (NOT): recibe un grado entre 0 y 1
    return 1 - valor            # complemento: si algo es 0.8 cierto, su negación es 0.2 cierta


# ------------------------------------------------------------------
# 2. FUNCIONES DE PERTENENCIA  (convierten un número en un grado 0..1)
# ------------------------------------------------------------------
def trapecio(x, a, b, c, d):    # figura de trapecio: sube de a a b, se queda en 1 de b a c, baja de c a d
    if x < a or x > d:          # si x está fuera de la figura...
        return 0.0              # ...no pertenece nada al conjunto
    if b <= x <= c:             # si x está en la parte plana de arriba...
        return 1.0              # ...pertenece totalmente
    if x < b:                   # si x está en la rampa de subida...
        return (x - a) / (b - a)  # ...crece en línea recta de 0 a 1
    return (d - x) / (d - c)    # si no, está en la rampa de bajada: decrece de 1 a 0


def fuzzificar(puntaje):        # recibe el puntaje de un rasgo (0 a 5) y lo vuelve "palabras con grado"
    return {                    # regresa un diccionario con los tres conjuntos difusos
        "bajo":  trapecio(puntaje, 0, 0, 1, 2.5),    # BAJO: total en 0-1, se desvanece hasta 2.5
        "medio": trapecio(puntaje, 1, 2.5, 2.5, 4),  # MEDIO: triángulo con pico en 2.5 (a=1, c=4)
        "alto":  trapecio(puntaje, 2.5, 4, 5, 5),    # ALTO: empieza en 2.5 y es total de 4 a 5
    }                           # ej. puntaje 3 -> bajo 0.0, medio 0.67, alto 0.33 (¡es medio Y algo alto!)


# ------------------------------------------------------------------
# 3. LAS PREGUNTAS  (rasgo que mide, texto, ¿se invierte?)
# ------------------------------------------------------------------
PREGUNTAS = [                                                                              # lista de las 10 situaciones
    ("sociable",   "En una fiesta me acerco a platicar con gente que no conozco.", False),  # más alto = más sociable
    ("sociable",   "Después de salir con amigos termino con MÁS energía.", False),
    ("organizado", "Mi cuarto o escritorio casi siempre está ordenado.", False),
    ("organizado", "Hago mis pendientes con tiempo, no a última hora.", False),
    ("creativo",   "Se me ocurren ideas diferentes para resolver problemas.", False),
    ("creativo",   "Me gusta dibujar, escribir, hacer música o crear cosas.", False),
    ("aventurero", "Me animo a probar comidas o actividades que nunca he hecho.", False),
    ("aventurero", "Prefiero un viaje improvisado a uno bien planeado.", False),
    ("tranquilo",  "Cuando algo sale mal, mantengo la calma.", False),
    ("tranquilo",  "Me preocupo mucho por cosas que todavía no pasan.", True),  # True = invertida: preocuparse MUCHO = MENOS tranquilo
]

RASGOS = ["sociable", "organizado", "creativo", "aventurero", "tranquilo"]  # los 5 rasgos, en el orden en que se muestran


# ------------------------------------------------------------------
# 4. BASE DE REGLAS DIFUSAS  (programación lógica difusa)
#    Cada personalidad = nombre, emoji, descripción, regla en texto,
#    y la regla como función que usa Y / O / NO sobre los grados (g).
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
     lambda g: Y(g["aventurero"]["alto"], O(g["sociable"]["medio"], g["sociable"]["alto"]))),

    ("El Estratega", "🧠", "Planeas todo con cabeza fría y prefieres grupos pequeños.",
     "SI organizado es ALTO  Y  tranquilo es ALTO  Y  NO sociable es ALTO",
     lambda g: Y(g["organizado"]["alto"], g["tranquilo"]["alto"], NO(g["sociable"]["alto"]))),

    ("El Alma de la Fiesta", "🎉", "Donde llegas hay risas, energía y planes locos.",
     "SI sociable es ALTO  Y  aventurero es ALTO",
     lambda g: Y(g["sociable"]["alto"], g["aventurero"]["alto"])),

    ("El Sabio Zen", "🧘", "Nada te altera; eres el que calma a los demás.",
     "SI tranquilo es ALTO  Y  NO aventurero es ALTO",
     lambda g: Y(g["tranquilo"]["alto"], NO(g["aventurero"]["alto"]))),

    ("El Observador", "🌙", "Reservado y reflexivo; notas lo que otros no ven.",
     "SI sociable es BAJO  Y  (creativo es MEDIO  O  creativo es ALTO)",
     lambda g: Y(g["sociable"]["bajo"], O(g["creativo"]["medio"], g["creativo"]["alto"]))),

    ("El Equilibrado", "⚖️", "Un poco de todo: te adaptas a cualquier situación.",
     "SI todos los rasgos son MEDIO",
     lambda g: Y(*(g[r]["medio"] for r in RASGOS))),
]


# ------------------------------------------------------------------
# 5. FUNCIONES DE APOYO (pantalla y entrada)
# ------------------------------------------------------------------
def barra(grado, ancho=20):                  # dibuja una barra con el grado (0..1)
    llenos = round(grado * ancho)            # cuántos cuadritos se rellenan
    return "█" * llenos + "░" * (ancho - llenos)  # cuadritos llenos + vacíos


def preguntar_0_a_5():                       # pide un número del 0 al 5 hasta que sea válido
    while True:                              # se repite hasta recibir algo correcto
        r = input("   Tu respuesta (0-5): ").strip()  # lee lo que escribe el jugador y quita espacios
        if r in ("0", "1", "2", "3", "4", "5"):       # ¿es un número permitido?
            return int(r)                    # sí: lo regresa como entero
        print("   ⚠ Escribe solo un número del 0 al 5.")  # no: avisa y vuelve a preguntar


# ------------------------------------------------------------------
# 6. PROGRAMA PRINCIPAL
# ------------------------------------------------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):         # si la consola lo permite...
        sys.stdout.reconfigure(encoding="utf-8")   # ...usa UTF-8 para acentos y emojis

    print("=" * 60)                                # línea decorativa
    print("   🔮  ¿QUÉ PERSONALIDAD TIENES?  (test con lógica difusa)")
    print("=" * 60)
    print("Qué tanto te identificas con cada situación:")
    print("   0 = nada que ver conmigo   ...   5 = ¡totalmente yo!\n")

    # ---- Paso A: hacer las preguntas y juntar puntos por rasgo ----
    suma = {r: 0 for r in RASGOS}                  # puntos acumulados de cada rasgo, empiezan en 0
    cuantas = {r: 0 for r in RASGOS}               # cuántas preguntas tuvo cada rasgo
    for i, (rasgo, texto, invertida) in enumerate(PREGUNTAS, 1):  # recorre las preguntas numeradas desde 1
        print(f"{i:2d}. {texto}")                  # muestra la situación
        valor = preguntar_0_a_5()                  # lee la respuesta del jugador
        if invertida:                              # si la pregunta mide lo contrario...
            valor = 5 - valor                      # ...se voltea la escala (5 se vuelve 0, 4 se vuelve 1, etc.)
        suma[rasgo] += valor                       # suma el valor al rasgo que mide
        cuantas[rasgo] += 1                        # cuenta una pregunta más para ese rasgo
        print()                                    # línea en blanco para que se lea mejor

    puntaje = {r: suma[r] / cuantas[r] for r in RASGOS}  # promedio de cada rasgo (queda entre 0 y 5)

    # ---- Paso B: FUZZIFICACIÓN (número -> grados BAJO/MEDIO/ALTO) ----
    grados = {r: fuzzificar(puntaje[r]) for r in RASGOS}  # aquí cada rasgo deja de ser "3.5" y pasa a ser "0.33 medio, 0.67 alto"

    print("=" * 60)
    print("   📊  TUS RASGOS (grado de pertenencia difusa)")
    print("=" * 60)
    for r in RASGOS:                                       # muestra cada rasgo
        g = grados[r]                                      # sus tres grados
        etiqueta = max(g, key=g.get).upper()               # la palabra con mayor grado (BAJO, MEDIO o ALTO)
        print(f"  {r.capitalize():11s} {puntaje[r]:.1f}/5 → {etiqueta}")
        for conjunto in ("bajo", "medio", "alto"):         # y el detalle de cada conjunto difuso
            print(f"      {conjunto:5s} {barra(g[conjunto])} {g[conjunto]:.2f}")

    # ---- Paso C: INFERENCIA con las reglas difusas (Y / O / NO) ----
    resultados = []                                        # aquí se guardan (grado, personalidad)
    for nombre, emoji, desc, regla_txt, regla in PERSONALIDADES:  # recorre cada regla
        grado = regla(grados)                              # evalúa la regla: da qué tan cierta es (0..1)
        resultados.append((grado, nombre, emoji, desc, regla_txt))  # la guarda
    resultados.sort(reverse=True)                          # ordena de mayor a menor grado

    print("\n" + "=" * 60)
    print("   🧩  QUÉ TANTO TE PARECES A CADA PERSONALIDAD")
    print("=" * 60)
    for grado, nombre, emoji, _, _ in resultados:          # muestra todas, ya ordenadas
        print(f"  {emoji} {nombre:22s} {barra(grado)} {grado * 100:5.1f}%")

    # ---- Paso D: resultado final ----
    grado, nombre, emoji, desc, regla_txt = resultados[0]  # la personalidad con mayor grado
    print("\n" + "=" * 60)
    if grado == 0:                                         # si ninguna regla se activó...
        print("  ✨ Eres difícil de clasificar: ¡tu personalidad es única!")
    else:
        print(f"  {emoji}  ERES: {nombre.upper()}  ({grado * 100:.0f}%)")
        print(f"      {desc}")
        print(f"      Regla que lo decidió: {regla_txt}")
        segundo = resultados[1]                            # la segunda más fuerte
        if segundo[0] == grado:                            # si tiene el mismo grado, es un empate
            print(f"      ¡Empatado con {segundo[2]} {segundo[1]}! Eres las dos a la vez.")
        elif segundo[0] > 0:                               # si no, pero tiene algo de grado...
            print(f"      Con un toque de {segundo[2]} {segundo[1]} ({segundo[0] * 100:.0f}%)")
    print("=" * 60)
    print("  En lógica difusa no eres 100% una sola cosa: ¡eres una mezcla!")


if __name__ == "__main__":         # solo se ejecuta si corres este archivo directamente
    try:
        main()                     # arranca el test
    except (KeyboardInterrupt, EOFError):  # si el jugador presiona Ctrl+C...
        print("\n\n¡Hasta luego!")  # ...se despide sin mostrar errores
