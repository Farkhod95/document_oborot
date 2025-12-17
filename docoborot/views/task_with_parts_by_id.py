from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from docoborot.models import Task, TaskPart
from docoborot.serializers import TaskSerializer, TaskPartSerializer, TaskWithPartsSerializer


class TaskWithPartsByIdView(APIView):
    """
    POST:
      - task_id: int (majburiy)

    Qaytaradi:
      - task: TaskSerializer
      - parts: TaskPartSerializer[] (shu taskga tegishli parts)
    """
    permission_classes = [IsAuthenticated]  # kerak bo'lsa NotClientUser

    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')

        # ---- validation ----
        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`task_id` majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        task = Task.objects.filter(id=task_id).first()
        if not task:
            return Response(
                {"detail": "Task topilmadi."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        # parts
        parts_qs = TaskPart.objects.filter(task_id=task_id).order_by('id')

        payload = {
            "task": TaskSerializer(task, context={"request": request}).data,
            "parts": TaskPartSerializer(parts_qs, many=True, context={"request": request}).data,
        }

        # xohlasangiz shu wrapper serializer bilan validatsiya ham qildiramiz:
        data = TaskWithPartsSerializer(payload).data

        return Response(data, status=drf_status.HTTP_200_OK)
