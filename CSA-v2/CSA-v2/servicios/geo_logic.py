# servicios/geo_logic.py — Geolocalización v4.0
import unicodedata, re

# ══════════════════════════════════════════════════════════════════
# CALLEJERO COMPLETO DE ALCALÁ DE HENARES → ZONA
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
    "carniceria": "Casco Histórico / Centro",
    "viento": "Casco Histórico / Centro",
    "barbacana": "Casco Histórico / Centro",
    "puerta de guadalajara": "Casco Histórico / Centro",
    "hostal del estudiante": "Casco Histórico / Centro",
    "era honda": "Casco Histórico / Centro",
    "era": "Casco Histórico / Centro",
    "honda": "Casco Histórico / Centro",
    "talamanca": "Casco Histórico / Centro",
    "tendillas": "Casco Histórico / Centro",
    "corral de comedias": "Casco Histórico / Centro",
    "capuchinas": "Casco Histórico / Centro",
    "libreria": "Casco Histórico / Centro",
    "convento": "Casco Histórico / Centro",

    # ── EL VAL ────────────────────────────────────────────────────
    "avenida del val": "El Val",
    "el val": "El Val",
    "rio sorbe": "El Val",
    "sorbe": "El Val",
    "rio aliste": "El Val",
    "aliste": "El Val",
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
    "pisuerga": "El Val",
    "rio duero": "El Val",
    "duero": "El Val",
    "rio eresma": "El Val",
    "eresma": "El Val",
    "rio tormes": "El Val",
    "tormes": "El Val",
    "rio manzanares": "El Val",
    "rio jarama": "El Val",
    "jarama": "El Val",
    "rio guadarrama": "El Val",
    "guadarrama": "El Val",
    "rio tajuna": "El Val",
    "tajuna": "El Val",
    "zamora": "El Val",
    "palencia": "El Val",
    "leon": "El Val",
    "burgos": "El Val",
    "logrono": "El Val",
    "miranda": "El Val",
    "aranda": "El Val",

    # ── LA GARENA ─────────────────────────────────────────────────
    "juan carlos i": "La Garena",
    "garena": "La Garena",
    "fausto elhuyar": "La Garena",
    "elhuyar": "La Garena",
    "agustin de betancourt": "La Garena",
    "betancourt": "La Garena",
    "rosa de luxembourg": "La Garena",
    "marie curie": "La Garena",
    "curie": "La Garena",
    "otto von guericke": "La Garena",
    "guericke": "La Garena",
    "blas de otero": "La Garena",
    "jardinillos": "La Garena",
    "hipercor": "La Garena",
    "multicentro": "La Garena",
    "arturo soria": "La Garena",
    "isaac peral": "La Garena",
    "peral": "La Garena",
    "torres quevedo": "La Garena",
    "severo ochoa": "La Garena",
    "ochoa": "La Garena",
    "alejandro malaspina": "La Garena",
    "malaspina": "La Garena",
    "jorge juan": "La Garena",
    "antonio de ulloa": "La Garena",
    "ulloa": "La Garena",
    "juan de la cierva": "La Garena",
    "cierva": "La Garena",
    "jose echegaray": "La Garena",
    "echegaray": "La Garena",
    "pedro duque": "La Garena",
    "monturiol": "La Garena",
    "avenida de los inventores": "La Garena",
    "inventores": "La Garena",
    "avenida del ejercito": "La Garena",
    "ejercito": "La Garena",

    # ── CHORRILLO / ENSANCHE ──────────────────────────────────────
    "juan de austria": "Chorrillo / Ensanche",
    "torrelaguna": "Chorrillo / Ensanche",
    "san ignacio": "Chorrillo / Ensanche",
    "valles": "Chorrillo / Ensanche",
    "san herculano": "Chorrillo / Ensanche",
    "lepanto": "Chorrillo / Ensanche",
    "don quijote": "Chorrillo / Ensanche",
    "quijote": "Chorrillo / Ensanche",
    "santa catalina": "Chorrillo / Ensanche",
    "boadilla": "Chorrillo / Ensanche",
    "chorrillo": "Chorrillo / Ensanche",
    "nuevo alcarreno": "Chorrillo / Ensanche",
    "camino de los afligidos": "Chorrillo / Ensanche",
    "afligidos": "Chorrillo / Ensanche",
    "juan de lanuza": "Chorrillo / Ensanche",
    "lanuza": "Chorrillo / Ensanche",
    "juan bravo": "Chorrillo / Ensanche",
    "pedro de mendoza": "Chorrillo / Ensanche",
    "mendoza": "Chorrillo / Ensanche",
    "padilla": "Chorrillo / Ensanche",
    "comunidades": "Chorrillo / Ensanche",
    "maldonado": "Chorrillo / Ensanche",
    "julian besteiro": "Chorrillo / Ensanche",
    "besteiro": "Chorrillo / Ensanche",
    "dos de mayo": "Chorrillo / Ensanche",
    "francisco de quevedo": "Chorrillo / Ensanche",
    "isabel de valois": "Chorrillo / Ensanche",
    "valois": "Chorrillo / Ensanche",
    "prolongacion": "Chorrillo / Ensanche",

    # ── REYES CATÓLICOS ───────────────────────────────────────────
    "reyes catolicos": "Reyes Católicos",
    "isabel la catolica": "Reyes Católicos",
    "nunez de guzman": "Reyes Católicos",
    "guzman": "Reyes Católicos",
    "puerta de madrid": "Reyes Católicos",
    "brihuega": "Reyes Católicos",
    "nueva los angeles": "Reyes Católicos",
    "los angeles": "Reyes Católicos",
    "fernando el catolico": "Reyes Católicos",
    "dos castillas": "Reyes Católicos",
    "princesa": "Reyes Católicos",
    "duque de lerma": "Reyes Católicos",
    "lerma": "Reyes Católicos",
    "condesa de buendia": "Reyes Católicos",
    "buendia": "Reyes Católicos",
    "marques de santillana": "Reyes Católicos",
    "santillana": "Reyes Católicos",
    "cardenal mendoza": "Reyes Católicos",
    "infantes": "Reyes Católicos",
    "velazquez": "Reyes Católicos",
    "goya": "Reyes Católicos",
    "murillo": "Reyes Católicos",
    "zurbaran": "Reyes Católicos",
    "ribera": "Reyes Católicos",
    "el greco": "Reyes Católicos",
    "greco": "Reyes Católicos",
    "sofonias": "Reyes Católicos",
    "naranjo": "Reyes Católicos",
    "pastrana": "Reyes Católicos",
    "sigüenza": "Reyes Católicos",
    "siguenza": "Reyes Católicos",

    # ── ESPARTALES ────────────────────────────────────────────────
    "espartales": "Espartales",
    "benito perez galdos": "Espartales",
    "galdos": "Espartales",
    "garcia lorca": "Espartales",
    "lorca": "Espartales",
    "quevedo": "Espartales",
    "juan ramon jimenez": "Espartales",
    "jimenez": "Espartales",
    "azorin": "Espartales",
    "campoamor": "Espartales",
    "rosalia de castro": "Espartales",
    "becquer": "Espartales",
    "pico del vizmaya": "Espartales",
    "vizmaya": "Espartales",
    "alfonso vi": "Espartales",
    "jose zorrilla": "Espartales",
    "zorrilla": "Espartales",
    "lope de vega": "Espartales",
    "calderon de la barca": "Espartales",
    "calderon": "Espartales",
    "tirso de molina": "Espartales",
    "tirso": "Espartales",
    "jorge manrique": "Espartales",
    "manrique": "Espartales",
    "jorge guillen": "Espartales",
    "guillen": "Espartales",
    "pedro salinas": "Espartales",
    "salinas": "Espartales",
    "rafael alberti": "Espartales",
    "alberti": "Espartales",
    "antonio machado": "Espartales",
    "machado": "Espartales",
    "miguel hernandez": "Espartales",
    "emilia pardo bazan": "Espartales",
    "pardo bazan": "Espartales",

    # ── NUEVA ALCALÁ ──────────────────────────────────────────────
    "nueva alcala": "Nueva Alcalá",
    "tabla pintora": "Nueva Alcalá",
    "pintora": "Nueva Alcalá",
    "vallebermejo": "Nueva Alcalá",
    "via complutense": "Nueva Alcalá",
    "avenida complutense": "Nueva Alcalá",
    "complutense": "Nueva Alcalá",
    "camino viejo": "Nueva Alcalá",
    "el encin": "Nueva Alcalá",
    "encin": "Nueva Alcalá",
    "senda de maria": "Nueva Alcalá",
    "prado de los pinos": "Nueva Alcalá",
    "huerta del obispo": "Nueva Alcalá",
    "los olivos": "Nueva Alcalá",
    "los pinos": "Nueva Alcalá",
    "las encinas": "Nueva Alcalá",

    # ── CIRCUNVALACIÓN / POLÍGONOS ────────────────────────────────
    "circunvalacion": "Circunvalación / Periférico",
    "autovia": "Circunvalación / Periférico",
    "a-2": "Circunvalación / Periférico",
    "r-2": "Circunvalación / Periférico",
    "poligono": "Circunvalación / Periférico",
    "cobo calleja": "Circunvalación / Periférico",
    "camino del juncal": "Circunvalación / Periférico",
    "juncal": "Circunvalación / Periférico",
    "ctra guadalajara": "Circunvalación / Periférico",
    "carretera guadalajara": "Circunvalación / Periférico",
    "ctra madrid": "Circunvalación / Periférico",
    "carretera madrid": "Circunvalación / Periférico",
    "ctra daganzo": "Circunvalación / Periférico",
    "ctra meco": "Circunvalación / Periférico",
    "ronda": "Circunvalación / Periférico",
    "industrial": "Circunvalación / Periférico",

    # ── MUNICIPIOS CERCANOS ───────────────────────────────────────
    "meco": "Municipio: Meco",
    "daganzo": "Municipio: Daganzo",
    "alovera": "Municipio: Alovera",
    "azuqueca": "Municipio: Azuqueca de Henares",
    "guadalajara": "Municipio: Guadalajara",
    "torrejon": "Municipio: Torrejón de Ardoz",
    "torrejón": "Municipio: Torrejón de Ardoz",
    "paracuellos": "Municipio: Paracuellos del Jarama",
    "santos de la humosa": "Municipio: Los Santos de la Humosa",
    "loeches": "Municipio: Loeches",
    "morata": "Municipio: Morata de Tajuña",
    "campo real": "Municipio: Campo Real",
    "valdilecha": "Municipio: Valdilecha",
}

