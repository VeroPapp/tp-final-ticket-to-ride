from werkzeug.security import generate_password_hash

from database.db import db_session
from models.usuario import Administrador, Cliente, Representante, Usuario
from models.validators import (
    validar_mail,
    validar_nombre,
    validar_password,
    validar_rol,
)


class UsuarioManager:
    def autenticar(self, mail, psw):
        return Usuario.iniciar_sesion(mail, psw)

    def cerrar_sesion(self, usuario):
        return usuario.cerrar_sesion() if usuario else True

    def crear_usuario(self, nombre, mail, psw, rol):
        rol = validar_rol(rol)

        if rol == "Cliente":
            return Cliente.registrarse(nombre, mail, psw).id

        nombre = validar_nombre(nombre)
        mail = validar_mail(mail)
        validar_password(psw)

        if db_session.query(Usuario).filter_by(mail=mail).first():
            raise ValueError(f"El correo '{mail}' ya está registrado.")

        clases = {
            "Representante": Representante,
            "Administrador": Administrador,
        }
        nuevo = clases[rol](
            nombre=nombre,
            mail=mail,
            psw=generate_password_hash(psw),
        )
        db_session.add(nuevo)
        db_session.commit()
        return nuevo.id

    def obtener_todos(self):
        return db_session.query(Usuario).all()

    def obtener_clientes(self):
        return db_session.query(Cliente).all()

    def obtener_representantes(self):
        return db_session.query(Representante).all()

    def obtener_por_id(self, uid):
        return db_session.get(Usuario, uid)

    def actualizar_usuario(self, uid, nombre=None, mail=None, disponible=None):
        usuario = self.obtener_por_id(uid)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if nombre:
            usuario.nombre = validar_nombre(nombre)

        if mail:
            mail = validar_mail(mail)
            existente = db_session.query(Usuario).filter_by(mail=mail).first()
            if existente and existente.id != usuario.id:
                raise ValueError(f"El correo '{mail}' ya está registrado.")
            usuario.mail = mail

        if disponible is not None:
            if not isinstance(usuario, Representante):
                raise ValueError("Solo los representantes tienen disponibilidad.")
            usuario.cambiar_disponibilidad(disponible)

        db_session.commit()
        return True

    def eliminar_usuario(self, uid):
        usuario = self.obtener_por_id(uid)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        from models.notificacion import Notificacion
        from models.ticket import Ticket

        if isinstance(usuario, Cliente):
            if db_session.query(Ticket).filter_by(cliente_id=uid).count() > 0:
                raise ValueError(
                    "No se puede eliminar un cliente que tiene tickets asociados."
                )
        elif isinstance(usuario, Representante):
            db_session.query(Ticket).filter_by(representante_id=uid).update(
                {"representante_id": None}, synchronize_session=False
            )

        db_session.query(Notificacion).filter_by(usuario_id=uid).delete(
            synchronize_session=False
        )
        db_session.delete(usuario)
        db_session.commit()
        return True
