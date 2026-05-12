# servicios/geocodificador.py — Geocodificador v5.0
# Google Maps (primario) → Photon/HERE (fallback) → base local (último recurso)
import re, unicodedata, os, json
from urllib import request, parse, error as urlerr

# ─── Cache en memoria ──────────────────────────────────────────────
_cache: dict = {}

# ─── Prefijos de tipo de vía a eliminar antes de buscar ───────────
_PREFIJOS = re.compile(
    r'^(calle|c/|c\.)\s+(de\s+la\s+|del\s+|de\s+los\s+|de\s+las\s+|de\s+|del\s+)?'
    r'|^(avenida|av\.|avda\.)\s+(de\s+la\s+|del\s+|de\s+|de\s+los\s+|de\s+las\s+)?'
    r'|^(paseo|pso\.)\s+(de\s+la\s+|del\s+|de\s+)?'
    r'|^(plaza|plz?\.)\s+(de\s+la\s+|del\s+|de\s+los\s+|de\s+)?'
    r'|^(camino|cno\.)\s+(de\s+la\s+|del\s+|de\s+)?'
    r'|^(carretera|ctra\.)\s+(de\s+|a\s+)?'
    r'|^(ronda|urbanizacion|urb\.)\s+',
    re.IGNORECASE
)

def _limpiar(texto: str) -> str:
    t = texto.lower().strip()
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', t)

def _sin_prefijo(d: str) -> str:
    return _PREFIJOS.sub('', d).strip()

def _separar_numero(d: str):
    """Separa 'Calle Era Honda 3' → ('Calle Era Honda', '3')"""
    m = re.match(r'^(.+?)[,\s]+(\d+)\s*$', d.strip())
    if m:
        return m.group(1).strip(), m.group(2)
    return d.strip(), ''


def _google_geocode(direccion: str, api_key: str):
    """Llama a Google Maps Geocoding API."""
    nombre, numero = _separar_numero(direccion)
    query = f"{nombre} {numero}, Alcalá de Henares, Madrid, España".strip()
    url = (
        "https://maps.googleapis.com/maps/api/geocode/json?"
        + parse.urlencode({"address": query, "key": api_key, "language": "es",
                           "region": "es", "components": "country:ES"})
    )
    try:
        with request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        if data.get("status") == "OK":
            loc    = data["results"][0]["geometry"]["location"]
            lat, lon = loc["lat"], loc["lng"]
            # Extraer barrio/distrito de address_components
            barrio = _extraer_barrio_google(data["results"][0].get("address_components", []))
            return lat, lon, barrio
    except Exception as e:
        print(f"[Geo/Google] Error: {e}")
    return None, None, None


def _extraer_barrio_google(components: list) -> str | None:
    """Extrae barrio o localidad de la respuesta de Google."""
    tipos_barrio = ["neighborhood", "sublocality", "sublocality_level_1",
                    "political", "locality"]
    for tipo in tipos_barrio:
        for c in components:
            if tipo in c.get("types", []):
                nombre = c.get("long_name", "")
                if nombre and nombre.lower() not in ("alcalá de henares", "madrid",
                                                      "españa", "comunidad de madrid"):
                    return nombre
    return None


def _photon_geocode(direccion: str):
    """Fallback: Photon (Komoot) — mejor motor que Nominatim estándar."""
    nombre, numero = _separar_numero(direccion)
    queries = [
        f"{nombre} {numero}, Alcalá de Henares",
        f"{_sin_prefijo(nombre)} {numero}, Alcalá de Henares",
        f"{_sin_prefijo(nombre)}, Alcalá de Henares",
    ]
    for q in queries:
        q = q.strip()
        url = (
            "https://photon.komoot.io/api/?"
            + parse.urlencode({"q": q, "lang": "es", "limit": 1,
                               "lat": 40.484, "lon": -3.364})
        )
        try:
            req = request.Request(url, headers={"User-Agent": "CSA-PoliciaLocal/4.0"})
            with request.urlopen(req, timeout=3) as r:
                data = json.loads(r.read())
            feats = data.get("features", [])
            if feats:
                coords = feats[0]["geometry"]["coordinates"]
                lon, lat = coords[0], coords[1]
                # Verificar que está en zona Alcalá/alrededores
                if 40.0 <= lat <= 41.5 and -4.5 <= lon <= -2.5:
                    props   = feats[0].get("properties", {})
                    barrio  = (props.get("district") or props.get("city_district")
                               or props.get("suburb") or None)
                    return lat, lon, barrio
        except Exception:
            continue
    return None, None, None


