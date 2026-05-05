# gui/styles.py — Sistema de diseño CSA v2.0

# ── Paleta principal ──────────────────────────────────────────────
POLICE_BLUE       = "#0A1F44"
POLICE_BLUE_LIGHT = "#1A3A6E"
ACCENT_BLUE       = "#1976D2"
WHITE             = "#FFFFFF"
GRAY_BG           = "#F4F6F9"
GRAY_CARD         = "#FFFFFF"
GRAY_BORDER       = "#DDE3ED"
GRAY_TEXT         = "#6B7280"
DARK_TEXT         = "#1E293B"

# ── Gravedad ──────────────────────────────────────────────────────
CRITICA_BG    = "#FEE2E2"; CRITICA_FG    = "#991B1B"; CRITICA_BORDER   = "#F87171"
ALTA_BG       = "#FEF3C7"; ALTA_FG       = "#92400E"; ALTA_BORDER      = "#FCD34D"
MEDIA_BG      = "#FEF9C3"; MEDIA_FG      = "#713F12"; MEDIA_BORDER     = "#FDE047"
BAJA_BG       = "#D1FAE5"; BAJA_FG       = "#065F46"; BAJA_BORDER      = "#34D399"
FINAL_BG      = "#E0E7FF"; FINAL_FG      = "#3730A3"

# ── Botones ───────────────────────────────────────────────────────
BTN_PRIMARY   = "#1976D2"; BTN_PRIMARY_TXT  = "#FFFFFF"
BTN_SUCCESS   = "#059669"; BTN_SUCCESS_TXT  = "#FFFFFF"
BTN_DANGER    = "#DC2626"; BTN_DANGER_TXT   = "#FFFFFF"
BTN_WARNING   = "#D97706"; BTN_WARNING_TXT  = "#FFFFFF"
BTN_INFO      = "#0891B2"; BTN_INFO_TXT     = "#FFFFFF"
BTN_NEUTRAL   = "#6B7280"; BTN_NEUTRAL_TXT  = "#FFFFFF"

# ── Tipografía ────────────────────────────────────────────────────
FF = "Segoe UI"
FONT_TITLE    = (FF, 15, "bold")
FONT_SUBTITLE = (FF, 12, "bold")
FONT_NORMAL   = (FF, 10)
FONT_SMALL    = (FF, 9)
FONT_MENU     = (FF, 10, "bold")
FONT_HEADER   = (FF, 13, "bold")

# ── Layout ────────────────────────────────────────────────────────
SIDEBAR_WIDTH = 230
PAD_X         = 24
PAD_Y         = 16

# ── Helpers ───────────────────────────────────────────────────────
GRAVEDAD_COLORS = {
    "muy alta":   (CRITICA_BG, CRITICA_FG, "🔴"),
    "alta":       (ALTA_BG,    ALTA_FG,    "🟠"),
    "media":      (MEDIA_BG,   MEDIA_FG,   "🟡"),
    "baja":       (BAJA_BG,    BAJA_FG,    "🟢"),
    "finalizado": (FINAL_BG,   FINAL_FG,   "✅"),
}

def color_por_tipo(tipo: str) -> tuple:
    t = str(tipo).upper()
    if any(x in t for x in ["CRÍTICA","CRITICA","PRIORIDAD","ARMA","DISPARO"]):
        return GRAVEDAD_COLORS["muy alta"]
    if "ALTA" in t:
        return GRAVEDAD_COLORS["alta"]
    if "MEDIA" in t:
        return GRAVEDAD_COLORS["media"]
    if "FINALIZADO" in t:
        return GRAVEDAD_COLORS["finalizado"]
    return GRAVEDAD_COLORS["baja"]

def make_button(parent, text, command, style="primary", **kwargs):
    import tkinter as tk
    palettes = {
        "primary": (BTN_PRIMARY, BTN_PRIMARY_TXT),
        "success": (BTN_SUCCESS, BTN_SUCCESS_TXT),
        "danger":  (BTN_DANGER,  BTN_DANGER_TXT),
        "warning": (BTN_WARNING, BTN_WARNING_TXT),
        "info":    (BTN_INFO,    BTN_INFO_TXT),
        "neutral": (BTN_NEUTRAL, BTN_NEUTRAL_TXT),
    }
    bg, fg = palettes.get(style, palettes["primary"])
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                     font=FONT_MENU, relief="flat", cursor="hand2",
                     padx=12, pady=6, **kwargs)

def make_header(parent, text, bg=None, fg=WHITE):
    import tkinter as tk
    if bg is None:
        bg = POLICE_BLUE
    frame = tk.Frame(parent, bg=bg)
    frame.pack(fill="x")
    tk.Label(frame, text=text, font=FONT_TITLE, fg=fg, bg=bg,
             pady=14, padx=PAD_X).pack(anchor="w")
    return frame
