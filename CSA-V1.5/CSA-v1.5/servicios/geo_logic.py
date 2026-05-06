# servicios/geo_logic.py — Geolocalización v3.0 — Alcalá de Henares completo
import unicodedata
import re
import time

# ══════════════════════════════════════════════════════════════════
# BASE DE DATOS COMPLETA DE CALLES DE ALCALÁ DE HENARES
# Fuente: callejero municipal + zonas policiales reales
# ══════════════════════════════════════════════════════════════════

CALLES_A_ZONA = {
    # ── CASCO HISTÓRICO / CENTRO ──────────────────────────────────
    "mayor": "Casco Histórico / Centro",
    "libreros": "Casco Histórico / Centro",
    "tinte": "Casco Histórico / Centro",
    "cervantes": "Casco Histórico / Centro",
    "santa maria": "Casco Histórico / Centro",
    "santiago": "Casco Histórico / Centro",
    "trinidad": "Casco Histórico / Centro",
    "bernaditas": "Casco Histórico / Centro",
    "panaderos": "Casco Histórico / Centro",
    "imagen": "Casco Histórico / Centro",
    "ayuntamiento": "Casco Histórico / Centro",
    "palacio": "Casco Histórico / Centro",
    "arzobispal": "Casco Histórico / Centro",
    "colegios": "Casco Histórico / Centro",
    "escritorios": "Casco Histórico / Centro",
    "plaza cervantes": "Casco Histórico / Centro",
    "academia": "Casco Histórico / Centro",
    "magistral": "Casco Histórico / Centro",
    "san bernardo": "Casco Histórico / Centro",
    "vitoria": "Casco Histórico / Centro",
    "cardenal cisneros": "Casco Histórico / Centro",
    "santa ursula": "Casco Histórico / Centro",
    "teatro": "Casco Histórico / Centro",
    "plaza de los irlandeses": "Casco Histórico / Centro",
    "plaza del val": "Casco Histórico / Centro",
    "arcipreste de hita": "Casco Histórico / Centro",
    "empecinado": "Casco Histórico / Centro",
    "san juan": "Casco Histórico / Centro",
    "san pedro": "Casco Histórico / Centro",
    "san francisco": "Casco Histórico / Centro",
    "santa clara": "Casco Histórico / Centro",
    "san felix": "Casco Histórico / Centro",
    "postigo": "Casco Histórico / Centro",
    "beatas": "Casco Histórico / Centro",
    "buzon": "Casco Histórico / Centro",
    "bodeguillas": "Casco Histórico / Centro",
    "obra pia": "Casco Histórico / Centro",
    "colegio del rey": "Casco Histórico / Centro",
    "nueva": "Casco Histórico / Centro",
    "carniceria": "Casco Histórico / Centro",
    "viento": "Casco Histórico / Centro",
    "cal": "Casco Histórico / Centro",
    "barbacana": "Casco Histórico / Centro",
    "puerta de guadalajara": "Casco Histórico / Centro",
    "hostal del estudiante": "Casco Histórico / Centro",

    # ── EL VAL ────────────────────────────────────────────────────
    "avenida del val": "El Val",
    "el val": "El Val",
    "rio sorbe": "El Val",
    "rio aliste": "El Val",
    "rio tajo": "El Val",
    "valladolid": "El Val",
    "laredo": "El Val",
    "avila": "El Val",
    "salamanca": "El Val",
    "segovia": "El Val",
    "soria": "El Val",
    "tordesillas": "El Val",
    "medina del campo": "El Val",
    "rio pisuerga": "El Val",
    "rio duero": "El Val",
    "rio esgueva": "El Val",
    "rio eresma": "El Val",
    "rio tormes": "El Val",
    "rio manzanares": "El Val",
    "rio jarama": "El Val",
    "rio guadarrama": "El Val",
    "rio tajuna": "El Val",
    "zamora": "El Val",
    "palencia": "El Val",
    "leon": "El Val",
    "burgos": "El Val",
    "logrono": "El Val",

    # ── LA GARENA ─────────────────────────────────────────────────
    "juan carlos i": "La Garena",
    "garena": "La Garena",
    "fausto elhuyar": "La Garena",
    "agustin de betancourt": "La Garena",
    "rosa de luxembourg": "La Garena",
    "marie curie": "La Garena",
    "otto von guericke": "La Garena",
    "blas de otero": "La Garena",
    "jardinillos": "La Garena",
    "hipercor": "La Garena",
    "multicentro": "La Garena",
    "arturo soria": "La Garena",
    "isaac peral": "La Garena",
    "torres quevedo": "La Garena",
    "severo ochoa": "La Garena",
    "alejandro malaspina": "La Garena",
    "jorge juan": "La Garena",
    "antonio de ulloa": "La Garena",
    "juan de la cierva": "La Garena",
    "jose echegaray": "La Garena",
    "pedro duque": "La Garena",
    "monturiol": "La Garena",
    "leonardo torres quevedo": "La Garena",
    "avenida de los inventores": "La Garena",
    "avenida del ejercito": "La Garena",

    # ── CHORRILLO / ENSANCHE ──────────────────────────────────────
    "juan de austria": "Chorrillo / Ensanche",
    "torrelaguna": "Chorrillo / Ensanche",
    "san ignacio": "Chorrillo / Ensanche",
    "valles": "Chorrillo / Ensanche",
    "san herculano": "Chorrillo / Ensanche",
    "lepanto": "Chorrillo / Ensanche",
    "don quijote": "Chorrillo / Ensanche",
    "santa catalina": "Chorrillo / Ensanche",
    "boadilla": "Chorrillo / Ensanche",
    "chorrillo": "Chorrillo / Ensanche",
    "nuevo alcarreno": "Chorrillo / Ensanche",
    "camino de los afligidos": "Chorrillo / Ensanche",
    "juan de lanuza": "Chorrillo / Ensanche",
    "juan bravo": "Chorrillo / Ensanche",
    "pedro de mendoza": "Chorrillo / Ensanche",
    "padilla": "Chorrillo / Ensanche",
    "comunidades": "Chorrillo / Ensanche",
    "maldonado": "Chorrillo / Ensanche",
    "julian besteiro": "Chorrillo / Ensanche",
    "america": "Chorrillo / Ensanche",
    "prolongacion": "Chorrillo / Ensanche",
    "dos de mayo": "Chorrillo / Ensanche",
    "alcala verde": "Chorrillo / Ensanche",
    "francisco de quevedo": "Chorrillo / Ensanche",
    "isabel de valois": "Chorrillo / Ensanche",

    # ── REYES CATÓLICOS ───────────────────────────────────────────
    "reyes catolicos": "Reyes Católicos",
    "isabel la catolica": "Reyes Católicos",
    "nunez de guzman": "Reyes Católicos",
    "puerta de madrid": "Reyes Católicos",
    "brihuega": "Reyes Católicos",
    "nueva los angeles": "Reyes Católicos",
    "fernando el catolico": "Reyes Católicos",
    "dos castillas": "Reyes Católicos",
    "princesa": "Reyes Católicos",
    "duque de lerma": "Reyes Católicos",
    "condesa de buendia": "Reyes Católicos",
    "marques de santillana": "Reyes Católicos",
    "juan de austria": "Reyes Católicos",
    "cardenal mendoza": "Reyes Católicos",
    "infantes": "Reyes Católicos",
    "velazquez": "Reyes Católicos",
    "goya": "Reyes Católicos",
    "murillo": "Reyes Católicos",
    "zurbaran": "Reyes Católicos",
    "ribera": "Reyes Católicos",
    "el greco": "Reyes Católicos",
    "sofonias": "Reyes Católicos",
    "naranjo": "Reyes Católicos",

    # ── ESPARTALES ────────────────────────────────────────────────
    "espartales": "Espartales",
    "benito perez galdos": "Espartales",
    "garcia lorca": "Espartales",
    "quevedo": "Espartales",
    "juan ramon jimenez": "Espartales",
    "azorin": "Espartales",
    "campoamor": "Espartales",
    "rosalia de castro": "Espartales",
    "becquer": "Espartales",
    "pico del vizmaya": "Espartales",
    "alfonso vi": "Espartales",
    "jose zorrilla": "Espartales",
    "lope de vega": "Espartales",
    "calderon de la barca": "Espartales",
    "tirso de molina": "Espartales",
    "jorge manrique": "Espartales",
    "jorge guillen": "Espartales",
    "pedro salinas": "Espartales",
    "rafael alberti": "Espartales",
    "miguel hernandez": "Espartales",
    "antonio machado": "Espartales",
    "juan antonio zunzunegui": "Espartales",
    "concha espina": "Espartales",
    "emilia pardo bazan": "Espartales",
    "fernandez de los rios": "Espartales",

    # ── NUEVA ALCALÁ ──────────────────────────────────────────────
    "nueva alcala": "Nueva Alcalá",
    "tabla pintora": "Nueva Alcalá",
    "vallebermejo": "Nueva Alcalá",
    "via complutense": "Nueva Alcalá",
    "avenida complutense": "Nueva Alcalá",
    "camino viejo": "Nueva Alcalá",
    "el encin": "Nueva Alcalá",
    "senda de maria": "Nueva Alcalá",
    "prado de los pinos": "Nueva Alcalá",
    "huerta del obispo": "Nueva Alcalá",
    "los olivos": "Nueva Alcalá",
    "los pinos": "Nueva Alcalá",
    "las encinas": "Nueva Alcalá",
    "prolongacion de la via": "Nueva Alcalá",

    # ── CIRCUNVALACIÓN / POLÍGONOS ────────────────────────────────
    "circunvalacion": "Circunvalación / Periférico",
    "autovia": "Circunvalación / Periférico",
    "a-2": "Circunvalación / Periférico",
    "r-2": "Circunvalación / Periférico",
    "poligono": "Circunvalación / Periférico",
    "cobo calleja": "Circunvalación / Periférico",
    "camino del juncal": "Circunvalación / Periférico",
    "senda del estudiante": "Circunvalación / Periférico",
    "camino de la fuente": "Circunvalación / Periférico",
    "ctra guadalajara": "Circunvalación / Periférico",
    "carretera guadalajara": "Circunvalación / Periférico",
    "ctra madrid": "Circunvalación / Periférico",
    "carretera madrid": "Circunvalación / Periférico",
    "ctra daganzo": "Circunvalación / Periférico",
    "ctra meco": "Circunvalación / Periférico",
    "ronda": "Circunvalación / Periférico",
    "industrial": "Circunvalación / Periférico",

    # ── PUEBLOS / MUNICIPIOS CERCANOS (para alertas fuera de núcleo)
    "meco": "Municipio: Meco",
    "daganzo": "Municipio: Daganzo",
    "alovera": "Municipio: Alovera",
    "azuqueca": "Municipio: Azuqueca de Henares",
    "guadalajara": "Municipio: Guadalajara",
    "torrejón": "Municipio: Torrejón de Ardoz",
    "torrejon": "Municipio: Torrejón de Ardoz",
    "paracuellos": "Municipio: Paracuellos del Jarama",
    "santos de la humosa": "Municipio: Los Santos de la Humosa",
    "loeches": "Municipio: Loeches",
    "morata": "Municipio: Morata de Tajuña",
    "morata de tajuna": "Municipio: Morata de Tajuña",
    "campo real": "Municipio: Campo Real",
    "valdilecha": "Municipio: Valdilecha",
}

