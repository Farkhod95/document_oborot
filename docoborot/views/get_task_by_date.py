from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from docoborot.serializers import TaskUnifiedItemSerializer
from ..models import Task, TaskPart  # pathni loyihangizga moslang


class TaskTaskPartByDateView(APIView):
    """
    GET /api/task-mix/?company=4&date=2026-01-12

    - Task va TaskPart start_date datetime bo'lsa ham date bo'yicha filter qiladi (time e'tiborsiz).
    - Natija: bir xil formatda list.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company_id = request.query_params.get("company")
        date_str = request.query_params.get("date")

        if not company_id:
            return Response(
                {"detail": "company_id param majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        d = parse_date(date_str) if date_str else None
        if not d:
            return Response(
                {"detail": "date param majburiy va YYYY-MM-DD formatda bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TASK: company_id + start_date__date
        tasks_qs = (
            Task.objects
            .filter(company_id=company_id, start_date__date=d)
            .select_related("signed_by", "department")
        )

        # TASK PART: task__company_id + start_date__date
        parts_qs = (
            TaskPart.objects
            .filter(task__company_id=company_id, start_date__date=d)
            .select_related("assignee", "department", "task")
        )

        results = []

        # Task -> unified format
        for t in tasks_qs:
            dept = None
            if getattr(t, "department", None):
                dept = {"id": t.department_id, "name": getattr(t.department, "name", None)}

            responsible = None
            if getattr(t, "signed_by", None):
                # agar sizda fullname field boshqacha bo'lsa shu yerini moslang
                responsible = getattr(t.signed_by, "fullname", None) or str(t.signed_by)

            results.append({
                "url": "task",
                "id": t.id,
                "title": getattr(t, "name", None),
                "start_date": getattr(t, "start_date", None),
                "end_date": getattr(t, "end_date", None),
                "responsible_person": responsible,
                "department": dept,
            })

        # TaskPart -> unified format
        for p in parts_qs:
            dept = None
            if getattr(p, "department", None):
                dept = {"id": p.department_id, "name": getattr(p.department, "name", None)}

            responsible = None
            if getattr(p, "assignee", None):
                responsible = getattr(p.assignee, "fullname", None) or str(p.assignee)

            results.append({
                "url": "task-part",
                "id": p.id,
                "title": getattr(p, "title", None),
                "start_date": getattr(p, "start_date", None),
                "end_date": getattr(p, "end_date", None),
                "responsible_person": responsible,
                "department": dept,
            })

        # ixtiyoriy: start_date bo'yicha sort (None bo'lsa oxiriga tushadi)
        results.sort(key=lambda x: (x["start_date"] is None, x["start_date"]))

        serializer = TaskUnifiedItemSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
