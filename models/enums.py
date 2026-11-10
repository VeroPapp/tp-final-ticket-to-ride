from enum import Enum


class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"

    @classmethod
    def valores(cls):
        return [prioridad.value for prioridad in cls]


class EstadoTicket(str, Enum):
    ABIERTO = "Abierto"
    EN_PROCESO = "EnProceso"
    RESUELTO = "Resuelto"
    CERRADO = "Cerrado"

    @classmethod
    def valores(cls):
        return [estado.value for estado in cls]


def normalizar_enum(valor, enum_clase, nombre):
    """Devuelve el valor string del enum, aceptando mayúsculas/minúsculas."""
    if isinstance(valor, enum_clase):
        return valor.value

    texto = (valor or "").strip()
    for opcion in enum_clase:
        if opcion.value.lower() == texto.lower():
            return opcion.value

    opciones = ", ".join(opcion.value for opcion in enum_clase)
    adjetivo = {"Prioridad": "inválida"}.get(nombre, "inválido")
    raise ValueError(f"{nombre} {adjetivo}: '{texto}'. Opciones: {opciones}.")
