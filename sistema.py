import os
import csv
from datetime import datetime
from dominio import Producto, ProductoNoEncontradoError, HistorialVacioError
from negocio import AccionAgregarProducto, AccionEliminarProducto, AccionDescontarStock, BusquedaPorCodigo

class ImportadorArchivo:
    def __init__(self):
        self.__fechaImportacion = datetime.now()

    def importarInventario(self, ruta_archivo):
        productos_leidos = []
        
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo '{ruta_archivo}' no fue encontrado en el sistema.")

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as f:
                lector_csv = csv.reader(f, delimiter=',')
                next(lector_csv, None) # Saltar encabezado
                
                for i, fila in enumerate(lector_csv, start=1):
                    try:
                        if len(fila) < 5: continue
                        
                        cod = fila[0]
                        nom = fila[1]
                        cat = fila[2]
                        cant = fila[3]
                        prec = fila[4]

                        prod = Producto(nom, cat, cant, prec, codigo=cod)
                        productos_leidos.append(prod)
                    except ValueError:
                        continue
            return productos_leidos

        except Exception as e:
            raise e

#==================================

class Inventario:
    def __init__(self):
        self.__productos = []
        self.__historialAcciones = []

    def get_productos_raw(self): return self.__productos

    def agregarProducto(self, producto):
        accion = AccionAgregarProducto(producto)
        accion.ejecutar(self)
        self.__historialAcciones.append(accion)

    def buscarProducto(self, estrategia, valor):
        return estrategia.buscar(self.__productos, valor)

    def eliminarProducto(self, producto):
        if producto not in self.__productos:
            raise ProductoNoEncontradoError("El producto que intenta eliminar no está en la lista.")
            
        accion = AccionEliminarProducto(producto)
        accion.ejecutar(self)
        self.__historialAcciones.append(accion)

    def descontarStock(self, producto, cantidad):
        accion = AccionDescontarStock(producto, cantidad)
        accion.ejecutar(self) 
        self.__historialAcciones.append(accion)
