import smtplib
import os, io, dotenv
import pandas as pd
import json
import zmq
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

dotenv.load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "cs361.notifications@gmail.com"
SENDER_PASSWORD = os.getenv("GMAIL_APP_PW")         # add a .env file to the project root with:    GMAIL_APP_PW="secret-pw"  (secret-pw should be shared over discord)

def build_csv_part(filename: str, data: list[dict]) -> MIMEBase:
    """
    builds a MIME attachment from a list of dicts using pandas...
    this will likely be replaced by another microservice call later
    """
    buf = io.StringIO()
    pd.DataFrame(data).to_csv(buf, index=False)
    part = MIMEBase("text", "csv")
    part.set_payload(buf.getvalue().encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=filename)
    return part


def send_email(recipients:list[str], subject:str, html_body:str, csv_attachments:list[dict]=[]):
    """
    send an email to one or more people with html formatted body and optional CSV attachments.
    """
    try:
        # input validation
        if type(recipients) != list:
            raise Exception("The recipients parameter needs to be a list of addresses as strings")
        if type(subject) != str:
            raise Exception("The subject parameter needs to be a string")
        if type(html_body) != str:
            raise Exception("The html_body parameter needs to be a string")
        if not html_body.startswith("<html>") or not html_body.endswith("</html>"):
            raise Exception("Invalid HTML body. Ensure you wrap the body in <html></html>")
        if type(csv_attachments) != list:
            raise Exception("csv_attachments must be a list of dicts with 'filename' and 'data' keys")
        for attachment in csv_attachments:
            if "filename" not in attachment or "data" not in attachment:
                raise Exception("Each csv attachment must have 'filename' and 'data' keys")
            if not attachment["filename"].endswith(".csv"):
                raise Exception(f"Attachment filename '{attachment['filename']}' must end in .csv")
            if not isinstance(attachment["data"], list) or not all(isinstance(row, dict) for row in attachment["data"]):
                raise Exception(f"Attachment 'data' for '{attachment['filename']}' must be a list of dicts")

        # build smtp payload
        msg = MIMEMultipart("mixed")
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        for attachment in csv_attachments:
            msg.attach(build_csv_part(attachment["filename"], attachment["data"]))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, local_hostname="localhost") as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            send_result = server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
            # sendmail() returns a dict of emails it failed to send to or {} if no failures.
            if send_result:
                raise Exception(f"Failed to send the email to {len(send_result)} emails.")
            
            return {"status": "OK", "message": "Successfully sent the email!"}
    except Exception as e:
        return {"status": "FAILED", "message": str(e)}
    


# ---------------------------------------------------------------------
# Set up spike protocol
# Create environment, initialize socket, listen for request from client
# ---------------------------------------------------------------------
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")


# run until client program quits
while True:
    print("Waiting for request...")
    message = socket.recv()
    print("Received request:")

    # quit microservice running, close socket, break
    if message.decode() == "Q":
        socket.send_string("Email microservice shutting down.")
        break

    # unpack payload and call send_email
    email_attr = json.loads(message)
    recip, subject, body, attachments = email_attr
    confirmation = send_email(recip, subject, body, attachments)

    # return email confirmation message to client
    socket.send_json(confirmation)

# close connection and clean up environment on exit
context.destroy()

# example usage (attachments are optional)
"""
print(send_email(
    ["someone@example.com"],
    "Monthly Report",
    "<html><b>See attached.</b></html>",
    csv_attachments=[{
        "filename": "report.csv",
        "data": [
            {"name": "person1", "score": 95},
            {"name": "person2", "score": 87},
        ]
    }]
)
)
"""
