# servicios/clasificador.py — Clasificador de incidentes v2.0
import re
import unicodedata

class ClasificadorIncidentes:
    """
    Clasifica texto libre de un incidente policial y devuelve:
      tipo      → categoría legal
      gravedad  → muy alta / alta / media / baja
      patrulla  → número de unidades recomendadas (str)
      emoji     → indicador visual
      confianza → palabras clave que activaron la clasificación
    """

    # ── Prioridades absolutas (se evalúan ANTES que las categorías) ──
    PRIORIDAD_EXTREMA = [
        "tiroteo","bomba","terrorismo","rehenes","secuestro",
        "disparando","disparo","francotirador","explosion","atentado",
        "artefacto","detonacion"
    ]
    ARMAS_FUEGO = [
        "pistola","fusil","escopeta","revolver","arma de fuego",
        "kalashnikov","subfusil","tiro","dispar"
    ]
    ARMAS_BLANCAS = [
        "navaja","cuchillo","machete","hacha","punal","apunal","apunala"
    ]

    # ── Categorías (orden = prioridad de detección) ──────────────────
    CATEGORIAS = {
        "homicidio": {
            "keywords": ["asesinato","asesin","mato","muerto","cadaver",
                         "homicidio","fallecido","muerte violenta"],
            "gravedad": "muy alta", "patrulla": "3",
            "emoji": "💀", "color_tag": "critica"
        },
        "agresion_armada": {
            "keywords": ["apunal","herida arma","navaja","cuchillo","agredido con"],
            "gravedad": "muy alta", "patrulla": "3",
            "emoji": "🔪", "color_tag": "critica"
        },
        "violacion": {
            "keywords": ["violacion","viola","agresion sexual","abuso sexual","agredida sexualmente"],
            "gravedad": "muy alta", "patrulla": "2",
            "emoji": "🆘", "color_tag": "critica"
        },
        "violencia_genero": {
            "keywords": ["genero","pareja","maltrato","mujer maltrat","domestica",
                         "violencia familiar","maltratada","ex pareja"],
            "gravedad": "alta", "patrulla": "2",
            "emoji": "⚠️", "color_tag": "alta"
        },
        "secuestro": {
            "keywords": ["secuestro","rehenes","retenido","capturado","raptado"],
            "gravedad": "muy alta", "patrulla": "3",
            "emoji": "🆘", "color_tag": "critica"
        },
        "agresion": {
            "keywords": ["pelea","agrediendo","golpe","lesion","herido","sangre",
                         "paliza","rina","punetazo","patada","agresion fisica"],
            "gravedad": "alta", "patrulla": "2",
            "emoji": "🥊", "color_tag": "alta"
        },
        "robo_con_violencia": {
            "keywords": ["atraco","tiron","intimidacion","asalto","pasamontana",
                         "arrebato","robo a mano armada","amenaza con"],
            "gravedad": "alta", "patrulla": "2",
            "emoji": "🔫", "color_tag": "alta"
        },
        "robo_con_fuerza": {
            "keywords": ["alunizaje","reventado","forzado","boquete","vivienda",
                         "trastero","butrón","rotura","cristal roto","cerradura"],
            "gravedad": "media", "patrulla": "1",
            "emoji": "🏠", "color_tag": "media"
        },
        "hurto": {
            "keywords": ["hurto","descuido","carterista","bolso","sustraccion",
                         "cartera","movil robado","bolsillo"],
            "gravedad": "media", "patrulla": "1",
            "emoji": "👜", "color_tag": "media"
        },
        "orden_publico": {
            "keywords": ["motin","manifestacion","desorden","tumulto","pelea multitudinaria",
                         "disturbio","algarada","botellón","concentracion violenta"],
            "gravedad": "alta", "patrulla": "2",
            "emoji": "👥", "color_tag": "alta"
        },
        "drogas": {
            "keywords": ["trapicheo","narcotrafico","alijo","estupefaciente",
                         "venta de droga","punto de venta","menudeo"],
            "gravedad": "media", "patrulla": "2",
            "emoji": "💊", "color_tag": "media"
        },
        "vandalismo": {
            "keywords": ["pintada","graffiti","destrozo","mobiliario","contenedor",
                         "quema","papelera","banco roto","cristal roto"],
            "gravedad": "baja", "patrulla": "1",
            "emoji": "🎨", "color_tag": "baja"
        },
        "accidente_trafico": {
            "keywords": ["choque","accidente","atropello","colision","velocidad",
                         "conductor","vehiculo","moto","ciclista","peatón atropellado"],
            "gravedad": "media", "patrulla": "1",
            "emoji": "🚗", "color_tag": "media"
        },
        "conduccion_peligrosa": {
            "keywords": ["alcohol","drogas al volante","semaforo","stop","sentido contrario",
                         "conduccion temeraria","sin carnet"],
            "gravedad": "media", "patrulla": "1",
            "emoji": "🍺", "color_tag": "media"
        },
        "auxilio_ciudadano": {
            "keywords": ["caida","anciano","enfermo","desmayo","inconsciente",
                         "socorro","necesita ayuda","persona en el suelo","desorientado"],
            "gravedad": "baja", "patrulla": "1",
            "emoji": "🏥", "color_tag": "baja"
        },
        "incendio": {
            "keywords": ["incendio","fuego","llamas","humo","arder","quemado"],
            "gravedad": "muy alta", "patrulla": "2",
            "emoji": "🔥", "color_tag": "critica"
        },
        "amenaza": {
            "keywords": ["amenaza","amenazando","amenazo","amedrenta"],
            "gravedad": "alta", "patrulla": "1",
            "emoji": "⚡", "color_tag": "alta"
        },
        "ruido_molestia": {
            "keywords": ["ruido","musica alta","vecino","molestia","gritos","escandalo"],
            "gravedad": "baja", "patrulla": "1",
            "emoji": "🔊", "color_tag": "baja"
        },
    }

    def __init__(self):
        pass

    @staticmethod
    def _limpiar(texto: str) -> str:
        if not texto:
            return ""
        texto = texto.lower()
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
        return ' '.join(texto.split())

    def _detectar_palabras(self, desc: str, lista: list) -> list:
        return [kw for kw in lista if kw in desc]

    def procesar_descripcion(self, descripcion_original: str) -> dict:
        desc = self._limpiar(descripcion_original)

        # 1. Prioridad máxima: armas de fuego / terrorismo
        hits_ext  = self._detectar_palabras(desc, self.PRIORIDAD_EXTREMA)
        hits_fuego = self._detectar_palabras(desc, self.ARMAS_FUEGO)
        hits_blanca = self._detectar_palabras(desc, self.ARMAS_BLANCAS)

        if hits_ext or hits_fuego:
            return {
                "tipo":      "PRIORIDAD CRÍTICA — ARMAS DE FUEGO / TERRORISMO",
                "gravedad":  "muy alta",
                "patrulla":  "3",
                "emoji":     "🔴",
                "color_tag": "critica",
                "confianza": hits_ext + hits_fuego,
            }

        # 2. Recorrer categorías
        for nombre, cfg in self.CATEGORIAS.items():
            hits = self._detectar_palabras(desc, cfg["keywords"])
            if hits:
                # Arma blanca sube gravedad si la categoría no es ya crítica
                extra_gravedad = bool(hits_blanca) and cfg["gravedad"] not in ("muy alta",)
                gravedad = "muy alta" if extra_gravedad else cfg["gravedad"]
                patrulla = "3" if extra_gravedad else cfg["patrulla"]

                return {
                    "tipo":      nombre.replace("_", " ").upper(),
                    "gravedad":  gravedad,
                    "patrulla":  patrulla,
                    "emoji":     cfg["emoji"],
                    "color_tag": "critica" if extra_gravedad else cfg["color_tag"],
                    "confianza": hits + (hits_blanca if extra_gravedad else []),
                }

        # 3. Por defecto
        return {
            "tipo":      "INCIDENCIA GENERAL",
            "gravedad":  "baja",
            "patrulla":  "1",
            "emoji":     "🔵",
            "color_tag": "baja",
            "confianza": [],
        }
