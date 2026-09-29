# ==================================================================
#  Práctica 1 - Segundo Parcial | Tópicos de IA
#  "¿Qué personalidad tienes?"  -  Versión con VENTANA GRÁFICA (tkinter)
# ------------------------------------------------------------------
#  Misma lógica difusa que la versión de consola:
#    1) Respuestas 0-5  ->  puntaje promedio de 5 rasgos.
#    2) FUZZIFICACIÓN: cada puntaje -> grados BAJO / MEDIO / ALTO.
#    3) INFERENCIA: reglas difusas con Y (min), O (max), NO (1-x).
#    4) La regla con mayor grado es tu personalidad.
#  Incluye animaciones: botones que rebotan al elegir, tarjetas que se
#  deslizan entre preguntas y barras de resultados que se llenan.
# ==================================================================

import math           # seno para los efectos de rebote y flotado
import time           # reloj para medir cuánto lleva cada animación
import ctypes         # para que Windows no se vea borroso con escala 125%/150%
import tkinter as tk  # librería de ventanas que ya viene incluida con Python

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)   # texto nítido en pantallas con escala
except Exception:
    pass                                            # (en Mac/Linux no aplica)


# ------------------------------------------------------------------
# 1. OPERADORES LÓGICOS DIFUSOS
# ------------------------------------------------------------------
def Y(*valores):                # Y difuso (AND)
    return min(valores)         # el menor grado: se cumple tanto como la condición más débil


def O(*valores):                # O difuso (OR)
    return max(valores)         # el mayor grado: basta con que una condición se cumpla


def NO(valor):                  # NO difuso (NOT)
    return 1 - valor            # complemento


# ------------------------------------------------------------------
# 2. FUNCIONES DE PERTENENCIA
# ------------------------------------------------------------------
def trapecio(x, a, b, c, d):    # sube de a->b, vale 1 en [b,c], baja de c->d
    if x < a or x > d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return 0.0 if b == a else (x - a) / (b - a)
    return 0.0 if d == c else (d - x) / (d - c)


def fuzzificar(puntaje):        # número 0..5 -> grados de BAJO / MEDIO / ALTO
    return {
        "bajo": trapecio(puntaje, 0, 0, 1, 2.5),
        "medio": trapecio(puntaje, 1, 2.5, 2.5, 4),
        "alto": trapecio(puntaje, 2.5, 4, 5, 5),
    }


# ------------------------------------------------------------------
# 3. LAS PREGUNTAS  (rasgo, texto, ¿invertida?)
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

    ("El Equilibrado", "⚖", "Un poco de todo: te adaptas a cualquier situación.",
     "SI todos los rasgos son MEDIO",
     lambda g: Y(*(g[r]["medio"] for r in RASGOS))),
]


# ------------------------------------------------------------------
# 5. CÁLCULO DIFUSO COMPLETO (lo que antes hacía main() en consola)
# ------------------------------------------------------------------
def calcular(respuestas):
    """respuestas: lista de 10 enteros 0..5 -> (puntaje, grados, resultados)."""
    suma = {r: 0 for r in RASGOS}
    for (rasgo, _, invertida), valor in zip(PREGUNTAS, respuestas):
        suma[rasgo] += (5 - valor) if invertida else valor           # voltea las preguntas invertidas

    puntaje = {r: suma[r] / sum(1 for p in PREGUNTAS if p[0] == r)   # promedio por rasgo (0..5)
               for r in RASGOS}
    grados = {r: fuzzificar(puntaje[r]) for r in RASGOS}             # FUZZIFICACIÓN

    resultados = [(regla(grados), nombre, emoji, desc, regla_txt)    # INFERENCIA: evalúa cada regla
                  for nombre, emoji, desc, regla_txt, regla in PERSONALIDADES]
    resultados.sort(key=lambda x: x[0], reverse=True)                # mayor grado primero
    return puntaje, grados, resultados


