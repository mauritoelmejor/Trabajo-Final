import sqlite3
# Intentar importar colorama para mejorar la interfaz (opcional)
try:
    from colorama import Fore, Style, init
    init(autoreset=True)  # Inicializar colorama y resetear colores automáticamente
    COLOR_TITULO = Fore.CYAN + Style.BRIGHT
    COLOR_OPCION = Fore.YELLOW
    COLOR_EXITO = Fore.GREEN
    COLOR_ERROR = Fore.RED
    COLOR_ADVERTENCIA = Fore.MAGENTA
except ImportError:
    # Si colorama no está instalado, usar cadenas vacías para no afectar la ejecución
    print("Módulo 'colorama' no encontrado. La interfaz se mostrará sin colores.")
    Fore = type('DummyFore', (object,), {'CYAN': '', 'YELLOW': '', 'GREEN': '', 'RED': '', 'MAGENTA': ''})
    Style = type('DummyStyle', (object,), {'BRIGHT': ''})
    init = lambda: None
    COLOR_TITULO = ''
    COLOR_OPCION = ''
    COLOR_EXITO = ''
    COLOR_ERROR = ''
    COLOR_ADVERTENCIA = ''

# --- Configuración de la Base de Datos ---

NOMBRE_DB = 'inventario.db'

def conectar_db():
    """Establece la conexión con la base de datos."""
    try:
        conn = sqlite3.connect(NOMBRE_DB)
        return conn
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}Error al conectar a la base de datos: {e}")
        return None

