from datetime import datetime

# =============================================================================
# CLASE PRODUCTO
# =============================================================================

class Producto:
    _contador_id = 0

    def __init__(self, nombre, categoria, cantidad, precio, codigo=None):
        self.__nombre = nombre.strip()
        self.__categoria = categoria.strip()
        self.__cantidad = int(cantidad)
        self.__precio = float(precio)
        self.__fechaCreacion = datetime.now()
        self.__fechaUltimaModificacion = datetime.now()

    # Getters
    def get_codigo(self): return self.__codigo
    def get_nombre(self): return self.__nombre
    def get_categoria(self): return self.__categoria
    def get_cantidad(self): return self.__cantidad
    def get_precio(self): return self.__precio
    def get_fechaCreacion(self): return self.__fechaCreacion
    def get_fechaUltimaModificacion(self): return self.__fechaUltimaModificacion

    def set_cantidad(self, cantidad): 
        self.__cantidad = cantidad
        self.__fechaUltimaModificacion = datetime.now()

    def mostrarInfo(self):
        return f"{self.__codigo:<10} {self.__nombre:<20} {self.__categoria:<15} {self.__precio:<10.2f} {self.__cantidad:<5}"

    def actualizarStock(self, cantidad):
        self.__cantidad = cantidad
        self.__fechaUltimaModificacion = datetime.now()