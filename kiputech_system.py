import os
import time
import csv
from abc import ABC, abstractmethod
from datetime import datetime


# =============================================================================
# EXCEPCIONES PERSONALIZADAS (NAMED EXCEPTIONS)
# =============================================================================

class InventarioError(Exception):
    """Clase base para excepciones del inventario."""
    pass


class StockInsuficienteError(InventarioError):
    """Se lanza cuando se intenta descontar más stock del disponible."""

    def __init__(self, stock_actual, cantidad_solicitada):
        self.stock_actual = stock_actual
        self.cantidad_solicitada = cantidad_solicitada
        super().__init__(f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad_solicitada}")


class HistorialVacioError(InventarioError):
    """Se lanza cuando se intenta deshacer y no hay acciones previas."""
    pass


class ProductoNoEncontradoError(InventarioError):
    """Se lanza cuando una operación requiere un producto que no existe."""
    pass


# =============================================================================
# CAPA DE LÓGICA DE NEGOCIO
# =============================================================================

class Producto:
    _contador_id = 0

    def __init__(self, nombre, categoria, cantidad, precio, codigo=None):
        if not codigo or codigo.strip() == "":
            Producto._contador_id += 1
            self.__codigo = f"P{Producto._contador_id:03d}"
        else:
            self.__codigo = codigo.strip()
            self.__actualizar_contador(self.__codigo)

        self.__nombre = nombre.strip()
        self.__categoria = categoria.strip()
        self.__cantidad = int(cantidad)
        self.__precio = float(precio)
        self.__fechaCreacion = datetime.now()
        self.__fechaUltimaModificacion = datetime.now()

    @classmethod
    def __actualizar_contador(cls, codigo_existente):
        try:
            nums = ''.join(filter(str.isdigit, codigo_existente))
            if nums:
                numero = int(nums)
                if numero > cls._contador_id:
                    cls._contador_id = numero
        except ValueError:
            pass

    # Getters
    def get_codigo(self):
        return self.__codigo

    def get_nombre(self):
        return self.__nombre

    def get_categoria(self):
        return self.__categoria

    def get_cantidad(self):
        return self.__cantidad

    def get_precio(self):
        return self.__precio

    def get_fechaCreacion(self):
        return self.__fechaCreacion

    def get_fechaUltimaModificacion(self):
        return self.__fechaUltimaModificacion

    def set_cantidad(self, cantidad):
        self.__cantidad = cantidad
        self.__fechaUltimaModificacion = datetime.now()

    def mostrarInfo(self):
        return f"{self.__codigo:<10} {self.__nombre:<20} {self.__categoria:<15} {self.__precio:<10.2f} {self.__cantidad:<5}"

    def actualizarStock(self, cantidad):
        self.__cantidad = cantidad
        self.__fechaUltimaModificacion = datetime.now()


# --- ESTRATEGIAS DE BÚSQUEDA ---
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


# --- ESTRATEGIAS DE ORDENAMIENTO ---
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


# --- COMANDOS (ACCIONES) ---
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

        # Validación con Excepción Personalizada
        if self.__producto.get_cantidad() < self.__cantidad_descontada:
            raise StockInsuficienteError(self.__producto.get_cantidad(), self.__cantidad_descontada)

        nuevo = self.__stock_anterior - self.__cantidad_descontada
        self.__producto.actualizarStock(nuevo)

    def revertir(self, inventario):
        self.__producto.actualizarStock(self.__stock_anterior)

    def get_descripcion(self):
        return f"Stock descontado: {self.__cantidad_descontada} uds. a {self.__producto.get_nombre()}"


# --- IMPORTADOR REAL ---
class ImportadorArchivo:
    def __init__(self):
        self.__fechaImportacion = datetime.now()

    def importarInventario(self, ruta_archivo):
        productos_leidos = []

        # Validación con Excepción Estándar de Python
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo '{ruta_archivo}' no fue encontrado en el sistema.")

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as f:
                lector_csv = csv.reader(f, delimiter=',')
                next(lector_csv, None)  # Saltar encabezado

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
            # Re-lanzamos errores de lectura inesperados
            raise e

        # --- CONTROLADOR PRINCIPAL: INVENTARIO ---


