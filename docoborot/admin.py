from django.contrib import admin

from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    fields =  ('company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    search_fields = ('company', 'command_number')


@admin.register(CommandFile)
class CommandFileAdmin(admin.ModelAdmin):
    list_display = ('command', 'title',)
    fields =  ('command', 'title', 'file')
    search_fields = ('command', 'title')


@admin.register(ReplyLetter)
class ReplyLetterAdmin(admin.ModelAdmin):
    list_display = ('company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment')
    fields =  ('company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment')
    search_fields = ('company', 'task')


@admin.register(ReplyLetterFile)
class ReplyLetterFileAdmin(admin.ModelAdmin):
    list_display = ('reply_letter', 'title',)
    fields =  ('reply_letter', 'title', 'file')
    search_fields = ('reply_letter', 'title')