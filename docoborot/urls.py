from django.urls import re_path, path

from docoborot.views.command import CommandView, CommandDetailView, CommandFieldInfoView
from docoborot.views.command_file import CommandFileView, CommandFileDetailView, CommandFileFieldInfoView
from docoborot.views.reply_letter import ReplyLetterView, ReplyLetterDetailView, ReplyLetterFieldInfoView
from docoborot.views.reply_letter_file import ReplyLetterFileView, ReplyLetterFileDetailView, \
    ReplyLetterFileFieldInfoView
from docoborot.views.task_file import TaskFileView, TaskFileDetailView, TaskFileFieldInfoView

urlpatterns = [

    re_path(r'^task-file/$', TaskFileView.as_view(), name='task_file_view'),
    path('task-file/<int:pk>', TaskFileDetailView.as_view(), name='task_file_detail_view'),
    path('task-file/fields/', TaskFileFieldInfoView.as_view(), name='task_file_fields_info'),
    re_path(r'^command/$', CommandView.as_view(), name='command_view'),
    path('command/<int:pk>', CommandDetailView.as_view(), name='command_detail_view'),
    path('command/fields/', CommandFieldInfoView.as_view(), name='command_fields_info'),

    re_path(r'^command-file/$', CommandFileView.as_view(), name='command_file_view'),
    path('command-file/<int:pk>', CommandFileDetailView.as_view(), name='command_file_detail_view'),
    path('command-file/fields/', CommandFileFieldInfoView.as_view(), name='command_file_fields_info'),

    re_path(r'^reply-letter/$', ReplyLetterView.as_view(), name='reply_letter_view'),
    path('reply-letter/<int:pk>', ReplyLetterDetailView.as_view(), name='reply_letter_detail_view'),
    path('reply-letter/fields/', ReplyLetterFieldInfoView.as_view(), name='reply_letter_fields_info'),

    re_path(r'^reply-letter-file/$', ReplyLetterFileView.as_view(), name='reply_letter_file_view'),
    path('reply-letter-file/<int:pk>', ReplyLetterFileDetailView.as_view(), name='reply_letter_file_detail_view'),
    path('reply-letter-file/fields/', ReplyLetterFileFieldInfoView.as_view(), name='reply_letter_file_fields_info'),
]
