from flask import Blueprint, request

from routes.utils import _handle, admin_required, login_required, p_manager

productos_bp = Blueprint("productos", __name__)


@productos_bp.route("/categorias/crear", methods=["POST"])
@login_required
@admin_required
def categorias_crear():
    d = request.get_json() or {}
    return _handle(lambda: p_manager.crear_categoria(d["nombre"]))


@productos_bp.route("/categorias/<int:cid>/eliminar", methods=["POST"])
@login_required
@admin_required
def categorias_eliminar(cid):
    return _handle(lambda: p_manager.eliminar_categoria(cid))


@productos_bp.route("/productos/crear", methods=["POST"])
@login_required
@admin_required
def productos_crear():
    d = request.get_json() or {}
    return _handle(
        lambda: p_manager.agregar_producto(
            d["nombre"],
            d.get("marca", ""),
            d.get("modelo", ""),
            d["codigo"],
            d["categoria_id"],
        ).id
    )


@productos_bp.route("/productos/<int:pid>/actualizar", methods=["POST"])
@login_required
@admin_required
def productos_actualizar(pid):
    d = request.get_json() or {}
    return _handle(
        lambda: p_manager.actualizar_producto(
            pid,
            d.get("nombre") or None,
            d.get("categoria_id") or None,
        )
    )


@productos_bp.route("/productos/<int:pid>/categoria", methods=["POST"])
@login_required
@admin_required
def productos_asignar_categoria(pid):
    d = request.get_json() or {}
    return _handle(lambda: p_manager.asignar_categoria(pid, d["categoria_id"]))


@productos_bp.route("/productos/<int:pid>/eliminar", methods=["POST"])
@login_required
@admin_required
def productos_eliminar(pid):
    return _handle(lambda: p_manager.eliminar_producto(pid))
