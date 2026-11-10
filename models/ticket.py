from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.db import Base
from models.enums import EstadoTicket, Prioridad, normalizar_enum
from models.mensaje import Mensaje


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    representante_id = Column(Integer, ForeignKey("usuarios.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default=EstadoTicket.ABIERTO.value)
    prioridad = Column(String(20), default=Prioridad.MEDIA.value)
    fecha_creacion = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente", foreign_keys=[cliente_id])
    representante = relationship("Representante", foreign_keys=[representante_id])
    producto = relationship("Producto")
    hitos = relationship(
        "Hito",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Hito.fecha",
    )
    mensajes = relationship(
        "Mensaje",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Mensaje.fecha",
    )
    notificaciones = relationship(
        "Notificacion",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Notificacion.fecha",
    )

    def cambiar_estado(self, nuevo_estado):
        self.estado = normalizar_enum(nuevo_estado, EstadoTicket, "Estado")
        return True

    def cambiar_prioridad(self, nueva_prioridad):
        self.prioridad = normalizar_enum(nueva_prioridad, Prioridad, "Prioridad")
        return True

    def registrar_hito(self, descripcion):
        descripcion = (descripcion or "").strip()
        if not descripcion:
            raise ValueError("La descripción del hito no puede estar vacía.")

        hito = Hito(descripcion=descripcion, fecha=datetime.now())
        self.hitos.append(hito)
        return hito

    def registrar_mensaje(self, remitente, contenido):
        contenido = (contenido or "").strip()
        if not contenido:
            raise ValueError("El mensaje no puede estar vacío.")

        mensaje = Mensaje(
            remitente=remitente,
            contenido=contenido,
            fecha=datetime.now(),
        )
        self.mensajes.append(mensaje)
        return mensaje

    def registrar_notificacion(self, notificacion):
        self.notificaciones.append(notificacion)
        return notificacion


class Hito(Base):
    __tablename__ = "hitos"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    ticket = relationship("Ticket", back_populates="hitos")
