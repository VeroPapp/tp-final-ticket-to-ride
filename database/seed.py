from werkzeug.security import generate_password_hash

from database.db import db_session
from models.mensaje import Mensaje
from models.notificacion import Notificacion
from models.producto import CategoriaProducto, Producto
from models.ticket import Hito, Ticket
from models.usuario import Administrador, Cliente, Representante


def cargar_datos_prueba():
    # 1. Usuarios
    admin = Administrador(
        nombre="Admin Sistema",
        mail="admin@test.com",
        psw=generate_password_hash("admin123"),
    )
    c1 = Cliente(
        nombre="Ana Martínez",
        mail="ana@test.com",
        psw=generate_password_hash("ana123"),
    )
    c2 = Cliente(
        nombre="Luis Rodríguez",
        mail="luis@test.com",
        psw=generate_password_hash("luis123"),
    )
    r1 = Representante(
        nombre="Juan Pérez",
        mail="juan@test.com",
        psw=generate_password_hash("juan123"),
        disponible=True,
    )
    r2 = Representante(
        nombre="María García",
        mail="maria@test.com",
        psw=generate_password_hash("maria123"),
        disponible=True,
    )
    db_session.add_all([admin, c1, c2, r1, r2])
    db_session.commit()

    # 2. Productos
    cat1 = CategoriaProducto(nombre="Hardware")
    cat2 = CategoriaProducto(nombre="Software")
    db_session.add_all([cat1, cat2])
    db_session.commit()

    p1 = Producto(
        nombre="Notebook Dell",
        marca="Dell",
        modelo="Latitude",
        codigo="DELL01",
        categoria_id=cat1.id,
    )
    p2 = Producto(
        nombre="Windows 11",
        marca="Microsoft",
        modelo="Pro",
        codigo="WIN11",
        categoria_id=cat2.id,
    )
    db_session.add_all([p1, p2])
    db_session.commit()

    # 3. Tickets
    t1 = Ticket(
        cliente_id=c1.id,
        representante_id=r1.id,
        producto_id=p1.id,
        descripcion="La notebook no enciende",
        prioridad="Alta",
    )
    t2 = Ticket(
        cliente_id=c2.id,
        representante_id=r2.id,
        producto_id=p2.id,
        descripcion="El sistema se cierra solo",
        prioridad="Urgente",
        estado="EnProceso",
    )
    db_session.add_all([t1, t2])
    db_session.commit()

    # 4. Hitos (eventos del sistema)
    h1 = Hito(ticket_id=t1.id, descripcion="Ticket creado por el sistema")
    h3 = Hito(ticket_id=t2.id, descripcion="Ticket creado por el sistema")
    db_session.add_all([h1, h3])
    db_session.commit()

    # 5. Mensajes de los usuarios
    m1 = Mensaje(
        ticket_id=t1.id,
        remitente_id=c1.id,
        contenido="Hola, no enciende desde ayer.",
    )
    db_session.add(m1)
    db_session.commit()

    # 6. Notificaciones
    n1 = Notificacion(
        usuario_id=c1.id,
        ticket_id=t1.id,
        descripcion="Su ticket fue creado.",
    )
    db_session.add(n1)
    db_session.commit()

    print("Datos de prueba cargados con exito.")
