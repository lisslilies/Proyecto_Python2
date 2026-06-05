# TRABAJO PRACTICO INTEGRADOR: BASE DE DATOS 

from datetime import datetime

# ==============================
# CONFIGURACIÓN DE ARCHIVOS
# ==============================

# Nombre de los archivos donde se guardan los datos:
ARCHIVO_EMPLEADOS = "empleados.txt"
ARCHIVO_HISTORIAL = "historial.txt"


# ==============================
# FUNCIONES DE ARCHIVOS
# ==============================

def cargar_empleados():
    """
    Lee el archivo empleados.txt y carga los datos en una lista de diccionarios.
    Cada empleado se guarda como un diccionario para poder acceder fácilmente a sus datos.
    """

    empleados = []

    try:
        with open(ARCHIVO_EMPLEADOS, "r") as f:
            for linea in f:
                # Separa los datos por coma:
                nombre, dias, fechas, estado = linea.strip().split(",")

                # Crea un diccionario por cada empleado:
                empleados.append({
                    "nombre": nombre,
                    "dias_disponibles": int(dias),  # convertimos a número
                    "fechas_reservadas": fechas,
                    "estado": estado
                })

    except:
        # Si el archivo no existe, devuelve lista vacía.
        pass

    return empleados


def guardar_empleados(empleados):
    """
    Guarda todos los empleados nuevamente en el archivo.
    Se usa después de modificar datos (por ejemplo, de restar días).
    """

    with open(ARCHIVO_EMPLEADOS, "w") as f:
        for emp in empleados:
            linea = f"{emp['nombre']},{emp['dias_disponibles']},{emp['fechas_reservadas']},{emp['estado']}\n"
            f.write(linea)


def registrar_historial(empleado, desde, hasta, resultado, motivo):
    """
    Guarda cada solicitud en historial.txt.
    Se usa tanto para aprobaciones como rechazos.
    """

    with open(ARCHIVO_HISTORIAL, "a") as f:
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        linea = f"{fecha_actual},{empleado},{desde},{hasta},{resultado},{motivo}\n"
        f.write(linea)


# ==============================
# FUNCIONES DEL SISTEMA
# ==============================

def buscar_empleado(nombre, empleados):
    """
    Busca un empleado por nombre (sin importar mayúsculas/minúsculas).
    """

    for emp in empleados:
        if emp["nombre"].lower() == nombre.lower():
            return emp

    return None


def ver_saldo():
    """
    Permite consultar los días disponibles de un empleado.
    """

    empleados = cargar_empleados()

    nombre = input("Ingrese su nombre: ")
    emp = buscar_empleado(nombre, empleados)

    if emp is None:
        print("\n❌ Empleado no encontrado.\n")
        return

    print(f"\n✅ Días disponibles: {emp['dias_disponibles']}\n")


def validar_saldo(dias_solicitados, disponibles):
    """
    Verifica que el empleado tenga suficientes días.
    """
    return dias_solicitados <= disponibles


def validar_fechas(fecha_desde, fecha_hasta, empleados):
    """
    Verifica que las fechas solicitadas no se superpongan con otras ya reservadas.
    """

    for emp in empleados:

        fechas = emp["fechas_reservadas"]

        # Si no tiene reservas, se ignora.
        if fechas == "---":
            continue

        try:
            # Separa fechas guardadas.
            desde, hasta = fechas.split("-")

            desde = datetime.strptime(desde.strip(), "%d/%m/%Y")
            hasta = datetime.strptime(hasta.strip(), "%d/%m/%Y")

            # Verifica si hay superposición.
            if fecha_desde <= hasta and fecha_hasta >= desde:
                return False

        except:
            continue

    return True


def solicitar_vacaciones():
    """
    Función principal del sistema.
    Maneja todo el flujo de solicitud de vacaciones.
    """

    empleados = cargar_empleados()

    nombre = input("Ingrese su nombre: ")
    emp = buscar_empleado(nombre, empleados)

    # Validación: empleado existe.
    if emp is None:
        print("\n❌ Empleado no encontrado.\n")

        registrar_historial(nombre, "-", "-", "RECHAZADO", "Empleado inexistente")
        return

    print(f"\nDías disponibles: {emp['dias_disponibles']}")

    desde = input("Desde (DD/MM/AAAA): ")
    hasta = input("Hasta (DD/MM/AAAA): ")

    # Validación de formato de fechas:
    try:
        fecha_desde = datetime.strptime(desde, "%d/%m/%Y")
        fecha_hasta = datetime.strptime(hasta, "%d/%m/%Y")

    except:
        print("\n❌ Formato de fecha inválido\n")

        registrar_historial(nombre, desde, hasta, "RECHAZADO", "Formato inválido")
        return

    # Calcula la cantidad de días:
    dias = (fecha_hasta - fecha_desde).days + 1

    print(f"\nDías solicitados: {dias}")

    # ==========================
    # GATEWAY 1 → VALIDAR SALDO
    # ==========================

    if not validar_saldo(dias, emp["dias_disponibles"]):
        print("\n❌ Saldo insuficiente\n")

        registrar_historial(nombre, desde, hasta, "RECHAZADO", "Saldo insuficiente")
        return

    # ==========================
    # GATEWAY 2 → VALIDAR FECHAS
    # ==========================

    if not validar_fechas(fecha_desde, fecha_hasta, empleados):
        print("\n❌ Fechas ocupadas\n")

        registrar_historial(nombre, desde, hasta, "RECHAZADO", "Fechas ocupadas")
        return

    # ==========================
    # APROBACIÓN
    # ==========================

    # Se actualizan los datos del empleado:
    emp["dias_disponibles"] -= dias
    emp["fechas_reservadas"] = f"{desde}-{hasta}"

    guardar_empleados(empleados)

    registrar_historial(nombre, desde, hasta, "APROBADO", "OK")

    print("\n✅ Vacaciones aprobadas\n")


def ver_historial():
    """
    Muestra todas las solicitudes registradas.
    """

    try:
        with open(ARCHIVO_HISTORIAL, "r") as f:
            print("\n===== HISTORIAL =====\n")

            for linea in f:
                print(linea.strip())

            print()

    except:
        print("\nNo hay historial\n")


# ==============================
# MENÚ PRINCIPAL
# ==============================

def main():
    """
    Menú interactivo del sistema.
    Permite al usuario elegir opciones.
    """

    while True:

        print("=================================")
        print(" BOT GESTOR DE VACACIONES")
        print("=================================")
        print("\n")
        print("¡Hola! Vamos a gestionar tus vacaciones...")
        print("1. Solicitar vacaciones")
        print("2. Ver saldo disponible")
        print("3. Ver historial")
        print("4. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            solicitar_vacaciones()

        elif opcion == "2":
            ver_saldo()

        elif opcion == "3":
            ver_historial()

        elif opcion == "4":
            print("\nSaliendo del sistema...\n")
            break

        else:
            print("\n❌ Opción inválida\n")


# ==============================
# INICIO DEL PROGRAMA
# ==============================

main()