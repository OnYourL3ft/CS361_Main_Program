import sys
import zmq
import subprocess
import time

# start up the microservice...
email_process = subprocess.Popen([sys.executable, 'email_sending_microservice/email_microservice.py'])
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5557")
time.sleep(1)   # wait for ms to start



# the client side send function  of the micro service pipe
def send_data(data) -> dict:
    socket.send_json(data)
    return socket.recv_json()

# test email 1 data
recipients = ["trewenger@gmail.com"]
subject = "This is a test of the email microservice"
html_body = "<html>This is a test of the <b>body</b> of the email microservice.</html>"
csv_attachments = [{
    "filename":"test.csv",
    "data": [
        {"fname": "Tre", "lname": "Wenger"}
    ]
}]

# send an email with an attachment
response = send_data([recipients, subject, html_body, csv_attachments])
print(response)

# send simple email without attachments
response = send_data([["trewenger@gmail.com"], "test 2", "<html>example without attachments.</html>", []])
print(response)

# stop the microservice
socket.send_string("Q")
socket.recv_string()
email_process.wait()
