from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.models import TaskComment
from docoborot.serializers import TaskCommentSerializer
from docoborot.filterset import TaskCommentFilter

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class TaskCommentFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []
        for field in TaskComment._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class TaskCommentView(ListCreateAPIView):
    """
    TaskComment (Izohlar):
    - Task/TaskPart bo‘yicha izohlar saqlanadi.
    - UI’da chip/tag yoki comment ro‘yxat bo‘lib ko‘rsatiladi.
    - Har bir izoh tarixga ham tushishi mumkin (TaskEvent COMMENTED).
    """
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskCommentSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskCommentFilter
    search_fields = ('text',)
    ordering = ['pk']

    def get_queryset(self):
        return TaskComment.objects.all()

    def post(self, request):
        serializer = TaskCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskCommentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        return TaskComment.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(TaskComment, id=pk)
        serializer = TaskCommentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(TaskComment, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(TaskComment, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)
