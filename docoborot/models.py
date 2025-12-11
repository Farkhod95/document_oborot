from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from directory.models import Region, District, Country
from restapp.models import BaseModel
from users.models import Company

User = settings.AUTH_USER_MODEL


class Task(BaseModel):
    company = models.ForeignKey(Company, related_name='command_task', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Vazifalar"))
    task_number = models.CharField(_('Task number'), max_length=100, null=True, blank=True, help_text=_("Task raqami"))


    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return self.task_number

class Command(BaseModel):
    company = models.ForeignKey(Company, related_name='command_company', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kompaniya"))
    command_number = models.CharField(_('Command number'), max_length=100, null=True, blank=True, help_text=_("Buyruq raqami"))
    basis = models.CharField(_('Basis '), max_length=255, null=True, blank=True, help_text=_("Hujjat uchun asos"))
    comment  = models.TextField(_('Comment'), blank=True, help_text=_("Izoh"))

    class Meta:
        verbose_name = _('Command')
        verbose_name_plural = _('Commands')

    def __str__(self):
        return self.command_number


class CommandFile(BaseModel):
    command = models.ForeignKey(Command, on_delete=models.CASCADE, related_name="files", verbose_name="Order document",)
    title = models.CharField("Title", max_length=255)
    file = models.FileField("File", upload_to="command/%Y/%m/%d", null=True, blank=True)

    class Meta:
        verbose_name = "Command file"
        verbose_name_plural = "Command files"

    def __str__(self):
        return f"{self.command.command_number} - {self.title}"



class ReplyLetter(BaseModel):
    company = models.ForeignKey(Company, related_name='company_letter', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kompaniya"))
    task = models.ForeignKey(Task, related_name='task_letter', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Vazifalar"))
    letter_number = models.CharField(_('Order number'), max_length=100, null=True, blank=True, help_text=_("Buyruq raqami"))
    responsible_person = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE, verbose_name=_('Foydalanuvchi'))
    basis = models.CharField(_('Basis '), max_length=255, null=True, blank=True, help_text=_("Hujjat uchun asos"))
    comment  = models.TextField(_('Comment'), blank=True, help_text=_("Izoh"))

    class Meta:
        verbose_name = _('Reply Letter')
        verbose_name_plural = _('Reply Letters')

    def __str__(self):
        return self.letter_number


class ReplyLetterFile(BaseModel):
    reply_letter = models.ForeignKey(ReplyLetter, on_delete=models.CASCADE, related_name="files", verbose_name="Order document",)
    title = models.CharField("Title", max_length=255)
    file = models.FileField("File", upload_to="replyletter/%Y/%m/%d", null=True, blank=True)

    class Meta:
        verbose_name = "Reply Letter file"
        verbose_name_plural = "Reply Letter files"

    def __str__(self):
        return f"{self.reply_letter.letter_number} - {self.title}"
