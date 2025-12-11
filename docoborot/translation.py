from modeltranslation.translator import register, TranslationOptions

from .models import Command


@register(Command)
class CommandTranslationOptions(TranslationOptions):
    fields = ('basis', 'comment')
