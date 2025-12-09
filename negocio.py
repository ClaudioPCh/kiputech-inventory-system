from abc import ABC, abstractmethod
from datetime import datetime
from dominio import StockInsuficienteError
# =============================================================================
# ESTRATEGIAS DE BÚSQUEDA
# =============================================================================
class Busqueda(ABC):
    @abstractmethod
    def buscar(self, lista_productos, valor): pass

class BusquedaPorCodigo(Busqueda):
    def buscar(self, lista_productos, valor):
        for p in lista_productos:
            if p.get_codigo().strip().upper() == valor.strip().upper():
                return p
        return None

class BusquedaPorNombre(Busqueda):
    def buscar(self, lista_productos, valor):
        return [p for p in lista_productos if valor.lower() in p.get_nombre().lower()]

# =============================================================================
# ESTRATEGIAS DE ORDENAMIENTO
# =============================================================================
class CriterioOrdenamiento(ABC):
    @abstractmethod
    def ordenar(self, lista_productos): pass

class OrdenarPorStockAsc(CriterioOrdenamiento):
    def ordenar(self, lista_productos): return sorted(lista_productos, key=lambda p: p.get_cantidad())

class OrdenarPorStockDesc(CriterioOrdenamiento):
    def ordenar(self, lista_productos): return sorted(lista_productos, key=lambda p: p.get_cantidad(), reverse=True)

class OrdenarPorPrecioAsc(CriterioOrdenamiento):
    def ordenar(self, lista_productos): return sorted(lista_productos, key=lambda p: p.get_precio())

class OrdenarPorPrecioDesc(CriterioOrdenamiento):
    def ordenar(self, lista_productos): return sorted(lista_productos, key=lambda p: p.get_precio(), reverse=True)


# =============================================================================
# COMANDOS (ACCIONES)
# =============================================================================
class Accion(ABC):
    def __init__(self):
        self._fecha = datetime.now()

    @abstractmethod
    def ejecutar(self, inventario): pass

    @abstractmethod
    def revertir(self, inventario): pass

    @abstractmethod
    def get_descripcion(self): pass


class AccionAgregarProducto(Accion):
    def __init__(self, producto):
        super().__init__()
        self.__producto = producto

    def ejecutar(self, inventario):
        inventario.get_productos_raw().append(self.__producto)

    def revertir(self, inventario):
        if self.__producto in inventario.get_productos_raw():
            inventario.get_productos_raw().remove(self.__producto)

    def get_descripcion(self):
        return f"Agregado: {self.__producto.get_nombre()}"


class AccionEliminarProducto(Accion):
    def __init__(self, producto):
        super().__init__()
        self.__producto = producto

    def ejecutar(self, inventario):
        if self.__producto in inventario.get_productos_raw():
            inventario.get_productos_raw().remove(self.__producto)

    def revertir(self, inventario):
        inventario.get_productos_raw().append(self.__producto)

    def get_descripcion(self):
        return f"Eliminación: {self.__producto.get_nombre()}"


class AccionDescontarStock(Accion):
    def __init__(self, producto, cantidad):
        super().__init__()
        self.__producto = producto
        self.__cantidad_descontada = cantidad
        self.__stock_anterior = 0

    def ejecutar(self, inventario):
        self.__stock_anterior = self.__producto.get_cantidad()

        if self.__producto.get_cantidad() < self.__cantidad_descontada:
            raise StockInsuficienteError(self.__producto.get_cantidad(), self.__cantidad_descontada)

        nuevo = self.__stock_anterior - self.__cantidad_descontada
        self.__producto.actualizarStock(nuevo)

    def revertir(self, inventario):
        self.__producto.actualizarStock(self.__stock_anterior)

    def get_descripcion(self):
        return f"Stock descontado: {self.__cantidad_descontada} uds. a {self.__producto.get_nombre()}"