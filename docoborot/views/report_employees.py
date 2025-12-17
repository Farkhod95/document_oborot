from django.db.models import Count, Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from users.models import Company  # Company qayerda bo'lsa, o'sha importni qo'ying
from docoborot.models import TaskPart

User = get_user_model()


class CompanyEmployeesReportView(APIView):
    """
    POST:
      - company_id: int (majburiy)
      - year: int (ixtiyoriy) -> default: joriy yil
      - month: int (ixtiyoriy, 1-12)

    Qaytaradi:
      - company_id, year, month
      - employees_total
      - employees: [
          {
            id, fullname, username, avatar, email, phone_number,
            stats: { total, done, in_progress, overdue }
          }, ...
        ]
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        year = request.data.get("year", None)
        month = request.data.get("month", None)

        # -------- validate company_id --------
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`company_id` majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        if not Company.objects.filter(id=company_id).exists():
            return Response(
                {"detail": "Berilgan `company_id` bo‘yicha kompaniya topilmadi."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # -------- validate year (optional) --------
        if year is None or year == "":
            year = timezone.localdate().year
        else:
            try:
                year = int(year)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "`year` integer bo‘lishi kerak. Masalan: 2025"},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )

        # -------- validate month (optional) --------
        if month is not None and month != "":
            try:
                month = int(month)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "`month` integer bo‘lishi kerak. Masalan: 12"},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
            if not (1 <= month <= 12):
                return Response(
                    {"detail": "`month` 1..12 oraliqda bo‘lishi kerak."},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            month = None

        today = timezone.localdate()

        # ===================== Employees (company users) =====================
        employees_qs = (
            User.objects
            .filter(companies__id=company_id, is_active=True)
            .distinct()
            .only("id", "fullname", "username", "avatar", "email", "phone_number")
            .order_by("id")
        )

        employee_ids = list(employees_qs.values_list("id", flat=True))

        # Agar kompaniyada xodim yo'q bo'lsa ham to'g'ri response
        if not employee_ids:
            return Response(
                {
                    "company_id": company_id,
                    "year": year,
                    "month": month,
                    "employees_total": 0,
                    "employees": [],
                },
                status=drf_status.HTTP_200_OK
            )

        # ===================== TaskPart stats grouped by assignee =====================
        base_parts = TaskPart.objects.filter(
            task__company_id=company_id,
            assignee_id__in=employee_ids,
            start_date__isnull=False,
            start_date__year=year,
        )
        if month is not None:
            base_parts = base_parts.filter(start_date__month=month)

        done_status = TaskPart.STATUS.DONE
        cancelled_status = TaskPart.STATUS.CANCELLED

        stats_rows = (
            base_parts
            .values("assignee_id")
            .annotate(
                total=Count("id"),
                done=Count("id", filter=Q(status=done_status)),
                overdue=Count(
                    "id",
                    filter=Q(end_date__lt=today) & ~Q(status__in=[done_status, cancelled_status])
                ),
                in_progress=Count(
                    "id",
                    filter=Q(status__in=[
                        TaskPart.STATUS.NEW,
                        TaskPart.STATUS.IN_PROGRESS,
                        TaskPart.STATUS.ON_REVIEW,
                        TaskPart.STATUS.RETURNED,
                    ]) & (Q(end_date__gte=today) | Q(end_date__isnull=True))
                ),
            )
        )

        stats_map = {r["assignee_id"]: r for r in stats_rows}

        # ===================== Build response list (even if 0 stats) =====================
        employees = []
        for u in employees_qs:
            row = stats_map.get(u.id, {})

            avatar_url = None
            if getattr(u, "avatar", None):
                try:
                    avatar_url = request.build_absolute_uri(u.avatar.url)
                except Exception:
                    avatar_url = None

            employees.append({
                "id": u.id,
                "fullname": getattr(u, "fullname", "") or "",
                "username": getattr(u, "username", "") or "",
                "avatar": avatar_url,
                "email": getattr(u, "email", None),
                "phone_number": getattr(u, "phone_number", None),
                "stats": {
                    "total": int(row.get("total", 0)),
                    "done": int(row.get("done", 0)),
                    "in_progress": int(row.get("in_progress", 0)),
                    "overdue": int(row.get("overdue", 0)),
                }
            })

        return Response(
            {
                "company_id": company_id,
                "year": year,
                "month": month,
                "employees_total": len(employee_ids),
                "employees": employees,
            },
            status=drf_status.HTTP_200_OK
        )
