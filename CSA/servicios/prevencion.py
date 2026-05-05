import pandas as pd
from servicios.historicos import listar_historicos_df

def clasificar_barrio(lat, lon):
    """Traduce coordenadas a barrios reales de Alcalá de Henares"""
    # Lógica de cercanía para Alcalá
    if 40.480 <= lat <= 40.486 and -3.370 <= lon <= -3.360:
        return "Casco Histórico"
    elif lat > 40.486:
        return "El Ensanche / Chorrillo"
    elif lon < -3.370:
        return "Reyes Católicos / La Garena"
    elif lat < 40.480 and lon > -3.360:
        return "Nueva Alcalá / Tabla Pintora"
    else:
        return "Distrito periférico / Vía Complutense"

def generar_orden_dinamica(barrio, franja, tipo):
    """Genera órdenes de servicio específicas según el tipo de delito y contexto"""
    t = str(tipo).lower()
    
    if "robo" in t or "hurto" in t:
        return (f"🚨 ALERTA DE REINCIDENCIA: Detectado patrón de hurtos en el sector {barrio}. "
                f"Se ordena despliegue de unidades de paisano en puntos de fuga comerciales. "
                f"Intensificar vigilancia en el tramo {franja} con patrullas Z en proximidad.")
    
    elif "vandalismo" in t or "pintadas" in t:
        return (f"🏢 PREVENCIÓN DE INCIVISMO: Aumento de daños al mobiliario en {barrio}. "
                f"Se recomienda patrullaje preventivo con rotativos apagados en parques y zonas escolares. "
                f"Vigilancia activa durante las {franja}.")
    
    elif "pelea" in t or "agresion" in t or "alcohol" in t:
        return (f"⚠️ ORDEN DE CONTROL DE OCIO: Alta probabilidad de altercados en {barrio}. "
                f"Posicionar unidades en zonas de restauración y puntos de reunión. "
                f"Mantener máxima visibilidad con luminosos durante la franja de las {franja}.")
    
    else:
        return (f"🛡️ PRESENCIA DISUASORIA: Actividad detectada por encima de la media en {barrio}. "
                f"Se ordena patrullaje preventivo constante en calles principales. "
                f"Objetivo: Mantener bajos los índices de {tipo} durante las {franja}.")

def obtener_analisis_predictivo():
    df = listar_historicos_df()
    if df.empty: 
        return None

    # Asignar barrio a cada registro
    df['barrio'] = df.apply(lambda x: clasificar_barrio(x['lat'], x['lon']), axis=1)
    
    # Análisis de Barrio
    barrio_top = df['barrio'].value_counts().idxmax()
    total_barrio = df['barrio'].value_counts().max()

    # Análisis de Hora
    try:
        df['fecha_dt'] = pd.to_datetime(df['fecha'])
        hora_top = df['fecha_dt'].dt.hour.value_counts().idxmax()
        franja = f"{hora_top:02d}:00 - {hora_top+1:02d}:00"
    except:
        franja = "18:00 - 22:00"

    # Análisis de Tipo
    tipo_top = df['tipo'].value_counts().idxmax()

    return {
        "barrio_critico": barrio_top,
        "total_incidentes": total_barrio,
        "hora_critica": franja,
        "tipo_frecuente": tipo_top,
        "lista_barrios": df['barrio'].value_counts().head(5).to_dict(),
        "recomendacion_ia": generar_orden_dinamica(barrio_top, franja, tipo_top)
    }