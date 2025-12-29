# docoborot/utils/emailing.py
from typing import Optional
from django.conf import settings
from django.core.mail import send_mail


def send_new_task_assigned_email(
    to_email: str,
    task_name: str = "",
    part_title: str = "",
    task_id: Optional[int] = None,
):
    if not to_email:
        return

    subject = "Sizga yangi task biriktirildi"
    lines = [
        "Assalomu alaykum!",
        "",
        "Sizga yangi task biriktirildi.",
    ]

    if task_name:
        lines.append(f"Task: {task_name}")
    if part_title:
        lines.append(f"Bo‘lim: {part_title}")
    if task_id is not None:
        lines.append(f"Task ID: {task_id}")

    lines += ["", "Hurmat bilan, Optivora tizimi."]

    send_mail(
        subject=subject,
        message="\n".join(lines),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[to_email],
        fail_silently=False,
    )
