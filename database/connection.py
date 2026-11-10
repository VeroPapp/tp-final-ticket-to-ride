from sqlalchemy import text

from database.db import Base, db_session, engine
from database.seed import cargar_datos_prueba

# Importar el paquete registra todos los modelos antes de create_all.
import models  # noqa: F401


def _migrar_mensajes():
    """Migra los mensajes viejos que estaban guardados como hitos."""
    tabla_hitos = db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name='hitos'")
    ).first()
    if not tabla_hitos:
        return

    columnas = [
        fila[1]
        for fila in db_session.execute(text("PRAGMA table_info(hitos)")).fetchall()
    ]
    if "remitente_id" not in columnas:
        return

    db_session.execute(
        text(
            """
            INSERT INTO mensajes (ticket_id, remitente_id, fecha, contenido)
            SELECT h.ticket_id, h.remitente_id, h.fecha, h.descripcion
            FROM hitos h
            WHERE h.remitente_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM mensajes m
                  WHERE m.ticket_id = h.ticket_id
                    AND m.remitente_id = h.remitente_id
                    AND m.contenido = h.descripcion
              )
            """
        )
    )
    db_session.execute(text("DELETE FROM hitos WHERE remitente_id IS NOT NULL"))
    db_session.commit()


def init_db(cargar_seed=True):
    Base.metadata.create_all(engine)
    _migrar_mensajes()

    if cargar_seed:
        from models.usuario import Usuario

        if db_session.query(Usuario).count() == 0:
            try:
                cargar_datos_prueba()
            except Exception as e:
                db_session.rollback()
                print(f"Error seed: {e}")
