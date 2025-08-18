import smtplib
from email.mime.text import MIMEText
from app.config import get_settings


settings = get_settings()


def send_support_email(subject: str, body: str):
	if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD and settings.SUPPORT_EMAIL_TO):
		return
	msg = MIMEText(body)
	msg["Subject"] = subject
	msg["From"] = settings.SUPPORT_EMAIL_FROM
	msg["To"] = settings.SUPPORT_EMAIL_TO

	with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
		server.starttls()
		server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
		server.sendmail(settings.SUPPORT_EMAIL_FROM, [settings.SUPPORT_EMAIL_TO], msg.as_string())