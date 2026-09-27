import requests
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

API_KEY = ""

MODEL = "gemini-3.8-flash"

URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    + MODEL +
    ":generateContent"
)


# ==========================================================
# PERSONALIDAD DE PELOPS
# ==========================================================

INSTRUCCIONES = """
Tu nombre es Pelops.

Eres una IA conversacional y educativa.

Ayudas con:

Matemáticas:
- operaciones
- ecuaciones
- fracciones
- porcentajes
- geometría
- problemas matemáticos

Lengua castellana:
- gramática
- ortografía
- literatura
- comprensión lectora
- redacción

Inglés:
- traducciones
- vocabulario
- gramática
- tiempos verbales
- ejercicios

También puedes ayudar con:
- ciencias
- física
- química
- biología
- historia
- geografía
- cultura general
- preguntas cotidianas
- conversación

Responde principalmente en español.

Explica de forma sencilla.
Si el usuario pide una respuesta corta, sé breve.
Si pide pasos, muestra los pasos.

No inventes información.
Si no estás seguro de algo, dilo claramente.

Tu nombre es Pelops.
"""


# ==========================================================
# APLICACIÓN
# ==========================================================

class PelopsApp(App):

    def build(self):

        self.title = "Pelops"

        self.historial = []

        self.mensaje_pensando = None

        # ==================================================
        # CONTENEDOR PRINCIPAL
        # ==================================================

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        # ==================================================
        # CABECERA
        # ==================================================

        titulo = Label(
            text="🤖 PELOPS",
            font_size=dp(27),
            bold=True,
            size_hint_y=None,
            height=dp(48)
        )

        principal.add_widget(titulo)

        subtitulo = Label(
            text="IA educativa y conversacional",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(28)
        )

        principal.add_widget(subtitulo)

        # ==================================================
        # CHAT
        # ==================================================

        self.scroll = ScrollView(
            do_scroll_x=False
        )

        self.chat = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            padding=dp(7),
            size_hint_y=None
        )

        self.chat.bind(
            minimum_height=self.chat.setter("height")
        )

        self.scroll.add_widget(self.chat)

        principal.add_widget(self.scroll)

        # ==================================================
        # MENSAJE INICIAL
        # ==================================================

        self.agregar_mensaje(
            "Pelops",
            "¡Hola! 👋\n\n"
            "Soy Pelops. Puedo ayudarte con matemáticas, "
            "lengua castellana, inglés, ciencias y muchas "
            "otras preguntas."
        )

        # ==================================================
        # BOTONES DE MATERIAS
        # ==================================================

        materias = GridLayout(
            cols=3,
            rows=2,
            spacing=dp(4),
            size_hint_y=None,
            height=dp(92)
        )

        opciones = [
            ("🧮 Matemáticas",
             "Quiero ayuda con matemáticas."),

            ("📚 Lengua",
             "Quiero ayuda con lengua castellana."),

            ("🇬🇧 Inglés",
             "Quiero ayuda con inglés."),

            ("🔬 Ciencias",
             "Quiero ayuda con ciencias."),

            ("🌎 Cultura",
             "Quiero hacerte una pregunta de cultura general."),

            ("💬 Conversar",
             "Quiero conversar contigo.")
        ]

        for nombre, mensaje in opciones:

            boton = Button(
                text=nombre,
                font_size=dp(11)
            )

            boton.bind(
                on_press=lambda boton,
                texto=mensaje:
                self.enviar_mensaje(texto)
            )

            materias.add_widget(boton)

        principal.add_widget(materias)

        # ==================================================
        # ENTRADA
        # ==================================================

        entrada = BoxLayout(
            orientation="horizontal",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(52)
        )

        self.caja = TextInput(
            hint_text="Escribe tu mensaje...",
            multiline=False,
            font_size=dp(16)
        )

        self.caja.bind(
            on_text_validate=lambda x:
            self.enviar_mensaje()
        )

        entrada.add_widget(self.caja)

        boton_enviar = Button(
            text="ENVIAR",
            size_hint_x=None,
            width=dp(90)
        )

        boton_enviar.bind(
            on_press=lambda x:
            self.enviar_mensaje()
        )

        entrada.add_widget(boton_enviar)

        principal.add_widget(entrada)

        # ==================================================
        # LIMPIAR
        # ==================================================

        boton_limpiar = Button(
            text="🗑️ Limpiar conversación",
            size_hint_y=None,
            height=dp(42)
        )

        boton_limpiar.bind(
            on_press=lambda x:
            self.limpiar()
        )

        principal.add_widget(boton_limpiar)

        return principal


    # ======================================================
    # AGREGAR MENSAJE
    # ======================================================

    def agregar_mensaje(self, autor, texto):

        etiqueta = Label(
            text=autor + ":\n" + texto,
            font_size=dp(15),
            halign="left",
            valign="top",
            size_hint_y=None,
            text_size=(dp(340), None),
            padding=(dp(8), dp(8))
        )

        def ajustar(instance, tamaño):

            instance.height = tamaño[1] + dp(16)

        etiqueta.bind(
            texture_size=ajustar
        )

        self.chat.add_widget(etiqueta)

        Clock.schedule_once(
            self.ir_abajo,
            0.1
        )

        return etiqueta


    # ======================================================
    # SCROLL AL FINAL
    # ======================================================

    def ir_abajo(self, dt):

        self.scroll.scroll_y = 0


    # ======================================================
    # ENVIAR MENSAJE
    # ======================================================

    def enviar_mensaje(self, mensaje=None):

        if mensaje is None:

            mensaje = self.caja.text.strip()

            if not mensaje:
                return

            self.caja.text = ""

        else:

            mensaje = mensaje.strip()

            if not mensaje:
                return

        # Mostrar mensaje del usuario

        self.agregar_mensaje(
            "Tú",
            mensaje
        )

        # Bloquear entrada mientras responde

        self.caja.disabled = True

        # Mostrar "pensando"

        self.mensaje_pensando = self.agregar_mensaje(
            "Pelops",
            "⏳ Pensando..."
        )

        # Ejecutar API fuera del hilo principal

        hilo = threading.Thread(
            target=self.consultar_api,
            args=(mensaje,),
            daemon=True
        )

        hilo.start()


    # ======================================================
    # CONSULTAR GEMINI
    # ======================================================

    def consultar_api(self, mensaje):

        try:

            # ----------------------------------------------
            # COMPROBAR API KEY
            # ----------------------------------------------

            if (
                not API_KEY
                or API_KEY == "PEGA_AQUI_TU_API_KEY"
            ):

                raise Exception(
                    "No has colocado tu API KEY."
                )

            # ----------------------------------------------
            # PREPARAR HISTORIAL
            # ----------------------------------------------

            if len(self.historial) == 0:

                contenido = (
                    INSTRUCCIONES
                    + "\n\nUsuario:\n"
                    + mensaje
                )

            else:

                contenido = mensaje

            self.historial.append({

                "role": "user",

                "parts": [
                    {
                        "text": contenido
                    }
                ]

            })

            datos = {
                "contents": self.historial
            }

            # ----------------------------------------------
            # PETICIÓN
            # ----------------------------------------------

            respuesta = requests.post(

                URL,

                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": API_KEY
                },

                json=datos,

                timeout=30
            )

            # ----------------------------------------------
            # JSON
            # ----------------------------------------------

            try:

                resultado = respuesta.json()

            except Exception:

                raise Exception(
                    "La API devolvió una respuesta que "
                    "no pude interpretar."
                )

            # ----------------------------------------------
            # ERROR HTTP
            # ----------------------------------------------

            if respuesta.status_code != 200:

                if "error" in resultado:

                    error = resultado["error"]

                    mensaje_error = error.get(
                        "message",
                        "Error desconocido."
                    )

                    raise Exception(
                        "Gemini respondió con error "
                        + str(respuesta.status_code)
                        + ":\n"
                        + mensaje_error
                    )

                raise Exception(
                    "Error HTTP "
                    + str(respuesta.status_code)
                )

            # ----------------------------------------------
            # COMPROBAR CANDIDATES
            # ----------------------------------------------

            if "candidates" not in resultado:

                raise Exception(
                    "Gemini no devolvió ninguna respuesta."
                )

            candidatos = resultado["candidates"]

            if not candidatos:

                raise Exception(
                    "La respuesta de Gemini está vacía."
                )

            # ----------------------------------------------
            # EXTRAER TEXTO
            # ----------------------------------------------

            partes = candidatos[0].get(
                "content",
                {}
            ).get(
                "parts",
                []
            )

            if not partes:

                raise Exception(
                    "Gemini no devolvió texto."
                )

            texto = partes[0].get(
                "text",
                ""
            )

            if not texto:

                raise Exception(
                    "Gemini devolvió una respuesta vacía."
                )

            # ----------------------------------------------
            # GUARDAR RESPUESTA
            # ----------------------------------------------

            self.historial.append({

                "role": "model",

                "parts": [
                    {
                        "text": texto
                    }
                ]

            })

            # ----------------------------------------------
            # ACTUALIZAR INTERFAZ
            # ----------------------------------------------

            Clock.schedule_once(
                lambda dt:
                self.mostrar_respuesta(texto),
                0
            )

        except requests.exceptions.Timeout:

            self.eliminar_pensando()

            Clock.schedule_once(
                lambda dt:
                self.mostrar_error(
                    "La conexión tardó demasiado. "
                    "Comprueba tu Internet."
                )
            )

        except requests.exceptions.ConnectionError:

            self.eliminar_pensando()

            Clock.schedule_once(
                lambda dt:
                self.mostrar_error(
                    "No pude conectarme a Internet."
                )
            )

        except Exception as error:

            self.eliminar_pensando()

            mensaje_error = str(error)

            Clock.schedule_once(
                lambda dt:
                self.mostrar_error(
                    mensaje_error
                )
            )


    # ======================================================
    # MOSTRAR RESPUESTA
    # ======================================================

    def mostrar_respuesta(self, texto):

        self.eliminar_pensando()

        self.agregar_mensaje(
            "Pelops",
            texto
        )

        self.caja.disabled = False
        self.caja.focus = True


    # ======================================================
    # MOSTRAR ERROR
    # ======================================================

    def mostrar_error(self, texto):

        self.agregar_mensaje(
            "Pelops ⚠️",
            texto
        )

        self.caja.disabled = False
        self.caja.focus = True


    # ======================================================
    # ELIMINAR "PENSANDO..."
    # ======================================================

    def eliminar_pensando(self):

        if self.mensaje_pensando is not None:

            if self.mensaje_pensando.parent:

                self.chat.remove_widget(
                    self.mensaje_pensando
                )

            self.mensaje_pensando = None


    # ======================================================
    # LIMPIAR CONVERSACIÓN
    # ======================================================

    def limpiar(self):

        self.historial.clear()

        self.chat.clear_widgets()

        self.mensaje_pensando = None

        self.agregar_mensaje(
            "Pelops",
            "Conversación borrada. 🗑️\n\n"
            "¿En qué puedo ayudarte?"
        )


# ==========================================================
# INICIAR
# ==========================================================

if __name__ == "__main__":

    PelopsApp().run()