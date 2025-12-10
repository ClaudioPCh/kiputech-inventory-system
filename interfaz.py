import os
import time
from dominio import Producto, StockInsuficienteError, HistorialVacioError, ProductoNoEncontradoError
from negocio import BusquedaPorCodigo, BusquedaPorNombre, OrdenarPorStockAsc, OrdenarPorStockDesc, OrdenarPorPrecioAsc, OrdenarPorPrecioDesc
from sistema import Inventario

# =============================================================================
# UTILIDADES DE CONSOLA
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



# =============================================================================
# EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    app = InterfazConsola()
    app.iniciar()

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

            if opcion == '1': self.pantalla_agregar()
            elif opcion == '2': self.pantalla_buscar()
            elif opcion == '3': self.pantalla_ordenar()
            elif opcion == '4': self.pantalla_eliminar()
            elif opcion == '5': self.pantalla_descontar()
            elif opcion == '6': self.pantalla_mostrar()
            elif opcion == '7': self.pantalla_importar()
            elif opcion == '8': self.pantalla_deshacer()
            elif opcion == '9':
                if self.pantalla_salir(): return




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

    def pantalla_agregar(self):
        imprimir_encabezado("AGREGAR PRODUCTO")
        print("Ingrese los datos del nuevo producto:")
        print("(El código se generará automáticamente)\n")
        
        nombre = input("Nombre    : ")
        categoria = input("Categoría : ")
        
        try:
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












    
# =============================================================================
# EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    app = InterfazConsola()
    app.iniciar()
