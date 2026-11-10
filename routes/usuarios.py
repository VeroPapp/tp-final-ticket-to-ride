from flask import Blueprint, request

from models.usuario import Representante
from routes.utils import (
    _handle,
    admin_required,
    login_required,
    r_manager,
    u_manager,
)

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios/crear", methods=["POST"])
@login_required
@admin_required
def usuarios_crear():
    d = request.get_json() or {}
    return _handle(
        lambda: u_manager.crear_usuario(d["nombre"], d["mail"], d["psw"], d["rol"])
    )


@usuarios_bp.route("/usuarios/<int:uid>/actualizar", methods=["POST"])
@login_required
@admin_required
def usuarios_actualizar(uid):
    d = request.get_json() or {}
    return _handle(
        lambda: u_manager.actualizar_usuario(
            uid,
            d.get("nombre") or None,
            d.get("mail") or None,
            d.get("disponible"),
        )
    )


@usuarios_bp.route("/usuarios/<int:uid>/eliminar", methods=["POST"])
@login_required
@admin_required
def usuarios_eliminar(uid):
    usuario = u_manager.obtener_por_id(uid)
    if isinstance(usuario, Representante):
        return _handle(lambda: r_manager.baja_representante(uid))
    return _handle(lambda: u_manager.eliminar_usuario(uid))
