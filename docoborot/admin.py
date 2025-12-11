from django.contrib import admin

from docoborot.models import Command, CommandFile


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('company', 'order_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    fields =  ('company', 'order_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru')
    search_fields = ('company', 'order_number')


@admin.register(CommandFile)
class CommandFileAdmin(admin.ModelAdmin):
    list_display = ('order_document', 'title',)
    fields =  ('order_document', 'title', 'file')
    search_fields = ('order_document', 'title')