# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.
# with open(textfile) as fp:
#     # Create a text/plain message
#     msg = EmailMessage()
#     msg.set_content(fp.read())

def sendIt(message):
    msg = EmailMessage()
    msg.set_content(message)
    # me == the sender's email address
    recipients = ["flexmethods@gmail.com", "sean.inbox@yahoo.com"]
    msg['Subject'] = "A new contestant entered the Tulip Contest"
    msg['From'] = "contest@whitechapelcemetery.com"
    msg['To'] = ", ".join(recipients)

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    return
