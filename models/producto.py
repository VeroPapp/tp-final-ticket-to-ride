from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class CategoriaProducto(Base):
    __tablename__ = "categorias_producto"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)

    productos = relationship("Producto", back_populates="categoria")

    def asignar_producto(self, producto):
        producto.categoria = self
        return True


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    marca = Column(String(80))
    modelo = Column(String(80))
    codigo = Column(String(50), unique=True)
    categoria_id = Column(Integer, ForeignKey("categorias_producto.id"))

    categoria = relationship("CategoriaProducto", back_populates="productos")

    def asignar_categoria(self, categoria):
        self.categoria = categoria
        return True
