from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.models import TaskEvent
from docoborot.serializers import TaskEventSerializer
from docoborot.filterset import TaskEventFilter

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class TaskEventFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []
        for field in TaskEvent._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class TaskEventView(ListCreateAPIView):
    """
    TaskEvent (Log / Tarix / Timeline):
    - Task bo‘yicha barcha harakatlar tarixi shu jadvalda.
    - Kim nima qildi (actor), qachon qildi (created_time), nima bo‘ldi (event_type).
    - UI’da: “Vazifalar tarixi” va “Amalga oshirish jarayoni” shu yerdan chiqadi.
    """
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskEventSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = TaskEventFilter
    search_fields = ('message', 'event_type')
    ordering = ['-created_time']

    def get_queryset(self):
        return TaskEvent.objects.all()

    def post(self, request):
        serializer = TaskEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskEventDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = TaskEventSerializer

    def get_queryset(self):
        return TaskEvent.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(TaskEvent, id=pk)
        serializer = TaskEventSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(TaskEvent, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(TaskEvent, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)
