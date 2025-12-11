from modeltranslation.translator import register, TranslationOptions

from .models import Region, District, Country, Department, Position


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Position)
class PositionTranslationOptions(TranslationOptions):
    fields = ('name',)