COORDS_ZONAS = {
    "Casco Histórico / Centro":       (40.4819, -3.3635),
    "El Val":                          (40.4780, -3.3440),
    "La Garena":                       (40.4824, -3.3892),
    "Chorrillo / Ensanche":            (40.4930, -3.3590),
    "Reyes Católicos":                 (40.4760, -3.3760),
    "Espartales":                      (40.5010, -3.3480),
    "Nueva Alcalá":                    (40.4740, -3.3520),
    "Circunvalación / Periférico":     (40.4850, -3.3700),
    "Municipio: Meco":                 (40.5600, -3.3400),
    "Municipio: Daganzo":              (40.5300, -3.4000),
    "Municipio: Alovera":              (40.5900, -3.2700),
    "Municipio: Azuqueca de Henares":  (40.5700, -3.2600),
    "Municipio: Guadalajara":          (40.6280, -3.1640),
    "Municipio: Torrejón de Ardoz":    (40.4590, -3.4670),
    "Municipio: Paracuellos del Jarama": (40.5100, -3.5200),
    "Municipio: Los Santos de la Humosa": (40.4200, -3.2500),
    "Municipio: Morata de Tajuña":     (40.2280, -3.4500),
    "Municipio: Campo Real":           (40.3270, -3.3130),
    "Zona desconocida":                (40.4839, -3.3644),
}

