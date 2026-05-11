# servicios/clasificador.py — Clasificador v3.0 — Operativo real
import re
import unicodedata

class ClasificadorIncidentes:
    """
    Clasificador de incidentes policiales para uso operativo real.
    Devuelve tipo, gravedad, patrullas recomendadas, emoji, confianza.
    """

    # ── Prioridad máxima (se evalúa ANTES que todo) ───────────────
    PRIORIDAD_EXTREMA = [
        "tiroteo","bomba","terrorismo","rehenes","secuestro",
        "francotirador","explosion","atentado","artefacto","detonacion",
        "amenaza bomba","paquete sospechoso","alerta terrorista",
    ]
    ARMAS_FUEGO = [
        "pistola","fusil","escopeta","revolver","arma de fuego",
        "disparando","disparo","tiros","tiro","bala","subfusil",
        "kalashnikov","ak","glock","defensa personal","escopeta recortada",
    ]
    ARMAS_BLANCAS = [
        "navaja","cuchillo","machete","hacha","punal","apunal","apunala",
        "arma blanca","cristal roto","botella rota","destornillador",
    ]

    CATEGORIAS = [
        # ── Delitos contra la vida ─────────────────────────────────
        ("HOMICIDIO / ASESINATO", {
            "kw": ["asesinato","asesin","mato a","muerto","cadaver",
                   "homicidio","fallecido","muerte violenta","cuerpo sin vida",
                   "persona muerta","encontrado muerto"],
            "gravedad": "muy alta", "patrulla": "3", "emoji": "💀",
        }),
        # ── Agresiones sexuales ────────────────────────────────────
        ("AGRESIÓN SEXUAL", {
            "kw": ["violacion","viola","agresion sexual","abuso sexual",
                   "agredida sexualmente","tocamientos","exhibicionismo",
                   "acoso sexual","pederastia","abuso menor"],
            "gravedad": "muy alta", "patrulla": "2", "emoji": "🆘",
        }),
        # ── Violencia de género ────────────────────────────────────
        ("VIOLENCIA DE GÉNERO", {
            "kw": ["violencia de genero","violencia genero","pareja","maltrato",
                   "mujer maltrat","violencia domestica","maltratada","ex pareja",
                   "marido","novio agresi","orden de alejamiento","violencia familiar",
                   "agresion a mujer","pegando a su mujer","pegando a su pareja"],
            "gravedad": "alta", "patrulla": "2", "emoji": "⚠️",
        }),
        # ── Agresión con arma blanca ───────────────────────────────
        ("AGRESIÓN CON ARMA BLANCA", {
            "kw": ["apunal","herida arma blanca","navaja","cuchillo al",
                   "machete","agredido con arma"],
            "gravedad": "muy alta", "patrulla": "3", "emoji": "🔪",
        }),
        # ── Agresiones físicas ─────────────────────────────────────
        ("AGRESIÓN FÍSICA", {
            "kw": ["pelea","agrediendo","golpe","lesion","herido","sangre",
                   "paliza","rina","punetazo","patada","agresion fisica",
                   "se estan peleando","estan peleando","persona inconsciente",
                   "inconsciente en suelo","tumba","tirado en suelo"],
            "gravedad": "alta", "patrulla": "2", "emoji": "🥊",
        }),
        # ── Robo con violencia / intimidación ─────────────────────
        ("ROBO CON VIOLENCIA", {
            "kw": ["atraco","tiron","intimidacion","asalto","pasamontana",
                   "robo a mano armada","amenaza con arma","pistola en mano",
                   "cuchillo en mano","arrebato bolso","arrebato movil",
                   "tirón","robando con violencia","atracador"],
            "gravedad": "alta", "patrulla": "2", "emoji": "🔫",
        }),
        # ── Robo con fuerza ───────────────────────────────────────
        ("ROBO CON FUERZA EN LAS COSAS", {
            "kw": ["alunizaje","reventado","forzado","boquete","cerradura forzada",
                   "cristal roto comercio","rotura escaparate","butrón",
                   "robo en vivienda","han entrado en","me han robado en casa",
                   "robo en local","forzaron la puerta","escalada de fachada"],
            "gravedad": "media", "patrulla": "1", "emoji": "🏠",
        }),
        # ── Hurtos ────────────────────────────────────────────────
        ("HURTO", {
            "kw": ["hurto","carterista","bolso","cartera","movil robado",
                   "me han quitado","sustraccion","le robaron la cartera",
                   "tirón de cadena","carterista metro","bolsillo","han robado mi",
                   "descuido","supermercado","tienda","establecimiento"],
            "gravedad": "media", "patrulla": "1", "emoji": "👜",
        }),
        # ── Desapariciones ────────────────────────────────────────
        ("DESAPARICIÓN / PERSONA BUSCADA", {
            "kw": ["desaparecido","desaparecida","no aparece","no llega",
                   "no le encuentro","menor desaparecido","anciano perdido",
                   "alzheimer","desorientado","persona perdida","buscamos a"],
            "gravedad": "alta", "patrulla": "2", "emoji": "🔍",
        }),
        # ── Incendios ─────────────────────────────────────────────
        ("INCENDIO", {
            "kw": ["incendio","fuego","llamas","humo","ardiendo","quemandose",
                   "incendio en piso","incendio en coche","incendio en contenedor",
                   "columna de humo","olemos a quemado","parece incendio"],
            "gravedad": "muy alta", "patrulla": "2", "emoji": "🔥",
        }),
        # ── Accidentes de tráfico ─────────────────────────────────
        ("ACCIDENTE DE TRÁFICO", {
            "kw": ["accidente","colision","choque","atropello","alcance",
                   "coche volcado","moto caida","ciclista atropellado",
                   "peaton atropellado","salida de via","heridos en accidente",
                   "colision multiple","accidente de trafico","hay heridos"],
            "gravedad": "media", "patrulla": "1", "emoji": "🚗",
        }),
        # ── Conductores peligrosos ────────────────────────────────
        ("CONDUCCIÓN PELIGROSA / INFRACTORES", {
            "kw": ["conductor borracho","alcohol al volante","drogas al volante",
                   "conduccion temeraria","sin carnet","exceso velocidad",
                   "saltarse semaforo","sentido contrario","no para",
                   "huye de la policia","persecucion vehiculo","velocidad"],
            "gravedad": "media", "patrulla": "1", "emoji": "🍺",
        }),
        # ── Orden público ─────────────────────────────────────────
        ("ALTERACIÓN DE ORDEN PÚBLICO", {
            "kw": ["motin","disturbio","algarada","botellón","peleas grupales",
                   "tumulto","manifestacion violenta","pelea multitudinaria",
                   "grupo peleando","concentracion conflictiva","barricada",
                   "apedreando","lanzando objetos"],
            "gravedad": "alta", "patrulla": "2", "emoji": "👥",
        }),
        # ── Drogas ────────────────────────────────────────────────
        ("TRÁFICO DE DROGAS", {
            "kw": ["trapicheo","narcotrafico","venta de droga","punto de venta",
                   "camello","alijo","estupefaciente","menudeo","consumo en via publica",
                   "jeringuilla","heroina","cocaina","pastillas","vendiendo droga"],
            "gravedad": "media", "patrulla": "2", "emoji": "💊",
        }),
        # ── Amenazas ──────────────────────────────────────────────
        ("AMENAZAS", {
            "kw": ["amenaza","amenazando","amenazo","amedrenta","esta amenazando",
                   "ha amenazado","me han amenazado","te voy a matar","te mato"],
            "gravedad": "alta", "patrulla": "1", "emoji": "⚡",
        }),
        # ── Acoso / stalking ──────────────────────────────────────
        ("ACOSO / STALKING", {
            "kw": ["acoso","me sigue","siguiendo","stalkeo","me vigila",
                   "acosador","no me deja en paz","me espera","me persigue"],
            "gravedad": "alta", "patrulla": "1", "emoji": "👁️",
        }),
        # ── Vandalismo ────────────────────────────────────────────
        ("VANDALISMO / DAÑOS", {
            "kw": ["pintada","graffiti","destrozo","mobiliario","contenedor",
                   "quema contenedor","papelera","banco roto","cristal roto calle",
                   "daños en vehículo","rayan coches","grafiti","lapiz"],
            "gravedad": "baja", "patrulla": "1", "emoji": "🎨",
        }),
        # ── Auxilio ciudadano ─────────────────────────────────────
        ("AUXILIO / PERSONA EN PELIGRO", {
            "kw": ["caida","anciano","enfermo","desmayo","inconsciente",
                   "socorro","necesita ayuda","persona en suelo","desorientado",
                   "no responde","ha caido","parece mal","crisis epileptica",
                   "le da algo","urgencia medica","pide socorro"],
            "gravedad": "baja", "patrulla": "1", "emoji": "🏥",
        }),
        # ── Ruidos / molestias ────────────────────────────────────
        ("RUIDOS / MOLESTIAS", {
            "kw": ["ruido","musica alta","vecino ruidoso","escandalo","gritos en la calle",
                   "musica hasta","no me dejan dormir","fiesta","petardos","cohetes",
                   "alarma disparada","alarma de coche","alarma local"],
            "gravedad": "baja", "patrulla": "1", "emoji": "🔊",
        }),
        # ── Ocupación ilegal ──────────────────────────────────────
        ("OCUPACIÓN ILEGAL / USURPACIÓN", {
            "kw": ["okupa","ocupacion","ocupan","han ocupado","han entrado a vivir",
                   "usurpacion","han usurpado","han tomado el piso"],
            "gravedad": "media", "patrulla": "1", "emoji": "🏘️",
        }),
        # ── Fraude / estafa ───────────────────────────────────────
        ("ESTAFA / FRAUDE", {
            "kw": ["estafa","fraude","timo","engano","me han timado","phishing",
                   "me han sacado el dinero","cuento del tio","engano anciana"],
            "gravedad": "media", "patrulla": "1", "emoji": "💸",
        }),
    ]

    @staticmethod
    def _limpiar(texto: str) -> str:
        if not texto:
            return ""
        t = texto.lower()
        t = ''.join(
            c for c in unicodedata.normalize('NFD', t)
            if unicodedata.category(c) != 'Mn'
        )
        t = re.sub(r'[^a-z0-9\s]', ' ', t)
        return ' '.join(t.split())

    def _hits(self, desc: str, lista: list) -> list:
        return [kw for kw in lista if kw in desc]

    def procesar_descripcion(self, descripcion_original: str) -> dict:
        desc = self._limpiar(descripcion_original)

        # 1. Terrorismo / armas de fuego (prioridad absoluta)
        hits_ext   = self._hits(desc, self.PRIORIDAD_EXTREMA)
        hits_fuego = self._hits(desc, self.ARMAS_FUEGO)
        if hits_ext or hits_fuego:
            return {
                "tipo":      "PRIORIDAD CRÍTICA — ARMAS DE FUEGO / AMENAZA GRAVE",
                "gravedad":  "muy alta",
                "patrulla":  "3",
                "emoji":     "🔴",
                "color_tag": "critica",
                "confianza": hits_ext + hits_fuego,
            }

        hits_blanca = self._hits(desc, self.ARMAS_BLANCAS)

        # 2. Recorrer categorías en orden
        for nombre, cfg in self.CATEGORIAS:
            hits = self._hits(desc, cfg["kw"])
            if hits:
                con_arma = bool(hits_blanca) and cfg["gravedad"] not in ("muy alta",)
                gravedad = "muy alta" if con_arma else cfg["gravedad"]
                patrulla = "3"       if con_arma else cfg["patrulla"]
                color_map = {
                    "muy alta": "critica", "alta": "alta",
                    "media": "media", "baja": "baja"
                }
                return {
                    "tipo":      nombre,
                    "gravedad":  gravedad,
                    "patrulla":  patrulla,
                    "emoji":     cfg["emoji"],
                    "color_tag": "critica" if con_arma else color_map.get(cfg["gravedad"],"baja"),
                    "confianza": hits + (hits_blanca if con_arma else []),
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