def _aqui_geocode(direccion: str, api_key: str):
    """Fallback HERE Maps (si hay API key)."""
    nombre, numero = _separar_numero(direccion)
    query = f"{nombre} {numero}, Alcalá de Henares, España"
    url = (
        "https://geocode.search.hereapi.com/v1/geocode?"
        + parse.urlencode({"q": query, "apiKey": api_key, "lang": "es-ES",
                           "in": "countryCode:ESP", "limit": 1})
    )
    try:
        with request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        items = data.get("items", [])
        if items:
            pos    = items[0]["position"]
            addr   = items[0].get("address", {})
            barrio = addr.get("district") or addr.get("subdistrict") or None
            return pos["lat"], pos["lng"], barrio
    except Exception as e:
        print(f"[Geo/HERE] Error: {e}")
    return None, None, None


# ─── Leer claves desde archivo de configuración ───────────────────
def _leer_config() -> dict:
    ruta = os.path.join(os.path.dirname(__file__), "..", "config.json")
    ruta = os.path.normpath(ruta)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def geocodificar(direccion: str) -> tuple:
    """
    Función principal. Devuelve (lat, lon, barrio_nombre, fuente).
    barrio_nombre puede ser None si no se detectó.
    fuente es 'google'|'photon'|'local'.
    """
    key = _limpiar(direccion)
    if key in _cache:
        return _cache[key]

    cfg       = _leer_config()
    google_key = cfg.get("GOOGLE_MAPS_API_KEY", "").strip()
    here_key   = cfg.get("HERE_API_KEY", "").strip()

    lat = lon = barrio = None
    fuente = "local"

    # 1. Google Maps (más preciso)
    if google_key:
        lat, lon, barrio = _google_geocode(direccion, google_key)
        if lat:
            fuente = "google"

    # 2. Photon (sin API key, buen motor)
    if not lat:
        lat, lon, barrio = _photon_geocode(direccion)
        if lat:
            fuente = "photon"

    # 3. HERE Maps
    if not lat and here_key:
        lat, lon, barrio = _aqui_geocode(direccion, here_key)
        if lat:
            fuente = "here"

    result = (lat, lon, barrio, fuente)
    _cache[key] = result
    return result


def geocodificar_direccion(direccion: str):
    """
    Compatibilidad con código existente.
    Devuelve (lat, lon, zona_csa).
    """
    from servicios.geo_logic import obtener_zona_por_direccion, _coords_a_zona, CALLES_A_ZONA

    lat, lon, barrio_google, fuente = geocodificar(direccion)

    # Determinar zona CSA
    if lat and lon:
        zona = _coords_a_zona(lat, lon)
        # Si Google/Photon nos dio un barrio más preciso, intentar mapearlo
        if barrio_google:
            zona_mapeada = _mapear_barrio_a_zona(barrio_google)
            if zona_mapeada:
                zona = zona_mapeada
    else:
        zona = obtener_zona_por_direccion(direccion)

    return lat, lon, zona


def _mapear_barrio_a_zona(barrio: str) -> str | None:
    """Intenta convertir el nombre de barrio de Google a una zona CSA."""
    from servicios.geo_logic import _limpiar as geo_limpiar, CALLES_A_ZONA
    b = barrio.lower()
    b = ''.join(c for c in unicodedata.normalize('NFD', b)
                if unicodedata.category(c) != 'Mn')

    mapeo_directo = {
        "casco historico": "Casco Histórico / Centro",
        "centro":           "Casco Histórico / Centro",
        "el val":           "El Val",
        "garena":           "La Garena",
        "la garena":        "La Garena",
        "chorrillo":        "Chorrillo / Ensanche",
        "ensanche":         "Chorrillo / Ensanche",
        "reyes catolicos":  "Reyes Católicos",
        "espartales":       "Espartales",
        "nueva alcala":     "Nueva Alcalá",
    }
    for k, v in mapeo_directo.items():
        if k in b:
            return v
    return None
