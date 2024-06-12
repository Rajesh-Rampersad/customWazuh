# crea un un scriptm para el envio de mensajes por correo electronico con formato
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Define email settings
SMTP_SERVER = "your_smtp_server"
SMTP_PORT = 587
FROM_EMAIL = "your_from_email"
PASSWORD = "your_password"
TO_EMAIL = "recipient_email"

# Define the message
SUBJECT = "Alerta importante"
BODY = """
<html>
  <head></head>
  <body>
    <h2>Alerta importante</h2>
    <p>Nível: {nivel}</p>
    <p>Descrição: {description}</p>
    <p>Agente: {agent_name} (ID: {agent_id})</p>
    <p>Localização: {location}</p>
    <p>Log completo: {full_log}</p>
  </body>
</html>
"""

# Define the alert data
nivel = 12
description = "This is a test alert"
agent_name = "Agent 1"
agent_id = 123
location = "Location 1"
full_log = "This is the full log"

# Replace placeholders with actual data
BODY = BODY.format(
    nivel=nivel,
    description=description,
    agent_name=agent_name,
    agent_id=agent_id,
    location=location,
    full_log=full_log
)

# Create the email message
msg = MIMEMultipart()
msg["From"] = FROM_EMAIL
msg["To"] = TO_EMAIL
msg["Subject"] = SUBJECT

# Add the HTML body
msg.attach(MIMEText(BODY, "html"))

# Send the email
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(FROM_EMAIL, PASSWORD)
server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
server.quit()

print("Email sent successfully!")
