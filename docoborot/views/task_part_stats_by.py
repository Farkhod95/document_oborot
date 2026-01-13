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
    """
    POST:
      - company_id or company: int (majburiy)
      - year: int (majburiy)
      - month: int (ixtiyoriy, 1-12)
      - status: str (ixtiyoriy) -> tanlangan model STATUS qiymatlaridan biri
      - assignee_id: int (ixtiyoriy) -> User ID
      - target: str (ixtiyoriy) -> "auto" | "task" | "part"
          auto: assignee_id bo'lsa roli bo'yicha tanlaydi, bo'lmasa default "part"
          task: Task bo'yicha (signed_by kesimida)
          part: TaskPart bo'yicha (assignee kesimida)

    Response STRUCTURE O'ZGARMAYDI.
    start_date datetime bo'lsa ham DATE bo'yicha guruhlanadi (time e'tiborsiz).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # --------- input ---------
        company_id = request.data.get('company_id', None)
        if company_id is None:
            company_id = request.data.get('company', None)

        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)
        assignee_id = request.data.get('assignee_id', None)
        target = (request.data.get('target') or 'auto').strip().lower()  # auto | task | part

        # --------- validation: company_id ---------
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

        # --------- validation: year ---------
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`year` majburiy va integer bo‘lishi kerak. Masalan: 2026"},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # --------- validation: month (optional) ---------
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

        # --------- validation: assignee_id (optional) ---------
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

        # --------- choose model: Task vs TaskPart ---------
        # Siz aytgandek:
        # - Task -> signed_by (Signatory uchun)
        # - TaskPart -> assignee (Performer uchun)
        if target not in {"auto", "task", "part"}:
            return Response(
                {"detail": "`target` noto‘g‘ri. Ruxsat: auto | task | part"},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        chosen = None  # "task" | "part"

        if target == "task":
            chosen = "task"
        elif target == "part":
            chosen = "part"
        else:
            # auto
            if assignee_user is None:
                chosen = "part"  # assignee_id bo'lmasa default performer kalendari (TaskPart)
            else:
                is_signatory = assignee_user.roles.filter(name__iexact="Signatory").exists()
                is_performer = assignee_user.roles.filter(name__iexact="Performer").exists()

                if is_signatory and not is_performer:
                    chosen = "task"
                elif is_performer and not is_signatory:
                    chosen = "part"
                elif is_signatory and is_performer:
                    # ikkala rol bo'lsa default performer (part)
                    chosen = "part"
                else:
                    # roli topilmasa ham default performer (part)
                    chosen = "part"

        # --------- base queryset ---------
        if chosen == "task":
            # Task signed_by kesimida (Signatory uchun)
            qs = Task.objects.filter(
                company_id=company_id,
                start_date__isnull=False,
                start_date__year=year,
            )
            if month is not None:
                qs = qs.filter(start_date__month=month)

            if assignee_id is not None:
                qs = qs.filter(signed_by_id=assignee_id)

            STATUS_CHOICES = Task.STATUS.choices
            status_field = "status"
            start_field = "start_date"
        else:
            # TaskPart assignee kesimida (Performer uchun)
            qs = TaskPart.objects.filter(
                task__company_id=company_id,
                start_date__isnull=False,
                start_date__year=year,
            )
            if month is not None:
                qs = qs.filter(start_date__month=month)

            if assignee_id is not None:
                qs = qs.filter(assignee_id=assignee_id)

            STATUS_CHOICES = TaskPart.STATUS.choices
            status_field = "status"
            start_field = "start_date"

        # --------- validation: status (optional) - tanlangan modelga mos ---------
        if status_param is not None and status_param != "":
            allowed_statuses = {code for code, _ in STATUS_CHOICES}
            if status_param not in allowed_statuses:
                return Response(
                    {
                        "detail": "`status` noto‘g‘ri. Ruxsat etilgan qiymatlar:",
                        "allowed": sorted(list(allowed_statuses)),
                        "target_used": chosen,
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
        for code, label in STATUS_CHOICES:
            c = overall_map.get(code, 0)
            total += c
            by_status[code] = {"label": str(label), "count": c}

        # =========================
        # 2) group by DATE(start_date) + status
        #    (time e'tiborsiz)
        # =========================
        date_status_rows = (
            qs.annotate(day=TruncDate(start_field))
              .values('day', status_field)
              .annotate(count=Count('id'))
              .order_by('day', status_field)
        )

        grouped = {}  # {date: {status_code: count}}
        for r in date_status_rows:
            d = r["day"]          # date object
            s = r[status_field]
            c = int(r["count"])
            grouped.setdefault(d, {})
            grouped[d][s] = c

        by_start_date = []
        for d in sorted(grouped.keys()):
            status_counts = grouped[d]
            day_total = 0
            day_by_status = {}

            for code, label in STATUS_CHOICES:
                c = int(status_counts.get(code, 0))
                day_total += c
                day_by_status[code] = {"label": str(label), "count": c}

            by_start_date.append({
                "start_date": d.isoformat(),  # "YYYY-MM-DD"
                "total": day_total,
                "by_status": day_by_status,
            })

        # ✅ Response strukturasi o'zgarmaydi
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
