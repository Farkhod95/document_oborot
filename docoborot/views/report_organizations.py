from django.db.models import Count, Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from docoborot.models import TaskPart, Task
from users.models import Company  # Company qayerda bo‘lsa o‘sha importni qo‘ying


class OrganizationsReportView(APIView):
    """
    POST:
      - company_id: int (majburiy)
      - year: int (ixtiyoriy) -> default: joriy yil
      - month: int (ixtiyoriy, 1-12)

    Qaytaradi (rasmdagi table uchun):
      items: [
        {
          "org": "Tashkilot nomi",
          "total": 0,
          "done": 0,
          "in_progress": 0,
          "overdue": 0
        }
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

        # ===================== base queryset (TaskPart) =====================
        qs = TaskPart.objects.filter(
            task__company_id=company_id,
            start_date__isnull=False,
            start_date__year=year,
        )

        if month is not None:
            qs = qs.filter(start_date__month=month)

        # sending_org bo'sh bo'lsa "Noma'lum" deb guruhlaymiz
        # DB-level COALESCE qilish uchun Case/When ishlatish mumkin,
        # lekin soddaroq: values('task__sending_org') bilan olib, python’da normalize qilamiz.
        done_status = TaskPart.STATUS.DONE
        cancelled_status = TaskPart.STATUS.CANCELLED

        rows = (
            qs.values("task__sending_org")
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
              .order_by("task__sending_org")
        )

        items = []
        for i, r in enumerate(rows, start=1):
            org = (r.get("task__sending_org") or "").strip()
            if not org:
                org = "Noma’lum"

            items.append({
                "index": i,
                "org": org,
                "total": int(r.get("total", 0)),
                "done": int(r.get("done", 0)),
                "in_progress": int(r.get("in_progress", 0)),
                "overdue": int(r.get("overdue", 0)),
            })

        return Response(
            {
                "company_id": company_id,
                "year": year,
                "month": month,
                "items_total": len(items),
                "items": items,
            },
            status=drf_status.HTTP_200_OK
        )
