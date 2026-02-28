from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from pathlib import Path
from enum import StrEnum

from src.core.config import settings
from src.core.traceback import traceBack, TrackType

class EmailType(StrEnum):
    REGISTRATION = "email/code.html"
    PASSWORD_RESET = "email/reset.html"
    TWOFA = "email/2fa.html"

class EmailServer:
    def __init__(self):
        self.connect()

    def connect(self) -> None:
        self.smtp = SMTP("smtp.gmail.com", 587)
        self.smtp.starttls()
        self.smtp.login(settings.EMAIL, settings.EMAIL_PASSWORD)
    
    def is_connected(self) -> bool:
        try:
            status = self.smtp.noop()[0]
            return 200 <= status <= 299
        except:
            return False

    def send_message(self, msg: EmailMessage | MIMEMultipart) -> None:
        if self.smtp is None or not self.is_connected():
            self.connect()
        try:
            self.smtp.send_message(msg)
        except Exception as e:
            traceBack(f"Resending after reconnect: {e}", type=TrackType.ERROR)
            self.connect()
            self.smtp.send_message(msg)

    def __del__(self):
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass
    
email_service: EmailServer = EmailServer()

def send_email(email: str, title: str, email_type: EmailType, **kwargs) -> None:
    template = settings.TEMPLATES.get_template(str(email_type))
    css = Path("src/static/styles/email.css").read_text()

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = settings.EMAIL
    message["To"] = email

    code = kwargs.get("code")
    link = kwargs.get("link")

    if code:
        mime_html = MIMEText(template.render(CONFIRMATION_CODE=code, INLINE_CSS=css), "html")
    elif link:
        mime_html = MIMEText(template.render(RESET_LINK=link, INLINE_CSS=css), "html")

    message.attach(mime_html)

    try:
        email_service.send_message(message)
    except Exception as e:
        traceBack(f"Mail has not been sended: {e}", type=TrackType.ERROR)