from rest_framework import serializers

from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile
from users.serializers import CompanySerializer, UserDetailSerializer


# Tarjima asosiy serializeri
class LocaleSerializer(serializers.ModelSerializer):
    name_en = serializers.CharField(allow_blank=False)
    name_uz = serializers.CharField(allow_blank=False)
    name_ru = serializers.CharField(allow_blank=False)

    title_en = serializers.CharField(allow_blank=False)
    title_uz = serializers.CharField(allow_blank=False)
    title_ru = serializers.CharField(allow_blank=False)

    subtitle_en = serializers.CharField(allow_blank=False)
    subtitle_uz = serializers.CharField(allow_blank=False)
    subtitle_ru = serializers.CharField(allow_blank=False)

    basis_en = serializers.CharField(allow_blank=False)
    basis_uz = serializers.CharField(allow_blank=False)
    basis_ru = serializers.CharField(allow_blank=False)

    comment_en = serializers.CharField(allow_blank=False)
    comment_uz = serializers.CharField(allow_blank=False)
    comment_ru = serializers.CharField(allow_blank=False)


class BaseLocaleSerializer(serializers.ModelSerializer):
    """
    Dinamik ko‘p tilli serializer:
    Modelda mavjud bo‘lgan *_en/_uz/_ru maydonlar avtomatik qo‘shiladi.
    """
    TRANSLATABLE_BASES = [
        # eng ko‘p uchraydiganlar
        'name',
    ]
    LANGS = ['en', 'uz', 'ru']
    REQUIRED_BASES = {'name', 'title', 'subtitle', 'basis', 'comment'}  # muhim maydonlar

    def get_fields(self):
        fields = super().get_fields()
        model = getattr(self.Meta, 'model', None)
        if not model:
            return fields

        # Modeldagi real maydonlar to‘plami
        model_field_names = {f.name for f in model._meta.get_fields()}

        for base in self.TRANSLATABLE_BASES:
            for lang in self.LANGS:
                f_name = f"{base}_{lang}"
                if f_name in model_field_names:
                    fields[f_name] = serializers.CharField(
                        allow_blank=False,
                        required=(base in self.REQUIRED_BASES)
                    )
        return fields


class CommandSerializer(LocaleSerializer):
    class Meta:
        model = Command
        fields = ('id', 'company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru', 'created_time')


class CommandListSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = Command
        fields = ('id', 'company', 'company_detail', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru', 'created_time')


class CommandFileSerializer(LocaleSerializer):
    class Meta:
        model = CommandFile
        fields = ('id', 'command', 'title', 'file')


class ReplyLetterSerializer(LocaleSerializer):
    class Meta:
        model = ReplyLetter
        fields = ('id', 'company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment')


class ReplyLetterListSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)
    responsible_person_detail = UserDetailSerializer(source='responsible_person', read_only=True)

    class Meta:
        model = ReplyLetter
        fields = ('id', 'company', 'company_detail', 'task', 'letter_number', 'responsible_person',
                  'responsible_person_detail', 'basis', 'comment')


class ReplyLetterFileSerializer(LocaleSerializer):
    class Meta:
        model = ReplyLetterFile
        fields = ('id', 'reply_letter', 'title', 'file')
