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
