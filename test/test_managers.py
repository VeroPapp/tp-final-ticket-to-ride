import pytest

from database.db import db_session
from managers.notificacion_manager import NotificacionManager
from managers.producto_manager import ProductoManager
from managers.representante_manager import RepresentanteManager
from managers.ticket_manager import TicketManager
from managers.usuario_manager import UsuarioManager
from models.notificacion import Notificacion
from models.producto import Producto
from models.ticket import Ticket


@pytest.fixture()
def managers():
    producto_manager = ProductoManager()
    representante_manager = RepresentanteManager(UsuarioManager())
    notificacion_manager = NotificacionManager()
    ticket_manager = TicketManager(
        producto_manager, representante_manager, notificacion_manager
    )
    return {
        "productos": producto_manager,
        "representantes": representante_manager,
        "notificaciones": notificacion_manager,
        "tickets": ticket_manager,
    }


def test_crear_ticket_asigna_representante_y_registra_hito(db, managers):
    ticket = managers["tickets"].crear_ticket(
        2, 1, "La notebook no enciende", "Alta"
    )

    assert ticket.id is not None
    assert ticket.cliente.mail == "ana@test.com"
    assert ticket.producto.codigo == "DELL01"
    assert ticket.representante is not None
    assert ticket.representante.esta_disponible() is True
    assert ticket.estado == "Abierto"
    assert ticket.prioridad == "Alta"
    assert any(
        hito.descripcion == "Ticket creado por el sistema"
        for hito in ticket.hitos
    )
    assert managers["notificaciones"].obtener_por_usuario(2)


def test_crear_ticket_con_representante_especifico(db, managers):
    ticket = managers["tickets"].crear_ticket(
        3, 2, "El sistema falla", "Media", representante_id=5
    )

    assert ticket.representante_id == 5


def test_crear_ticket_valida_cliente_y_producto(db, managers):
    with pytest.raises(ValueError, match="Cliente no válido"):
        managers["tickets"].crear_ticket(999, 1, "Descripción", "Media")

    with pytest.raises(ValueError, match="Producto no válido"):
        managers["tickets"].crear_ticket(2, 999, "Descripción", "Media")


def test_cambiar_estado_registra_hito_y_notificacion(db, managers):
    ticket = managers["tickets"].crear_ticket(2, 1, "Descripción", "Media")
    notificaciones_antes = managers["notificaciones"].contar_no_leidas(2)

    managers["tickets"].cambiar_estado(ticket.id, "EnProceso")
    ticket = managers["tickets"].buscar_ticket(ticket.id)

    assert ticket.estado == "EnProceso"
    assert any(hito.descripcion == "Estado cambiado" for hito in ticket.hitos)
    assert (
        managers["notificaciones"].contar_no_leidas(2)
        == notificaciones_antes + 1
    )


def test_agregar_mensaje_crea_mensaje_hito_y_notificacion(db, managers):
    ticket = managers["tickets"].crear_ticket(2, 1, "Descripción", "Media")
    notificaciones_antes = managers["notificaciones"].contar_no_leidas(2)

    managers["tickets"].agregar_mensaje(ticket.id, 4, "Respuesta del representante")

    historial = managers["tickets"].consultar_historial(ticket.id)
    assert len(historial["mensajes"]) == 1
    assert historial["mensajes"][0]["contenido"] == "Respuesta del representante"
    assert historial["mensajes"][0]["remitente"] == "Juan Pérez"
    assert any(
        hito["descripcion"] == "Mensaje agregado"
        for hito in historial["hitos"]
    )
    assert (
        managers["notificaciones"].contar_no_leidas(2)
        == notificaciones_antes + 1
    )


def test_cerrar_sin_mensajes_falla_y_con_mensaje_cierra(db, managers):
    ticket = managers["tickets"].crear_ticket(2, 1, "Descripción", "Media")

    with pytest.raises(ValueError, match="al menos una respuesta"):
        managers["tickets"].cerrar_ticket(ticket.id)

    managers["tickets"].agregar_mensaje(ticket.id, 2, "Mensaje del cliente")

    assert managers["tickets"].cerrar_ticket(ticket.id) is True
    assert managers["tickets"].buscar_ticket(ticket.id).estado == "Cerrado"


def test_reabrir_ticket(db, managers):
    ticket = managers["tickets"].crear_ticket(2, 1, "Descripción", "Media")
    managers["tickets"].agregar_mensaje(ticket.id, 2, "Mensaje del cliente")
    managers["tickets"].cerrar_ticket(ticket.id)

    assert managers["tickets"].reabrir_ticket(ticket.id) is True
    assert managers["tickets"].buscar_ticket(ticket.id).estado == "Abierto"


def test_actualizar_ticket_y_asignar_representante(db, managers):
    ticket = managers["tickets"].crear_ticket(2, 1, "Descripción", "Media")

    managers["tickets"].actualizar_ticket(
        ticket.id,
        descripcion="Descripción actualizada",
        prioridad="Baja",
        representante_id=5,
        admin_id=1,
    )

    ticket = managers["tickets"].buscar_ticket(ticket.id)
    assert ticket.descripcion == "Descripción actualizada"
    assert ticket.prioridad == "Baja"
    assert ticket.representante_id == 5


def test_producto_manager_asignar_categoria(db, managers):
    assert managers["productos"].asignar_categoria(1, 2) is True

    producto = db_session.get(Producto, 1)
    assert producto.categoria_id == 2
    assert managers["productos"].buscar_categoria(2).nombre == "Software"


def test_representante_manager_alta_y_baja(db, managers):
    representante = managers["representantes"].alta_representante(
        "Nuevo Representante", "nuevo.rep@test.com", "rep12345"
    )

    assert representante.id is not None
    assert managers["representantes"].buscar_representante(representante.id)

    assert managers["representantes"].baja_representante(representante.id) is True
    assert managers["representantes"].buscar_representante(representante.id) is None


def test_baja_representante_desasigna_sus_tickets(db, managers):
    ticket = db_session.get(Ticket, 1)
    assert ticket.representante_id == 4

    managers["representantes"].baja_representante(4)

    db_session.expire_all()
    ticket = db_session.get(Ticket, 1)
    assert ticket.representante_id is None
    assert managers["representantes"].buscar_representante(4) is None


def test_notificacion_manager_crear_enviar_y_marcar(db, managers):
    notificacion = managers["notificaciones"].crear_notificacion(
        2, 1, "Notificación de prueba"
    )
    notificacion_id = managers["notificaciones"].enviar_notificacion(notificacion)

    assert notificacion_id is not None
    assert managers["notificaciones"].contar_no_leidas(2) >= 1

    assert managers["notificaciones"].marcar_como_leida(notificacion_id) is True
    notificacion = db_session.get(Notificacion, notificacion_id)
    assert notificacion.leida is True
