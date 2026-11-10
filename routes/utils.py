from functools import wraps

from flask import jsonify, session

from database.db import db_session
from managers.notificacion_manager import NotificacionManager
from managers.producto_manager import ProductoManager
from managers.representante_manager import RepresentanteManager
from managers.ticket_manager import TicketManager
from managers.usuario_manager import UsuarioManager

u_manager = UsuarioManager()
r_manager = RepresentanteManager(u_manager)
p_manager = ProductoManager()
n_manager = NotificacionManager()
t_manager = TicketManager(p_manager, r_manager, n_manager)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(ok=False, message="No autenticado."), 401
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_rol") != "Administrador":
            return jsonify(ok=False, message="Requiere rol Administrador."), 403
        return view(*args, **kwargs)

    return wrapped


def _handle(func):
    """Maneja las excepciones de las rutas y devuelve JSON estandarizado."""
    try:
        result = func()
        return jsonify(ok=True, message="Operación exitosa", data=result)
    except ValueError as e:
        db_session.rollback()
        return jsonify(ok=False, message=str(e)), 400
    except Exception as e:
        db_session.rollback()
        return jsonify(ok=False, message=f"Error inesperado: {e}"), 500
