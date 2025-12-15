from django.contrib import admin
from directory.models import (
    District, Region, Country, Department, Position, DocumentForm, ListOfMagazine
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code', 'region', 'geo_json')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'code')
    
    
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru')
    fields = ('name', 'name_en', 'name_uz', 'name_ru')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'name_en', 'name_uz', 'name_ru')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'department')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru')


@admin.register(DocumentForm)
class DocumentFormAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru')
    fields = ('name', 'name_en', 'name_uz', 'name_ru')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru')


@admin.register(ListOfMagazine)
class ListOfMagazineAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru')
    fields = ('name', 'name_en', 'name_uz', 'name_ru')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru')