from database.db import db_session
from models.producto import CategoriaProducto, Producto


class ProductoManager:
    def _validar_no_vacio(self, valor, campo):
        valor = (valor or "").strip()
        if not valor:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        return valor

    @property
    def productos(self):
        return self.obtener_productos()

    # ==========================================
    # CRUD CATEGORÍAS
    # ==========================================
    def crear_categoria(self, nombre):
        nombre = self._validar_no_vacio(nombre, "nombre de categoría").capitalize()

        if db_session.query(CategoriaProducto).filter_by(nombre=nombre).first():
            raise ValueError(f"Ya existe la categoría '{nombre}'.")

        nueva = CategoriaProducto(nombre=nombre)
        db_session.add(nueva)
        db_session.commit()
        return nueva.id

    def obtener_categorias(self):
        return db_session.query(CategoriaProducto).all()

    def buscar_categoria(self, categoria_id):
        return db_session.get(CategoriaProducto, categoria_id)

    def eliminar_categoria(self, cat_id):
        categoria = self.buscar_categoria(cat_id)
        if not categoria:
            raise ValueError(f"No existe categoría con ID {cat_id}.")

        if db_session.query(Producto).filter_by(categoria_id=cat_id).count() > 0:
            raise ValueError(
                "No se puede eliminar una categoría que tiene productos asignados. "
                "Reasigná o eliminá primero esos productos."
            )

        db_session.delete(categoria)
        db_session.commit()
        return True

    # ==========================================
    # CRUD PRODUCTOS
    # ==========================================
    def agregar_producto(self, nombre, marca, modelo, codigo, categoria_id):
        nombre = self._validar_no_vacio(nombre, "nombre del producto")
        codigo = self._validar_no_vacio(codigo, "código del producto")

        categoria = self.buscar_categoria(categoria_id)
        if not categoria:
            raise ValueError(f"No existe categoría con ID {categoria_id}.")

        if db_session.query(Producto).filter_by(codigo=codigo).first():
            raise ValueError(f"Ya existe un producto con código '{codigo}'.")

        nuevo = Producto(
            nombre=nombre,
            marca=marca,
            modelo=modelo,
            codigo=codigo,
            categoria=categoria,
        )
        db_session.add(nuevo)
        db_session.commit()
        return nuevo

    def buscar_producto(self, producto_id):
        return db_session.get(Producto, producto_id)

    def obtener_productos(self):
        return db_session.query(Producto).all()

    def actualizar_producto(self, prod_id, nombre=None, categoria_id=None):
        producto = self.buscar_producto(prod_id)
        if not producto:
            raise ValueError(f"No existe producto con ID {prod_id}.")

        if nombre is None and categoria_id is None:
            return False

        if nombre is not None:
            producto.nombre = self._validar_no_vacio(nombre, "nombre del producto")

        if categoria_id is not None:
            self.asignar_categoria(prod_id, categoria_id, commit=False)

        db_session.commit()
        return True

    def asignar_categoria(self, producto_id, categoria_id, commit=True):
        producto = self.buscar_producto(producto_id)
        if not producto:
            raise ValueError(f"No existe producto con ID {producto_id}.")

        categoria = self.buscar_categoria(categoria_id)
        if not categoria:
            raise ValueError(f"No existe categoría con ID {categoria_id}.")

        producto.asignar_categoria(categoria)
        if commit:
            db_session.commit()
        return True

    def eliminar_producto(self, prod_id):
        producto = self.buscar_producto(prod_id)
        if not producto:
            raise ValueError(f"No existe producto con ID {prod_id}.")

        db_session.delete(producto)
        db_session.commit()
        return True
