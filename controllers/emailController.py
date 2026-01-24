import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.globals import APP_PASSWORD
from datetime import datetime

router = APIRouter()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "iamminhtran13102003@gmail.com"
SMTP_PASS = APP_PASSWORD

class SendMailDTO(BaseModel):
    to: str
    subject: str
    content: str

async def send_mail(data: SendMailDTO, emailCollection, is_html_template: bool = False):
    payload = data.model_dump()
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = payload["to"]
        msg["Subject"] = payload["subject"]
        msg.attach(MIMEText(payload["content"], "html" if is_html_template else "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        doc = {
            "to": payload["to"],
            "subject": payload["subject"],
            "content": payload["content"],
            "sent_at": datetime.utcnow(),
            "status": "sent"
        }

        emailCollection.insert_one(doc)

        return {"success": True}
    except Exception as e:
        doc = {
            "to": payload["to"],
            "subject": payload["subject"],
            "content": payload["content"],
            "sent_at": datetime.utcnow(),
            "status": "failed"
        }

        emailCollection.insert_one(doc)
        raise HTTPException(status_code=500, detail=str(e))    