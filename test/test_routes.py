from database.db import db_session
from models.notificacion import Notificacion
from models.producto import Producto
from models.ticket import Ticket
from models.usuario import Cliente, Representante, Usuario


def login(client, mail, psw):
    return client.post(
        "/login",
        data={"mail": mail, "psw": psw},
        follow_redirects=False,
    )


def test_login_correcto_y_logout(client):
    assert login(client, "ana@test.com", "ana123").status_code == 302

    assert client.get("/").status_code == 200

    assert client.get("/logout").status_code == 302
    assert client.get("/tickets/1/detalle").status_code == 401


def test_login_incorrecto(client):
    respuesta = client.post(
        "/login",
        data={"mail": "ana@test.com", "psw": "incorrecta"},
    )

    assert respuesta.status_code == 200
    assert "incorrectos" in respuesta.get_data(as_text=True)


def test_no_autenticado_recibe_401(client):
    assert client.get("/tickets/1/detalle").status_code == 401
    assert (
        client.post("/tickets/1/estado", json={"nuevo_estado": "Resuelto"}).status_code
        == 401
    )


def test_cliente_crea_ticket_y_no_accede_a_ajeno(client):
    login(client, "ana@test.com", "ana123")

    respuesta = client.post(
        "/tickets/crear",
        json={"producto_id": 1, "descripcion": "La notebook no enciende"},
    )

    assert respuesta.status_code == 200
    ticket_id = respuesta.get_json()["data"]

    assert client.get(f"/tickets/{ticket_id}/detalle").status_code == 200
    assert client.get("/tickets/2/detalle").status_code == 403


def test_cliente_no_puede_cambiar_estado_ni_crear_categoria(client):
    login(client, "ana@test.com", "ana123")

    assert (
        client.post("/tickets/1/estado", json={"nuevo_estado": "Cerrado"}).status_code
        == 403
    )
    assert (
        client.post("/categorias/crear", json={"nombre": "Otra"}).status_code == 403
    )


def test_representante_no_accede_a_ticket_ajeno(client):
    login(client, "juan@test.com", "juan123")

    assert client.get("/tickets/1/detalle").status_code == 200
    assert client.get("/tickets/2/detalle").status_code == 403


def test_admin_cambia_estado_y_registra_notificacion(client):
    login(client, "admin@test.com", "admin123")
    notificaciones_antes = (
        db_session.query(Notificacion).filter_by(usuario_id=2).count()
    )

    respuesta = client.post(
        "/tickets/1/estado", json={"nuevo_estado": "EnProceso"}
    )

    assert respuesta.status_code == 200

    db_session.expire_all()
    ticket = db_session.get(Ticket, 1)
    notificaciones_despues = (
        db_session.query(Notificacion).filter_by(usuario_id=2).count()
    )

    assert ticket.estado == "EnProceso"
    assert notificaciones_despues == notificaciones_antes + 1


def test_estado_invalido_devuelve_400(client):
    login(client, "admin@test.com", "admin123")

    respuesta = client.post(
        "/tickets/1/estado", json={"nuevo_estado": "Volando"}
    )

    assert respuesta.status_code == 400
    assert "Estado inválido" in respuesta.get_json()["message"]


def test_representante_agrega_mensaje_cierra_y_reabre(client):
    login(client, "juan@test.com", "juan123")

    assert (
        client.post(
            "/tickets/1/mensaje", json={"contenido": "Respuesta del representante"}
        ).status_code
        == 200
    )

    assert client.post("/tickets/1/cerrar").status_code == 200

    detalle = client.get("/tickets/1/detalle").get_json()
    assert detalle["ticket"]["estado"] == "Cerrado"
    assert detalle["historial"]["mensajes"][-1]["contenido"] == (
        "Respuesta del representante"
    )
    assert any(
        hito["descripcion"] == "Mensaje agregado"
        for hito in detalle["historial"]["hitos"]
    )

    assert client.post("/tickets/1/reabrir").status_code == 200
    assert client.get("/tickets/1/detalle").get_json()["ticket"]["estado"] == (
        "Abierto"
    )


def test_admin_asigna_categoria_y_representante(client):
    login(client, "admin@test.com", "admin123")

    assert (
        client.post("/productos/1/categoria", json={"categoria_id": 2}).status_code
        == 200
    )
    assert (
        client.post(
            "/tickets/1/actualizar",
            json={"prioridad": "Baja", "representante_id": 5},
        ).status_code
        == 200
    )

    db_session.expire_all()
    producto = db_session.get(Producto, 1)
    ticket = db_session.get(Ticket, 1)

    assert producto.categoria_id == 2
    assert ticket.prioridad == "Baja"
    assert ticket.representante_id == 5


def test_admin_crea_categoria_producto_y_usuario(client):
    login(client, "admin@test.com", "admin123")

    categoria = client.post("/categorias/crear", json={"nombre": "Redes"})
    assert categoria.status_code == 200
    categoria_id = categoria.get_json()["data"]

    producto = client.post(
        "/productos/crear",
        json={
            "nombre": "Router",
            "marca": "TP-Link",
            "modelo": "Archer",
            "codigo": "RTR01",
            "categoria_id": categoria_id,
        },
    )
    assert producto.status_code == 200

    usuario = client.post(
        "/usuarios/crear",
        json={
            "nombre": "Cliente Nuevo",
            "mail": "cliente.nuevo@test.com",
            "psw": "clave123",
            "rol": "Cliente",
        },
    )
    assert usuario.status_code == 200

    db_session.expire_all()
    assert db_session.query(Producto).filter_by(codigo="RTR01").one()
    assert db_session.query(Usuario).filter_by(mail="cliente.nuevo@test.com").one()


def test_admin_ve_nombre_y_rol_en_notificaciones(client):
    login(client, "admin@test.com", "admin123")

    html = client.get("/").get_data(as_text=True)

    assert "Ana Martínez" in html
    assert "Cliente" in html


def test_notificacion_ajena_devuelve_403(client):
    login(client, "luis@test.com", "luis123")

    assert client.post("/notificaciones/1/leer").status_code == 403


def test_admin_no_elimina_cliente_con_tickets(client):
    login(client, "admin@test.com", "admin123")

    respuesta = client.post("/usuarios/2/eliminar")

    assert respuesta.status_code == 400
    assert "tickets asociados" in respuesta.get_json()["message"]


def test_admin_elimina_representante_y_desasigna_sus_tickets(client):
    login(client, "admin@test.com", "admin123")

    assert client.post("/usuarios/4/eliminar").status_code == 200

    db_session.expire_all()
    ticket = db_session.get(Ticket, 1)
    representante = (
        db_session.query(Representante).filter_by(mail="juan@test.com").first()
    )

    assert ticket.representante_id is None
    assert representante is None


def test_admin_elimina_ticket(client):
    login(client, "admin@test.com", "admin123")

    assert client.post("/tickets/1/eliminar").status_code == 200

    db_session.expire_all()
    assert db_session.get(Ticket, 1) is None
    assert db_session.query(Cliente).filter_by(mail="ana@test.com").one()
