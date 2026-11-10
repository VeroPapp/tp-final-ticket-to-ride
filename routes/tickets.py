from flask import Blueprint, jsonify, request, session

from routes.utils import _handle, login_required, t_manager

tickets_bp = Blueprint("tickets", __name__)


def obj_to_dict(obj):
    if not obj:
        return None
    return {columna.name: getattr(obj, columna.name) for columna in obj.__table__.columns}


def _puede_acceder(ticket):
    rol = session["user_rol"]
    if rol == "Cliente":
        return ticket.cliente_id == session["user_id"]
    if rol == "Representante":
        return ticket.representante_id in (None, session["user_id"])
    return True


def _ticket_autorizado(tid):
    ticket = t_manager.buscar_ticket(tid)
    if not ticket:
        return None, (jsonify(ok=False, message="Ticket no existe"), 404)
    if not _puede_acceder(ticket):
        return None, (
            jsonify(ok=False, message="No tenés permiso para acceder a este ticket."),
            403,
        )
    return ticket, None


@tickets_bp.route("/tickets/crear", methods=["POST"])
@login_required
def tickets_crear():
    d = request.get_json() or {}

    producto_id = d.get("producto_id")
    descripcion = d.get("descripcion")
    if not producto_id or not descripcion:
        return jsonify(
            ok=False, message="El producto y la descripción son obligatorios."
        ), 400

    if session["user_rol"] == "Cliente":
        cliente_id = session["user_id"]
        prioridad = "Media"
        representante_id = None
    else:
        cliente_id = d.get("cliente_id")
        prioridad = d.get("prioridad", "Media")
        representante_id = d.get("representante_id")

    return _handle(
        lambda: t_manager.crear_ticket(
            cliente_id, producto_id, descripcion, prioridad, representante_id
        ).id
    )


@tickets_bp.route("/tickets/<int:tid>/detalle")
@login_required
def tickets_detalle(tid):
    ticket, error = _ticket_autorizado(tid)
    if error:
        return error

    historial = t_manager.consultar_historial(tid)
    return jsonify(ok=True, ticket=obj_to_dict(ticket), historial=historial)


@tickets_bp.route("/tickets/<int:tid>/mensaje", methods=["POST"])
@login_required
def tickets_mensaje(tid):
    _, error = _ticket_autorizado(tid)
    if error:
        return error

    d = request.get_json() or {}
    if session["user_rol"] == "Administrador":
        remitente_id = d.get("remitente_id")
    else:
        remitente_id = session["user_id"]

    return _handle(
        lambda: t_manager.agregar_mensaje(tid, remitente_id, d.get("contenido"))
    )


@tickets_bp.route("/tickets/<int:tid>/estado", methods=["POST"])
@login_required
def tickets_estado(tid):
    if session["user_rol"] == "Cliente":
        return jsonify(
            ok=False, message="Los clientes no pueden cambiar el estado de un ticket."
        ), 403

    _, error = _ticket_autorizado(tid)
    if error:
        return error

    d = request.get_json() or {}
    return _handle(lambda: t_manager.cambiar_estado(tid, d["nuevo_estado"]))


@tickets_bp.route("/tickets/<int:tid>/cerrar", methods=["POST"])
@login_required
def tickets_cerrar(tid):
    if session["user_rol"] == "Cliente":
        return jsonify(
            ok=False, message="Los clientes no pueden cerrar tickets."
        ), 403

    _, error = _ticket_autorizado(tid)
    if error:
        return error

    return _handle(lambda: t_manager.cerrar_ticket(tid))


@tickets_bp.route("/tickets/<int:tid>/reabrir", methods=["POST"])
@login_required
def tickets_reabrir(tid):
    if session["user_rol"] == "Cliente":
        return jsonify(
            ok=False, message="Los clientes no pueden reabrir tickets."
        ), 403

    _, error = _ticket_autorizado(tid)
    if error:
        return error

    return _handle(lambda: t_manager.reabrir_ticket(tid))


@tickets_bp.route("/tickets/<int:tid>/actualizar", methods=["POST"])
@login_required
def tickets_actualizar(tid):
    if session["user_rol"] == "Cliente":
        return jsonify(
            ok=False, message="Los clientes no pueden actualizar datos del ticket."
        ), 403

    _, error = _ticket_autorizado(tid)
    if error:
        return error

    d = request.get_json() or {}
    es_admin = session["user_rol"] == "Administrador"
    representante_id = (d.get("representante_id") or None) if es_admin else None
    admin_id = session["user_id"] if es_admin else None

    return _handle(
        lambda: t_manager.actualizar_ticket(
            tid,
            d.get("descripcion") or None,
            d.get("prioridad") or None,
            representante_id,
            admin_id,
        )
    )


@tickets_bp.route("/tickets/<int:tid>/eliminar", methods=["POST"])
@login_required
def tickets_eliminar(tid):
    if session["user_rol"] != "Administrador":
        return jsonify(
            ok=False, message="Solo el administrador puede eliminar tickets."
        ), 403

    return _handle(lambda: t_manager.eliminar_ticket(tid))
