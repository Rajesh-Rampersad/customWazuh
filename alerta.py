import os
import sys
import json
import datetime
from pathlib import PureWindowsPath, PurePosixPath, Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Definir o caminho do arquivo JSON de acordo com o sistema operacional
JSON_FILE = Path(
    "/home/rajesh/Documents/CustomActiveResponse/active_response.log")

OS_SUCCESS = 0
OS_INVALID = -1


def write_debug_file(ar_name, msg):
    # Grava informações de depuração no arquivo JSON
    with open(JSON_FILE, "a") as log_file:
        # Converte o caminho do Windows em um caminho POSIX para registro
        ar_name_posix = str(PurePosixPath(PureWindowsPath(
            ar_name[ar_name.find("active-response"):])))
        # Escreva a entrada de log com o carimbo de data/hora atual, nome AR e mensagem
        log_file.write(str(datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg + "\n")


def send_email(subject, body, recipients):
    # Obtenha os valores de usuário e senha do arquivo.env
    user = os.environ['GMAIL_USER']
    password = os.environ['GMAIL_PASSWORD']
    sender = os.environ['SENDER_EMAIL']

    # Personalizar o assunto e o cuerpo del correo electrónico

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    # Anexe o corpo HTML à mensagem
    msg.attach(MIMEText(body, "html"))

    try:
      # Estabeleça uma conexão SMTP com o Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # Iniciar criptografia TLS
        server.starttls()
        # Faça login na conta do Gmail
        server.login(user, password)
        # Envie o e-mail para os destinatários
        server.sendmail(sender, recipients, msg.as_string())
        # Saia da conexão SMTP
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")
        print(f"Failed to send email: {e}")


def main():
    # Carrega variáveis ​​de ambiente do arquivo .env
    os.environ.update(dict(line.split('=') for line in open('.env')))

    # Carrega o arquivo JSON de entrada
    # Defina o caminho para o arquivo STDIN JSON
    STDIN = Path("/home/rajesh/Documents/CustomActiveResponse/stdin.json")
    try:
        with open(STDIN, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado: {STDIN}")
        sys.exit(OS_INVALID)
    except json.JSONDecodeError as e:
        print(f"Erro ao analisar o arquivo JSON: {e}")
        sys.exit(OS_INVALID)

    # Extraia os dados do alerta do JSON
    alert = json_data.get("parameters", {}).get("alert")
    if not alert:
        print("Erro: Alerta não encontrado no JSON")
        sys.exit(OS_INVALID)

    # Extraia o nível de regra e o ID dos dados de alerta
    nivel = alert["rule"]["level"]
    keys = [alert["rule"]["id"]]
    if nivel >= 12:
        write_debug_file(sys.argv[0], f"Processing alert with rule ID: {keys}")

        # Personalizar a alerta escrevendo mais detalhes no arquivo de resultados
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

        # Preparar o corpo do e-mail

        body = f"""
        <html>
          <head></head>
          <body>
            <h2>Alerta importante</h2>
            <p>Nível: {alert['rule']['level']}</p>
            <p>Descrição: {alert['rule']['description']}</p>
            <p>Agente: {alert['agent']['name']} (ID: {alert['agent']['id']})</p>
            <p>Localização: {alert['location']}</p>
            <p>Log completo: {alert['full_log']}</p>
          </body>
        </html>
        """

        # Lista de destinatarios
        recipients = os.environ['RECIPIENTS'].split(',')
        send_email("Alerta importante", body, recipients)

    sys.exit(OS_SUCCESS)


if __name__ == "__main__":
    main()
