from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from docoborot.models import Task
from users.models import Company  # Company qayerda bo‘lsa o‘sha importni qo‘ying

User = get_user_model()


class CompanyDashboardStatsView(APIView):
    """
    POST:
      - company_id: int (majburiy)
      - year: int (ixtiyoriy) -> default: joriy yil

    Qaytaradi:
      - cards: employees/documents/archive/orders
      - charts:
          accepted_vs_archived (oylar bo'yicha)
          documents_by_status (oylar bo'yicha statuslar kesimida)
    """
    permission_classes = [IsAuthenticated]  # kerak bo'lsa NotClientUser ga almashtiring

    MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'App', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    STATUS_LABELS_UZ = {
        Task.STATUS.NEW: "Yangi ro‘yxatga olingan",
        Task.STATUS.IN_PROGRESS: "Jarayonda",
        Task.STATUS.ON_REVIEW: "Ko‘rib chiqilmoqda",
        Task.STATUS.RETURNED: "Qaytarilgan",
        Task.STATUS.DONE: "Ijrosi ta’minlangan",
        Task.STATUS.CANCELLED: "Bekor qilingan",
    }

    def _month_map(self, rows):
        """
        rows: [{"m": 1, "count": 5}, ...]
        return: {1:5, 2:0, ..., 12:0}
        """
        m = {i: 0 for i in range(1, 13)}
        for r in rows:
            if r["m"]:
                m[int(r["m"])] = int(r["count"])
        return m

    def post(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        year = request.data.get("year", None)

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

        # ===================== CARDS =====================
        employees_count = (
            User.objects.filter(companies__id=company_id, is_active=True)
            .distinct()
            .count()
        )

        documents_qs = Task.objects.filter(company_id=company_id, type=Task.TYPE.TASK)
        orders_qs = Task.objects.filter(company_id=company_id, type=Task.TYPE.APPLICATION)

        documents_count = documents_qs.count()
        archive_documents_count = Task.objects.filter(company_id=company_id, status=Task.STATUS.DONE).count()
        orders_count = orders_qs.count()

        # ===================== CHART 1: accepted vs archived (by month) =====================
        # accepted: shu yilda yaratilgan tasklar (created_time oy bo‘yicha)
        accepted_rows = (
            Task.objects.filter(company_id=company_id, created_time__year=year)
            .annotate(m=ExtractMonth("created_time"))
            .values("m")
            .annotate(count=Count("id"))
            .order_by("m")
        )
        accepted_map = self._month_map(accepted_rows)

        # archived: DONE bo‘lib yakunlanganlar (updated_time oy bo‘yicha)
        archived_rows = (
            Task.objects.filter(company_id=company_id, status=Task.STATUS.DONE, updated_time__year=year)
            .annotate(m=ExtractMonth("updated_time"))
            .values("m")
            .annotate(count=Count("id"))
            .order_by("m")
        )
        archived_map = self._month_map(archived_rows)

        accepted_vs_archived = {
            "labels": self.MONTH_LABELS,
            "datasets": [
                {
                    "key": "accepted",
                    "label": "Qabul qilingan",
                    "data": [accepted_map[i] for i in range(1, 13)],
                },
                {
                    "key": "archived",
                    "label": "Arxiv (DONE)",
                    "data": [archived_map[i] for i in range(1, 13)],
                },
            ]
        }

        # ===================== CHART 2: documents by status (by month) =====================
        # (created_time oy bo‘yicha, hozirgi statusiga qarab)
        docs_base = Task.objects.filter(company_id=company_id, created_time__year=year)

        documents_by_status = {"labels": self.MONTH_LABELS, "datasets": []}

        for status_code, status_label in Task.STATUS.choices:
            rows = (
                docs_base.filter(status=status_code)
                .annotate(m=ExtractMonth("created_time"))
                .values("m")
                .annotate(count=Count("id"))
                .order_by("m")
            )
            m_map = self._month_map(rows)

            documents_by_status["datasets"].append({
                "key": status_code,
                "label": self.STATUS_LABELS_UZ.get(status_code, str(status_label)),
                "data": [m_map[i] for i in range(1, 13)],
            })

        return Response(
            {
                "company_id": company_id,
                "year": year,

                "cards": {
                    "employees_count": employees_count,
                    "documents_count": documents_count,
                    "archive_documents_count": archive_documents_count,
                    "orders_count": orders_count,
                },

                "charts": {
                    "accepted_vs_archived": accepted_vs_archived,
                    "documents_by_status": documents_by_status,
                },
            },
            status=drf_status.HTTP_200_OK
        )
