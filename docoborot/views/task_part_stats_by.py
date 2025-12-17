from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from docoborot.models import TaskPart


class TaskPartStatsByStartDateView(APIView):
    """
    POST:
      - year: int (majburiy)
      - month: int (ixtiyoriy, 1-12)
      - status: str (ixtiyoriy) -> TaskPart.STATUS qiymatlaridan biri

    Qaytaradi:
      - Umumiy: year, month, status, total, by_status
      - start_date bo‘yicha gruppa: by_start_date (har bir sanada statuslar kesimida count)
    """
    permission_classes = [IsAuthenticated]  # kerak bo'lsa NotClientUser ga almashtiring

    def post(self, request, *args, **kwargs):
        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)

        # -------------------- validation: year --------------------
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {"detail": "`year` majburiy va integer bo‘lishi kerak. Masalan: 2025"},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # -------------------- validation: month (optional) --------------------
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

        # -------------------- validation: status (optional) --------------------
        if status_param is not None and status_param != "":
            allowed_statuses = {code for code, _ in TaskPart.STATUS.choices}
            if status_param not in allowed_statuses:
                return Response(
                    {
                        "detail": "`status` noto‘g‘ri. Ruxsat etilgan qiymatlar:",
                        "allowed": sorted(list(allowed_statuses)),
                    },
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            status_param = None

        # -------------------- base queryset --------------------
        qs = TaskPart.objects.filter(
            start_date__isnull=False,
            start_date__year=year,
        )
        if month is not None:
            qs = qs.filter(start_date__month=month)

        if status_param is not None:
            qs = qs.filter(status=status_param)

        # -------------------- overall by_status --------------------
        overall_rows = (
            qs.values('status')
              .annotate(count=Count('id'))
              .order_by('status')
        )
        overall_map = {r["status"]: int(r["count"]) for r in overall_rows}

        total = 0
        by_status = {}
        for code, label in TaskPart.STATUS.choices:
            c = overall_map.get(code, 0)
            total += c
            by_status[code] = {"label": str(label), "count": c}

        # -------------------- group by start_date + status --------------------
        date_status_rows = (
            qs.values('start_date', 'status')
              .annotate(count=Count('id'))
              .order_by('start_date', 'status')
        )

        grouped = {}  # {date_obj: {status_code: count}}
        for r in date_status_rows:
            d = r["start_date"]
            s = r["status"]
            c = int(r["count"])
            grouped.setdefault(d, {})
            grouped[d][s] = c

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
                "start_date": d.isoformat(),   # "YYYY-MM-DD"
                "total": day_total,
                "by_status": day_by_status,
            })

        return Response(
            {
                "year": year,
                "month": month,                 # None bo‘lishi mumkin
                "status": status_param,         # None bo‘lishi mumkin
                "total": total,
                "by_status": by_status,         # umumiy status kesimida (filter bo'lsa ham 0 bilan to'liq)
                "by_start_date": by_start_date, # start_date bo‘yicha gruppalab
            },
            status=drf_status.HTTP_200_OK
        )
