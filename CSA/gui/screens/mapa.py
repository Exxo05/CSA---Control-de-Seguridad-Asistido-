# gui/screens/mapa.py — Visor de mapa v2.0
import tkinter as tk
from tkinter import ttk
import os, tempfile, webbrowser
from mapas.mapa_principal import crear_mapa_principal
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    FONT_NORMAL, FONT_SMALL, make_button, make_header, PAD_X
)

class MapaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._mapa_path = None
        self._build()

    def _build(self):
        make_header(self, "🗺️  Mapa Operativo en Tiempo Real")

        # ── Barra de controles ────────────────────────────────────
        ctrl = tk.Frame(self, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=PAD_X, pady=(12,0))
        inner = tk.Frame(ctrl, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        self.var_solo_activos = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Mostrar solo activos",
                       variable=self.var_solo_activos,
                       font=FONT_NORMAL, bg=WHITE,
                       command=self._generar).pack(side="left", padx=(0,16))

        make_button(inner, "🔄  Actualizar mapa", self._generar, "info").pack(side="left", padx=4)
        make_button(inner, "🌐  Abrir en navegador", self._abrir_browser, "neutral").pack(side="left", padx=4)

        self.lbl_estado = tk.Label(inner, text="", font=FONT_SMALL,
                                    bg=WHITE, fg=GRAY_TEXT)
        self.lbl_estado.pack(side="right")

        # ── Área del mapa ─────────────────────────────────────────
        self.frame_mapa = tk.Frame(self, bg=GRAY_BG)
        self.frame_mapa.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        # Intentar webview embebido, si no mostrar botón para navegador
        self._webview_ok = self._intentar_webview()
        if not self._webview_ok:
            self._mostrar_fallback()

        self._generar()

    def _intentar_webview(self) -> bool:
        try:
            import tkinterweb  # type: ignore
            self._webview_widget = tkinterweb.HtmlFrame(
                self.frame_mapa, horizontal_scrollbar="auto")
            self._webview_widget.pack(fill="both", expand=True)
            return True
        except ImportError:
            return False

    def _mostrar_fallback(self):
        info = tk.Frame(self.frame_mapa, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        info.pack(fill="both", expand=True)
        tk.Label(info,
                 text="🗺️\n\nEl mapa se genera como archivo HTML interactivo.\n"
                      "Pulse «Abrir en navegador» para verlo,\n"
                      "o instale tkinterweb para embeber el mapa aquí.\n\n"
                      "pip install tkinterweb",
                 font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT,
                 justify="center").pack(expand=True)

    def _generar(self):
        solo = self.var_solo_activos.get()
        try:
            mapa = crear_mapa_principal(solo_activos=solo)
            tmp  = tempfile.NamedTemporaryFile(
                delete=False, suffix=".html",
                dir=os.path.dirname(os.path.abspath(__file__))
            )
            mapa.save(tmp.name)
            self._mapa_path = tmp.name

            filtro = "Activos" if solo else "Todos"
            self.lbl_estado.config(text=f"Mapa generado  ({filtro})  ✅")

            if self._webview_ok:
                self._webview_widget.load_file(self._mapa_path)
        except Exception as e:
            self.lbl_estado.config(text=f"Error: {e}")

    def _abrir_browser(self):
        if not self._mapa_path:
            self._generar()
        if self._mapa_path:
            webbrowser.open(f"file://{self._mapa_path}")
