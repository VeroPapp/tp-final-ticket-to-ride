from flask import Blueprint, redirect, render_template, session, url_for

from routes.utils import n_manager, p_manager, t_manager, u_manager

main_bp = Blueprint("main", __name__)


def usuario_to_dict(usuario):
    """Convierte un usuario a dict, omitiendo la contraseña."""
    if not usuario:
        return None
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "mail": usuario.mail,
        "rol": usuario.rol,
        "disponible": getattr(usuario, "disponible", None),
    }


def obj_to_dict(obj):
    """Para tickets, productos, categorías, etc. (no tienen contraseñas)."""
    if not obj:
        return None
    return {
        columna.name: getattr(obj, columna.name)
        for columna in obj.__table__.columns
    }


def notificacion_to_dict(notificacion):
    if not notificacion:
        return None
    return {
        "id": notificacion.id,
        "usuario_id": notificacion.usuario_id,
        "ticket_id": notificacion.ticket_id,
        "descripcion": notificacion.descripcion,
        "leida": notificacion.leida,
        "fecha": notificacion.fecha.strftime("%Y-%m-%d %H:%M")
        if notificacion.fecha
        else "",
        "usuario_nombre": notificacion.usuario.nombre
        if notificacion.usuario
        else "-",
        "usuario_rol": notificacion.usuario.rol if notificacion.usuario else "-",
    }


@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    usuarios = u_manager.obtener_todos()
    productos = p_manager.obtener_productos()

    rol = session["user_rol"]
    todos_los_tickets = t_manager.listar_tickets()
    if rol == "Administrador":
        tickets = todos_los_tickets
    elif rol == "Representante":
        tickets = [
            ticket
            for ticket in todos_los_tickets
            if ticket.representante_id == session["user_id"]
            or ticket.representante_id is None
        ]
    else:
        tickets = t_manager.listar_tickets_cliente(session["user_id"])

    tickets_data = []
    for ticket in tickets:
        ticket_dict = obj_to_dict(ticket)
        ticket_dict["cliente_nombre"] = (
            ticket.cliente.nombre if ticket.cliente else "-"
        )
        ticket_dict["representante_nombre"] = (
            ticket.representante.nombre if ticket.representante else "-"
        )
        ticket_dict["producto_nombre"] = (
            ticket.producto.nombre if ticket.producto else "-"
        )
        tickets_data.append(ticket_dict)

    notificaciones = (
        n_manager.obtener_todas()
        if rol == "Administrador"
        else n_manager.obtener_por_usuario(session["user_id"])
    )

    return render_template(
        "index.html",
        usuarios=[usuario_to_dict(usuario) for usuario in usuarios]
        if rol == "Administrador"
        else [],
        todos_los_usuarios=[usuario_to_dict(usuario) for usuario in usuarios],
        clientes=[usuario_to_dict(cliente) for cliente in u_manager.obtener_clientes()],
        representantes=[
            usuario_to_dict(representante)
            for representante in u_manager.obtener_representantes()
        ],
        productos=[obj_to_dict(producto) for producto in productos],
        categorias=[
            obj_to_dict(categoria)
            for categoria in p_manager.obtener_categorias()
        ],
        tickets=tickets_data,
        notificaciones=[notificacion_to_dict(n) for n in notificaciones],
        sin_leer=n_manager.contar_no_leidas(session["user_id"]),
        total_usuarios=len(usuarios),
        total_productos=len(productos),
        total_tickets=len(tickets),
    )