# Cache de geocodificación
_cache: dict = {}


def _norm(texto: str) -> str:
    t = texto.lower().strip()
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', t)


def _quitar_prefijos(texto: str) -> str:
    """Elimina 'Calle de la', 'Av. de', etc. para quedarse con el nombre."""
    prefijos = [
        r'^calle\s+(de\s+la\s+|del\s+|de\s+los\s+|de\s+las\s+|de\s+|del\s+)?',
        r'^avenida\s+(de\s+la\s+|del\s+|de\s+los\s+|de\s+las\s+|de\s+)?',
        r'^av\.\s+', r'^avda\.\s+', r'^c/\s*', r'^cl\.\s+',
        r'^paseo\s+(de\s+la\s+|del\s+|de\s+)?',
        r'^plaza\s+(de\s+la\s+|del\s+|de\s+los\s+|de\s+)?',
        r'^camino\s+(de\s+la\s+|del\s+|de\s+)?',
        r'^carretera\s+(de\s+la\s+|del\s+|a\s+)?',
        r'^ronda\s+(de\s+)?',
        r'^urbanizacion\s+',
    ]
    t = texto
    for p in prefijos:
        t = re.sub(p, '', t, flags=re.IGNORECASE).strip()
    return t


def _variantes(direccion: str) -> list[str]:
    """Genera variantes de búsqueda para Nominatim."""
    d = direccion.strip()
    # Separar número si lo hay al final
    m = re.match(r'^(.+?)\s*,?\s*(\d+)\s*$', d)
    nombre = m.group(1).strip() if m else d
    numero = m.group(2) if m else ""

    nombre_limpio = _quitar_prefijos(nombre)

    variantes = []
    base = "Alcalá de Henares, Madrid, España"

    # Variante 1: completa con número
    if numero:
        variantes.append(f"{nombre} {numero}, {base}")
    # Variante 2: nombre completo sin número
    variantes.append(f"{nombre}, {base}")
    # Variante 3: nombre sin prefijos
    if nombre_limpio != nombre:
        variantes.append(f"{nombre_limpio}, {base}")
        if numero:
            variantes.append(f"{nombre_limpio} {numero}, {base}")
    # Variante 4: solo palabras clave (quitar artículos)
    sin_art = re.sub(r'\b(de|del|la|las|el|los|un|una)\b', '', nombre_limpio,
                     flags=re.IGNORECASE)
    sin_art = re.sub(r'\s+', ' ', sin_art).strip()
    if sin_art and sin_art != nombre_limpio:
        variantes.append(f"{sin_art}, {base}")

    return list(dict.fromkeys(variantes))  # deduplicar manteniendo orden


