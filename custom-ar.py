import os
import sys
import json
import datetime
from pathlib import PureWindowsPath, PurePosixPath, Path

# Definir el archivo de registro
LOG_FILE = Path(
    "/home/rajesh/Documents/CustomActiveResponse/active_response.log")

# Definir constantes para comandos y estados
ADD_COMMAND = 0
DELETE_COMMAND = 1
CONTINUE_COMMAND = 2
ABORT_COMMAND = 3
OS_SUCCESS = 0
OS_INVALID = -1

# Clase para representar el mensaje


class Message:
    def __init__(self, alert=None, command=0):
        self.alert = alert or {}
        self.command = command

# Función para escribir en el archivo de registro


def write_debug_file(ar_name, msg):
    with open(LOG_FILE, "a") as log_file:
        ar_name_posix = str(PurePosixPath(PureWindowsPath(
            ar_name[ar_name.find("active-response"):])))
        log_file.write(str(datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg + "\n")

# Función para leer el mensaje JSON de la entrada estándar


def read_message():
    try:
        raw_message = input()
        return json.loads(raw_message)
    except json.JSONDecodeError as e:
        write_debug_file(
            sys.argv[0], f"Error al decodificar el mensaje JSON: {e}")
        return None

# Función para enviar el mensaje JSON a la salida estándar


def send_message(message):
    try:
        json_message = json.dumps(message)
        print(json_message)
        sys.stdout.flush()
    except json.JSONDecodeError as e:
        write_debug_file(
            sys.argv[0], f"Error al codificar el mensaje JSON: {e}")

# Función para configurar y verificar el mensaje


def setup_and_check_message(argv):
    # Leer el mensaje JSON de la entrada estándar
    try:
        raw_message = input()
        data = json.loads(raw_message)
    except json.JSONDecodeError as e:
        write_debug_file(argv[0], f"Error al decodificar el mensaje JSON: {e}")
        return Message(command=OS_INVALID)

    command = data.get("command")

    if command == "add":
        return Message(data.get("parameters", {}).get("alert"), ADD_COMMAND)
    elif command == "delete":
        return Message(data.get("parameters", {}).get("alert"), DELETE_COMMAND)
    else:
        write_debug_file(argv[0], 'Not valid command: ' + str(command))
        return Message(command=OS_INVALID)


def main(argv):

    write_debug_file(argv[0], "Started")

    # Validar el JSON y obtener el comando
    msg = setup_and_check_message(argv)

    if msg.command < 0:
        sys.exit(OS_INVALID)

    if msg.command == ADD_COMMAND:
        # Lógica para la acción 'add'

        # Obtener las claves necesarias para la acción
        alert = msg.alert
        keys = [alert["rule"]["id"]]

        # Crear el mensaje de control
        control_message = {
            "version": 1,
            "origin": {
                "name": argv[0],
                "module": "active-response"
            },
            "command": "check_keys",
            "parameters": {
                "keys": keys
            }
        }

        # Enviar el mensaje de control
        send_message(control_message)

        # Esperar la respuesta
        response = read_message()
        if response is None:
            sys.exit(OS_INVALID)

        # Analizar la respuesta
        action = response.get("command")
        if action != "continue":
            write_debug_file(argv[0], "Invalid command")
            sys.exit(OS_INVALID)

        # Ejecutar la acción personalizada
        with open("ar-test-result.txt", mode="a") as test_file:
            test_file.write(
                f"Active response triggered by rule ID: <{keys}>\n")

    elif msg.command == DELETE_COMMAND:
        # Lógica para la acción 'delete'

        # Eliminar el archivo si existe
        if Path("ar-test-result.txt").exists():
            os.remove("ar-test-result.txt")

    else:
        write_debug_file(argv[0], "Invalid command")

    write_debug_file(argv[0], "Ended")

    # Imprimir el nivel de alerta
    nivel = msg.alert["rule"]["level"]
    if nivel == 16:
        print(f"Alerta crítica: Nivel {nivel}")
    elif nivel >= 10:
        print(f"Alerta importante: Nivel {nivel}")
    else:
        print(f"Alerta de nivel {nivel}")

    sys.exit(OS_SUCCESS)


# Si se ejecuta como script principal
if __name__ == "__main__":
    main(sys.argv)
