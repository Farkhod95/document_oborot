from django_filters.rest_framework import FilterSet
import django_filters
from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile, EmployeeAccount

from docoborot.models import Task, TaskPart, TaskEvent, TaskAttachment, TaskComment


class TaskFilter(FilterSet):
    class Meta:
        model = Task
        fields = {
            'company': ['exact'],
            'type': ['exact'],
            'status': ['exact'],
            'priority': ['exact'],
            # 'department': ['exact'],
            # 'signed_by': ['exact'],
            'task_type': ['exact'],
            'name': ['exact', 'icontains'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte'],
            'signed_date': ['exact', 'gte', 'lte'],
        }


class TaskPartFilter(FilterSet):
    start_date = django_filters.DateFromToRangeFilter(field_name='start_date', lookup_expr='date')
    end_date   = django_filters.DateFromToRangeFilter(field_name='end_date', lookup_expr='date')
    show_date  = django_filters.DateFromToRangeFilter(field_name='show_date', lookup_expr='date')

    class Meta:
        model = TaskPart
        fields = {
            'task': ['exact'],
            # 'department': ['exact'],
            # 'assignee': ['exact'],
            'status': ['exact'],
            'title': ['exact', 'icontains'],
            # 'start_date': ['exact', 'gte', 'lte'],
            # 'end_date': ['exact', 'gte', 'lte'],
            # 'show_date': ['exact', 'gte', 'lte'],
        }


class TaskEventFilter(FilterSet):
    class Meta:
        model = TaskEvent
        fields = {
            'task': ['exact'],
            'part': ['exact'],
            'actor': ['exact'],
            'event_type': ['exact'],
            'from_status': ['exact'],
            'to_status': ['exact'],
        }


class TaskAttachmentFilter(FilterSet):
    class Meta:
        model = TaskAttachment
        fields = {
            'task': ['exact'],
            'part': ['exact'],
            'comment': ['exact'],
            'link': ['exact'],
            'title': ['exact', 'icontains'],
            'uploaded_by': ['exact'],
        }


class TaskCommentFilter(FilterSet):
    class Meta:
        model = TaskComment
        fields = {
            'task': ['exact'],
            'part': ['exact'],
            'author': ['exact'],
            'is_system': ['exact'],
            'text': ['exact', 'icontains'],
        }


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
            'organization': ['exact'],
            'responsible_person': ['exact'],
        }


class ReplyLetterFileFilter(FilterSet):
    class Meta:
        model = ReplyLetterFile
        fields = {
            'reply_letter': ['exact'],
            'title': ['exact', 'icontains'],
        }



class EmployeeAccountFilter(FilterSet):
    class Meta:
        model = EmployeeAccount
        fields = {
            'company': ['exact'],
            'employee': ['exact'],
            'date': ['exact'],
            'type': ['exact'],
        }
