from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from docoborot.models import Task, TaskPart
from users.models import Company

User = get_user_model()


class TaskPartStatsByStartDateView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ Faqat kerakli 6 ta status
    ALLOWED_STATUSES = [
        "new",
        "in_progress",
        "on_review",
        "returned",
        "done",
        "cancelled",
    ]

    # label'larni yo'qotmaslik uchun (i18n bilan)
    ALLOWED_STATUS_LABELS = {
        "new": "New",
        "in_progress": "In progress",
        "on_review": "On review",
        "returned": "Returned",
        "done": "Done",
        "cancelled": "Cancelled",
    }

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company_id', None)
        if company_id is None:
            company_id = request.data.get('company', None)

        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)
        assignee_id = request.data.get('assignee_id', None)
        target = (request.data.get('target') or 'auto').strip().lower()  # auto | task | part

        # --------- company_id ---------
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`company_id` (yoki `company`) majburiy va integer bo‘lishi kerak."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        if not Company.objects.filter(id=company_id).exists():
            return Response(
                {"detail": "Berilgan `company_id` bo‘yicha kompaniya topilmadi."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # --------- year ---------
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`year` majburiy va integer bo‘lishi kerak. Masalan: 2026"},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # --------- month (optional) ---------
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

        # --------- assignee_id (optional) ---------
        assignee_user = None
        if assignee_id is not None and assignee_id != "":
            try:
                assignee_id = int(assignee_id)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "`assignee_id` integer bo‘lishi kerak."},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )

            assignee_user = User.objects.filter(id=assignee_id).first()
            if not assignee_user:
                return Response(
                    {"detail": "Berilgan `assignee_id` bo‘yicha user topilmadi."},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            assignee_id = None

        # --------- choose model ---------
        if target not in {"auto", "task", "part"}:
            return Response(
                {"detail": "`target` noto‘g‘ri. Ruxsat: auto | task | part"},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        if target == "task":
            chosen = "task"
        elif target == "part":
            chosen = "part"
        else:
            if assignee_user is None:
                chosen = "part"
            else:
                is_signatory = assignee_user.roles.filter(name__iexact="Signatory").exists()
                is_performer = assignee_user.roles.filter(name__iexact="Performer").exists()
                if is_signatory and not is_performer:
                    chosen = "task"
                else:
                    chosen = "part"

        # --------- base queryset ---------
        if chosen == "task":
            qs = Task.objects.filter(
                company_id=company_id,
                end_date__isnull=False,
                end_date__year=year,
            )
            if month is not None:
                qs = qs.filter(end_date__month=month)
            if assignee_id is not None:
                qs = qs.filter(signed_by_id=assignee_id)

            status_field = "status"
            start_field = "end_date"
        else:
            qs = TaskPart.objects.filter(
                task__company_id=company_id,
                end_date__isnull=False,
                end_date__year=year,
            )
            if month is not None:
                qs = qs.filter(end_date__month=month)
            if assignee_id is not None:
                qs = qs.filter(assignee_id=assignee_id)

            status_field = "status"
            start_field = "end_date"

        # ✅ Faqat 6 ta statusni qoldiramiz (qolganlari umuman hisoblanmaydi)
        qs = qs.filter(**{f"{status_field}__in": self.ALLOWED_STATUSES})

        # --------- status filter (optional, lekin faqat 6 tadan biri bo'lsa) ---------
        if status_param is not None and status_param != "":
            if status_param not in self.ALLOWED_STATUSES:
                return Response(
                    {
                        "detail": "`status` noto‘g‘ri. Ruxsat etilgan qiymatlar:",
                        "allowed": self.ALLOWED_STATUSES,
                    },
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
            qs = qs.filter(**{status_field: status_param})
        else:
            status_param = None

        # =========================
        # 1) overall by_status
        # =========================
        overall_rows = (
            qs.values(status_field)
              .annotate(count=Count('id'))
              .order_by(status_field)
        )
        overall_map = {r[status_field]: int(r["count"]) for r in overall_rows}

        total = 0
        by_status = {}
        for code in self.ALLOWED_STATUSES:
            c = overall_map.get(code, 0)
            total += c
            by_status[code] = {"label": self.ALLOWED_STATUS_LABELS.get(code, code), "count": c}

        # =========================
        # 2) group by DATE(start_date) + status (time e'tiborsiz)
        # =========================
        date_status_rows = (
            qs.annotate(day=TruncDate(start_field))
              .values('day', status_field)
              .annotate(count=Count('id'))
              .order_by('day', status_field)
        )

        grouped = {}
        for r in date_status_rows:
            d = r["day"]
            s = r[status_field]
            c = int(r["count"])
            grouped.setdefault(d, {})
            grouped[d][s] = c

        by_start_date = []
        for d in sorted(grouped.keys()):
            status_counts = grouped[d]
            day_total = 0
            day_by_status = {}

            for code in self.ALLOWED_STATUSES:
                c = int(status_counts.get(code, 0))
                day_total += c
                day_by_status[code] = {"label": self.ALLOWED_STATUS_LABELS.get(code, code), "count": c}

            by_start_date.append({
                "start_date": d.isoformat(),  # YYYY-MM-DD
                "total": day_total,
                "by_status": day_by_status,
            })

        return Response(
            {
                "company_id": company_id,
                "year": year,
                "month": month,
                "status": status_param,
                "assignee_id": assignee_id,
                "total": total,
                "by_status": by_status,
                "by_start_date": by_start_date,
            },
            status=drf_status.HTTP_200_OK
        )
