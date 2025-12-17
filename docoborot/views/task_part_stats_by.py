from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from docoborot.models import TaskPart
from users.models import Company  # Company qayerda bo‘lsa shu importni qo‘ying

User = get_user_model()


class TaskPartStatsByStartDateView(APIView):
    """
    POST:
      - company_id: int (majburiy)
      - year: int (majburiy)
      - month: int (ixtiyoriy, 1-12)
      - status: str (ixtiyoriy) -> TaskPart.STATUS qiymatlaridan biri
      - assignee_id: int (ixtiyoriy) -> User ID
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company_id')
        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)
        assignee_id = request.data.get('assignee_id', None)

        # -------- company_id (required) --------
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            return Response({"detail": "`company_id` majburiy va integer bo‘lishi kerak."},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        if not Company.objects.filter(id=company_id).exists():
            return Response({"detail": "Berilgan `company_id` bo‘yicha kompaniya topilmadi."},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        # -------- year (required) --------
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({"detail": "`year` majburiy va integer bo‘lishi kerak. Masalan: 2025"},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        # -------- month (optional) --------
        if month is not None and month != "":
            try:
                month = int(month)
            except (TypeError, ValueError):
                return Response({"detail": "`month` integer bo‘lishi kerak. Masalan: 12"},
                                status=drf_status.HTTP_400_BAD_REQUEST)
            if not (1 <= month <= 12):
                return Response({"detail": "`month` 1..12 oraliqda bo‘lishi kerak."},
                                status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            month = None

        # -------- status (optional) --------
        if status_param is not None and status_param != "":
            allowed = {code for code, _ in TaskPart.STATUS.choices}
            if status_param not in allowed:
                return Response(
                    {"detail": "`status` noto‘g‘ri.", "allowed": sorted(list(allowed))},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            status_param = None

        # -------- assignee_id (optional) --------
        if assignee_id is not None and assignee_id != "":
            try:
                assignee_id = int(assignee_id)
            except (TypeError, ValueError):
                return Response({"detail": "`assignee_id` integer bo‘lishi kerak."},
                                status=drf_status.HTTP_400_BAD_REQUEST)

            if not User.objects.filter(id=assignee_id).exists():
                return Response({"detail": "Berilgan `assignee_id` bo‘yicha user topilmadi."},
                                status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            assignee_id = None

        # =========================================================
        # MUHIM: TaskPart hammasi company_id bo‘yicha FILTER
        # =========================================================
        qs = TaskPart.objects.filter(task__company_id=company_id)

        # keyin qolgan ixtiyoriy filterlar
        qs = qs.filter(start_date__isnull=False, start_date__year=year)

        if month is not None:
            qs = qs.filter(start_date__month=month)

        if status_param is not None:
            qs = qs.filter(status=status_param)

        if assignee_id is not None:
            qs = qs.filter(assignee_id=assignee_id)

        # -------- overall by_status --------
        overall_rows = qs.values('status').annotate(count=Count('id')).order_by('status')
        overall_map = {r["status"]: int(r["count"]) for r in overall_rows}

        total = 0
        by_status = {}
        for code, label in TaskPart.STATUS.choices:
            c = overall_map.get(code, 0)
            total += c
            by_status[code] = {"label": str(label), "count": c}

        # -------- group by start_date + status --------
        date_status_rows = (
            qs.values('start_date', 'status')
              .annotate(count=Count('id'))
              .order_by('start_date', 'status')
        )

        grouped = {}
        for r in date_status_rows:
            d = r["start_date"]
            s = r["status"]
            grouped.setdefault(d, {})
            grouped[d][s] = int(r["count"])

        by_start_date = []
        for d in sorted(grouped.keys()):
            status_counts = grouped[d]
            day_total = 0
            day_by_status = {}

            for code, label in TaskPart.STATUS.choices:
                c = int(status_counts.get(code, 0))
                day_total += c
                day_by_status[code] = {"label": str(label), "count": c}

            by_start_date.append({
                "start_date": d.isoformat(),
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
