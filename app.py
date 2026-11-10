from flask import Flask
from database.connection import init_db
from database.db import db_session

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secreto_ticket_to_ride"
    
    init_db()

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.usuarios import usuarios_bp
    from routes.productos import productos_bp
    from routes.tickets import tickets_bp
    from routes.notificaciones import notificaciones_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(notificaciones_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)