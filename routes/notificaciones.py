from flask import Blueprint, jsonify, session

from routes.utils import _handle, login_required, n_manager

notificaciones_bp = Blueprint("notificaciones", __name__)


def _notificacion_autorizada(nid):
    notificacion = n_manager.buscar_notificacion(nid)
    if not notificacion:
        return None, (jsonify(ok=False, message="Notificación no existe"), 404)
    if (
        session["user_rol"] != "Administrador"
        and notificacion.usuario_id != session["user_id"]
    ):
        return None, (
            jsonify(ok=False, message="No tenés permiso sobre esta notificación."),
            403,
        )
    return notificacion, None


@notificaciones_bp.route("/notificaciones/<int:nid>/leer", methods=["POST"])
@login_required
def notificaciones_leer(nid):
    _, error = _notificacion_autorizada(nid)
    if error:
        return error
    return _handle(lambda: n_manager.marcar_como_leida(nid))


@notificaciones_bp.route("/notificaciones/<int:nid>/eliminar", methods=["POST"])
@login_required
def notificaciones_eliminar(nid):
    _, error = _notificacion_autorizada(nid)
    if error:
        return error
    return _handle(lambda: n_manager.eliminar_notificacion(nid))
