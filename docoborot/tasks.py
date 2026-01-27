from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from docoborot.models import Task, TaskPart

CHECK_INTERVAL = timedelta(hours=2)  # har 2 soatda tekshiramiz
TTL_SECONDS = int(timedelta(days=14).total_seconds())

# Eslatma thresholdlari
THRESHOLDS = (
    ("24h", timedelta(hours=24), "⏰", "24 soat"),
    ("3h", timedelta(hours=3), "⚠️", "3 soat"),
)


# =========================
# COMMON HELPERS
# =========================
def _from_email() -> str | None:
    return getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None))


def _frontend_url() -> str:
    return getattr(settings, "FRONTEND_URL", "https://doc.optivora-group.com/")


def _safe_email(user) -> str | None:
    email = getattr(user, "email", None) if user else None
    if not email:
        return None
    email = email.strip()
    return email or None


def _uniq_emails(*emails: str | None) -> list[str]:
    return [e for e in {x.strip() for x in emails if x and x.strip()}]


def _send(subject: str, message: str, recipients: list[str]) -> bool:
    recipients = _uniq_emails(*recipients)
    if not recipients:
        return False

    send_mail(
        subject=subject,
        message=message,
        from_email=_from_email(),
        recipient_list=recipients,
        fail_silently=False,
    )
    return True


def _cache_key(prefix: str, obj_id: int, end_dt) -> str:
    end_iso = end_dt.isoformat() if end_dt else "none"
    return f"deadline_notify:{prefix}:{obj_id}:{end_iso}"


def _in_window(end_dt, threshold: timedelta) -> bool:
    """
    Har 2 soatda tekshirish uchun "oyna":
      remaining <= threshold
      remaining > threshold - CHECK_INTERVAL
    """
    if not end_dt:
        return False

    now = timezone.now()
    remaining = end_dt - now

    if remaining <= timedelta(0):
        return False

    lower = threshold - CHECK_INTERVAL
    return (remaining <= threshold) and (remaining > lower)


# =========================
# DEADLINE REMINDERS (BEAT)
# =========================
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_deadline_reminders_task(self) -> dict:
    try:
        now = timezone.now()
        # max threshold=24h, interval=2h => 26h ichida bo‘lganlar
        horizon = now + timedelta(hours=26)
        link = _frontend_url()

        stats = {
            "task_sent": {"24h": 0, "3h": 0},
            "part_sent": {"24h": 0, "3h": 0},
            "checked_tasks": 0,
            "checked_parts": 0,
            "skipped_no_email": 0,
        }

        # --- TASKS ---
        tasks = (
            Task.objects
            .select_related("signed_by", "respon_person")
            .filter(end_date__isnull=False, end_date__gt=now, end_date__lte=horizon)
        )

        for t in tasks:
            stats["checked_tasks"] += 1

            recipients = _uniq_emails(
                _safe_email(getattr(t, "signed_by", None)),
                _safe_email(getattr(t, "respon_person", None)),
            )
            if not recipients:
                stats["skipped_no_email"] += 1
                continue

            task_name = t.name or f"Task#{t.id}"

            for key_suffix, threshold, icon, label in THRESHOLDS:
                if not _in_window(t.end_date, threshold):
                    continue

                key = _cache_key(f"task_{key_suffix}", t.id, t.end_date)
                if not cache.add(key, True, timeout=TTL_SECONDS):
                    continue  # oldin yuborilgan

                subject = f"{icon} Vazifa muddati yaqinlashmoqda ({label} qoldi)"
                msg = (
                    "Assalomu alaykum!\n\n"
                    f"Vazifa muddati tugashiga taxminan {label} qoldi.\n\n"
                    f"Vazifa: {task_name}\n"
                    f"Tugash vaqti: {t.end_date}\n\n"
                    "Iltimos tizimga kirib nazorat qiling.\n"
                    f"Link: {link}\n"
                )
                if _send(subject, msg, recipients):
                    stats["task_sent"][key_suffix] += 1

        # --- PARTS ---
        parts = (
            TaskPart.objects
            .select_related("assignee", "task")
            .filter(end_date__isnull=False, end_date__gt=now, end_date__lte=horizon)
        )

        for p in parts:
            stats["checked_parts"] += 1

            assignee_email = _safe_email(getattr(p, "assignee", None))
            if not assignee_email:
                stats["skipped_no_email"] += 1
                continue

            task_name = p.task.name or f"Task#{p.task_id}"

            for key_suffix, threshold, icon, label in THRESHOLDS:
                if not _in_window(p.end_date, threshold):
                    continue

                key = _cache_key(f"part_{key_suffix}", p.id, p.end_date)
                if not cache.add(key, True, timeout=TTL_SECONDS):
                    continue

                subject = f"{icon} Vazifa muddati yaqinlashmoqda ({label} qoldi)"
                msg = (
                    "Assalomu alaykum!\n\n"
                    f"Sizga biriktirilgan Vazifa muddati tugashiga taxminan {label} qoldi.\n\n"
                    f"Vazifa: {task_name}\n"
                    f"Izoh: {p.title}\n"
                    f"Tugash vaqti: {p.end_date}\n\n"
                    "Iltimos tizimga kirib bo‘limingizni ko‘rib chiqing.\n"
                    f"Link: {link}\n"
                )
                if _send(subject, msg, [assignee_email]):
                    stats["part_sent"][key_suffix] += 1

        return {"ok": True, "stats": stats}

    except Exception as exc:
        raise self.retry(exc=exc)


