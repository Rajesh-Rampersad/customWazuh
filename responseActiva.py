import os
import sys
import json
import datetime
from pathlib import PureWindowsPath, PurePosixPath, Path

# Definir o caminho do arquivo JSON de acordo com o sistema operacional
# Em outros sistemas operacionais (Linux, macOS, etc.)
JSON_FILE = Path(
    "/home/rajesh/Documents/CustomActiveResponse/active_response.log")

# Definir constantes para comandos e estados
ADD_COMMAND = 0
DELETE_COMMAND = 1
CONTINUE_COMMAND = 2
ABORT_COMMAND = 3
OS_SUCCESS = 0
OS_INVALID = -1


class Message:
    def __init__(self, alert=None, command=0):
        self.alert = alert or {}
        self.command = command


def write_debug_file(ar_name, msg):
    with open(JSON_FILE, "a") as log_file:
        ar_name_posix = str(PurePosixPath(PureWindowsPath(
            ar_name[ar_name.find("active-response"):])))
        log_file.write(str(datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg + "\n")


def setup_and_check_message(data):
    command = data.get("command")
    if command == "add":
        return Message(data.get("parameters", {}).get("alert"), ADD_COMMAND)
    elif command == "delete":
        return Message(data.get("parameters", {}).get("alert"), DELETE_COMMAND)
    else:
        write_debug_file(sys.argv[0], f'Comando não válido: {command}')
        return Message(command=OS_INVALID)


def send_keys_and_check_message(argv, keys):
    keys_msg = json.dumps({"version": 1, "origin": {"name": argv[0], "module": "active-response"},
                          "command": "check_keys", "parameters": {"keys": keys}})
    write_debug_file(argv[0], keys_msg)
    # Implementar a lógica para enviar chaves e verificar mensagens
    return CONTINUE_COMMAND


def main():
    STDIN = Path(
        "/home/rajesh/Documents/CustomActiveResponse/stdin.json")
    try:
        with open(STDIN, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado: {JSON_FILE}")
        sys.exit(OS_INVALID)
    except json.JSONDecodeError as e:
        print(f"Erro ao analisar o arquivo JSON: {e}")
        sys.exit(OS_INVALID)

    msg = setup_and_check_message(json_data)
    if msg.command == OS_INVALID:
        sys.exit(OS_INVALID)

    if msg.command == ADD_COMMAND:
        alert = msg.alert
        keys = [alert["rule"]["id"]]
        action = send_keys_and_check_message(sys.argv, keys)
        if action != CONTINUE_COMMAND:
            if action == ABORT_COMMAND:
                write_debug_file(sys.argv[0], "Abortado")
                sys.exit(OS_SUCCESS)
            else:
                write_debug_file(sys.argv[0], "Comando não válido")
                sys.exit(OS_INVALID)

        # Personalizar o alerta escrevendo mais detalhes no arquivo de resultados
        with open("ar-test-result.txt", mode="a") as test_file:
            test_file.write(
                "Active response triggered by rule ID: <" + str(keys) + ">\n")
            # test_file.write(f"Descrição: {alert['rule']['description']}\n")
            # test_file.write(f"Nível: {alert['rule']['level']}\n")
            # test_file.write(
            #     f"Agente: {alert['agent']['name']} (ID: {alert['agent']['id']})\n")
            # test_file.write(f"Localização: {alert['location']}\n")
            # test_file.write(f"Log completo: {alert['full_log']}\n")
            # test_file.write("----\n")

        # Considerar o nível de alerta para imprimir a mensagem
        nivel = alert["rule"]["level"]
        if nivel == 16:
            print(f"Alerta crítica: Nível {nivel}")
        elif nivel >= 10:
            print(f"Alerta importante: Nível {nivel}")
        else:
            print(f"Alerta de nível {nivel}")

    elif msg.command == DELETE_COMMAND:
        # Implementar a lógica para excluir o alerta
        if os.path.exists("ar-test-result.txt"):
            os.remove("ar-test-result.txt")

    else:
        write_debug_file(sys.argv[0], "Comando não válido")
        sys.exit(OS_INVALID)

    sys.exit(OS_SUCCESS)


if __name__ == "__main__":
    main()
