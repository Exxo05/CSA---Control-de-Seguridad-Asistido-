# servicios/prevencion.py — Análisis predictivo v2.1
# Usa tanto incidentes registrados como históricos
import pandas as pd
from servicios.listar import listar_incidentes_df
from servicios.historicos import listar_historicos_df

def _obtener_df_combinado() -> pd.DataFrame:
    """Combina incidentes registrados + históricos para el análisis."""
    df_inc  = listar_incidentes_df()
    df_hist = listar_historicos_df()

    frames = []
    if not df_inc.empty:
        # Normalizar columnas mínimas
        df_inc = df_inc[["tipo","fecha","zona"]].copy()
        df_inc.rename(columns={"zona": "barrio"}, inplace=True)
        frames.append(df_inc)

    if not df_hist.empty and "tipo" in df_hist.columns:
        df_hist2 = df_hist[["tipo","fecha"]].copy()
        df_hist2["barrio"] = df_hist.get("zona", "Sin zona")
        frames.append(df_hist2)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df["barrio"] = df["barrio"].fillna("Sin zona")
    df["tipo"]   = df["tipo"].fillna("Desconocido")
    return df


def _limpiar_tipo(tipo: str) -> str:
    import re
    t = re.sub(r'[^\w\s\-/]', '', str(tipo)).strip()
    for pfx in ["CRÍTICA —","CRITICA —","ALTA —","MEDIA —","BAJA —","MUY ALTA —"]:
        t = t.replace(pfx, "").strip()
    return t[:40] if t else "Desconocido"


def generar_orden_dinamica(barrio: str, franja: str, tipo: str) -> str:
    t = str(tipo).lower()
    if any(x in t for x in ["robo","hurto","atraco","carterista"]):
        return (
            f"🚨 ALERTA REINCIDENCIA — {barrio.upper()}\n\n"
            f"Detectado patrón de sustracciones. Se ordena despliegue de unidades "
            f"de paisano en accesos comerciales y transporte público.\n\n"
            f"• Franja crítica: {franja}\n"
            f"• Reforzar identificaciones en puntos de fuga\n"
            f"• Coordinar con comercios para instalación de dispositivos de alarma"
        )
    if any(x in t for x in ["pelea","agresion","violencia","rina"]):
        return (
            f"⚠️ CONTROL DE ORDEN PÚBLICO — {barrio.upper()}\n\n"
            f"Alta probabilidad de altercados en la franja {franja}.\n\n"
            f"• Posicionar unidades en zonas de ocio nocturno\n"
            f"• Mantener máxima visibilidad con luminosos\n"
            f"• Coordinar con Cruz Roja para asistencia médica preventiva"
        )
    if any(x in t for x in ["vandalismo","pintada","destrozo"]):
        return (
            f"🏢 PREVENCIÓN DE INCIVISMO — {barrio.upper()}\n\n"
            f"Aumento de daños a mobiliario urbano detectado.\n\n"
            f"• Patrullaje con rotativos apagados en parques y zonas escolares\n"
            f"• Vigilancia activa durante {franja}\n"
            f"• Informar a servicios municipales de limpieza"
        )
    if any(x in t for x in ["droga","narco","trapicheo"]):
        return (
            f"💊 OPERACIÓN ANTIDROGAS — {barrio.upper()}\n\n"
            f"Actividad de venta detectada recurrentemente.\n\n"
            f"• Vigilancia encubierta en puntos identificados\n"
            f"• Franja horaria crítica: {franja}\n"
            f"• Coordinar con brigada de estupefacientes"
        )
    return (
        f"🛡️ PRESENCIA DISUASORIA — {barrio.upper()}\n\n"
        f"Actividad por encima de la media. Patrullaje preventivo reforzado.\n\n"
        f"• Mantener visibilidad constante en calles principales\n"
        f"• Franja de mayor riesgo: {franja}\n"
        f"• Tipología predominante: {_limpiar_tipo(tipo)}"
    )


def obtener_analisis_predictivo() -> dict | None:
    df = _obtener_df_combinado()
    if df.empty:
        return None

    df["tipo_limpio"] = df["tipo"].apply(_limpiar_tipo)

    barrio_top   = df["barrio"].value_counts().idxmax()
    tipo_top     = df["tipo_limpio"].value_counts().idxmax()
    lista_barrios = df["barrio"].value_counts().head(8).to_dict()

    try:
        df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha_dt"])
        hora_top = df["fecha_dt"].dt.hour.value_counts().idxmax()
        franja = f"{hora_top:02d}:00 – {(hora_top+1)%24:02d}:00"
    except Exception:
        franja = "Franja no disponible"

    return {
        "barrio_critico":   barrio_top,
        "hora_critica":     franja,
        "tipo_frecuente":   tipo_top,
        "total_incidentes": len(df),
        "lista_barrios":    lista_barrios,
        "recomendacion_ia": generar_orden_dinamica(barrio_top, franja, tipo_top),
    }