# ── Coordenadas por zona ──────────────────────────────────────────
COORDS_ZONAS = {
    "Casco Histórico / Centro":    (40.4819, -3.3635),
    "El Val":                       (40.4780, -3.3440),
    "La Garena":                    (40.4824, -3.3892),
    "Chorrillo / Ensanche":         (40.4930, -3.3590),
    "Reyes Católicos":              (40.4760, -3.3760),
    "Espartales":                   (40.5010, -3.3480),
    "Nueva Alcalá":                 (40.4740, -3.3520),
    "Circunvalación / Periférico":  (40.4850, -3.3700),
    "Municipio: Meco":              (40.5600, -3.3400),
    "Municipio: Daganzo":           (40.5300, -3.4000),
    "Municipio: Alovera":           (40.5900, -3.2700),
    "Municipio: Azuqueca de Henares": (40.5700, -3.2600),
    "Municipio: Guadalajara":       (40.6280, -3.1640),
    "Municipio: Torrejón de Ardoz": (40.4590, -3.4670),
    "Municipio: Paracuellos del Jarama": (40.5100, -3.5200),
    "Municipio: Los Santos de la Humosa": (40.4200, -3.2500),
    "Municipio: Morata de Tajuña": (40.2280, -3.4500),
    "Municipio: Campo Real":       (40.3270, -3.3130),
    "Zona desconocida":             (40.4839, -3.3644),
}

