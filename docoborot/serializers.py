from rest_framework import serializers

from users.serializers import UserDetailSerializer


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
    REQUIRED_BASES = {'name', 'title', 'subtitle'}  # muhim maydonlar

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
