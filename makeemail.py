from secrets_email import EMAIL_ADDRESS, APP_PSWD
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import traceback

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# This file is specific to the use case of the website. If you also want to be 
# emailed your own results, you must create a file called secrets_email.py in 
# the main directory. It must contain the following, in the case of emails: 
# EMAIL_ADDRESS, and APP_PSWD, set the terms of you gmail's insecure app 
# password system
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

Thank you so much for using this service! As someone who learned from open-source tools like this, it means a lot knowing people are engaging with something I built. My hope is that anyone interested in the field has their interest sparked by this program. If you have any questions, or want to contribute to the antenna part of the program, please email me at s7henry@ucsd.edu, and check out https://github.com/sandulhenry/hline_observation. 

- Sandul H.
"""
        msg.attach(MIMEText(body_string, 'plain'))
            
        filenames = ["freq_v_PSD.png", "heatmap.png", "threeDplot.png"]

        for fname in filenames:
            fpath = os.path.join(path, fname)
            if os.path.exists(fpath):
                with open(fpath, 'rb') as file:
                    attachment = MIMEApplication(file.read(), Name=fname)
                    attachment['Content-Disposition'] = f'attachment; filename="{fname}"'
                    msg.attach(attachment)
            else:
                print(f"Warning: File not found and skipped: {fpath}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, APP_PSWD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())

        print(f"Email sent to {recipient}. ")
    except Exception as e:
        print(f"Error thrown as {e}")
        traceback.print_exc()