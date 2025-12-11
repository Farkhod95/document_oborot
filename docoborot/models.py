from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from directory.models import Region, District, Country
from restapp.models import BaseModel
from users.models import Company

User = settings.AUTH_USER_MODEL


class Command(BaseModel):
    company = models.ForeignKey(Company, related_name='command_company', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kompaniya"))
    order_number = models.CharField(_('Order number'), max_length=100, null=True, blank=True, help_text=_("Buyruq raqami"))
    basis = models.CharField(_('Basis '), max_length=255, null=True, blank=True, help_text=_("Hujjat uchun asos"))
    comment  = models.TextField(_('Comment'), blank=True, help_text=_("Izoh"))

    class Meta:
        verbose_name = _('Command')
        verbose_name_plural = _('Commands')

    def __str__(self):
        return self.order_number


class CommandFile(BaseModel):
    order_document = models.ForeignKey(Command, on_delete=models.CASCADE, related_name="files", verbose_name="Order document",)
    title = models.CharField("Title", max_length=255)
    file = models.FileField("File", upload_to="order_documents/")

    class Meta:
        verbose_name = "Command file"
        verbose_name_plural = "Command files"

    def __str__(self):
        return f"{self.order_document.order_number} - {self.title}"
