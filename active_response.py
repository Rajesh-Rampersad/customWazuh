import os
import sys
import json
import datetime
from pathlib import PureWindowsPath, PurePosixPath, Path

# Definir o caminho do arquivo JSON de acordo com o sistema operacional
# Em outros sistemas operacionais (Linux, macOS, etc.)
JSON_FILE = Path(
    "/home/rajesh/Documents/CustomActiveResponse/active_response.log")

OS_SUCCESS = 0
OS_INVALID = -1


def write_debug_file(ar_name, msg):
    with open(JSON_FILE, "a") as log_file:
        ar_name_posix = str(PurePosixPath(PureWindowsPath(
            ar_name[ar_name.find("active-response"):])))
        log_file.write(str(datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg + "\n")


def main():
    STDIN = Path(
        "/home/rajesh/Documents/CustomActiveResponse/stdin.json")
    try:
        with open(STDIN, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado: {STDIN}")
        sys.exit(OS_INVALID)
    except json.JSONDecodeError as e:
        print(f"Erro ao analisar o arquivo JSON: {e}")
        sys.exit(OS_INVALID)

    alert = json_data.get("parameters", {}).get("alert")
    if not alert:
        print("Erro: Alerta não encontrado no JSON")
        sys.exit(OS_INVALID)

    nivel = alert["rule"]["level"]
    keys = [alert["rule"]["id"]]
    if nivel >= 12:
        write_debug_file(sys.argv[0], f"Processing alert with rule ID: {keys}")

        # Personalizar o alerta escrevendo mais detalhes no arquivo de resultados
        result_file_path = "ar-test-result.txt"
        with open(result_file_path, mode="a") as test_file:
            test_file.write(
                "Active response triggered by rule ID: <" + str(keys) + ">\n")
            test_file.write(f"Descrição: {alert['rule']['description']}\n")
            test_file.write(f"Nível: {alert['rule']['level']}\n")
            test_file.write(
                f"Agente: {alert['agent']['name']} (ID: {alert['agent']['id']})\n")
            test_file.write(f"Localização: {alert['location']}\n")
            test_file.write(f"Log completo: {alert['full_log']}\n")
            test_file.write("----\n")

    sys.exit(OS_SUCCESS)


if __name__ == "__main__":
    main()
