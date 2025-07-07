from secrets_email import EMAIL_ADDRESS, APP_PSWD
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(recipient: str, hash):
    try:
        path = "/home/pi/Documents/HLINE/hline_observation/observations_img/" + str(hash) 
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = "Hydrogen Line observation " + str(hash)
        msg.attach(MIMEText("Attached are the results for your observation.", 'plain'))

        with open(path + "/freq_v_PSD.png", 'rb') as file:
            attachment = MIMEApplication(file.read(), Name=path + "/freq_v_PSD.png") # Specify desired filename in email
            msg.attach(attachment)
        with open(path + "/heatmap.png", 'rb') as file:
            attachment = MIMEApplication(file.read(), Name=path + "/heatmap.png") # Specify desired filename in email
            msg.attach(attachment)
        with open(path + "/threeDplot.png", 'rb') as file:
            attachment = MIMEApplication(file.read(), Name=path + "/threeDplot.png") # Specify desired filename in email
            msg.attach(attachment)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, APP_PSWD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())

        print("Email sent?")
    except Exception as e:
        print(f"Error thrown as {e}")

send_email("sandul.henry.05@gmail.com", 730308819060215494)