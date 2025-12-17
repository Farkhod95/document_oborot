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
      - status: str (ixtiyoriy)
      - assignee_id: int (ixtiyoriy)

    Qaytaradi:
      - total
      - by_status: faqat mavjud statuslar
      - by_start_date: har sanada faqat mavjud statuslar
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company_id')
        year = request.data.get('year')
        month = request.data.get('month', None)
        status_param = request.data.get('status', None)
        assignee_id = request.data.get('assignee_id', None)

        # company_id
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            return Response({"detail": "`company_id` majburiy va integer bo‘lishi kerak."},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        if not Company.objects.filter(id=company_id).exists():
            return Response({"detail": "Berilgan `company_id` bo‘yicha kompaniya topilmadi."},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        # year
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({"detail": "`year` majburiy va integer bo‘lishi kerak. Masalan: 2025"},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        # month (optional)
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

        # status (optional)
        if status_param is not None and status_param != "":
            allowed = {code for code, _ in TaskPart.STATUS.choices}
            if status_param not in allowed:
                return Response(
                    {"detail": "`status` noto‘g‘ri.", "allowed": sorted(list(allowed))},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
        else:
            status_param = None

        # assignee_id (optional)
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

        # queryset (company_id filter majburiy)
        qs = TaskPart.objects.filter(
            task__company_id=company_id,
            start_date__isnull=False,
            start_date__year=year,
        )

        if month is not None:
            qs = qs.filter(start_date__month=month)

        if status_param is not None:
            qs = qs.filter(status=status_param)

        if assignee_id is not None:
            qs = qs.filter(assignee_id=assignee_id)

        # overall by_status (faqat mavjudlari)
        overall_rows = qs.values('status').annotate(count=Count('id')).order_by('status')
        total = 0
        by_status = []
        for r in overall_rows:
            total += int(r["count"])
            by_status.append({"status": r["status"], "count": int(r["count"])})

        # group by start_date + status (faqat mavjudlari)
        date_status_rows = (
            qs.values('start_date', 'status')
              .annotate(count=Count('id'))
              .order_by('start_date', 'status')
        )

        grouped = {}  # {"YYYY-MM-DD": [{"status": "...", "count": n}, ...]}
        totals_by_date = {}  # {"YYYY-MM-DD": total}

        for r in date_status_rows:
            d = r["start_date"].isoformat()
            grouped.setdefault(d, [])
            grouped[d].append({"status": r["status"], "count": int(r["count"])})
            totals_by_date[d] = totals_by_date.get(d, 0) + int(r["count"])

        by_start_date = []
        for d in sorted(grouped.keys()):
            by_start_date.append({
                "start_date": d,
                "total": totals_by_date.get(d, 0),
                "by_status": grouped[d],
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
