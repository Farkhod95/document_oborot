from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from docoborot.filterset import ReplyLetterFileFilter
from docoborot.models import ReplyLetterFile
from docoborot.serializers import ReplyLetterFileSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class ReplyLetterFileFieldInfoView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        field_info = []

        for field in ReplyLetterFile._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class ReplyLetterFileView(ListCreateAPIView):
    serializer_class = ReplyLetterFileSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ReplyLetterFileFilter
    search_fields = ('reply_letter', 'title')
    ordering = ['pk']

    def get_queryset(self):
        return ReplyLetterFile.objects.all()

    def post(self, request):
        serializer = ReplyLetterFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ReplyLetterFileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReplyLetterFileSerializer

    def get_queryset(self):
        return ReplyLetterFile.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(ReplyLetterFile, id=pk)
        serializer = ReplyLetterFileSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(ReplyLetterFile, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(ReplyLetterFile, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