# =========================
# TASK CREATED / ASSIGNED EMAIL
# =========================
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_task_emails_task(self, task_id: int) -> dict:
    try:
        task = (
            Task.objects
            .select_related("signed_by", "respon_person", "company", "department")
            .prefetch_related("parts__assignee", "parts__department")
            .filter(id=task_id)
            .first()
        )
        if not task:
            return {"ok": False, "detail": f"Task topilmadi: {task_id}"}

        task_name = task.name or f"Task#{task.id}"
        link = _frontend_url()

        stats = {
            "sent_to_signed_by": False,
            "sent_to_respon_person": False,
            "sent_to_assignees_count": 0,
            "skipped_assignees_no_email": 0,
        }

        # 1) signed_by
        signed_email = _safe_email(task.signed_by)
        if signed_email:
            subject = "Yangi Vazifa biriktirildi"
            msg = (
                "Assalomu alaykum!\n\n"
                "Sizga yangi Vazifa biriktirildi.\n\n"
                f"Vazifa: {task_name}\n"
                f"Status: {task.status}\n"
                f"Boshlash: {task.start_date or '-'}\n"
                f"Tugash: {task.end_date or '-'}\n\n"
                "Iltimos tizimga kirib ko‘rib chiqing.\n"
                f"Link: {link}\n"
            )
            _send(subject, msg, [signed_email])
            stats["sent_to_signed_by"] = True

        # 1.1) respon_person
        resp_email = _safe_email(task.respon_person)
        if resp_email:
            subject = "Siz mas’ul shaxs etib biriktirildingiz"
            msg = (
                "Assalomu alaykum!\n\n"
                "Siz ushbu vazifa uchun mas’ul shaxs etib belgilandingiz.\n\n"
                f"Vazifa: {task_name}\n"
                f"Status: {task.status}\n"
                f"Boshlash: {task.start_date or '-'}\n"
                f"Tugash: {task.end_date or '-'}\n\n"
                "Iltimos tizimga kirib nazorat qiling.\n"
                f"Link: {link}\n"
            )
            _send(subject, msg, [resp_email])
            stats["sent_to_respon_person"] = True

        # 2) assignees unique
        assignee_emails = set()
        for part in task.parts.all():
            email = _safe_email(getattr(part, "assignee", None))
            if email:
                assignee_emails.add(email)
            else:
                stats["skipped_assignees_no_email"] += 1

        if assignee_emails:
            subject = "Sizga yangi vazifa biriktirildi"
            base_msg = (
                "Assalomu alaykum!\n\n"
                "Sizga yangi vazifa biriktirildi.\n\n"
                f"Vazifa: {task_name}\n"
                f"Umumiy status: {task.status}\n\n"
                "Iltimos tizimga kirib bo‘limingizni ko‘rib chiqing.\n"
                f"Link: {link}\n"
            )
            # Har bir emailga alohida yuboramiz (xohlasangiz bitta send_mail ham qilsa bo‘ladi)
            for email in assignee_emails:
                _send(subject, base_msg, [email])
                stats["sent_to_assignees_count"] += 1

        return {"ok": True, "task_id": task.id, "task_name": task_name, **stats}

    except Exception as exc:
        raise self.retry(exc=exc)
