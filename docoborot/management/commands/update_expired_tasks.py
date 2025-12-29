from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from docoborot.models import Task, TaskPart, TaskEvent


class Command(BaseCommand):
    help = "Muddati o‘tgan Task va TaskPart larni avtomatik EXPIRED qiladi."

    def handle(self, *args, **options):
        now = timezone.now()

        changed_task_ids = set()
        expired_parts_count = 0
        expired_tasks_count = 0

        with transaction.atomic():
            # 1) TaskPart: end_date < now va status DONE/CANCELLED/EXPIRED bo‘lmasa -> EXPIRED
            parts_qs = TaskPart.objects.select_related('task').filter(
                end_date__isnull=False,
                end_date__lt=now
            ).exclude(status__in=[
                TaskPart.STATUS.DONE,
                TaskPart.STATUS.CANCELLED,
                TaskPart.STATUS.EXPIRED,
            ])

            for part in parts_qs:
                old_status = part.status
                part.status = TaskPart.STATUS.EXPIRED
                part.save(update_fields=['status', 'updated_time'])

                TaskEvent.log(
                    task=part.task,
                    part=part,
                    actor=None,
                    event_type=TaskEvent.TYPE.EXPIRED,
                    message="Cron: muddat tugadi, TaskPart EXPIRED bo‘ldi",
                    from_status=old_status,
                    to_status=part.status,
                    extra={"reason": "cron_update", "end_date": part.end_date.isoformat() if part.end_date else None}
                )

                expired_parts_count += 1
                changed_task_ids.add(part.task_id)

            # 2) Part yo‘q Task lar: end_date < now bo‘lsa -> EXPIRED
            tasks_no_parts_qs = Task.objects.filter(
                end_date__isnull=False,
                end_date__lt=now
            ).exclude(status__in=[
                Task.STATUS.DONE,
                Task.STATUS.CANCELLED,
                Task.STATUS.ARCHIVE,
                Task.STATUS.EXPIRED,
            ]).filter(parts__isnull=True)

            for task in tasks_no_parts_qs:
                old_status = task.status
                task.status = Task.STATUS.EXPIRED
                task.save(update_fields=['status', 'updated_time'])

                TaskEvent.log(
                    task=task,
                    part=None,
                    actor=None,
                    event_type=TaskEvent.TYPE.EXPIRED,
                    message="Cron: muddat tugadi, Task EXPIRED bo‘ldi (part yo‘q)",
                    from_status=old_status,
                    to_status=task.status,
                    extra={"reason": "cron_update", "end_date": task.end_date.isoformat() if task.end_date else None}
                )
                expired_tasks_count += 1

            # 3) Partlari o‘zgargan Task larni recompute qilish
            for task_id in changed_task_ids:
                task = Task.objects.get(pk=task_id)
                task.recompute_status(save=True)

        self.stdout.write(self.style.SUCCESS(
            f"OK. EXPIRED TaskPart: {expired_parts_count}, EXPIRED Task (no parts): {expired_tasks_count}, recomputed tasks: {len(changed_task_ids)}"
        ))
