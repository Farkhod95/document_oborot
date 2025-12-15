from django.db import models
from django.utils.translation import gettext_lazy as _

from restapp.models import BaseModel


class Country(BaseModel):
    code = models.CharField(_('Country code'), max_length=50, null=True, blank=True, help_text=_("Mamlakat kodi"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Mamlakat nomi"))

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name


class Region(BaseModel):
    code = models.CharField(_('Region code'), max_length=50, null=True, blank=True, help_text=_("Viloyat kodi"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Viloyat nomi"))
    geo_json = models.TextField(_('GeoJson'), blank=True, help_text=_("Deo json"))

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    def __str__(self):
        return f"{self.name}"


class District(BaseModel):
    code = models.CharField(_('District code'), max_length=50, null=True, blank=True, help_text=_("Tuman kodi"))
    name = models.CharField(_('District name'), max_length=255, null=True, blank=True, help_text=_("Tuman nomi"))
    region = models.ForeignKey(Region, related_name='districts', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Viloyat jadvali bilan bog'lanish"))
    geo_json = models.TextField(_('GeoJson'), blank=True, help_text=_("Geo json"))

    class Meta:
        verbose_name = _('district')
        verbose_name_plural = _('districts')

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(_('Department name'), max_length=255, null=True, blank=True,
                            help_text=_("Bo‘limning nomini kiriting"))

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return self.name


class Position(BaseModel):
    name = models.CharField(_('Position name'), max_length=255, null=True, blank=True,
                            help_text=_("Lavozim nomini kiriting"))
    department = models.ForeignKey(Department, related_name='positions', on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("Lavozim tegishli bo‘lgan bo‘limni tanlang"))

    class Meta:
        verbose_name = _('position')
        verbose_name_plural = _('positions')

    def __str__(self):
        return self.name


class DocumentForm(BaseModel):
    name = models.CharField(_('Document form'), max_length=255, null=True, blank=True,
                            help_text=_("Hujjat shakli"))

    class Meta:
        verbose_name = _('Document Form')
        verbose_name_plural = _('Document Forms')

    def __str__(self):
        return self.name



class ListOfMagazine(BaseModel):
    name = models.CharField(_('Jurnal name'), max_length=255, null=True, blank=True,
                            help_text=_("Jurnal nomi"))

    class Meta:
        verbose_name = _('List Of Magazine')
        verbose_name_plural = _('List Of Magazines')

    def __str__(self):
        return self.name