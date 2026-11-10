from database.db import db_session
from models.notificacion import Notificacion


class NotificacionManager:
    def crear_notificacion(self, usuario_id, ticket_id, mensaje):
        mensaje = (mensaje or "").strip()
        if not mensaje:
            raise ValueError("La descripción de la notificación no puede estar vacía.")

        return Notificacion(
            usuario_id=usuario_id,
            ticket_id=ticket_id,
            descripcion=mensaje,
        )

    def enviar_notificacion(self, notificacion):
        db_session.add(notificacion)
        db_session.commit()
        return notificacion.id

    def buscar_notificacion(self, notif_id):
        return db_session.get(Notificacion, notif_id)

    def obtener_por_usuario(self, usuario_id):
        return (
            db_session.query(Notificacion)
            .filter_by(usuario_id=usuario_id)
            .order_by(Notificacion.fecha.desc())
            .all()
        )

    def obtener_todas(self):
        return db_session.query(Notificacion).order_by(Notificacion.fecha.desc()).all()

    def contar_no_leidas(self, usuario_id):
        return (
            db_session.query(Notificacion)
            .filter_by(usuario_id=usuario_id, leida=False)
            .count()
        )

    def marcar_como_leida(self, notif_id):
        notificacion = db_session.get(Notificacion, notif_id)
        if not notificacion:
            raise ValueError(f"No existe notificación con ID {notif_id}.")

        notificacion.marcar_como_leida()
        db_session.commit()
        return True

    def eliminar_notificacion(self, notif_id):
        notificacion = db_session.get(Notificacion, notif_id)
        if not notificacion:
            raise ValueError(f"No existe notificación con ID {notif_id}.")

        db_session.delete(notificacion)
        db_session.commit()
        return True