# Cache de geocodificación para no repetir peticiones
_geocodificacion_cache: dict = {}

def _normalizar(texto: str) -> str:
    """Quita tildes, minúsculas y normaliza espacios."""
    t = texto.lower().strip()
    t = ''.join(
        c for c in unicodedata.normalize('NFD', t)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', t)


def obtener_zona_por_direccion(direccion: str) -> str:
    """
    Detecta la zona de una dirección en dos pasos:
    1. Búsqueda en base de datos local de calles (instantánea)
    2. Si no encuentra, intenta geocodificación real con Nominatim
    """
    if not direccion or len(direccion.strip()) < 3:
        return "Zona desconocida"

    d = _normalizar(direccion)

    # ── Paso 1: base de datos local ───────────────────────────────
    # Ordenar por longitud descendente para que las frases largas tengan prioridad
    for kw, zona in sorted(CALLES_A_ZONA.items(), key=lambda x: -len(x[0])):
        if _normalizar(kw) in d:
            return zona

    # ── Paso 2: geocodificación Nominatim (solo si hay conexión) ──
    zona_geo = _geocodificar_nominatim(direccion)
    if zona_geo:
        return zona_geo

    return "Zona desconocida"


def _geocodificar_nominatim(direccion: str) -> str | None:
    """
    Llama a Nominatim para obtener coordenadas y las convierte a zona.
    Con caché para no repetir peticiones.
    """
    key = _normalizar(direccion)
    if key in _geocodificacion_cache:
        return _geocodificacion_cache[key]

    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError

        geolocator = Nominatim(user_agent="CSA_policia_alcala_v2", timeout=3)
        query = f"{direccion}, Alcalá de Henares, Madrid, España"
        location = geolocator.geocode(query, language="es")

        if location:
            zona = _coords_a_zona(location.latitude, location.longitude)
            _geocodificacion_cache[key] = zona
            return zona

    except Exception:
        pass  # Sin conexión o error → devuelve None

    _geocodificacion_cache[key] = None
    return None


def _coords_a_zona(lat: float, lon: float) -> str:
    """
    Dadas coordenadas, devuelve la zona más cercana por distancia euclidiana.
    Descarta municipios externos a menos que estén muy lejos de Alcalá.
    """
    # Si las coords están claramente fuera de Alcalá, buscar municipio
    centro_alcala = (40.4839, -3.3644)
    dist_alcala = ((lat - centro_alcala[0])**2 + (lon - centro_alcala[1])**2)**0.5

    zonas_internas = {k: v for k, v in COORDS_ZONAS.items()
                      if not k.startswith("Municipio") and k != "Zona desconocida"}
    zonas_municipios = {k: v for k, v in COORDS_ZONAS.items()
                        if k.startswith("Municipio")}

    if dist_alcala > 0.15:  # ~15km fuera del núcleo
        pool = {**zonas_municipios, "Zona desconocida": COORDS_ZONAS["Zona desconocida"]}
    else:
        pool = zonas_internas

    mejor, dist_min = "Zona desconocida", float("inf")
    for zona, (zlat, zlon) in pool.items():
        d = ((lat - zlat)**2 + (lon - zlon)**2)**0.5
        if d < dist_min:
            dist_min = d
            mejor = zona
    return mejor


def obtener_coords_zona(zona: str) -> tuple:
    return COORDS_ZONAS.get(zona, COORDS_ZONAS["Zona desconocida"])


def listar_zonas() -> list:
    return [z for z in COORDS_ZONAS.keys()
            if z not in ("Zona desconocida",)]


def clasificar_tipo_incidente(texto: str) -> str:
    """Compatibilidad con código antiguo."""
    from servicios.clasificador import ClasificadorIncidentes
    r = ClasificadorIncidentes().procesar_descripcion(texto)
    mapa = {"muy alta": "CRÍTICA", "alta": "ALTA", "media": "MEDIA", "baja": "BAJA"}
    return f"{mapa.get(r['gravedad'],'BAJA')} — {r['tipo']}"
