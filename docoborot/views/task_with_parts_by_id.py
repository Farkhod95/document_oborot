from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from docoborot.models import Task, TaskPart
from docoborot.serializers import TaskWithPartsSerializer


class TaskWithPartsByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')

        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`task_id` majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        task = Task.objects.filter(id=task_id).first()
        if not task:
            return Response({"detail": "Task topilmadi."}, status=drf_status.HTTP_404_NOT_FOUND)

        parts_qs = TaskPart.objects.filter(task_id=task_id).order_by('id')

        serializer = TaskWithPartsSerializer(
            instance={"task": task, "parts": parts_qs},
            context={"request": request},
        )
        return Response(serializer.data, status=drf_status.HTTP_200_OK)
