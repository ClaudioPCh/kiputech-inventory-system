from abc import ABC, abstractmethod
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