from flask import Blueprint, redirect, render_template, request, session, url_for

from routes.utils import u_manager

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mail = request.form.get("mail", "").strip().lower()
        psw = request.form.get("psw", "")

        usuario = u_manager.autenticar(mail, psw)

        if usuario:
            session["user_id"] = usuario.id
            session["user_nombre"] = usuario.nombre
            session["user_rol"] = usuario.rol
            return redirect(url_for("main.index"))

        return render_template(
            "login.html", error="Email o contraseña incorrectos."
        )

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    if session.get("user_id"):
        usuario = u_manager.obtener_por_id(session["user_id"])
        if usuario:
            u_manager.cerrar_sesion(usuario)
    session.clear()
    return redirect(url_for("auth.login"))
