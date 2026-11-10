from sqlalchemy import text

from database.connection import _migrar_mensajes
from database.db import db_session
from models.mensaje import Mensaje
from models.ticket import Hito


def test_migra_mensajes_viejos_de_hitos_a_mensajes(db):
    # Simula la tabla vieja, que guardaba los mensajes como hitos.
    db_session.execute(text("ALTER TABLE hitos ADD COLUMN remitente_id INTEGER"))
    db_session.execute(
        text(
            """
            INSERT INTO hitos (ticket_id, descripcion, remitente_id, fecha)
            VALUES (1, 'Mensaje legado', 2, CURRENT_TIMESTAMP)
            """
        )
    )
    db_session.commit()

    assert (
        db_session.query(Hito)
        .filter_by(descripcion="Mensaje legado")
        .count()
        == 1
    )

    _migrar_mensajes()
    db_session.expire_all()

    assert (
        db_session.query(Hito)
        .filter_by(descripcion="Mensaje legado")
        .count()
        == 0
    )

    mensaje = (
        db_session.query(Mensaje)
        .filter_by(contenido="Mensaje legado")
        .one()
    )
    assert mensaje.ticket_id == 1
    assert mensaje.remitente_id == 2

    # La migración debe ser idempotente.
    _migrar_mensajes()
    assert (
        db_session.query(Mensaje)
        .filter_by(contenido="Mensaje legado")
        .count()
        == 1
    )
