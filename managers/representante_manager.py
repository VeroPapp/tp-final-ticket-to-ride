from database.db import db_session
from managers.usuario_manager import UsuarioManager
from models.usuario import Representante


class RepresentanteManager:
    def __init__(self, usuario_manager=None):
        self.usuario_manager = usuario_manager or UsuarioManager()

    @property
    def representantes(self):
        return self.listar_representantes()

    def listar_representantes(self):
        return db_session.query(Representante).all()

    def buscar_representante(self, representante_id):
        return db_session.get(Representante, representante_id)

    def alta_representante(self, nombre, mail, psw):
        representante_id = self.usuario_manager.crear_usuario(
            nombre, mail, psw, "Representante"
        )
        return self.buscar_representante(representante_id)

    def baja_representante(self, representante_id):
        representante = self.buscar_representante(representante_id)
        if not representante:
            raise ValueError(f"No existe usuario con ID {representante_id}.")

        return self.usuario_manager.eliminar_usuario(representante_id)

    def obtener_representante_disponible(self):
        return db_session.query(Representante).filter_by(disponible=True).first()

    def cambiar_disponibilidad(self, representante_id, disponible):
        representante = self.buscar_representante(representante_id)
        if not representante:
            raise ValueError(f"No existe usuario con ID {representante_id}.")

        representante.cambiar_disponibilidad(disponible)
        db_session.commit()
        return True
