# gui/screens/mapa_calor.py — v3.0 con servidor HTTP
import tkinter as tk
import os, webbrowser, threading, datetime

from mapas.mapa_calor  import crear_mapa_calor
from servicios.eventos import suscribir, desuscribir
import servicios.mapa_server as mapa_server
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, GRAY_TEXT,
    FONT_NORMAL, FONT_SMALL, make_button, make_header, PAD_X
)

_RUTA_MAPAS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


class MapaCalorScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._auto_id   = None
        self._generando = False
        mapa_server.iniciar(_RUTA_MAPAS)
        self._build()
        for ev in ("incidente_registrado", "incidente_finalizado"):
            suscribir(ev, self._on_cambio)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        for ev in ("incidente_registrado", "incidente_finalizado"):
            desuscribir(ev, self._on_cambio)
        if self._auto_id:
            self.after_cancel(self._auto_id)

    def _on_cambio(self, **kw):
        if self._auto_id:
            self.after_cancel(self._auto_id)
        self._auto_id = self.after(1000, self._generar_bg)

    def _build(self):
        make_header(self, "🔥  Mapa de Calor — Densidad de Incidentes")

        ctrl = tk.Frame(self, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner = tk.Frame(ctrl, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        make_button(inner, "🔄 Regenerar", self._generar_bg,  "info").pack(side="left", padx=4)
        make_button(inner, "🌐 Abrir en navegador", self._abrir, "neutral").pack(side="left", padx=4)

        url_lbl = tk.Label(inner, text=f"🔗 {mapa_server.url_calor()}",
                           font=("Consolas", 9), bg=WHITE, fg="#1976D2", cursor="hand2")
        url_lbl.pack(side="left", padx=12)
        url_lbl.bind("<Button-1>", lambda e: self._abrir())

        self.lbl_estado = tk.Label(inner, text="", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT)
        self.lbl_estado.pack(side="right")

        self.frame_info = tk.Frame(self, bg=WHITE,
                                   highlightbackground=GRAY_BORDER, highlightthickness=1)
        self.frame_info.pack(fill="both", expand=True, padx=PAD_X, pady=12)
        self._build_panel()
        self._generar_bg()

    def _build_panel(self):
        try:
            import tkinterweb  # type: ignore
            wv = tkinterweb.HtmlFrame(self.frame_info, messages_enabled=False)
            wv.pack(fill="both", expand=True)
            wv.load_url(mapa_server.url_calor())
            self._wv = wv
            self._wv_ok = True
            return
        except Exception:
            self._wv_ok = False

        c = tk.Frame(self.frame_info, bg=WHITE)
        c.pack(expand=True)
        tk.Label(c, text="🔥", font=("Segoe UI",48), bg=WHITE).pack(pady=(40,8))
        tk.Label(c, text="Mapa de Calor de Incidencias",
                 font=("Segoe UI",16,"bold"), bg=WHITE, fg=POLICE_BLUE).pack()
        tk.Label(c,
                 text="Se actualiza automáticamente.\nÁbrelo en el navegador — se refresca solo.",
                 font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT, justify="center").pack(pady=12)
        make_button(c, "🌐  Abrir mapa de calor", self._abrir, "danger").pack(pady=8)

    def _generar_bg(self):
        if self._generando: return
        self._generando = True
        self.lbl_estado.config(text="⏳ Generando…", fg="#D97706")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            mapa = crear_mapa_calor()
            ruta = os.path.join(_RUTA_MAPAS, "mapa_calor.html")
            mapa.save(ruta)
            hora = datetime.datetime.now().strftime("%H:%M:%S")
            self.after(0, lambda: self.lbl_estado.config(
                text=f"✅ Actualizado — {hora}", fg="#059669"))
            if getattr(self, "_wv_ok", False):
                self.after(200, lambda: self._wv.load_url(
                    mapa_server.url_calor() + f"?t={int(datetime.datetime.now().timestamp())}"))
        except Exception as e:
            self.after(0, lambda: self.lbl_estado.config(text=f"❌ {e}", fg="#DC2626"))
        finally:
            self._generando = False

    def _abrir(self):
        webbrowser.open(mapa_server.url_calor())
