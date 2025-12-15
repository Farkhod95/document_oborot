from modeltranslation.translator import register, TranslationOptions

from .models import Region, District, Country, Department, Position, DocumentForm, ListOfMagazine


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


@register(DocumentForm)
class DocumentFormTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ListOfMagazine)
class ListOfMagazineTranslationOptions(TranslationOptions):
    fields = ('name',)