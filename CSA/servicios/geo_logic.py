# servicios/geo_logic.py — Geolocalización v2.0 para Alcalá de Henares

# ── Mapa de zonas con palabras clave ─────────────────────────────
ZONAS_KEYWORDS = {
    "Casco Histórico / Centro": [
        "mayor","libreros","plaza cervantes","ayuntamiento","tinte","vitoria",
        "escritorios","academia","palacio","arzobispal","colegio mayor",
        "magistral","santa maria","cervantes","santiago","trinidad","san bernardo",
        "trinidad","bernaditas","colegios","panaderos","imagen"
    ],
    "El Val": [
        "rio sorbe","rio aliste","rio tajo","avenida del val","valladolid",
        "laredo","avila","salamanca","segovia","rio pisuerga","soria",
        "tordesillas","medina del campo","el val"
    ],
    "La Garena": [
        "juan carlos i","arturo soria","garena","fausto elhuyar","agustin de betancourt",
        "rosa de luxembourg","marie curie","otto von guericke","blas de otero",
        "jardinillos","hipercor","multicentro"
    ],
    "Chorrillo / Ensanche": [
        "juan de austria","torrelaguna","san ignacio","valles","san herculano",
        "lepanto","don quijote","santa catalina","boadilla","chorrillo",
        "camino de los afligidos","nuevo alcarreno"
    ],
    "Reyes Católicos": [
        "reyes catolicos","isabel la catolica","nunez de guzman","puerta de madrid",
        "brihuega","nueva los angeles","fernando el catolicol","dos castillas",
        "princesa","duque de lerma"
    ],
    "Espartales": [
        "benito perez galdos","alfonso vi","pico del vizmaya","becquer",
        "espartales","garcia lorca","quevedo","juan ramon jimenez","azorin",
        "campoamor","rosalia de castro"
    ],
    "Nueva Alcalá": [
        "nueva alcalá","tabla pintora","vallebermejo","vía complutense",
        "avenida complutense","camino viejo"
    ],
    "Circunvalación / Periférico": [
        "circunvalacion","ronda","autovia","a-2","r-2","periferico",
        "poligono industrial","cobo calleja"
    ],
}

# ── Coordenadas representativas de cada zona ─────────────────────
COORDS_ZONAS = {
    "Casco Histórico / Centro":    (40.4819, -3.3635),
    "El Val":                       (40.4800, -3.3450),
    "La Garena":                    (40.4824, -3.3892),
    "Chorrillo / Ensanche":         (40.4930, -3.3590),
    "Reyes Católicos":              (40.4780, -3.3750),
    "Espartales":                   (40.5050, -3.3500),
    "Nueva Alcalá":                 (40.4760, -3.3550),
    "Circunvalación / Periférico":  (40.4850, -3.3700),
    "Zona desconocida":             (40.4839, -3.3644),  # centro de Alcalá
}


def obtener_zona_por_direccion(direccion: str) -> str:
    """Devuelve el nombre de zona según palabras clave en la dirección."""
    d = direccion.lower()
    # Eliminar tildes para comparación más robusta
    import unicodedata
    d = ''.join(
        c for c in unicodedata.normalize('NFD', d)
        if unicodedata.category(c) != 'Mn'
    )
    for zona, keywords in ZONAS_KEYWORDS.items():
        if any(kw in d for kw in keywords):
            return zona
    return "Zona desconocida"


def obtener_coords_zona(zona: str) -> tuple:
    """Devuelve (lat, lon) para una zona. Útil para el mapa."""
    return COORDS_ZONAS.get(zona, COORDS_ZONAS["Zona desconocida"])


def clasificar_tipo_incidente(texto: str) -> str:
    """Clasificación rápida para compatibilidad con código antiguo."""
    from servicios.clasificador import ClasificadorIncidentes
    clf = ClasificadorIncidentes()
    resultado = clf.procesar_descripcion(texto)
    gravedad = resultado["gravedad"]
    tipo     = resultado["tipo"]
    mapa = {
        "muy alta": f"CRÍTICA — {tipo}",
        "alta":     f"ALTA — {tipo}",
        "media":    f"MEDIA — {tipo}",
        "baja":     f"BAJA — {tipo}",
    }
    return mapa.get(gravedad, tipo)


def listar_zonas() -> list:
    """Devuelve la lista de zonas conocidas."""
    return list(ZONAS_KEYWORDS.keys())
