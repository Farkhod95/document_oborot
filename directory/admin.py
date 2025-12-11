from django.contrib import admin
from directory.models import (
    District, Region, Country
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code', 'region', 'geo_json')
    search_fields = ('name', 'name_en', 'name_uz', 'name_ru', 'name_lt', 'code')