from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    fecha = Column(DateTime, default=datetime.now)
    descripcion = Column(String(255), nullable=False)
    leida = Column(Boolean, default=False)

    usuario = relationship("Usuario")
    ticket = relationship("Ticket", back_populates="notificaciones")

    def marcar_como_leida(self):
        self.leida = True
        return True
