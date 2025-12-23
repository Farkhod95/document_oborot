from django.contrib import admin

from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile, TaskAttachment, Task, TaskPart, \
    TaskEvent, TaskComment


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    fields =  ('company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    search_fields = ('company__name', 'command_number')


@admin.register(CommandFile)
class CommandFileAdmin(admin.ModelAdmin):
    list_display = ('command', 'title',)
    fields =  ('command', 'title', 'file')
    search_fields = ('company__name', 'title')


@admin.register(ReplyLetter)
class ReplyLetterAdmin(admin.ModelAdmin):
    list_display = ('company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment', 'organization')
    fields =  ('company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment', 'organization')
    search_fields = ('company__name', 'task__name')


@admin.register(ReplyLetterFile)
class ReplyLetterFileAdmin(admin.ModelAdmin):
    list_display = ('reply_letter', 'title',)
    fields =  ('reply_letter', 'title', 'file')
    search_fields = ('reply_letter__letter_number', 'title')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'title', 'part')
    fields =  ('task', 'title', 'file', 'part')
    search_fields = ('task__name', 'title', 'part__title')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('status', 'company', 'type', 'task_type')
    fields =  ('status', 'company', 'type', 'name',
            'task_form', 'sending_org', 'input_doc_number', 'output_doc_number',
            'start_date', 'end_date', 'priority', 'sending_respon_person',
            'department', 'signed_by', 'note', 'task_type',
            'created_time', 'updated_time', 'created_by', 'updated_by', 'list_of_magazine')
    search_fields = ('status', 'company__name',)


@admin.register(TaskPart)
class TaskPartAdmin(admin.ModelAdmin):
    list_display = ('task', 'title',)
    fields =  ('task', 'title', 'department',
            'assignee', 'start_date', 'end_date', 'status', 'note',
            'created_time', 'updated_time', 'created_by', 'updated_by',)
    search_fields = ('task__name', 'title')



@admin.register(TaskEvent)
class TaskEventAdmin(admin.ModelAdmin):
    list_display = ('task', 'part',)
    fields =  ('task', 'part', 'actor',
            'event_type', 'message', 'from_status', 'to_status', 'extra',
            'created_time', 'updated_time', 'created_by', 'updated_by',)
    search_fields = ('task__name', 'part__title')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'part', 'text', 'is_system')
    fields =  ('task', 'author', 'part', 'text', 'is_system')
    search_fields = ('task__name', 'part__title')