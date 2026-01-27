from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.models import TaskAttachment, TaskPart
from docoborot.serializers import TaskAttachmentSerializer
from docoborot.filterset import TaskAttachmentFilter

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class TaskAttachmentFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []
        for field in TaskAttachment._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class TaskAttachmentAllView(ListCreateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskAttachmentSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskAttachmentFilter
    search_fields = ('title', 'file')
    ordering = ['pk']
    http_method_names = ['get']

    def get_queryset(self):
        qs = (
            TaskAttachment.objects
            .select_related('task', 'part', 'comment', 'uploaded_by')
            .all()
        )

        task_id = self.request.query_params.get('task')
        if task_id:
            # ✅ 1) Task'ga bevosita bog'langan attachmentlar (task_id=task_id)
            # ✅ 2) Shu task'ning status=done bo'lgan partlariga bog'langan attachmentlar
            qs = qs.filter(
                Q(task_id=task_id) |
                Q(part__task_id=task_id, part__status=TaskPart.STATUS.DONE)
            ).distinct()

        return qs



class TaskAttachmentView(ListCreateAPIView):
    """
    TaskAttachment (Fayllar):
    - Task yoki TaskPartga fayl biriktirish uchun.
    - UI’da “Fayllar” blokida ko‘rinadi (docx/pdf/...).
    - Fayl yuklanganda tarixga event yozish mumkin (TaskEvent FILE_ADDED).
    """
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskAttachmentSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskAttachmentFilter
    search_fields = ('title', 'file')
    ordering = ['pk']

    def get_queryset(self):
        return TaskAttachment.objects.all()

    def post(self, request):
        serializer = TaskAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskAttachmentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskAttachmentSerializer

    def get_queryset(self):
        return TaskAttachment.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(TaskAttachment, id=pk)
        serializer = TaskAttachmentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(TaskAttachment, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(TaskAttachment, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)


class TaskAttachmentIsReadView(APIView):
    def patch(self, request, pk):
        instance = get_object_or_404(TaskAttachment, pk=pk)

        if not instance.is_read_file:
            instance.is_read_file = True
            instance.save(update_fields=["is_read_file", "updated_time"])

        return Response({"message": "Successfully completed!"}, status=status.HTTP_200_OK)