class Inventario:
    def __init__(self):
        self.__productos = []
        self.__historialAcciones = []

    def get_productos_raw(self):
        return self.__productos

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
        # La validación de stock está dentro de Accion.ejecutar,
        # así que aquí solo necesitamos instanciar y ejecutar.
        accion = AccionDescontarStock(producto, cantidad)
        accion.ejecutar(self)  # Esto puede lanzar StockInsuficienteError
        self.__historialAcciones.append(accion)

    def ordenarInventario(self, criterio):
        return criterio.ordenar(self.__productos)

    def importarDesdeArchivo(self, ruta):
        imp = ImportadorArchivo()
        # Esta llamada puede lanzar FileNotFoundError
        lista = imp.importarInventario(ruta)

        count = 0
        duplicados = 0
        for p in lista:
            existe = self.buscarProducto(BusquedaPorCodigo(), p.get_codigo())
            if not existe:
                self.agregarProducto(p)
                count += 1
            else:
                duplicados += 1
        return count, duplicados

    def get_ultima_accion(self):
        if self.__historialAcciones:
            return self.__historialAcciones[-1]
        return None

    def revertirUltimaAccion(self):
        if not self.__historialAcciones:
            raise HistorialVacioError("No existen acciones previas para deshacer.")

        accion = self.__historialAcciones.pop()
        accion.revertir(self)
        return True


# =============================================================================
# CAPA DE INTERFAZ DE USUARIO (CONSOLA)
# =============================================================================

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def imprimir_encabezado(titulo):
    limpiar_pantalla()
    print("-" * 75)
    print(f"{titulo:^75}")
    print("-" * 75)
    print()


def pausa():
    print()
    input("[Enter] Para continuar...")


