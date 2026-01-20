from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from docoborot.models import Task, TaskPart
from users.models import Company


class TaskPartSelfByStartDateView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ faqat 6 ta status
    ALLOWED_STATUSES = ["new", "in_progress", "on_review", "returned", "done", "cancelled"]

    # label (kalendarda ko'rsatish uchun)
    ALLOWED_STATUS_LABELS = {
        "new": "New",
        "in_progress": "In progress",
        "on_review": "On review",
        "returned": "Returned",
        "done": "Done",
        "cancelled": "Cancelled",
    }

    def post(self, request, *args, **kwargs):
        user = request.user

        # input
        company_id = request.data.get('company_id', None)
        if company_id is None:
            company_id = request.data.get('company', None)

        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)

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

        # --------- status (optional, faqat 6 tadan biri) ---------
        if status_param is not None and status_param != "":
            if status_param not in self.ALLOWED_STATUSES:
                return Response(
                    {
                        "detail": "`status` noto‘g‘ri. Ruxsat etilgan qiymatlar:",
                        "allowed": self.ALLOWED_STATUSES,
                    },
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            status_param = None

        # --------- role detect ---------
        is_signatory = user.roles.filter(name__iexact="Signatory").exists()
        is_performer = user.roles.filter(name__iexact="Performer").exists()

        # userda ikkisi ham bo'lmasa ham, xatoga urmaymiz — 0 natija qaytaramiz
        task_qs = Task.objects.none()
        part_qs = TaskPart.objects.none()

        if is_signatory:
            task_qs = Task.objects.filter(
                company_id=company_id,
                signed_by_id=user.id,
                end_date__isnull=False,
                end_date__year=year,
                status__in=self.ALLOWED_STATUSES,
            )
            if month is not None:
                task_qs = task_qs.filter(end_date__month=month)
            if status_param is not None:
                task_qs = task_qs.filter(status=status_param)

        if is_performer:
            part_qs = TaskPart.objects.filter(
                task__company_id=company_id,
                assignee_id=user.id,
                end_date__isnull=False,
                end_date__year=year,
                status__in=self.ALLOWED_STATUSES,
            )
            if month is not None:
                part_qs = part_qs.filter(end_date__month=month)
            if status_param is not None:
                part_qs = part_qs.filter(status=status_param)

        # =========================
        # 1) overall by_status (Task + TaskPart qo'shib)
        # =========================
        task_overall = (
            task_qs.values("status")
                   .annotate(count=Count("id"))
        )
        part_overall = (
            part_qs.values("status")
                   .annotate(count=Count("id"))
        )

        overall_map = {s: 0 for s in self.ALLOWED_STATUSES}
        for r in task_overall:
            overall_map[r["status"]] += int(r["count"])
        for r in part_overall:
            overall_map[r["status"]] += int(r["count"])

        total = 0
        by_status = {}
        for code in self.ALLOWED_STATUSES:
            c = int(overall_map.get(code, 0))
            total += c
            by_status[code] = {"label": self.ALLOWED_STATUS_LABELS.get(code, code), "count": c}

        # =========================
        # 2) by_start_date (DATE bo'yicha, Task + TaskPart qo'shib)
        # =========================
        task_rows = (
            task_qs.annotate(day=TruncDate("end_date"))
                   .values("day", "status")
                   .annotate(count=Count("id"))
        )
        part_rows = (
            part_qs.annotate(day=TruncDate("end_date"))
                   .values("day", "status")
                   .annotate(count=Count("id"))
        )

        grouped = {}  # {date: {status: count}}

        for r in task_rows:
            d = r["day"]
            s = r["status"]
            c = int(r["count"])
            grouped.setdefault(d, {})
            grouped[d][s] = grouped[d].get(s, 0) + c

        for r in part_rows:
            d = r["day"]
            s = r["status"]
            c = int(r["count"])
            grouped.setdefault(d, {})
            grouped[d][s] = grouped[d].get(s, 0) + c

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

        # ✅ strukturani o'zgartirmaymiz
        return Response(
            {
                "company_id": company_id,
                "year": year,
                "month": month,
                "status": status_param,
                "assignee_id": user.id,  # self endpoint => doim user.id
                "total": total,
                "by_status": by_status,
                "by_start_date": by_start_date,
            },
            status=drf_status.HTTP_200_OK
        )
