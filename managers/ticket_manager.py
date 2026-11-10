from database.db import db_session
from managers.notificacion_manager import NotificacionManager
from managers.producto_manager import ProductoManager
from managers.representante_manager import RepresentanteManager
from models.enums import EstadoTicket, Prioridad
from models.ticket import Ticket
from models.usuario import Administrador, Cliente, Usuario


class TicketManager:
    def __init__(
        self,
        producto_manager=None,
        representante_manager=None,
        notificacion_manager=None,
    ):
        self.producto_manager = producto_manager or ProductoManager()
        self.representante_manager = representante_manager or RepresentanteManager()
        self.notificacion_manager = notificacion_manager or NotificacionManager()

    @property
    def tickets(self):
        return self.listar_tickets()

    # ==========================================
    # CREACIÓN Y CONSULTA
    # ==========================================
    def crear_ticket(
        self,
        cliente_id,
        producto_id,
        descripcion,
        prioridad=Prioridad.MEDIA.value,
        representante_id=None,
    ):
        cliente = db_session.get(Cliente, cliente_id)
        if not cliente:
            raise ValueError("Cliente no válido.")

        producto = self.producto_manager.buscar_producto(producto_id)
        if not producto:
            raise ValueError("Producto no válido.")

        descripcion = (descripcion or "").strip()
        if not descripcion:
            raise ValueError("La descripción del ticket no puede estar vacía.")

        if representante_id:
            representante = self.representante_manager.buscar_representante(
                representante_id
            )
            if not representante:
                raise ValueError("Representante no válido.")
        else:
            representante = (
                self.representante_manager.obtener_representante_disponible()
            )

        nuevo = Ticket(
            cliente=cliente,
            representante=representante,
            producto=producto,
            descripcion=descripcion,
        )
        nuevo.cambiar_prioridad(prioridad or Prioridad.MEDIA.value)

        db_session.add(nuevo)
        db_session.flush()

        nuevo.registrar_hito("Ticket creado por el sistema")
        self._notificar(cliente.id, nuevo, "Su ticket fue creado.")
        db_session.commit()
        return nuevo

    def buscar_ticket(self, ticket_id):
        return db_session.get(Ticket, ticket_id)

    def listar_tickets(self):
        return db_session.query(Ticket).order_by(Ticket.id.desc()).all()

    def listar_tickets_cliente(self, cliente_id):
        return (
            db_session.query(Ticket)
            .filter_by(cliente_id=cliente_id)
            .order_by(Ticket.id.desc())
            .all()
        )

    # ==========================================
    # CAMBIOS DE ESTADO / PRIORIDAD
    # ==========================================
    def cambiar_estado(self, ticket_id, nuevo_estado):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")

        ticket.cambiar_estado(nuevo_estado)
        ticket.registrar_hito("Estado cambiado")
        self._notificar(ticket.cliente_id, ticket, "Estado actualizado")
        db_session.commit()
        return True

    def cambiar_prioridad(self, ticket_id, nueva_prioridad):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")
        if ticket.estado == EstadoTicket.CERRADO.value:
            raise ValueError("No se puede modificar un ticket cerrado.")

        ticket.cambiar_prioridad(nueva_prioridad)
        db_session.commit()
        return True

    def cerrar_ticket(self, ticket_id):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")
        if not ticket.mensajes:
            raise ValueError("Debe haber al menos una respuesta antes de cerrar.")

        return self.cambiar_estado(ticket_id, EstadoTicket.CERRADO.value)

    def reabrir_ticket(self, ticket_id):
        return self.cambiar_estado(ticket_id, EstadoTicket.ABIERTO.value)

    # ==========================================
    # MENSAJES
    # ==========================================
    def agregar_mensaje(self, ticket_id, remitente_id, contenido):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket or ticket.estado == EstadoTicket.CERRADO.value:
            raise ValueError("Ticket no válido o cerrado.")

        remitente = db_session.get(Usuario, remitente_id)
        if not remitente:
            raise ValueError("Remitente no válido.")

        ticket.registrar_mensaje(remitente, contenido)
        ticket.registrar_hito("Mensaje agregado")

        destinatario = (
            ticket.cliente_id
            if remitente_id != ticket.cliente_id
            else ticket.representante_id
        )
        if destinatario:
            self._notificar(destinatario, ticket, "Nuevo mensaje en su ticket")
        else:
            db_session.commit()
        return True

    # ==========================================
    # ACTUALIZACIÓN Y ASIGNACIÓN
    # ==========================================
    def actualizar_ticket(
        self,
        ticket_id,
        descripcion=None,
        prioridad=None,
        representante_id=None,
        admin_id=None,
    ):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")
        if ticket.estado == EstadoTicket.CERRADO.value:
            raise ValueError("No se puede modificar un ticket cerrado.")

        if descripcion:
            ticket.descripcion = descripcion.strip()
        if prioridad:
            ticket.cambiar_prioridad(prioridad)
        if representante_id:
            self.asignar_representante(
                ticket_id, representante_id, admin_id=admin_id, commit=False
            )

        db_session.commit()
        return True

    def asignar_representante(
        self, ticket_id, representante_id, admin_id=None, commit=True
    ):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")

        representante = self.representante_manager.buscar_representante(
            representante_id
        )
        if not representante:
            raise ValueError("Representante no válido.")

        if admin_id is not None:
            admin = db_session.get(Administrador, admin_id)
            if not isinstance(admin, Administrador):
                raise ValueError(
                    "Solo un administrador puede asignar representantes."
                )
            admin.asignar_representante(ticket, representante)
        else:
            ticket.representante = representante

        if commit:
            db_session.commit()
        return True

    def eliminar_ticket(self, ticket_id):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")

        db_session.delete(ticket)
        db_session.commit()
        return True

    # ==========================================
    # HISTORIAL
    # ==========================================
    def consultar_historial(self, ticket_id):
        ticket = self.buscar_ticket(ticket_id)
        if not ticket:
            raise ValueError("Ticket no existe.")

        def formatear_fecha(fecha):
            return fecha.strftime("%Y-%m-%d %H:%M") if fecha else ""

        hitos = [
            {
                "id": hito.id,
                "descripcion": hito.descripcion,
                "fecha": formatear_fecha(hito.fecha),
            }
            for hito in ticket.hitos
        ]
        mensajes = [
            {
                "id": mensaje.id,
                "remitente": mensaje.remitente.nombre if mensaje.remitente else "Sistema",
                "contenido": mensaje.contenido,
                "fecha": formatear_fecha(mensaje.fecha),
            }
            for mensaje in ticket.mensajes
        ]
        return {"hitos": hitos, "mensajes": mensajes}

    # ==========================================
    # INTERNOS
    # ==========================================
    def _notificar(self, usuario_id, ticket, descripcion):
        notificacion = self.notificacion_manager.crear_notificacion(
            usuario_id, ticket.id, descripcion
        )
        ticket.registrar_notificacion(notificacion)
        self.notificacion_manager.enviar_notificacion(notificacion)
        return notificacion
