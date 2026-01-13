from django.urls import re_path, path

from docoborot.views.command import CommandView, CommandDetailView, CommandFieldInfoView
from docoborot.views.command_file import CommandFileView, CommandFileDetailView, CommandFileFieldInfoView
from docoborot.views.dashboard_report import CompanyDashboardStatsView
from docoborot.views.employee_account import EmployeeAccountView, EmployeeAccountDetailView, \
    EmployeeAccountFieldInfoView
from docoborot.views.get_task_by_date import TaskTaskPartByDateView, SelfTaskTaskPartByDateView
from docoborot.views.reply_letter import ReplyLetterView, ReplyLetterDetailView, ReplyLetterFieldInfoView
from docoborot.views.reply_letter_file import ReplyLetterFileView, ReplyLetterFileDetailView, \
    ReplyLetterFileFieldInfoView
from docoborot.views.report_employees import CompanyEmployeesReportView
from docoborot.views.report_organizations import OrganizationsReportView
from docoborot.views.self_task_part_stats_by import TaskPartSelfByStartDateView
from docoborot.views.send_to_email import SendToEmailView
from docoborot.views.task import TaskView, TaskDetailView, TaskFieldInfoView, TaskSelfView, TaskArchiveView
from docoborot.views.task_attachment import TaskAttachmentView, TaskAttachmentDetailView, TaskAttachmentFieldInfoView
from docoborot.views.task_comment import TaskCommentView, TaskCommentDetailView, TaskCommentFieldInfoView
from docoborot.views.task_event import TaskEventView, TaskEventDetailView, TaskEventFieldInfoView
from docoborot.views.task_part import TaskPartView, TaskPartDetailView, TaskPartFieldInfoView
from docoborot.views.task_part_stats_by import TaskPartStatsByStartDateView
from docoborot.views.task_with_parts_by_id import TaskWithPartsByIdView

urlpatterns = [

    # TASK
    re_path(r'^task/$', TaskView.as_view(), name='task_view'),
    path('task/<int:pk>', TaskDetailView.as_view(), name='task_detail_view'),
    path('task/<int:pk>/archive/', TaskArchiveView.as_view(), name='task_archive_view'),
    path('task/self/', TaskSelfView.as_view(), name='task_self_view'),
    path('task/fields/', TaskFieldInfoView.as_view(), name='task_fields_info'),
    path('task/with-parts/by-id/', TaskWithPartsByIdView.as_view(), name='task-with-parts-by-id'),
    path("task/send-to-email/", SendToEmailView.as_view(), name="send-to-email"),

    # TASK PART
    re_path(r'^task-part/$', TaskPartView.as_view(), name='task_part_view'),
    path('task-part/<int:pk>', TaskPartDetailView.as_view(), name='task_part_detail_view'),
    path('task-part/fields/', TaskPartFieldInfoView.as_view(), name='task_part_fields_info'),
    path('task-calendar/stats/by-start-date/', TaskPartStatsByStartDateView.as_view(), name='task-part-stats-by-start-date'),
    path('task-calendar/self/by-start-date/', TaskPartSelfByStartDateView.as_view(), name='task-part-stats-by-start-date'),
    path('task-calendar/get-task-by-date/', TaskTaskPartByDateView.as_view(), name='task-part-stats-by-start-date'),
    path('task-calendar/self/get-task-by-date/', SelfTaskTaskPartByDateView.as_view(), name='task-part-stats-by-start-date'),

    # TASK EVENT (LOG)
    re_path(r'^task-event/$', TaskEventView.as_view(), name='task_event_view'),
    path('task-event/<int:pk>', TaskEventDetailView.as_view(), name='task_event_detail_view'),
    path('task-event/fields/', TaskEventFieldInfoView.as_view(), name='task_event_fields_info'),

    # TASK ATTACHMENT
    re_path(r'^task-attachment/$', TaskAttachmentView.as_view(), name='task_attachment_view'),
    path('task-attachment/<int:pk>', TaskAttachmentDetailView.as_view(), name='task_attachment_detail_view'),
    path('task-attachment/fields/', TaskAttachmentFieldInfoView.as_view(), name='task_attachment_fields_info'),

    # TASK COMMENT
    re_path(r'^task-comment/$', TaskCommentView.as_view(), name='task_comment_view'),
    path('task-comment/<int:pk>', TaskCommentDetailView.as_view(), name='task_comment_detail_view'),
    path('task-comment/fields/', TaskCommentFieldInfoView.as_view(), name='task_comment_fields_info'),

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

    re_path(r'^employee-account/$', EmployeeAccountView.as_view(), name='employee_account_view'),
    path('employee-account/<int:pk>', EmployeeAccountDetailView.as_view(), name='employee_account_detail_view'),
    path('employee-account/fields/', EmployeeAccountFieldInfoView.as_view(), name='employee_account_fields_info'),

    path("dashboard/stats/", CompanyDashboardStatsView.as_view(), name="dashboard-stats"),
    path('reports/employees/', CompanyEmployeesReportView.as_view(), name='report-employees'),
    path('reports/organizations/', OrganizationsReportView.as_view(), name='report-organizations'),
]
