def obtener_zona_por_direccion(direccion):
    d = direccion.lower()
    mapping = {
        "El Val": ["rio sorbe", "rio aliste", "rio tajo", "avenida del val", "valladolid", "laredo", "avila"],
        "Centro": ["mayor", "libreros", "plaza cervantes", "ayuntamiento", "tinte", "vitoria", "escritorios"],
        "La Garena": ["juan carlos i", "arturo soria", "garena", "fausto elhuyar", "agustin de betancourt"],
        "Chorrillo": ["juan de austria", "torrelaguna", "san ignacio", "valles", "san herculano"],
        "Reyes Católicos": ["reyes catolicos", "isabel la catolica", "nunez de guzman", "puerta de madrid"],
        "Espartales": ["benito perez galdos", "alfonso vi", "pico del vizmaya", "becquer"]
    }
    for zona, palabras in mapping.items():
        if any(p in d for p in palabras):
            return zona
    return "Distrito Centro"

def clasificar_tipo_incidente(texto):
    t = texto.lower()
    if any(w in t for w in ["pistola", "arma", "cuchillo", "navaja", "disparo", "atentado", "rehen", "matar"]):
        return "CRÍTICA (ARMAS)"
    if any(w in t for w in ["robo", "atraco", "pelea", "agresion", "tienda", "tiron", "violencia"]):
        return "ALTA (DELITO VIOLENTO)"
    if any(w in t for w in ["hurto", "descuido", "cartera", "vandalismo", "pintada"]):
        return "MEDIA (PATRIMONIO)"
    return "BAJA (ASISTENCIA)"