def crear_tabla():
    """Crea la tabla 'productos' si no existe."""
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    cantidad INTEGER NOT NULL,
                    precio REAL NOT NULL,
                    categoria TEXT
                )
            """)
            conn.commit()
            # print(f"{COLOR_EXITO}Tabla 'productos' verificada/creada correctamente.")
        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al crear la tabla: {e}")
        finally:
            conn.close()

# --- Funcionalidades de la Aplicación ---

def registrar_producto():
    """Permite al usuario registrar un nuevo producto."""
    print(f"\n{COLOR_TITULO}*** REGISTRAR NUEVO PRODUCTO ***")
    try:
        nombre = input("Nombre del producto (obligatorio): ").strip()
        if not nombre:
            print(f"{COLOR_ERROR}El nombre no puede estar vacío.")
            return

        descripcion = input("Descripción del producto: ").strip()

        try:
            cantidad = int(input("Cantidad disponible (obligatorio): "))
            if cantidad < 0:
                 print(f"{COLOR_ERROR}La cantidad no puede ser negativa.")
                 return
        except ValueError:
            print(f"{COLOR_ERROR}Cantidad inválida. Debe ser un número entero.")
            return

        try:
            precio = float(input("Precio del producto (obligatorio): "))
            if precio < 0:
                print(f"{COLOR_ERROR}El precio no puede ser negativo.")
                return
        except ValueError:
            print(f"{COLOR_ERROR}Precio inválido. Debe ser un número real.")
            return

        categoria = input("Categoría del producto: ").strip()

        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, descripcion, cantidad, precio, categoria))
                conn.commit()
                print(f"\n{COLOR_EXITO}Producto '{nombre}' registrado con éxito con ID: {cursor.lastrowid}")
            except sqlite3.Error as e:
                print(f"{COLOR_ERROR}Error al insertar el producto: {e}")
            finally:
                conn.close()

    except Exception as e:
        print(f"{COLOR_ERROR}Ocurrió un error inesperado durante el registro: {e}")


def visualizar_productos():
    """Muestra todos los productos registrados en la base de datos."""
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos ORDER BY id")
            productos = cursor.fetchall()

            print(f"\n{COLOR_TITULO}*** LISTA DE PRODUCTOS EN INVENTARIO ***")
            if not productos:
                print(f"{COLOR_ADVERTENCIA}No hay productos registrados.")
                return

            # Cabecera de la tabla
            print("-" * 90)
            print(f"{'ID':<4} {'Nombre':<20} {'Cantidad':<10} {'Precio':<10} {'Categoría':<15} {'Descripción'}")
            print("-" * 90)

            # Contenido de la tabla
            for prod in productos:
                id_prod, nombre, descripcion, cantidad, precio, categoria = prod
                # Limitar la descripción para que la tabla sea legible
                desc_corta = (descripcion[:30] + '...') if len(descripcion) > 33 else descripcion
                print(f"{id_prod:<4} {nombre:<20} {cantidad:<10} {precio:<10.2f} {categoria:<15} {desc_corta}")
            print("-" * 90)

        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al visualizar productos: {e}")
        finally:
            conn.close()


def actualizar_producto():
    """Permite actualizar la información de un producto por su ID."""
    print(f"\n{COLOR_TITULO}*** ACTUALIZAR PRODUCTO ***")
    try:
        producto_id = int(input("Ingrese el ID del producto a actualizar: "))
    except ValueError:
        print(f"{COLOR_ERROR}ID inválido. Debe ser un número entero.")
        return

    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar si el producto existe
            cursor.execute("SELECT nombre, cantidad, precio FROM productos WHERE id = ?", (producto_id,))
            producto = cursor.fetchone()

            if not producto:
                print(f"{COLOR_ADVERTENCIA}No se encontró ningún producto con ID {producto_id}.")
                return

            nombre_actual, cantidad_actual, precio_actual = producto
            print(f"\nProducto actual: {nombre_actual} (Cant: {cantidad_actual}, Precio: {precio_actual:.2f})")
            print("Deje el campo vacío si no desea modificarlo.")

            # Recopilar nuevos datos
            nuevo_nombre = input(f"Nuevo nombre ({nombre_actual}): ").strip() or nombre_actual
            nueva_descripcion = input("Nueva descripción: ").strip()

            nueva_cantidad_str = input(f"Nueva cantidad ({cantidad_actual}): ").strip()
            if nueva_cantidad_str:
                try:
                    nueva_cantidad = int(nueva_cantidad_str)
                    if nueva_cantidad < 0:
                        print(f"{COLOR_ERROR}La cantidad no puede ser negativa. Actualización cancelada.")
                        return
                except ValueError:
                    print(f"{COLOR_ERROR}Cantidad inválida. Actualización cancelada.")
                    return
            else:
                nueva_cantidad = cantidad_actual # Mantener el valor actual

            nuevo_precio_str = input(f"Nuevo precio ({precio_actual:.2f}): ").strip()
            if nuevo_precio_str:
                try:
                    nuevo_precio = float(nuevo_precio_str)
                    if nuevo_precio < 0:
                        print(f"{COLOR_ERROR}El precio no puede ser negativo. Actualización cancelada.")
                        return
                except ValueError:
                    print(f"{COLOR_ERROR}Precio inválido. Actualización cancelada.")
                    return
            else:
                nuevo_precio = precio_actual # Mantener el valor actual

            nueva_categoria = input("Nueva categoría: ").strip()

            # Construir la consulta de actualización
            campos_a_actualizar = []
            parametros = []

            # Solo agregar los campos que se modificaron o que se ingresaron
            if nuevo_nombre != nombre_actual:
                campos_a_actualizar.append("nombre = ?")
                parametros.append(nuevo_nombre)

            if nueva_descripcion or nueva_descripcion == "": # Acepta que se ingrese cadena vacía para limpiar
                campos_a_actualizar.append("descripcion = ?")
                parametros.append(nueva_descripcion)

            if nueva_cantidad_str: # Solo si se ingresó un valor (ya verificado)
                campos_a_actualizar.append("cantidad = ?")
                parametros.append(nueva_cantidad)

            if nuevo_precio_str: # Solo si se ingresó un valor (ya verificado)
                campos_a_actualizar.append("precio = ?")
                parametros.append(nuevo_precio)

            if nueva_categoria or nueva_categoria == "": # Acepta que se ingrese cadena vacía para limpiar
                campos_a_actualizar.append("categoria = ?")
                parametros.append(nueva_categoria)


            if not campos_a_actualizar:
                print(f"{COLOR_ADVERTENCIA}No se ingresaron cambios. Producto no actualizado.")
                return

            query = f"UPDATE productos SET {', '.join(campos_a_actualizar)} WHERE id = ?"
            parametros.append(producto_id)

            cursor.execute(query, tuple(parametros))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"\n{COLOR_EXITO}Producto con ID {producto_id} actualizado con éxito.")
            else:
                 print(f"{COLOR_ADVERTENCIA}No se pudo actualizar el producto (¿ID correcto?).")

        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al actualizar el producto: {e}")
        finally:
            conn.close()


def eliminar_producto():
    """Elimina un producto por su ID."""
    print(f"\n{COLOR_TITULO}*** ELIMINAR PRODUCTO ***")
    try:
        producto_id = int(input("Ingrese el ID del producto a eliminar: "))
    except ValueError:
        print(f"{COLOR_ERROR}ID inválido. Debe ser un número entero.")
        return

    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Obtener el nombre para el mensaje de confirmación
            cursor.execute("SELECT nombre FROM productos WHERE id = ?", (producto_id,))
            resultado = cursor.fetchone()

            if not resultado:
                print(f"{COLOR_ADVERTENCIA}No se encontró ningún producto con ID {producto_id}.")
                return

            nombre_producto = resultado[0]
            confirmacion = input(f"{COLOR_ADVERTENCIA}¿Está seguro que desea eliminar '{nombre_producto}' (ID {producto_id})? (s/N): ").lower()

            if confirmacion == 's':
                cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"\n{COLOR_EXITO}Producto '{nombre_producto}' (ID {producto_id}) eliminado con éxito.")
                else:
                    # Este caso es poco probable si ya se hizo el fetchone, pero es una buena práctica
                    print(f"{COLOR_ADVERTENCIA}No se pudo eliminar el producto. Verifique el ID.")
            else:
                print(f"{COLOR_ADVERTENCIA}Eliminación cancelada.")

        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al eliminar el producto: {e}")
        finally:
            conn.close()


def buscar_producto():
    """Permite buscar productos por ID, nombre o categoría."""
    print(f"\n{COLOR_TITULO}*** BUSCAR PRODUCTO ***")
    print(f"Opciones de búsqueda:")
    print(f"  {COLOR_OPCION}1{Style.RESET_ALL}. Buscar por ID")
    print(f"  {COLOR_OPCION}2{Style.RESET_ALL}. Buscar por Nombre")
    print(f"  {COLOR_OPCION}3{Style.RESET_ALL}. Buscar por Categoría")
    opcion = input("Seleccione una opción: ").strip()

    query = "SELECT * FROM productos WHERE "
    parametro = None
    columna = ""

    if opcion == '1':
        try:
            id_busqueda = int(input("Ingrese el ID del producto: "))
            query += "id = ?"
            parametro = (id_busqueda,)
            columna = "ID"
        except ValueError:
            print(f"{COLOR_ERROR}ID inválido. Debe ser un número entero.")
            return

    elif opcion == '2':
        nombre_busqueda = input("Ingrese parte del nombre del producto: ").strip()
        if not nombre_busqueda:
            print(f"{COLOR_ERROR}El nombre no puede estar vacío.")
            return
        query += "nombre LIKE ?"
        parametro = (f"%{nombre_busqueda}%",)
        columna = "Nombre"

    elif opcion == '3':
        categoria_busqueda = input("Ingrese la categoría del producto: ").strip()
        if not categoria_busqueda:
            print(f"{COLOR_ERROR}La categoría no puede estar vacía.")
            return
        query += "categoria LIKE ?"
        parametro = (f"%{categoria_busqueda}%",)
        columna = "Categoría"
    else:
        print(f"{COLOR_ERROR}Opción no válida.")
        return

    conn = conectar_db()
    if conn and parametro:
        try:
            cursor = conn.cursor()
            cursor.execute(query, parametro)
            productos = cursor.fetchall()

            print(f"\n{COLOR_TITULO}*** RESULTADOS DE BÚSQUEDA por {columna} ***")
            if not productos:
                print(f"{COLOR_ADVERTENCIA}No se encontraron productos con el criterio de búsqueda.")
                return

            # Cabecera de la tabla (igual que en visualizar)
            print("-" * 90)
            print(f"{'ID':<4} {'Nombre':<20} {'Cantidad':<10} {'Precio':<10} {'Categoría':<15} {'Descripción'}")
            print("-" * 90)

            for prod in productos:
                id_prod, nombre, descripcion, cantidad, precio, categoria = prod
                desc_corta = (descripcion[:30] + '...') if len(descripcion) > 33 else descripcion
                print(f"{id_prod:<4} {nombre:<20} {cantidad:<10} {precio:<10.2f} {categoria:<15} {desc_corta}")
            print("-" * 90)

        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al buscar productos: {e}")
        finally:
            conn.close()


def reporte_stock_bajo():
    """Genera un reporte de productos con stock igual o inferior a un límite."""
    print(f"\n{COLOR_TITULO}*** REPORTE DE STOCK BAJO ***")
    try:
        limite = int(input("Ingrese el límite máximo de cantidad para el reporte (Ej: 10): "))
        if limite < 0:
            print(f"{COLOR_ERROR}El límite no puede ser negativo.")
            return
    except ValueError:
        print(f"{COLOR_ERROR}Límite inválido. Debe ser un número entero.")
        return

    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Seleccionar productos donde la cantidad es menor o igual al límite
            cursor.execute("SELECT id, nombre, cantidad, categoria FROM productos WHERE cantidad <= ? ORDER BY cantidad ASC", (limite,))
            productos = cursor.fetchall()

            print(f"\n{COLOR_TITULO}*** PRODUCTOS CON STOCK <= {limite} UNIDADES ***")
            if not productos:
                print(f"{COLOR_EXITO}¡Inventario saludable! No hay productos con stock igual o inferior a {limite}.")
                return

            # Cabecera del reporte
            print("-" * 60)
            print(f"{'ID':<4} {'Nombre':<30} {'Cantidad':<10} {'Categoría':<10}")
            print("-" * 60)

            # Contenido del reporte
            for id_prod, nombre, cantidad, categoria in productos:
                # Usar color de advertencia para destacar el stock bajo
                color_linea = COLOR_ADVERTENCIA if cantidad <= limite else ""
                print(f"{color_linea}{id_prod:<4} {nombre:<30} {cantidad:<10} {categoria:<10}{Style.RESET_ALL}")
            print("-" * 60)
            print(f"{COLOR_ADVERTENCIA}Se encontraron {len(productos)} productos con stock bajo.")

        except sqlite3.Error as e:
            print(f"{COLOR_ERROR}Error al generar el reporte: {e}")
        finally:
            conn.close()

# --- Interfaz de Usuario (Terminal) ---

def mostrar_menu():
    """Muestra el menú principal de la aplicación."""
    print(f"\n{COLOR_TITULO}========================================")
    print(f"|    SISTEMA DE GESTIÓN DE INVENTARIO    |")
    print(f"========================================")
    print(f"  {COLOR_OPCION}1{Style.RESET_ALL}. Registrar nuevo producto")
    print(f"  {COLOR_OPCION}2{Style.RESET_ALL}. Visualizar todos los productos")
    print(f"  {COLOR_OPCION}3{Style.RESET_ALL}. Actualizar producto (por ID)")
    print(f"  {COLOR_OPCION}4{Style.RESET_ALL}. Eliminar producto (por ID)")
    print(f"  {COLOR_OPCION}5{Style.RESET_ALL}. Buscar producto")
    print(f"  {COLOR_OPCION}6{Style.RESET_ALL}. Reporte de stock bajo")
    print(f"  {COLOR_OPCION}0{Style.RESET_ALL}. Salir")
    print("-" * 40)

def main():
    """Función principal que ejecuta el programa."""
    crear_tabla() # Asegurar que la tabla exista al iniciar

    while True:
        mostrar_menu()
        opcion = input(f"Ingrese su opción ({COLOR_OPCION}0-6{Style.RESET_ALL}): ").strip()

        if opcion == '1':
            registrar_producto()
        elif opcion == '2':
            visualizar_productos()
        elif opcion == '3':
            actualizar_producto()
        elif opcion == '4':
            eliminar_producto()
        elif opcion == '5':
            buscar_producto()
        elif opcion == '6':
            reporte_stock_bajo()
        elif opcion == '0':
            print(f"\n{COLOR_TITULO}¡Gracias por usar el Sistema de Inventario! Hasta pronto.")
            break
        else:
            print(f"{COLOR_ERROR}Opción no válida. Por favor, intente de nuevo.")
        
        # Pausa para que el usuario pueda ver los resultados antes de limpiar
        if opcion != '0':
            input(f"\nPresione {COLOR_OPCION}ENTER{Style.RESET_ALL} para continuar al menú...")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()