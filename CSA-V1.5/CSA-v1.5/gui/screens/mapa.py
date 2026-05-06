# gui/screens/mapa.py — v3.0 con servidor HTTP interno + auto-refresco real
import tkinter as tk
from tkinter import ttk
import os, webbrowser, threading
import datetime

from mapas.mapa_principal import crear_mapa_principal
from servicios.eventos    import suscribir, desuscribir
import servicios.mapa_server as mapa_server
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, FONT_NORMAL, FONT_SMALL,
    make_button, make_header, PAD_X
)

EVENTOS_MAPA = ("incidente_registrado", "incidente_finalizado",
                "incidente_modificado", "unidad_actualizada")

# Carpeta donde viven los HTMLs del mapa (raíz del proyecto)
_RUTA_MAPAS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


class MapaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._auto_id   = None
        self._generando = False

        # Arrancar servidor HTTP (idempotente)
        mapa_server.iniciar(_RUTA_MAPAS)

        self._build()

        for ev in EVENTOS_MAPA:
            suscribir(ev, self._on_cambio)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        for ev in EVENTOS_MAPA:
            desuscribir(ev, self._on_cambio)
        if self._auto_id:
            self.after_cancel(self._auto_id)

    def _on_cambio(self, **kwargs):
        """Debounce: regenera el HTML 700ms después del último evento."""
        if self._auto_id:
            self.after_cancel(self._auto_id)
        self._auto_id = self.after(700, self._generar_bg)

    def _build(self):
        make_header(self, "🗺️  Mapa Operativo en Tiempo Real")

        # ── Toolbar ───────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner = tk.Frame(ctrl, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        self.var_solo_activos = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Solo activos",
                       variable=self.var_solo_activos,
                       font=FONT_NORMAL, bg=WHITE,
                       command=self._generar_bg).pack(side="left")

        make_button(inner, "🔄 Regenerar mapa",
                    self._generar_bg, "info").pack(side="left", padx=(12, 4))
        make_button(inner, "🌐 Abrir en navegador",
                    self._abrir_browser, "neutral").pack(side="left", padx=4)

        # Indicador URL del servidor
        url_lbl = tk.Label(inner,
                           text=f"🔗 {mapa_server.url_mapa()}",
                           font=("Consolas", 9), bg=WHITE, fg="#1976D2",
                           cursor="hand2")
        url_lbl.pack(side="left", padx=12)
        url_lbl.bind("<Button-1>", lambda e: self._abrir_browser())

        self.lbl_estado = tk.Label(inner, text="", font=FONT_SMALL,
                                    bg=WHITE, fg=GRAY_TEXT)
        self.lbl_estado.pack(side="right")

        # ── Panel informativo (siempre visible) ───────────────────
        self.frame_info = tk.Frame(self, bg=WHITE,
                                   highlightbackground=GRAY_BORDER,
                                   highlightthickness=1)
        self.frame_info.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        self._build_info_panel()
        self._generar_bg()

    def _build_info_panel(self):
        for w in self.frame_info.winfo_children():
            w.destroy()

        # Intentar webview embebido
        try:
            import tkinterweb  # type: ignore
            self._wv = tkinterweb.HtmlFrame(
                self.frame_info, horizontal_scrollbar="auto",
                messages_enabled=False)
            self._wv.pack(fill="both", expand=True)
            self._wv.load_url(mapa_server.url_mapa())
            self._webview_ok = True
            return
        except Exception:
            self._webview_ok = False

        # Fallback visual mejorado
        center = tk.Frame(self.frame_info, bg=WHITE)
        center.pack(expand=True)

        tk.Label(center, text="🗺️", font=("Segoe UI", 48),
                 bg=WHITE).pack(pady=(40, 8))
        tk.Label(center,
                 text="Mapa Operativo Interactivo",
                 font=("Segoe UI", 16, "bold"), bg=WHITE, fg=POLICE_BLUE).pack()
        tk.Label(center,
                 text="El mapa se actualiza automáticamente.\n"
                      "Ábrelo en el navegador y se refrescará solo cada 4 segundos.",
                 font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT,
                 justify="center").pack(pady=(8, 20))

        url = mapa_server.url_mapa()
        url_frame = tk.Frame(center, bg="#EFF6FF", padx=16, pady=10)
        url_frame.pack()
        tk.Label(url_frame, text=url, font=("Consolas", 11),
                 bg="#EFF6FF", fg="#1976D2", cursor="hand2").pack()
        url_frame.bind("<Button-1>", lambda e: self._abrir_browser())

        make_button(center, "🌐  Abrir mapa ahora",
                    self._abrir_browser, "primary").pack(pady=16)

        tk.Label(center,
                 text="💡  El navegador se recarga automáticamente — no necesitas hacer nada más.",
                 font=("Segoe UI", 9), bg=WHITE, fg="#059669").pack(pady=(0, 40))

        # Instalar tkinterweb
        tk.Label(center,
                 text="Para ver el mapa aquí dentro del programa:   pip install tkinterweb",
                 font=("Segoe UI", 8), bg=WHITE, fg=GRAY_TEXT).pack()

    def _generar_bg(self):
        """Regenera el mapa en un hilo para no bloquear la UI."""
        if self._generando:
            return
        self._generando = True
        self.lbl_estado.config(text="⏳ Generando…", fg="#D97706")
        threading.Thread(target=self._generar_worker, daemon=True).start()

    def _generar_worker(self):
        try:
            solo = self.var_solo_activos.get()
            mapa = crear_mapa_principal(solo_activos=solo)
            ruta = os.path.join(_RUTA_MAPAS, "mapa.html")
            mapa.save(ruta)
            hora = datetime.datetime.now().strftime("%H:%M:%S")
            filtro = "activos" if solo else "todos"
            self.after(0, lambda: self.lbl_estado.config(
                text=f"✅ Mapa actualizado ({filtro}) — {hora}", fg="#059669"))
            # Si hay webview, recargarlo
            if getattr(self, "_webview_ok", False):
                self.after(200, lambda: self._wv.load_url(
                    mapa_server.url_mapa() + f"?t={int(datetime.datetime.now().timestamp())}"))
        except Exception as e:
            self.after(0, lambda: self.lbl_estado.config(
                text=f"❌ Error: {e}", fg="#DC2626"))
        finally:
            self._generando = False

    def _abrir_browser(self):
        webbrowser.open(mapa_server.url_mapa())
