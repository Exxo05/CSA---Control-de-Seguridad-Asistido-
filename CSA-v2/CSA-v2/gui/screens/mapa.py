# gui/screens/mapa.py — v3.2 solo visualización; regeneración en mapa_manager
import tkinter as tk
import os, webbrowser, datetime, threading

import servicios.mapa_server as mapa_server
import servicios.mapa_manager as mapa_manager
from servicios.eventos import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, GRAY_TEXT,
    FONT_NORMAL, FONT_SMALL, make_button, make_header, PAD_X
)

_RUTA_MAPAS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", ".."))

EVENTOS = ("incidente_registrado", "incidente_finalizado",
           "incidente_modificado", "unidad_actualizada")


class MapaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva     = True
        self._debounce = None
        mapa_server.iniciar(_RUTA_MAPAS)
        self._build()
        for ev in EVENTOS:
            suscribir(ev, self._on_cambio)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        self._viva = False
        for ev in EVENTOS:
            desuscribir(ev, self._on_cambio)
        if self._debounce:
            self.after_cancel(self._debounce)

    def _on_cambio(self, **kw):
        """Cuando hay un evento, actualizar el indicador de estado."""
        if not self._viva:
            return
        if self._debounce:
            self.after_cancel(self._debounce)
        # Esperar un poco a que mapa_manager termine de regenerar
        self._debounce = self.after(1200, self._actualizar_estado)

    def _actualizar_estado(self):
        if not self._viva:
            return
        self._debounce = None
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_estado.config(
            text=f"✅ Mapa actualizado — {hora}", fg="#059669")
        if getattr(self, "_webview_ok", False):
            ts = int(datetime.datetime.now().timestamp())
            try:
                self._wv.load_url(f"{mapa_server.url_mapa()}?t={ts}")
            except Exception:
                pass

    def _build(self):
        make_header(self, "🗺️  Mapa Operativo en Tiempo Real")

        ctrl = tk.Frame(self, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner = tk.Frame(ctrl, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        make_button(inner, "🔄 Forzar regeneración",
                    self._forzar, "info").pack(side="left", padx=4)
        make_button(inner, "🌐 Abrir en navegador",
                    self._abrir, "neutral").pack(side="left", padx=4)

        url_lbl = tk.Label(inner, text=f"🔗 {mapa_server.url_mapa()}",
                           font=("Consolas", 9), bg=WHITE, fg="#1976D2",
                           cursor="hand2")
        url_lbl.pack(side="left", padx=12)
        url_lbl.bind("<Button-1>", lambda e: self._abrir())

        self.lbl_estado = tk.Label(inner, text="✅ Mapa listo",
                                    font=FONT_SMALL, bg=WHITE, fg="#059669")
        self.lbl_estado.pack(side="right")

        self.frame_mapa = tk.Frame(self, bg=WHITE,
                                    highlightbackground=GRAY_BORDER,
                                    highlightthickness=1)
        self.frame_mapa.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        self._webview_ok = False
        self._build_panel()

    def _build_panel(self):
        try:
            import tkinterweb  # type: ignore
            self._wv = tkinterweb.HtmlFrame(
                self.frame_mapa, horizontal_scrollbar="auto",
                messages_enabled=False)
            self._wv.pack(fill="both", expand=True)
            self._wv.load_url(mapa_server.url_mapa())
            self._webview_ok = True
            return
        except Exception:
            pass

        # Fallback sin tkinterweb
        c = tk.Frame(self.frame_mapa, bg=WHITE)
        c.pack(expand=True)
        tk.Label(c, text="🗺️", font=("Segoe UI", 52), bg=WHITE).pack(pady=(30, 8))
        tk.Label(c, text="Mapa Operativo — Auto-refresco activo",
                 font=("Segoe UI", 15, "bold"), bg=WHITE, fg=POLICE_BLUE).pack()
        tk.Label(c,
                 text=(
                     "El mapa se regenera automáticamente cuando hay cambios.\n"
                     "Ábrelo en el navegador — se recarga solo cada 4 segundos.\n\n"
                     "No necesitas hacer nada más."
                 ),
                 font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT,
                 justify="center").pack(pady=(10, 20))

        box = tk.Frame(c, bg="#EFF6FF", padx=20, pady=12)
        box.pack()
        lbl = tk.Label(box, text=mapa_server.url_mapa(),
                       font=("Consolas", 12), bg="#EFF6FF",
                       fg="#1976D2", cursor="hand2")
        lbl.pack()
        lbl.bind("<Button-1>", lambda e: self._abrir())
        box.bind("<Button-1>",  lambda e: self._abrir())

        make_button(c, "🌐  Abrir mapa ahora",
                    self._abrir, "primary").pack(pady=16)
        tk.Label(c,
                 text="Para ver el mapa dentro del programa:  pip install tkinterweb",
                 font=("Segoe UI", 8), bg=WHITE, fg=GRAY_TEXT).pack()

    def _forzar(self):
        """Fuerza una regeneración inmediata."""
        self.lbl_estado.config(text="⏳ Regenerando…", fg="#D97706")
        mapa_manager._regenerar_todos()
        self.after(2000, self._actualizar_estado)

    def _abrir(self):
        webbrowser.open(mapa_server.url_mapa())