class InterfazConsola:
    def __init__(self):
        self.inv = Inventario()
        # Datos de prueba iniciales
        self.inv.agregarProducto(Producto("Laptop Base", "Tecnologia", 5, 2000.00, codigo="P000"))

    def iniciar(self):
        while True:
            limpiar_pantalla()
            print("-" * 60)
            print("     SISTEMA DE GESTIÓN DE INVENTARIOS  -  KIPUTECH")
            print("-" * 60)
            print("Bienvenido al sistema de gestión de inventarios de Kiputech.\n")
            print("[1] Ingresar al sistema")
            print("[2] Salir\n")
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.menu_principal()
            elif opcion == '2':
                limpiar_pantalla()
                print("Gracias por usar el sistema.")
                break

    def menu_principal(self):
        while True:
            imprimir_encabezado("MENÚ PRINCIPAL - KIPUTECH")
            print("[1] Agregar producto")
            print("[2] Buscar producto")
            print("[3] Ordenar inventario")
            print("[4] Eliminar producto")
            print("[5] Descontar stock")
            print("[6] Mostrar inventario")
            print("[7] Importar inventario desde archivo")
            print("[8] Deshacer última acción")
            print("[9] Salir")
            print("-" * 75)

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.pantalla_agregar()
            elif opcion == '2':
                self.pantalla_buscar()
            elif opcion == '3':
                self.pantalla_ordenar()
            elif opcion == '4':
                self.pantalla_eliminar()
            elif opcion == '5':
                self.pantalla_descontar()
            elif opcion == '6':
                self.pantalla_mostrar()
            elif opcion == '7':
                self.pantalla_importar()
            elif opcion == '8':
                self.pantalla_deshacer()
            elif opcion == '9':
                if self.pantalla_salir(): return

    def pantalla_agregar(self):
        imprimir_encabezado("AGREGAR PRODUCTO")
        print("Ingrese los datos del nuevo producto:")
        print("(El código se generará automáticamente)\n")

        nombre = input("Nombre    : ")
        categoria = input("Categoría : ")

        try:
            # TRY-EXCEPT para validar entradas numéricas
            precio_str = input("Precio    : ")
            stock_str = input("Stock     : ")

            precio = float(precio_str)
            stock = int(stock_str)

            if precio < 0 or stock < 0:
                raise ValueError("Los valores no pueden ser negativos.")

            print("\n[1] Guardar producto")
            print("[2] Cancelar y volver al menú")
            opc = input("\nOpción: ")

            if opc == '1':
                nuevo = Producto(nombre, categoria, stock, precio)
                self.inv.agregarProducto(nuevo)
                print(f"\nMensaje: Producto registrado correctamente.")
                print(f"CÓDIGO ASIGNADO: {nuevo.get_codigo()}")
                pausa()
            else:
                return

        except ValueError as e:
            # Captura error de conversión (str -> int/float) o valores negativos
            print(f"\n[ERROR DE ENTRADA]: Dato inválido. {e}")
            pausa()

    def pantalla_buscar(self):
        imprimir_encabezado("BUSCAR PRODUCTO")
        print("Seleccione tipo de búsqueda:\n")
        print("[1] Buscar por CÓDIGO (Ver todos los detalles)")
        print("[2] Buscar por NOMBRE (Ver lista resumen)")
        print("[3] Volver al menú")

        opc = input("\nOpción: ")

        if opc == '1':
            cod = input("\nIngrese código del producto: ")
            res = self.inv.buscarProducto(BusquedaPorCodigo(), cod)
            print("\nResultado:")
            if res:
                print("-" * 40)
                print(f"Código       : {res.get_codigo()}")
                print(f"Nombre       : {res.get_nombre()}")
                print(f"Categoría    : {res.get_categoria()}")
                print(f"Precio       : {res.get_precio():.2f}")
                print(f"Stock        : {res.get_cantidad()}")
                print(f"Fecha Creac. : {res.get_fechaCreacion().strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"Ult. Modif.  : {res.get_fechaUltimaModificacion().strftime('%d/%m/%Y %H:%M:%S')}")
                print("-" * 40)
            else:
                print("Mensaje: No se encontró ningún producto con ese criterio.")
            pausa()

        elif opc == '2':
            nom = input("\nIngrese nombre del producto: ")
            res = self.inv.buscarProducto(BusquedaPorNombre(), nom)
            print(f"\nSe encontraron {len(res)} coincidencias:")
            if res:
                print(f"\n{'Código':<10} {'Nombre':<20} {'Categoría':<15} {'Precio':<10} {'Stock':<5}")
                print("-" * 65)
                for p in res:
                    print(p.mostrarInfo())
            else:
                print("No hubo resultados.")
            pausa()

    def pantalla_ordenar(self):
        imprimir_encabezado("ORDENAR INVENTARIO")
        print("Seleccione criterio de orden:\n")
        print("[1] Ordenar por STOCK (menor a mayor)")
        print("[2] Ordenar por STOCK (mayor a menor)")
        print("[3] Ordenar por PRECIO (menor a mayor)")
        print("[4] Ordenar por PRECIO (mayor a menor)")
        print("[5] Volver al menú")

        opc = input("\nOpción: ")
        criterio = None

        if opc == '1':
            criterio = OrdenarPorStockAsc()
        elif opc == '2':
            criterio = OrdenarPorStockDesc()
        elif opc == '3':
            criterio = OrdenarPorPrecioAsc()
        elif opc == '4':
            criterio = OrdenarPorPrecioDesc()
        elif opc == '5':
            return

        if criterio:
            lista = self.inv.ordenarInventario(criterio)
            print("\nMensaje: Inventario ordenado correctamente.")
            print("\nListado (resumen):")
            print(f"{'Código':<10} {'Nombre':<20} {'Categoría':<15} {'Precio':<10} {'Stock':<5}")
            print("-" * 65)
            for p in lista:
                print(p.mostrarInfo())
            pausa()

    def pantalla_eliminar(self):
        imprimir_encabezado("ELIMINAR PRODUCTO")
        cod = input("Ingrese el código del producto a eliminar: ")
        prod = self.inv.buscarProducto(BusquedaPorCodigo(), cod)

        if prod:
            print("\nDatos del producto:")
            print(f"Código   : {prod.get_codigo()}")
            print(f"Nombre   : {prod.get_nombre()}")

            print("\n¿Desea eliminar este producto?")
            print("[1] Sí, eliminar")
            print("[2] No, cancelar")

            confirm = input("\nOpción: ")
            if confirm == '1':
                try:
                    # TRY-EXCEPT para operaciones lógicas
                    self.inv.eliminarProducto(prod)
                    print("\nMensaje: Producto eliminado correctamente.")
                except ProductoNoEncontradoError as e:
                    print(f"\n[ERROR LÓGICO]: {e}")
            else:
                print("\nOperación cancelada.")
        else:
            print("\nError: Producto no encontrado.")
        pausa()

    def pantalla_descontar(self):
        imprimir_encabezado("DESCONTAR STOCK DE PRODUCTO")
        cod = input("Ingrese código del producto: ")
        prod = self.inv.buscarProducto(BusquedaPorCodigo(), cod)

        if not prod:
            print("\nError: Producto no encontrado.")
            pausa()
            return

        try:
            cant_str = input("Ingrese cantidad a descontar: ")
            cant = int(cant_str)
            if cant <= 0:
                raise ValueError("La cantidad debe ser mayor a 0.")

            print("\nVerificando stock...")
            time.sleep(0.5)

            # TRY-EXCEPT principal para lógica de negocio
            stock_ant = prod.get_cantidad()
            self.inv.descontarStock(prod, cant)

            print("\nMensaje: Stock actualizado correctamente.")
            print(f"Stock anterior: {stock_ant}")
            print(f"Stock actual  : {prod.get_cantidad()}")

        except ValueError as e:
            print(f"\n[ERROR DE ENTRADA]: {e}")
        except StockInsuficienteError as e:
            print(f"\n[ERROR DE NEGOCIO]: {e}")
            print("(No se realizó ningún descuento).")

        pausa()

    def pantalla_mostrar(self):
        imprimir_encabezado("INVENTARIO ACTUAL")
        lista = self.inv.get_productos_raw()

        print(f"{'Código':<10} {'Nombre':<20} {'Categoría':<15} {'Precio':<10} {'Stock':<5}")
        print("-" * 65)

        if not lista:
            print("Inventario vacío.")
        else:
            for p in lista:
                print(p.mostrarInfo())

        print(f"\nTotal de productos: {len(lista)}")
        print("\n[Enter] Volver al menú principal")
        input()

    def pantalla_importar(self):
        imprimir_encabezado("IMPORTAR INVENTARIO DESDE ARCHIVO")

        print("Ingrese el nombre/ruta del archivo CSV (ej: inventario.csv).")
        print("El archivo debe existir en su equipo.\n")

        ruta = input("Nombre del archivo: ").strip()

        print(f"\nBuscando archivo: {ruta} ...")
        time.sleep(0.5)

        try:
            # TRY-EXCEPT para manejo de archivos
            agregados, duplicados = self.inv.importarDesdeArchivo(ruta)

            print("\nProcesando...")
            time.sleep(0.5)
            print("\nMensaje final:")
            print(f"\"Importación completada. {agregados} nuevos agregados, {duplicados} omitidos por duplicidad.\"")

        except FileNotFoundError as e:
            # Captura específica de archivo no encontrado
            print(f"\n[ERROR DE ARCHIVO]: {e}")
            print("Por favor verifique la ruta e intente nuevamente.")
        except Exception as e:
            # Captura genérica por si el archivo está corrupto, etc.
            print(f"\n[ERROR INESPERADO]: Ocurrió un problema al leer el archivo.")
            print(f"Detalle: {e}")

        print("\n[Enter] Volver al menú principal")
        input()

    def pantalla_deshacer(self):
        imprimir_encabezado("DESHACER ÚLTIMA ACCIÓN")
        ultima = self.inv.get_ultima_accion()

        if ultima:
            print("Última acción registrada:")
            print(f"Detalle   : {ultima.get_descripcion()}")
            print(f"Fecha/Hora: {ultima._fecha.strftime('%d/%m/%Y %H:%M')}")

            print("\n¿Desea revertir esta acción?")
            print("[1] Sí, deshacer")
            print("[2] No, cancelar")

            opc = input("\nOpción: ")
            if opc == '1':
                try:
                    # TRY-EXCEPT para lógica de historial
                    self.inv.revertirUltimaAccion()
                    print("\nMensaje: Acción revertida correctamente.")
                except HistorialVacioError as e:
                    print(f"\n[ERROR]: {e}")
            else:
                print("Operación cancelada.")
        else:
            print("\nMensaje: No hay acciones disponibles para deshacer.")
        pausa()

    def pantalla_salir(self):
        imprimir_encabezado("SALIR DEL SISTEMA")
        print("¿Está seguro que desea salir?\n")
        print("[1] Sí, salir")
        print("[2] No, volver al menú")

        opc = input("\nOpción: ")
        if opc == '1':
            print("\nGracias por usar el Sistema de Gestión de Inventarios de Kiputech.")
            return True
        return False


# =============================================================================
# EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    app = InterfazConsola()
    app.iniciar()