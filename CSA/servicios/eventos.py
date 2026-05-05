# servicios/eventos.py
class CanalEventos:
    _suscriptores = []

    @classmethod
    def suscribir(cls, funcion):
        cls._suscriptores.append(funcion)

    @classmethod
    def emitir_cambio(cls):
        for funcion in cls._suscriptores:
            funcion()