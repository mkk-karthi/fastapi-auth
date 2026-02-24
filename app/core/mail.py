from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
from typing import Optional
from loguru import logger
from pydantic import BaseModel, EmailStr

from app.core.config import settings


class MailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    body: str
    attachment: Optional[str] = None


def mailSend(mail: MailSchema) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = mail.recipient
        msg["To"] = settings.MAIL_FROM
        msg["Subject"] = mail.subject
        body = MIMEText(mail.body, "html")
        msg.attach(body)

        # Add attachment
        if mail.attachment and Path(mail.attachment).exists():
            with open(mail.attachment, "rb") as attachment:
                file = MIMEBase("application", "octet-stream")
                file.set_payload(attachment.read())

            encoders.encode_base64(file)
            fileName = Path(mail.attachment).name
            file.add_header("Content-Disposition", f"attachment; filename= {fileName}")
            msg.attach(file)

        # Send mail
        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()

            server.login(settings.MAIL_FROM, settings.MAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Mail sended: {mail.recipient}")

        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
