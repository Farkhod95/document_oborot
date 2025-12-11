from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.filterset import CommandFileFilter
from docoborot.models import CommandFile
from docoborot.serializers import CommandFileSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class CommandFileFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []

        for field in CommandFile._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class CommandFileView(ListCreateAPIView):
    serializer_class = CommandFileSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = CommandFileFilter
    search_fields = ('order_document', 'title')
    ordering = ['pk']

    def get_queryset(self):
        return CommandFile.objects.all()

    def post(self, request):
        serializer = CommandFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CommandFileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommandFileSerializer

    def get_queryset(self):
        return CommandFile.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(CommandFile, id=pk)
        serializer = CommandFileSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(CommandFile, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(CommandFile, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



