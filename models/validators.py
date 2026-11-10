import re

ROLES_VALIDOS = ("Administrador", "Representante", "Cliente")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LEN = 6


def normalizar_mail(mail):
    return (mail or "").strip().lower()


def validar_mail(mail):
    mail = normalizar_mail(mail)
    if not EMAIL_REGEX.match(mail):
        raise ValueError(f"El correo '{mail}' no es válido.")
    return mail


def validar_password(psw):
    psw = psw or ""
    if len(psw) < PASSWORD_MIN_LEN:
        raise ValueError(
            f"La contraseña debe tener al menos {PASSWORD_MIN_LEN} caracteres."
        )
    return psw


def validar_nombre(nombre):
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    return nombre


def validar_rol(rol):
    rol = (rol or "").strip().capitalize()
    if rol not in ROLES_VALIDOS:
        raise ValueError(f"Rol inválido: '{rol}'.")
    return rol
