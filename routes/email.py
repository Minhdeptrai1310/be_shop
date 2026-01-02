from fastapi import APIRouter, Depends
from controllers.emailController import SendMailDTO, send_mail
from database.collections import get_mail_collection
email = APIRouter()

@email.post("/send-mail")
async def sendMail(data: SendMailDTO, emailCollection=Depends(get_mail_collection)):
    return await send_mail(data, emailCollection)