import re
import unicodedata

class ClasificadorIncidentes:
    def __init__(self):
        # 1. Diccionario mejorado (evitamos palabras de 4 letras que den falsos positivos)
        self.categorias = {
            "homicidio": ["asesinato", "asesin", "mato", "muerto", "cadaver", "homicidio"],
            "agresion": ["pelea", "agrediendo", "golpe", "lesion", "herido", "sangre", "apunal", "paliza", "rina"],
            "robo_violencia": ["atraco", "navaja", "pistola", "tiron", "intimidacion", "asalto", "pasamontana"],
            "robo_fuerza": ["alunizaje", "reventado", "forzado", "boquete", "vivienda", "trastero"],
            "hurto": ["hurto", "descuido", "carterista", "bolso", "sustraccion"],
            "libertad_sexual": ["viola", "agresion sexual", "abuso", "acoso"],
            "violencia_genero": ["genero", "pareja", "maltrato", "mujer", "domestica"],
            "vandalismo": ["pintada", "graffiti", "destrozo", "mobiliario", "contenedor", "quema"],
            "drogas": ["trapicheo", "narcotrafico", "alijo", "estupefaciente"], # Quitamos "pasa"
            "orden_publico": ["motin", "manifestacion", "desorden", "tumulto", "pelea multitudinaria"],
            "auxilio": ["caida", "anciano", "enfermo", "desmayo", "inconsciente", "socorro"],
            "seguridad_vial": ["alcohol", "velocidad", "choque", "accidente", "atropello"]
        }

        # 2. Factores de Riesgo (Estos van PRIMERO en la lógica)
        self.prioridad_extrema = ["tiroteo", "bomba", "terrorismo", "rehenes", "secuestro", "disparando", "disparo"]
        self.armas_fuego = ["pistola", "fusil", "tiro", "dispar", "escopeta", "arma de fuego"]

    def limpiar_texto(self, texto):
        if not texto: return ""
        texto = texto.lower()
        # Quitar acentos
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        # Mantener solo letras y números
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        return " ".join(texto.split())

    def procesar_descripcion(self, descripcion_original):
        desc = self.limpiar_texto(descripcion_original)
        
        # --- LÓGICA DE GRAVEDAD PRIMERO (Para que no se pierda) ---
        es_critico = any(k in desc for k in self.prioridad_extrema) or any(k in desc for k in self.armas_fuego)
        
        # Detectar Tipo
        tipo = "otros"
        for cat, keywords in self.categorias.items():
            if any(k in desc for k in keywords):
                tipo = cat
                break
        
        # Ajustar tipo si es crítico
        if es_critico:
            tipo = "PRIORIDAD CRÍTICA (ARMAS/DISPAROS)"

        # --- ASIGNACIÓN DE GRAVEDAD Y PATRULLAS ---
        if es_critico:
            return {
                "tipo": tipo.upper(),
                "gravedad": "muy alta",
                "patrulla": "3" # Enviamos el número para que la pantalla de recomendación lo entienda
            }

        if tipo in ["homicidio", "libertad_sexual", "violencia_genero"] or "herido" in desc:
            return {
                "tipo": tipo.upper(),
                "gravedad": "alta",
                "patrulla": "2"
            }

        if tipo in ["robo_violencia", "agresion", "orden_publico"]:
            return {
                "tipo": tipo.upper(),
                "gravedad": "media",
                "patrulla": "2"
            }

        # Por defecto
        return {
            "tipo": tipo.upper(),
            "gravedad": "baja",
            "patrulla": "1"
        }