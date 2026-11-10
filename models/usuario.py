from sqlalchemy import Boolean, Column, Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import Base, db_session
from models.validators import (
    normalizar_mail,
    validar_mail,
    validar_nombre,
    validar_password,
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    mail = Column(String(120), unique=True, nullable=False)
    psw = Column(String(255), nullable=False)
    rol = Column(String(20))

    __mapper_args__ = {
        "polymorphic_identity": "Usuario",
        "polymorphic_on": rol,
    }

    def verificar_password(self, psw):
        return check_password_hash(self.psw, psw)

    @classmethod
    def iniciar_sesion(cls, mail, psw):
        mail = normalizar_mail(mail)
        usuario = db_session.query(cls).filter_by(mail=mail).first()
        if usuario and usuario.verificar_password(psw):
            return usuario
        return None

    def cerrar_sesion(self):
        """La sesión HTTP la cierra la capa de rutas; acá solo confirmamos."""
        return True


class Cliente(Usuario):
    __mapper_args__ = {"polymorphic_identity": "Cliente"}

    @classmethod
    def registrarse(cls, nombre, mail, psw):
        nombre = validar_nombre(nombre)
        mail = validar_mail(mail)
        validar_password(psw)

        if db_session.query(Usuario).filter_by(mail=mail).first():
            raise ValueError(f"El correo '{mail}' ya está registrado.")

        nuevo = cls(
            nombre=nombre,
            mail=mail,
            psw=generate_password_hash(psw),
        )
        db_session.add(nuevo)
        db_session.commit()
        return nuevo


class Representante(Usuario):
    __mapper_args__ = {"polymorphic_identity": "Representante"}

    disponible = Column(Boolean, default=True)

    def cambiar_disponibilidad(self, disponible):
        self.disponible = bool(disponible)
        return True

    def esta_disponible(self):
        return bool(self.disponible)


class Administrador(Usuario):
    __mapper_args__ = {"polymorphic_identity": "Administrador"}

    def asignar_representante(self, ticket, representante):
        ticket.representante = representante
        return True
