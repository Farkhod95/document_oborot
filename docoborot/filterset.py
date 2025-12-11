from django_filters.rest_framework import FilterSet

from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile


class CommandFilter(FilterSet):
    class Meta:
        model = Command
        fields = {
            'company': ['exact'],
            'command_number': ['exact', 'icontains'],
        }


class CommandFileFilter(FilterSet):
    class Meta:
        model = CommandFile
        fields = {
            'command': ['exact'],
            'title': ['exact', 'icontains'],
        }


class ReplyLetterFilter(FilterSet):
    class Meta:
        model = ReplyLetter
        fields = {
            'company': ['exact'],
            'task': ['exact'],
            'letter_number': ['exact'],
            'responsible_person': ['exact'],
        }


class ReplyLetterFileFilter(FilterSet):
    class Meta:
        model = ReplyLetterFile
        fields = {
            'reply_letter': ['exact'],
            'title': ['exact', 'icontains'],
        }