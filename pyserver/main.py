# Do not include this in AWS Lambda
# ====================================START======================================= #
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
# =====================================END====================================== #


import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from mangum import Mangum
from pydantic import BaseModel


def send_contact_email(name: str, email: str, subject: str, phone: str, message: str):
    smtp_server: str = os.getenv("ADMIN_EMAIL_HOST")
    port: int = int(os.getenv("ADMIN_EMAIL_PORT"))  # For starttls
    # port = 465  # For SSL
    password: str = os.getenv("ADMIN_EMAIL_HOST_PASSWORD")
    sender_email = os.getenv("ADMIN_EMAIL_USER")
    receiver_email = "mdshayon0@gmail.com"
    formatted_message = MIMEMultipart("alternative")
    formatted_message["Subject"] = "Contact request: " + subject
    formatted_message["From"] = sender_email
    formatted_message["To"] = receiver_email
    formatted_message.add_header("reply-to", email)

    # Create the plain-text and HTML version of your message
    text = "A new contact request is been sent"
    html = (
        f"<html>"
        + f"<body>"
        + f"<h4>name: {name}</h4>"
        + f"<h4>Subject: {subject}</h4>"
        + f"<h4>Phone: {phone}</h4>"
        + f"<h4>Email: {email}</h4>"
        + f"<br />"
        + f"<h4>Message</h4>"
        + f"<p style='color: rgb(24, 237, 70);'>{message}</p>"
        + f"</body>"
        + f"</html>"
    )

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    formatted_message.attach(part1)
    formatted_message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, formatted_message.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)


# send_email("abc", "msg", "Phone")

app = FastAPI(
    docs_url=None,  # Disable docs (Swagger UI)
    redoc_url=None,  # Disable redoc
)
handler = Mangum(app)


class SendEmailModal(BaseModel):
    name: str
    email: str
    subject: str
    phone: str
    message: str


@app.post("/api/sendemail")
def make_contact(send_email: SendEmailModal):
    name = send_email.name
    email = send_email.email
    subject = send_email.subject
    phone = send_email.phone
    message = send_email.message
    send_contact_email(
        name=name, email=email, subject=subject, phone=phone, message=message
    )
    json_compatible_data = jsonable_encoder(send_email)
    return JSONResponse(
        content=json_compatible_data, status_code=status.HTTP_201_CREATED
    )
