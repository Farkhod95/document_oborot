# from celery import shared_task
# from django.db import transaction
# from django.utils import timezone
#
# from docoborot.models import TaskPart, Task, TaskEvent
#
# @shared_task
# def expire_overdue_task_parts():
#     """
#     end_date o'tib ketgan TaskPart larni EXPIRED ga o'tkazadi.
#     Keyin parent Task statusini recompute qiladi.
#     """
#     now = timezone.now()
#
#     # Qaysi statuslardan EXPIRED ga o'tsin:
#     can_expire_statuses = [
#         TaskPart.STATUS.NEW,
#         TaskPart.STATUS.IN_PROGRESS,
#         TaskPart.STATUS.ON_REVIEW,
#         TaskPart.STATUS.RETURNED,
#     ]
#
#     qs = (
#         TaskPart.objects
#         .select_related("task")
#         .filter(end_date__isnull=False, end_date__lt=now, status__in=can_expire_statuses)
#         .order_by("id")
#     )
#
#     updated_count = 0
#
#     # katta bazada xavfsizroq bo‘lishi uchun bo‘lib ishlatamiz
#     for part in qs.iterator(chunk_size=500):
#         with transaction.atomic():
#             # qayta tekshiruv (race condition bo'lmasin)
#             part = TaskPart.objects.select_for_update().select_related("task").get(pk=part.pk)
#
#             if not part.end_date or part.end_date >= now:
#                 continue
#             if part.status not in can_expire_statuses:
#                 continue
#
#             old_status = part.status
#             part.status = TaskPart.STATUS.EXPIRED
#             part.save(update_fields=["status", "updated_time"])
#
#             # log
#             TaskEvent.log(
#                 task=part.task,
#                 part=part,
#                 actor=None,  # system
#                 event_type=TaskEvent.TYPE.STATUS_CHANGED,
#                 message="Muddati tugadi (avtomatik).",
#                 from_status=old_status,
#                 to_status=part.status,
#                 extra={"expired_at": now.isoformat()}
#             )
#
#             # parent task status
#             part.task.recompute_status(save=True)
#
#             updated_count += 1
#
#     # agar xohlasangiz Task ning o'z end_date'i ham bo'lsa (sizda bor),
#     # lekin TaskPart bo'lmasa ham EXPIRED bo'lsin degan qoida ham qo‘shish mumkin.
#     # Hozir asosiy trigger TaskPart.
#
#     return {"expired_task_parts": updated_count, "checked_at": now.isoformat()}
