from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.filterset import CommandFilter
from docoborot.models import Command
from docoborot.serializers import CommandSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class CommandFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []

        for field in Command._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class CommandView(ListCreateAPIView):
    serializer_class = CommandSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = CommandFilter
    search_fields = ('company', 'order_number',  'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    ordering = ['pk']

    def get_queryset(self):
        return Command.objects.all()

    def post(self, request):
        serializer = CommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CommandDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommandSerializer

    def get_queryset(self):
        return Command.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Command, id=pk)
        serializer = CommandSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Command, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(Command, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