def obtener_zona_por_direccion(direccion: str) -> str:
    if not direccion or len(direccion.strip()) < 3:
        return "Zona desconocida"

    d = _norm(direccion)
    d_sin_prefijo = _norm(_quitar_prefijos(d))

    # Buscar en base local — primero frases largas, luego cortas
    for kw, zona in sorted(CALLES_A_ZONA.items(), key=lambda x: -len(x[0])):
        kw_n = _norm(kw)
        if kw_n in d or kw_n in d_sin_prefijo:
            return zona

    return "Zona desconocida"


def geocodificar_direccion(direccion: str):
    """
    Devuelve (lat, lon, zona). Delega al geocodificador multi-motor.
    """
    try:
        from servicios.geocodificador import geocodificar_direccion as _gd
        return _gd(direccion)
    except Exception:
        zona = obtener_zona_por_direccion(direccion)
        return None, None, zona


def _coords_a_zona(lat: float, lon: float) -> str:
    centro = (40.4839, -3.3644)
    dist_centro = ((lat - centro[0])**2 + (lon - centro[1])**2)**0.5

    zonas_internas = {k: v for k, v in COORDS_ZONAS.items()
                      if not k.startswith("Municipio") and k != "Zona desconocida"}
    zonas_ext = {k: v for k, v in COORDS_ZONAS.items() if k.startswith("Municipio")}

    pool = zonas_ext if dist_centro > 0.15 else zonas_internas
    mejor, dist_min = "Zona desconocida", float("inf")
    for zona, (zlat, zlon) in pool.items():
        d = ((lat - zlat)**2 + (lon - zlon)**2)**0.5
        if d < dist_min:
            dist_min, mejor = d, zona
    return mejor


def obtener_coords_zona(zona: str) -> tuple:
    return COORDS_ZONAS.get(zona, COORDS_ZONAS["Zona desconocida"])


def listar_zonas() -> list:
    return [z for z in COORDS_ZONAS if not z.startswith("Zona")]


def clasificar_tipo_incidente(texto: str) -> str:
    from servicios.clasificador import ClasificadorIncidentes
    r = ClasificadorIncidentes().procesar_descripcion(texto)
    return {"muy alta": "CRÍTICA", "alta": "ALTA",
            "media": "MEDIA", "baja": "BAJA"}.get(r["gravedad"],"BAJA") + f" — {r['tipo']}"