def valores_usados(regla_txt, grados):
    """Vuelve a evaluar una regla anotando qué grados difusos leyó (para explicarla)."""
    regla = next(p[4] for p in PERSONALIDADES if p[3] == regla_txt)
    usados = []

    class Espia:                                    # se hace pasar por grados[rasgo]
        def __init__(self, rasgo):
            self.rasgo = rasgo

        def __getitem__(self, conjunto):            # cada vez que la regla lee un grado...
            v = grados[self.rasgo][conjunto]
            usados.append(f"{self.rasgo} {conjunto.upper()} = {v:.2f}")  # ...lo anotamos
            return v

    resultado = regla({r: Espia(r) for r in RASGOS})
    return usados, resultado


# ------------------------------------------------------------------
# 6. ESTILO VISUAL
# ------------------------------------------------------------------
FONDO = "#17142a"         # fondo de la ventana
TARJETA = "#241f3d"       # fondo de los recuadros
TARJETA_2 = "#2f2950"     # recuadros internos / barras vacías
TEXTO = "#f4f1ff"         # texto principal
SUAVE = "#a9a2cc"         # texto secundario
ACENTO = "#8b5cf6"        # morado principal
ACENTO_HOVER = "#a78bfa"
BLANCO = "#ffffff"

COLOR_RASGO = {           # un color por rasgo
    "sociable": "#f472b6",
    "organizado": "#60a5fa",
    "creativo": "#fbbf24",
    "aventurero": "#34d399",
    "tranquilo": "#a78bfa",
}
EMOJI_RASGO = {"sociable": "💬", "organizado": "📋", "creativo": "💡",
               "aventurero": "🧗", "tranquilo": "🌿"}

# colores de los botones 0..5 (de gris a morado intenso)
COLOR_OPCION = ["#475569", "#5b5a86", "#6b5fa8", "#7a5fc4", "#8659dc", "#9b4dff"]

F = "Segoe UI"            # tipografía
F_EMOJI = "Segoe UI Emoji"
ESCALA = 1.0             # se ajusta al abrir la ventana según la escala de Windows


def px(n):               # convierte pixeles "de diseño" a pixeles reales de la pantalla
    return int(n * ESCALA)


# ------------------------------------------------------------------
# 7. MOTOR DE ANIMACIONES
#    Tkinter no trae animaciones, así que las hacemos "a mano":
#    cada ~16 ms (≈60 cuadros por segundo) cambiamos un poquito
#    una propiedad (color, posición, tamaño) hasta llegar al final.
# ------------------------------------------------------------------
def suave(t):
    """Easing 'ease-out': arranca rápido y frena al final (se siente natural)."""
    return 1 - (1 - t) ** 3


def rebote(t):
    """Easing 'ease-out-back': se pasa un poquito del final y regresa (efecto pop)."""
    c1 = 1.70158
    return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2


