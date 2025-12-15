from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, TaskPart, TaskEvent


@receiver(post_save, sender=Task)
def create_default_part_for_task(sender, instance: Task, created: bool, **kwargs):
    if created:
        TaskEvent.log(
            task=instance,
            created_by=getattr(instance, "signed_by", None),
            event_type=TaskEvent.TYPE.CREATED,
            message="Task yaratildi",
            extra={"task_id": instance.pk, "name": instance.name, "status": instance.status},
        )

    # Agar Task bo‘laklari yo‘q bo‘lsa — default 1 ta part
    if instance.parts.count() == 0:
        title = instance.name or "Umumiy vazifa"
        part = TaskPart.objects.create(
            task=instance,
            title=title,
            department=instance.department,
            assignee=None,  # xohlasangiz: signed_by yoki boshqa default
            start_date=instance.start_date,
            end_date=instance.end_date,
            status=TaskPart.STATUS.NEW,
            note=instance.note or "",
        )
        TaskEvent.log(
            task=instance,
            part=part,
            created_by=getattr(instance, "signed_by", None),
            event_type=TaskEvent.TYPE.PART_CREATED,
            message="Default bo‘lim yaratildi (bo‘linmagan task)",
            extra={"part_id": part.pk, "title": part.title},
        )
