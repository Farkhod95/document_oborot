from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.models import Task
from docoborot.serializers import TaskSerializer
from docoborot.filterset import TaskFilter

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class TaskFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []
        for field in Task._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class TaskView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskFilter
    search_fields = ('name', 'sending_org', 'input_doc_number', 'output_doc_number', 'note')
    ordering = ['pk']

    ROLE_PRIORITY = ("Admin", "Manager", "Performer", "Signatory")

    def _has_role(self, user, role_name: str) -> bool:
        roles_rel = getattr(user, "roles", None)
        if roles_rel is not None:
            try:
                if roles_rel.filter(name__iexact=role_name).exists():
                    return True
            except Exception:
                pass
        return user.groups.filter(name__iexact=role_name).exists()

    def _highest_role(self, user) -> str | None:
        # Superuser bo‘lsa - Admindek ko‘ramiz
        if getattr(user, "is_superuser", False):
            return "Admin"

        for role in self.ROLE_PRIORITY:
            if self._has_role(user, role):
                return role
        return None

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.all()

        role = self._highest_role(user)

        # ✅ 1) Admin/Manager -> hammasi
        if role in ("Admin", "Manager"):
            return qs

        # ✅ 2) Performer -> eski logika
        if role == "Performer":
            return qs.filter(parts__assignee_id=user.id).distinct()

        # ✅ 3) Signatory -> eski logika
        if role == "Signatory":
            return qs.filter(signed_by_id=user.id)

        # ✅ Hech qanday rol bo‘lmasa default (xohlasangiz qs.none() ham qilsa bo‘ladi)
        return qs.none()


    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Task, id=pk)
        serializer = TaskSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Task, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(Task, id=pk)
        instance.status = 'archive'
        instance.save()
        # instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)
