from django.urls import re_path, path

from docoborot.views.command import CommandView, CommandDetailView, CommandFieldInfoView
from docoborot.views.command_file import CommandFileView, CommandFileDetailView, CommandFileFieldInfoView

urlpatterns = [
    re_path(r'^command$', CommandView.as_view(), name='command$_view'),
    path('command$/<int:pk>', CommandDetailView.as_view(), name='command$_detail_view'),
    path('command$/fields/', CommandFieldInfoView.as_view(), name='command$_fields_info'),

    re_path(r'^command-file$', CommandFileView.as_view(), name='command_file_view'),
    path('command-file/<int:pk>', CommandFileDetailView.as_view(), name='command_file_detail_view'),
    path('command-file/fields/', CommandFileFieldInfoView.as_view(), name='command_file_fields_info'),
]
