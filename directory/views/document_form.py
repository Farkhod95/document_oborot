from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.filterset import DocumentFormFilter
from directory.models import DocumentForm
from directory.serializers import DocumentFormSerializer

from restapp.pagination import ResultsSetPagination
from rest_framework.permissions import AllowAny


class DocumentFormFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []

        for field in DocumentForm._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class DocumentFormView(ListCreateAPIView):
    serializer_class = DocumentFormSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DocumentFormFilter
    search_fields = ('name_ru', 'name_en', 'name_uz')
    ordering = ['-pk']

    def get_queryset(self):
        return DocumentForm.objects.all()

    def post(self, request, **kwargs):
        serializer = DocumentFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class DocumentFormDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentFormSerializer

    def get_queryset(self):
        return DocumentForm.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(DocumentForm, id=pk)
        serializer = DocumentFormSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(DocumentForm, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
