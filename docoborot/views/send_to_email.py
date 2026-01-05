from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status

from docoborot.models import Task

User = get_user_model()


class SendToEmailView(APIView):
    """
    POST: { "task_id": 123 }

    - Task.signed_by.email ga xabar
    - Shu taskga bog'langan TaskPart.assignee.email larga xabar
    """

    def post(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")

        # 1) task_id validatsiya
        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`task_id` majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # 2) Taskni olish
        task = (
            Task.objects
            .select_related("signed_by", "company", "department")
            .prefetch_related("parts__assignee", "parts__department")
            .filter(id=task_id)
            .first()
        )

        if not task:
            return Response(
                {"detail": f"`task_id`={task_id} bo‘yicha task topilmadi."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        task_name = task.name or f"Task#{task.id}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
        base_link = getattr(settings, "FRONTEND_URL", "https://doc.optivora-group.com/")

        sent_to_signed_by = False
        sent_to_assignees_count = 0
        skipped_assignees_no_email = 0

        # 3) signed_by ga email
        if task.signed_by and task.signed_by.email:
            subject = "Yangi Vazifa biriktirildi"
            msg = (
                "Assalomu alaykum!\n\n"
                "Sizga yangi Vazifa biriktirildi.\n\n"
                f"Vazifa: {task_name}\n"
                f"Status: {task.status}\n"
                f"Boshlash: {task.start_date or '-'}\n"
                f"Tugash: {task.end_date or '-'}\n\n"
                "Iltimos tizimga kirib ko‘rib chiqing.\n"
                f"Link: {base_link}\n"
            )

            send_mail(
                subject=subject,
                message=msg,
                from_email=from_email,
                recipient_list=[task.signed_by.email],
                fail_silently=False,
            )
            sent_to_signed_by = True

        # 4) TaskPart assignee larga email (takror email bo'lsa ham 1 marta jo'natamiz)
        #    (unique emails)
        assignee_emails = set()
        parts = task.parts.all()

        for part in parts:
            if part.assignee and part.assignee.email:
                assignee_emails.add(part.assignee.email)
            else:
                skipped_assignees_no_email += 1

        if assignee_emails:
            subject = "Sizga yangi vazifa biriktirildi"
            # Har bir ijrochiga alohida yuborish (istasa bir xil matn)
            for email in assignee_emails:
                msg = (
                    "Assalomu alaykum!\n\n"
                    "Sizga yangi vazifa biriktirildi.\n\n"
                    f"Vazifa: {task_name}\n"
                    f"Umumiy status: {task.status}\n\n"
                    "Iltimos tizimga kirib bo‘limingizni ko‘rib chiqing.\n"
                    f"Link: {base_link}\n"
                )

                send_mail(
                    subject=subject,
                    message=msg,
                    from_email=from_email,
                    recipient_list=[email],
                    fail_silently=False,
                )
                sent_to_assignees_count += 1

        return Response(
            {
                "task_id": task.id,
                "task_name": task_name,
                "sent_to_signed_by": sent_to_signed_by,
                "sent_to_assignees_count": sent_to_assignees_count,
                "skipped_assignees_no_email": skipped_assignees_no_email,
            },
            status=drf_status.HTTP_200_OK
        )
