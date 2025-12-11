from django_filters.rest_framework import FilterSet

from docoborot.models import Command, CommandFile


class CommandFilter(FilterSet):
    class Meta:
        model = Command
        fields = {
            'company': ['exact'],
            'order_number': ['exact', 'icontains'],
        }


class CommandFileFilter(FilterSet):
    class Meta:
        model = CommandFile
        fields = {
            'order_document': ['exact'],
            'title': ['exact', 'icontains'],
        }