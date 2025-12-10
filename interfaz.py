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






    
# =============================================================================
# EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    app = InterfazConsola()
    app.iniciar()
