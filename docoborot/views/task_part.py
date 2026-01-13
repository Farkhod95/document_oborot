from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from docoborot.models import TaskPart
from docoborot.serializers import TaskPartSerializer
from docoborot.filterset import TaskPartFilter

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class TaskPartFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []
        for field in TaskPart._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class SelfTaskPartFieldInfoView(ListCreateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskPartSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskPartFilter
    search_fields = ('title', 'note')
    ordering = ['pk']
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        task_part = TaskPart.objects.filter(assignee=user)
        return task_part


class TaskPartView(ListCreateAPIView):
    """
    TaskPart (Vazifa bo‘lagi / Subtask):
    - Task ichidagi alohida qism.
    - Har bir qism bitta ijrochiga (assignee) biriktiriladi.
    - Status va muddatlar qism bo‘yicha alohida yuradi.
    """
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskPartSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskPartFilter
    search_fields = ('title', 'note')
    ordering = ['pk']

    def get_queryset(self):
        return TaskPart.objects.all()

    def post(self, request):
        serializer = TaskPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskPartDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskPartSerializer

    def get_queryset(self):
        return TaskPart.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(TaskPart, id=pk)

        # ✅ Agar zapros yuboruvchi assignee bo'lsa va status NEW bo'lsa -> IN_PROGRESS
        if instance.assignee_id == request.user.id and instance.status == TaskPart.STATUS.NEW:
            instance.status = TaskPart.STATUS.IN_PROGRESS

            # ixtiyoriy: birinchi ko‘rish vaqtini yozib qo‘yish
            if not instance.show_date:
                instance.show_date = timezone.now()

            # kim update qilganini yozib qo‘yamiz
            instance.updated_by = request.user

            # model save() ichidagi log + recompute_status ishlashi uchun .save() chaqiramiz
            instance.save(
                actor=request.user,
                update_fields=["status", "show_date", "updated_by", "updated_time"],
            )

        serializer = TaskPartSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(TaskPart, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(TaskPart, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)
