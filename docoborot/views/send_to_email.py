from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status

from docoborot.models import Task
from docoborot.tasks import send_task_emails_task


class SendToEmailView(APIView):
    def post(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")

        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`task_id` majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        exists = Task.objects.filter(id=task_id).exists()
        if not exists:
            return Response(
                {"detail": f"`task_id`={task_id} bo‘yicha task topilmadi."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        # ✅ Backgroundga yuborish
        async_result = send_task_emails_task.delay(task_id)

        return Response(
            {
                "ok": True,
                "detail": "Email yuborish backgroundga qo‘yildi.",
                "task_id": task_id,
                "celery_task_id": async_result.id,
            },
            status=drf_status.HTTP_202_ACCEPTED
        )
