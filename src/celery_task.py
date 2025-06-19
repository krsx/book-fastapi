from celery import Celery
from asgiref.sync import async_to_sync
import os
from src.email.mail import create_message, mail

os.environ["FORKED_BY_MULTIPROCESSING"] = (
    "1"  # Fix for Windows compatibility with Celery and FastAPI Mail
)

celery_app = Celery()
celery_app.config_from_object("src.config")


@celery_app.task()
def send_email_task(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
