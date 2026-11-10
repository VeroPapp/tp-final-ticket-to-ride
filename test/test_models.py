import pytest

from database.db import db_session
from models.enums import EstadoTicket, Prioridad
from models.notificacion import Notificacion
from models.producto import CategoriaProducto, Producto
from models.ticket import Ticket
from models.usuario import Cliente, Representante, Usuario


def test_enums_tienen_los_valores_del_uml():
    assert EstadoTicket.valores() == ["Abierto", "EnProceso", "Resuelto", "Cerrado"]
    assert Prioridad.valores() == ["Baja", "Media", "Alta", "Urgente"]


def test_iniciar_sesion_valida_credenciales(db):
    usuario = Usuario.iniciar_sesion("ana@test.com", "ana123")

    assert usuario is not None
    assert usuario.mail == "ana@test.com"
    assert isinstance(usuario, Cliente)
    assert Usuario.iniciar_sesion("ana@test.com", "incorrecta") is None
    assert Usuario.iniciar_sesion("noexiste@test.com", "ana123") is None


def test_cliente_registrarse_crea_usuario_y_valida_datos(db):
    cliente = Cliente.registrarse("  Nuevo Cliente ", "Nuevo@Test.com", "secreto123")

    assert cliente.id is not None
    assert cliente.nombre == "Nuevo Cliente"
    assert cliente.mail == "nuevo@test.com"
    assert cliente.verificar_password("secreto123")

    with pytest.raises(ValueError, match="ya está registrado"):
        Cliente.registrarse("Otro", "nuevo@test.com", "secreto123")

    with pytest.raises(ValueError, match="al menos"):
        Cliente.registrarse("Corto", "corto@test.com", "123")


def test_representante_cambia_disponibilidad(db):
    representante = (
        db_session.query(Representante).filter_by(mail="juan@test.com").one()
    )

    assert representante.esta_disponible() is True
    representante.cambiar_disponibilidad(False)
    assert representante.esta_disponible() is False
    representante.cambiar_disponibilidad(True)
    assert representante.esta_disponible() is True


def test_ticket_cambia_estado_y_prioridad(db):
    ticket = db_session.get(Ticket, 1)

    ticket.cambiar_estado("EnProceso")
    assert ticket.estado == "EnProceso"

    ticket.cambiar_estado("cerrado")
    assert ticket.estado == "Cerrado"

    ticket.cambiar_prioridad("urgente")
    assert ticket.prioridad == "Urgente"

    with pytest.raises(ValueError, match="Estado inválido"):
        ticket.cambiar_estado("Volando")

    with pytest.raises(ValueError, match="Prioridad inválida"):
        ticket.cambiar_prioridad("Altísima")


def test_ticket_registra_hitos_y_mensajes(db):
    ticket = db_session.get(Ticket, 1)
    cliente = db_session.get(Cliente, 2)
    hitos_antes = len(ticket.hitos)
    mensajes_antes = len(ticket.mensajes)

    ticket.registrar_hito("Nuevo hito")
    ticket.registrar_mensaje(cliente, "Nuevo mensaje")

    assert len(ticket.hitos) == hitos_antes + 1
    assert len(ticket.mensajes) == mensajes_antes + 1
    assert ticket.mensajes[-1].remitente is cliente
    assert ticket.mensajes[-1].contenido == "Nuevo mensaje"

    with pytest.raises(ValueError, match="no puede estar vacía"):
        ticket.registrar_hito("   ")

    with pytest.raises(ValueError, match="no puede estar vacío"):
        ticket.registrar_mensaje(cliente, "   ")


def test_producto_asigna_categoria(db):
    producto = db_session.get(Producto, 1)
    producto2 = db_session.get(Producto, 2)
    categoria = db_session.get(CategoriaProducto, 2)

    assert producto.asignar_categoria(categoria) is True
    assert producto.categoria is categoria

    assert categoria.asignar_producto(producto2) is True
    assert producto2.categoria is categoria


def test_notificacion_marcar_como_leida(db):
    notificacion = db_session.get(Notificacion, 1)

    assert notificacion.leida is False
    assert notificacion.marcar_como_leida() is True
    assert notificacion.leida is True
