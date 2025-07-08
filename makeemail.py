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

        body_string = f"""\
Attached are the results of your observation.

Your experiment ID is: {hash}

Included attachments:
- A 3D plot of Time vs Frequency vs Relative Gain
- A heatmap of Time vs Frequency vs Relative Gain (color-coded)
- A 2D plot of Frequency vs PSD for every iteration in your experiment

Thank you so much for using this service! As someone who learned from open-source tools like this, it means a lot knowing people are engaging with something I built.

- Sandul H.
"""
        msg.attach(MIMEText(body_string, 'plain'))

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

        print(f"Email sent to {recipient}. ")
    except Exception as e:
        print(f"Error thrown as {e}")