def mezclar(color1, color2, t):
    """Color intermedio entre color1 y color2 (t=0 -> color1, t=1 -> color2)."""
    a = [int(color1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def animar(widget, duracion, paso, al_terminar=None, retraso=0):
    """Llama paso(t) con t yendo de 0 a 1 durante 'duracion' ms.
    Si el widget ya tenía una animación en curso, la cancela (evita choques)."""
    raiz = widget.winfo_toplevel()
    anterior = getattr(widget, "_animacion", None)
    if anterior:
        raiz.after_cancel(anterior)
    inicio = [None]

    def cuadro():
        if not widget.winfo_exists():          # el widget se destruyó (cambió la pantalla)
            return
        if inicio[0] is None:
            inicio[0] = time.perf_counter()
        t = min(1.0, (time.perf_counter() - inicio[0]) * 1000 / duracion)
        paso(t)
        if t < 1:
            widget._animacion = raiz.after(16, cuadro)   # siguiente cuadro
        else:
            widget._animacion = None
            if al_terminar:
                al_terminar()

    widget._animacion = raiz.after(retraso, cuadro)


def boton(padre, texto, comando, bg=ACENTO, hover=ACENTO_HOVER, fg=BLANCO,
          fuente=(F, 13, "bold"), **kw):
    """Botón plano cuyo color cambia suavemente al pasar el mouse."""
    b = tk.Button(padre, text=texto, command=comando, bg=bg, fg=fg,
                  activebackground=hover, activeforeground=fg, relief="flat",
                  bd=0, cursor="hand2", font=fuente, **kw)
    b.bloqueado = False                        # True mientras se anima la selección

    def cambiar_a(destino):
        if b.bloqueado:
            return
        desde = b.cget("bg")
        animar(b, 140, lambda t: b.config(bg=mezclar(desde, destino, suave(t))))

    b.bind("<Enter>", lambda e: cambiar_a(hover))
    b.bind("<Leave>", lambda e: cambiar_a(bg))
    return b


def barra(padre, grado, color, ancho=200, alto=12, fondo=TARJETA,
          retraso=None, etiqueta=None, formato=None):
    """Barra horizontal (Canvas) que se llena según el grado 0..1.
    Con 'retraso' se anima creciendo desde 0; si hay 'etiqueta', su número va contando."""
    ancho, alto = px(ancho), px(alto)
    c = tk.Canvas(padre, width=ancho, height=alto, bg=fondo, highlightthickness=0)
    c.create_rectangle(0, 0, ancho, alto, fill=TARJETA_2, outline="")
    relleno = c.create_rectangle(0, 0, 0, alto, fill=color, outline="")

    def pintar(valor):
        c.coords(relleno, 0, 0, ancho * valor if valor > 0 else 0, alto)
        if etiqueta is not None:
            etiqueta.config(text=formato(valor))

    if retraso is None:
        pintar(grado)
    else:
        pintar(0)
        animar(c, 700, lambda t: pintar(grado * suave(t)), retraso=retraso)
    return c


# ------------------------------------------------------------------
# 8. LA VENTANA
# ------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global ESCALA
        ESCALA = self.winfo_fpixels("1i") / 96          # 1.0 = 100%, 1.25 = 125%...
        self.title("¿Qué personalidad tienes? · Lógica difusa")
        self.geometry(f"{px(1000)}x{px(790)}")
        self.minsize(px(900), px(760))
        self.configure(bg=FONDO)

        self.respuestas = [None] * len(PREGUNTAS)   # respuesta de cada pregunta
        self.indice = 0                              # pregunta actual
        self.en_pregunta = False                     # ¿estamos en la pantalla de preguntas?
        self.animando = False                        # bloquea clics mientras corre una animación
        self.progreso = 0.0                          # valor dibujado en la barra de progreso (0..1)
        self.tarjeta = None                          # tarjeta de la pregunta visible
        self.botones = []                            # botones 0..5 de la tarjeta visible

        self.contenedor = tk.Frame(self, bg=FONDO)
        self.contenedor.pack(fill="both", expand=True, padx=px(26), pady=px(18))

        self.bind("<Key>", self.tecla)               # permite contestar con el teclado
        self.pantalla_inicio()

    def limpiar(self):
        for w in self.contenedor.winfo_children():
            w.destroy()

    # ---------------- Pantalla 1: inicio ----------------
    def pantalla_inicio(self):
        self.limpiar()
        self.en_pregunta = False
        caja = tk.Frame(self.contenedor, bg=FONDO)
        caja.place(relx=0.5, rely=0.5, anchor="center")

        bola = tk.Label(caja, text="🔮", font=(F_EMOJI, 64), bg=FONDO, fg=TEXTO)
        bola.pack(pady=(px(10), 0))
        tk.Label(caja, text="¿Qué personalidad tienes?", font=(F, 32, "bold"),
                 bg=FONDO, fg=TEXTO).pack(pady=(6, 4))
        tk.Label(caja, text="Un test que decide tu personalidad usando lógica difusa",
                 font=(F, 14), bg=FONDO, fg=SUAVE).pack()

        info = tk.Frame(caja, bg=TARJETA, padx=28, pady=18)
        info.pack(pady=28)
        for linea in ("📝  10 situaciones cortas",
                      "🎯  Contesta del 0 (nada que ver conmigo) al 5 (¡totalmente yo!)",
                      "⏱️  Toma menos de 2 minutos"):
            tk.Label(info, text=linea, font=(F, 13), bg=TARJETA, fg=TEXTO,
                     anchor="w").pack(fill="x", pady=3)

        boton(caja, "Comenzar  →", self.comenzar, fuente=(F, 16, "bold"),
              padx=36, pady=10).pack()
        self.flotar(bola)

    def flotar(self, bola):
        """ANIMACIÓN: la bola de cristal sube y baja suavemente sin parar."""
        def ciclo():
            if not bola.winfo_exists():
                return
            y = (math.sin(time.perf_counter() * 2.5) + 1) / 2        # oscila entre 0 y 1
            bola.pack_configure(pady=(round(px(10) * (1 - y)), round(px(10) * y)))
            self.after(33, ciclo)
        ciclo()

    def comenzar(self):
        self.respuestas = [None] * len(PREGUNTAS)
        self.indice = 0
        self.progreso = 0.0
        self.construir_marco_preguntas()
        self.mostrar_pregunta(direccion=1)                  # la primera entra deslizándose

    # ---------------- Pantalla 2: preguntas ----------------
    def construir_marco_preguntas(self):
        """Encabezado, zona de la tarjeta y pie: se crean UNA vez y se reutilizan."""
        self.limpiar()
        self.en_pregunta = True
        self.tarjeta = None

        arriba = tk.Frame(self.contenedor, bg=FONDO)
        arriba.pack(fill="x")
        self.lbl_num = tk.Label(arriba, font=(F, 13, "bold"), bg=FONDO, fg=SUAVE)
        self.lbl_num.pack(side="left")
        self.lbl_pct = tk.Label(arriba, text="0%", font=(F, 13, "bold"), bg=FONDO, fg=SUAVE)
        self.lbl_pct.pack(side="right")
        self.canvas_prog = tk.Canvas(self.contenedor, height=px(10), bg=FONDO,
                                     highlightthickness=0)
        self.canvas_prog.pack(fill="x", pady=(8, 0))
        self.canvas_prog.bind("<Configure>", lambda e: self.dibujar_progreso())

        abajo = tk.Frame(self.contenedor, bg=FONDO)
        abajo.pack(side="bottom", fill="x")
        self.btn_anterior = boton(abajo, "←  Anterior", self.anterior, bg=TARJETA,
                                  hover=TARJETA_2, fuente=(F, 12), padx=16, pady=6)
        tk.Label(abajo, text="Tip: usa las teclas 0 – 5  ·  ← para regresar",
                 font=(F, 11), bg=FONDO, fg=SUAVE).pack(side="right")

        # zona donde se deslizan las tarjetas (lo que sale de aquí se recorta)
        self.zona = tk.Frame(self.contenedor, bg=FONDO)
        self.zona.pack(fill="both", expand=True, pady=26)

    def crear_tarjeta(self):
        """Construye la tarjeta de la pregunta actual (todavía sin colocarla)."""
        _, texto, _ = PREGUNTAS[self.indice]
        tarjeta = tk.Frame(self.zona, bg=TARJETA, padx=40, pady=40)

        tk.Label(tarjeta, text="¿Qué tanto te identificas con esto?",
                 font=(F, 13), bg=TARJETA, fg=SUAVE).pack()
        tk.Label(tarjeta, text=f"“{texto}”", font=(F, 24, "bold"), bg=TARJETA,
                 fg=TEXTO, wraplength=px(760), justify="center").pack(expand=True, pady=20)

        # fila de botones 0..5: cada uno vive en una "celda" de tamaño fijo,
        # así cuando el botón se hunde o crece no mueve a los demás
        fila = tk.Frame(tarjeta, bg=TARJETA)
        fila.pack()
        self.botones = []
        lado = px(82)
        for v in range(6):
            celda = tk.Frame(fila, width=lado, height=lado, bg=TARJETA)
            celda.pack_propagate(False)
            celda.grid(row=0, column=v, padx=px(5))
            elegido = self.respuestas[self.indice] == v
            b = boton(celda, str(v), lambda v=v: self.seleccionar(v),
                      bg=TEXTO if elegido else COLOR_OPCION[v],
                      hover=ACENTO_HOVER, fg=FONDO if elegido else BLANCO,
                      fuente=(F, 22, "bold"))
            b.pack(fill="both", expand=True)
            self.botones.append(b)

        etiquetas = tk.Frame(tarjeta, bg=TARJETA)
        etiquetas.pack(fill="x", pady=(10, 0), padx=px(70))
        tk.Label(etiquetas, text="😐  Nada que ver conmigo", font=(F, 11),
                 bg=TARJETA, fg=SUAVE).pack(side="left")
        tk.Label(etiquetas, text="¡Totalmente yo!  😄", font=(F, 11),
                 bg=TARJETA, fg=SUAVE).pack(side="right")
        return tarjeta

    def mostrar_pregunta(self, direccion):
        """ANIMACIÓN: la tarjeta nueva entra deslizándose y la vieja sale.
        direccion = 1 -> hacia adelante (entra por la derecha), -1 -> hacia atrás."""
        self.animando = True
        self.lbl_num.config(text=f"Pregunta {self.indice + 1} de {len(PREGUNTAS)}")
        self.animar_progreso(self.indice / len(PREGUNTAS))
        if self.indice > 0:
            self.btn_anterior.pack(side="left")
        else:
            self.btn_anterior.pack_forget()

        vieja = self.tarjeta
        nueva = self.crear_tarjeta()
        self.tarjeta = nueva
        nueva.place(relx=direccion, rely=0, relwidth=1, relheight=1)

        def paso(t):
            e = suave(t)
            nueva.place_configure(relx=direccion * (1 - e))       # de afuera hacia 0
            if vieja is not None:
                vieja.place_configure(relx=-direccion * e)        # de 0 hacia afuera

        def fin():
            if vieja is not None:
                vieja.destroy()
            self.animando = False

        animar(nueva, 380, paso, fin)

    def seleccionar(self, v):
        """ANIMACIÓN al elegir: el botón se hunde, rebota y se ilumina; los demás se apagan."""
        if self.animando or not self.en_pregunta:
            return
        self.animando = True
        self.respuestas[self.indice] = v
        for b in self.botones:
            b.bloqueado = True                     # desactiva el efecto hover mientras dura

        # 1) los botones NO elegidos se atenúan
        for k, b in enumerate(self.botones):
            if k != v:
                bg0, fg0 = b.cget("bg"), b.cget("fg")
                animar(b, 220, lambda t, b=b, bg0=bg0, fg0=fg0: b.config(
                    bg=mezclar(bg0, TARJETA_2, suave(t)),
                    fg=mezclar(fg0 if fg0.startswith("#") else BLANCO, SUAVE, suave(t))))

        # 2) el elegido: se hunde (se hace chico) y luego rebota más grande
        elegido = self.botones[v]
        base = elegido.cget("bg")
        hundir = px(9)

        def pulso(t):
            if t < 0.3:                                        # fase 1: se hunde
                k = suave(t / 0.3)
                margen = hundir * k
                color = mezclar(base, BLANCO, k)
                texto = mezclar(BLANCO, FONDO, k)
                tam = 22 - 4 * k
            else:                                              # fase 2: rebota
                k = (t - 0.3) / 0.7
                margen = hundir * (1 - suave(k))
                color = mezclar(BLANCO, ACENTO, suave(k))
                texto = mezclar(FONDO, BLANCO, suave(k))
                tam = 18 + 4 * k + 9 * math.sin(math.pi * k)  # 18 -> ~28 -> 22
            elegido.pack_configure(padx=round(margen), pady=round(margen))
            elegido.config(bg=color, activebackground=color, fg=texto, font=(F, round(tam), "bold"))

        animar(elegido, 420, pulso, lambda: self.after(90, self.siguiente))

    def siguiente(self):
        self.indice += 1
        if self.indice < len(PREGUNTAS):
            self.mostrar_pregunta(direccion=1)
            return
        # ya fue la última: la barra llega a 100% y la tarjeta sale antes de los resultados
        self.animar_progreso(1.0)
        tarjeta = self.tarjeta
        animar(tarjeta, 320, lambda t: tarjeta.place_configure(relx=-suave(t)),
               self.pantalla_resultados)

    def anterior(self):
        if self.animando or self.indice == 0:
            return
        self.indice -= 1
        self.mostrar_pregunta(direccion=-1)

    def animar_progreso(self, destino):
        """ANIMACIÓN: la barra de progreso avanza (o retrocede) suavemente."""
        origen = self.progreso

        def paso(t):
            self.progreso = origen + (destino - origen) * suave(t)
            self.dibujar_progreso()

        animar(self.canvas_prog, 450, paso)

    def dibujar_progreso(self):
        c = self.canvas_prog
        ancho, alto = c.winfo_width(), px(10)
        c.delete("all")
        c.create_rectangle(0, 0, ancho, alto, fill=TARJETA_2, outline="")
        if self.progreso > 0:
            c.create_rectangle(0, 0, ancho * self.progreso, alto, fill=ACENTO, outline="")
        self.lbl_pct.config(text=f"{round(self.progreso * 100)}%")

    def tecla(self, evento):
        if not self.en_pregunta:
            return
        if evento.char and evento.char in "012345":
            self.seleccionar(int(evento.char))
        elif evento.keysym in ("BackSpace", "Left"):
            self.anterior()

    # ---------------- Pantalla 3: resultados ----------------
    def pantalla_resultados(self):
        self.limpiar()
        self.en_pregunta = False
        self.animando = False
        puntaje, grados, resultados = calcular(self.respuestas)   # <- aquí trabaja la lógica difusa
        grado, nombre, emoji, desc, regla_txt = resultados[0]

        # ---- tarjeta principal: tu personalidad ----
        heroe = tk.Frame(self.contenedor, bg=TARJETA, padx=px(24), pady=px(14))
        heroe.pack(fill="x")
        caja_emoji = tk.Frame(heroe, bg=TARJETA, width=px(110), height=px(110))
        caja_emoji.pack_propagate(False)                  # tamaño fijo: el emoji crece sin mover nada
        caja_emoji.pack(side="left", padx=(0, px(14)))
        lbl_emoji = tk.Label(caja_emoji, text=emoji if grado > 0 else "✨",
                             font=(F_EMOJI, 1), bg=TARJETA, fg=TEXTO)
        lbl_emoji.pack(expand=True)
        # ANIMACIÓN: el emoji aparece con efecto "pop" (crece, se pasa y regresa)
        animar(lbl_emoji, 650, lambda t: lbl_emoji.config(
            font=(F_EMOJI, max(1, round(44 * rebote(t))))), retraso=120)

        info = tk.Frame(heroe, bg=TARJETA)
        info.pack(side="left", fill="x", expand=True)

        if grado == 0:
            tk.Label(info, text="Eres difícil de clasificar", font=(F, 26, "bold"),
                     bg=TARJETA, fg=TEXTO, anchor="w").pack(fill="x")
            tk.Label(info, text="Ninguna regla se activó: ¡tu personalidad es única!",
                     font=(F, 13), bg=TARJETA, fg=SUAVE, anchor="w").pack(fill="x")
        else:
            tk.Label(info, text="TU PERSONALIDAD ES", font=(F, 11, "bold"),
                     bg=TARJETA, fg=SUAVE, anchor="w").pack(fill="x")
            lbl_nombre = tk.Label(info, font=(F, 24, "bold"), bg=TARJETA, fg=TEXTO, anchor="w")
            lbl_nombre.pack(fill="x")
            # ANIMACIÓN: el porcentaje cuenta desde 0 hasta tu grado
            animar(lbl_nombre, 900, lambda t: lbl_nombre.config(
                text=f"{nombre}  ·  {grado * 100 * suave(t):.0f}%"))
            tk.Label(info, text=desc, font=(F, 12), bg=TARJETA, fg=TEXTO,
                     anchor="w").pack(fill="x")
            tk.Label(info, text=f"Regla que lo decidió:  {regla_txt}",
                     font=("Consolas", 10), bg=TARJETA, fg=ACENTO_HOVER, anchor="w",
                     justify="left", wraplength=px(720)).pack(fill="x", pady=(px(4), 0))
            segundo = resultados[1]
            if segundo[0] == grado:
                extra = f"¡También coincides con {segundo[2]} {segundo[1]}!"
            elif segundo[0] > 0:
                extra = f"Con un toque de {segundo[2]} {segundo[1]} ({segundo[0] * 100:.0f}%)"
            else:
                extra = ""
            if extra:
                tk.Label(info, text=extra, font=(F, 11), bg=TARJETA, fg=SUAVE,
                         anchor="w").pack(fill="x", pady=(px(2), 0))

        # ---- dos columnas: rasgos (fuzzificación) y personalidades (inferencia) ----
        columnas = tk.Frame(self.contenedor, bg=FONDO)
        columnas.pack(fill="x", pady=px(12))
        columnas.columnconfigure(0, weight=1, uniform="c")
        columnas.columnconfigure(1, weight=1, uniform="c")

        izq = tk.Frame(columnas, bg=TARJETA, padx=px(18), pady=px(12))
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, px(6)))
        der = tk.Frame(columnas, bg=TARJETA, padx=px(18), pady=px(12))
        der.grid(row=0, column=1, sticky="nsew", padx=(px(6), 0))

        # columna izquierda: cada rasgo en una fila con sus grados BAJO / MEDIO / ALTO
        tk.Label(izq, text="📊  Tus rasgos", font=(F, 14, "bold"), bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x")
        tk.Label(izq, text="Fuzzificación: pertenencia a Bajo · Medio · Alto",
                 font=(F, 10), bg=TARJETA, fg=SUAVE, anchor="w").pack(fill="x", pady=(0, px(6)))
        tabla = tk.Frame(izq, bg=TARJETA)
        tabla.pack(fill="x")
        for fila, r in enumerate(RASGOS):
            g = grados[r]
            etiqueta = max(g, key=g.get).upper()
            tk.Label(tabla, text=f"{EMOJI_RASGO[r]} {r.capitalize()}", font=(F, 11, "bold"),
                     bg=TARJETA, fg=COLOR_RASGO[r], anchor="w").grid(
                         row=fila, column=0, sticky="w", pady=px(3))
            for k, conjunto in enumerate(("bajo", "medio", "alto")):
                celda = tk.Frame(tabla, bg=TARJETA)
                celda.grid(row=fila, column=k + 1, padx=px(4))
                lbl = tk.Label(celda, font=(F, 8), bg=TARJETA, fg=SUAVE)
                # ANIMACIÓN: las barras crecen en cascada (cada rasgo un poquito después)
                barra(celda, g[conjunto], COLOR_RASGO[r], ancho=58, alto=8,
                      retraso=200 + fila * 110 + k * 40, etiqueta=lbl,
                      formato=lambda val, c=conjunto: f"{c[0].upper()} {val:.2f}").pack()
                lbl.pack()
            tk.Label(tabla, text=f"{puntaje[r]:.1f} → {etiqueta}", font=(F, 10, "bold"),
                     bg=TARJETA, fg=TEXTO, anchor="e").grid(row=fila, column=4, sticky="e")
        tabla.columnconfigure(4, weight=1)

        # columna derecha: grado de cada regla / personalidad
        tk.Label(der, text="🧩  Parecido con cada personalidad", font=(F, 14, "bold"),
                 bg=TARJETA, fg=TEXTO, anchor="w").pack(fill="x")
        tk.Label(der, text="Inferencia: reglas con Y = min · O = max · NO = 1 − x",
                 font=(F, 10), bg=TARJETA, fg=SUAVE, anchor="w").pack(fill="x", pady=(0, px(6)))
        for i, (gr, nom, emo, _, _) in enumerate(resultados):
            fila = tk.Frame(der, bg=TARJETA)
            fila.pack(fill="x", pady=px(2))
            color = ACENTO if i == 0 and gr > 0 else "#6d6594"
            tk.Label(fila, text=emo, font=(F_EMOJI, 12), bg=TARJETA, fg=TEXTO,
                     width=2).pack(side="left")
            tk.Label(fila, text=nom, font=(F, 10, "bold" if i == 0 else "normal"),
                     bg=TARJETA, fg=TEXTO, anchor="w").pack(side="left", padx=(px(4), 0))
            lbl_pct = tk.Label(fila, font=(F, 10, "bold"), bg=TARJETA, fg=TEXTO,
                               width=5, anchor="e")
            lbl_pct.pack(side="right")
            barra(fila, gr, color, ancho=130, alto=10, retraso=350 + i * 90,
                  etiqueta=lbl_pct, formato=lambda val: f"{val * 100:.0f}%"
                  ).pack(side="right", padx=px(6))

        # ---- pie ----
        pie = tk.Frame(self.contenedor, bg=FONDO)
        pie.pack(side="bottom", fill="x")   # se reserva primero para que nunca se salga
        tk.Label(pie, text="En lógica difusa no eres 100% una sola cosa: ¡eres una mezcla!",
                 font=(F, 12, "italic"), bg=FONDO, fg=SUAVE).pack(side="left")
        boton(pie, "Salir", self.destroy, bg=TARJETA, hover=TARJETA_2,
              fuente=(F, 12), padx=16, pady=6).pack(side="right")
        boton(pie, "🔁  Repetir test", self.comenzar, fuente=(F, 12, "bold"),
              padx=16, pady=6).pack(side="right", padx=10)

        # ---- ¿cómo se calculó? (los pasos de la lógica difusa con tus números) ----
        como = tk.Frame(self.contenedor, bg=TARJETA, padx=px(18), pady=px(12))
        como.pack(fill="both", expand=True, pady=(0, px(12)))
        tk.Label(como, text="🔍  ¿Cómo se calculó?", font=(F, 14, "bold"), bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x")
        pasos = [
            "1. Tus respuestas (0–5) se promediaron por rasgo; la pregunta de preocuparte se invierte (5 − x).",
            "2. Fuzzificación: cada promedio se convirtió en grados de BAJO, MEDIO y ALTO (tabla de la izquierda).",
            "3. Inferencia: cada personalidad es una regla SI…ENTONCES evaluada con Y = min, O = max, NO = 1 − x.",
        ]
        if grado > 0:
            usados, res = valores_usados(regla_txt, grados)
            pasos.append(f"4. Regla ganadora ({nombre}) usó:  " + "   ·   ".join(usados)
                         + f"   ⇒   grado = {res:.2f}  ({res * 100:.0f}%)")
        else:
            pasos.append("4. Todas las reglas dieron 0: ninguna combinación de rasgos coincidió.")
        for texto in pasos:
            tk.Label(como, text=texto, font=(F, 10), bg=TARJETA, fg=SUAVE, anchor="w",
                     justify="left", wraplength=px(900)).pack(fill="x", pady=px(1))


if __name__ == "__main__":
    App().mainloop()
