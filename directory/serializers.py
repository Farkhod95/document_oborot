from rest_framework import serializers

from .models import Region, District, Country, Department, Position, DocumentForm, ListOfMagazine


# Tarjima asosiy serializeri
class LocaleSerializer(serializers.ModelSerializer):
    name_en = serializers.CharField(allow_blank=False)
    name_uz = serializers.CharField(allow_blank=False)
    name_ru = serializers.CharField(allow_blank=False)


class CountrySerializer(LocaleSerializer):
    class Meta:
        model = Country
        fields = ('id', 'code', 'name', 'name_en', 'name_uz', 'name_ru')
        extra_kwargs = {
            'code': {"required": True},
            'name_en': {"required": True},
            'name_uz': {"required": True},
            'name_ru': {"required": True},
        }


class CountryListSerializer(LocaleSerializer):
    class Meta:
        model = Country
        fields = ('id', 'code', 'name')


class RelatedRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class RelatedDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name')


class RelatedPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class RegionSerializer(LocaleSerializer):
    class Meta:
        model = Region
        fields = ('id', 'code', 'name', 'name_en', 'name_uz', 'name_ru')
        extra_kwargs = {
            'code': {"required": True},
            'name_en': {"required": True},
            'name_uz': {"required": True},
            'name_ru': {"required": True},
        }


class RegionListSerializer(LocaleSerializer):
    class Meta:
        model = Region
        fields = ('id', 'code', 'name', 'name_en', 'name_uz', 'name_ru')


class RegionListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Region
        fields = ('id', 'code', 'name')


class DistrictListPublicSerializer(LocaleSerializer):
    class Meta:
        model = District
        fields = ('id', 'code', 'name')


class DistrictListSerializer(LocaleSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)

    class Meta:
        model = District
        fields = ('id', 'code', 'name', 'name_en', 'name_uz', 'name_ru', 'region', 'region_detail')


class DistrictSerializer(LocaleSerializer):
    class Meta:
        model = District
        fields = ('id', 'code', 'name', 'name_en', 'name_uz', 'name_ru', 'region')
        extra_kwargs = {
            'code': {"required": True},
            'region': {"required": True},
            'name_en': {"required": True},
            'name_uz': {"required": True},
            'name_ru': {"required": True},
        }


class DepartmentSerializer(LocaleSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru')
        extra_kwargs = {
            'name_en': {"required": True},
            'name_uz': {"required": True},
            'name_ru': {"required": True},
        }


class DepartmentListSerializer(LocaleSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru',)


class DepartmentListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class PositionSerializer(LocaleSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru', 'department')
        extra_kwargs = {
            'department': {"required": True},
            'name_en': {"required": True},
            'name_uz': {"required": True},
            'name_ru': {"required": True},
        }


class PositionListSerializer(LocaleSerializer):
    department_detail = DepartmentListPublicSerializer(source="department", read_only=True)

    class Meta:
        model = Position
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru', 'department', 'department_detail')


class PositionListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name')


class DocumentFormSerializer(LocaleSerializer):

    class Meta:
        model = DocumentForm
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru',)


class ListOfMagazineSerializer(LocaleSerializer):

    class Meta:
        model = ListOfMagazine
        fields = ('id', 'name', 'name_en', 'name_uz', 'name_ru',)

