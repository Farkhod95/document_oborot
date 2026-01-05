from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

from restapp.models import BaseModel
from users.models import Company
from directory.models import DocumentForm, Department, ListOfMagazine
from docoborot.utils.emailing import send_new_task_assigned_email

User = settings.AUTH_USER_MODEL


class Task(BaseModel):
    """Asosiy (umumiy) vazifa: hujjat bo‘yicha parent task. Bo‘linmasa ham, kamida 1 ta TaskPart bilan ishlaydi."""
    class PRIORITY(models.TextChoices):
        ORDINARY = 'ordinary', _('Ordinary')
        ORGENTLY = 'orgently', _('Urgently')

    class TYPE(models.TextChoices):
        TASK = 'task', _('Task')
        APPLICATION = 'application', _('Application')

    class TASK_TYPE(models.TextChoices):
        TASK_TYPE1 = 'simple', _('Simple')
        TASK_TYPE2 = 'divide_into_parts', _('Divide into parts')

    class STATUS(models.TextChoices):
        NEW = 'new', _('New')
        IN_PROGRESS = 'in_progress', _('In progress')
        ON_REVIEW = 'on_review', _('On review')
        RETURNED = 'returned', _('Returned')
        DONE = 'done', _('Done')
        CANCELLED = 'cancelled', _('Cancelled')
        ARCHIVE = 'archive', _('Archive')
        EXPIRED = 'expired', _('Expired')

    status = models.CharField(choices=STATUS.choices, max_length=20, default=STATUS.NEW, help_text=_("Holati"))
    task_type = models.CharField(choices=TASK_TYPE.choices, max_length=20, default=TASK_TYPE.TASK_TYPE1, help_text=_("Vazifa turi"))
    company = models.ForeignKey(Company, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kompaniya"))
    type = models.CharField(choices=TYPE.choices, max_length=12, null=True, blank=True, help_text=_("Tip"))
    name = models.CharField(_('Task number'), max_length=100, null=True, blank=True, help_text=_("Task raqami"))
    task_form = models.ForeignKey(DocumentForm, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Hujjat shakli"))
    sending_org = models.CharField(_('Sending'), max_length=255, null=True, blank=True, help_text=_("Yuboruvchi tashkilot"))
    input_doc_number = models.CharField(_('Input doc number'), max_length=255, null=True, blank=True, help_text=_("Kiruvchi hujjat raqami"))
    output_doc_number = models.CharField(_('Output doc number'), max_length=255, null=True, blank=True, help_text=_("Chiquvchi hujjat raqami"))
    # start_date = models.DateField(_('Start date'), null=True, blank=True, help_text=_("Boshlash sanasi"))
    # end_date = models.DateField(_('End date'), null=True, blank=True, help_text=_("Tugash sanasi"))
    start_date = models.DateTimeField(_('Start date'), null=True, blank=True, help_text=_("Boshlash sanasi/vaqti"))
    end_date = models.DateTimeField(_('End date'), null=True, blank=True, help_text=_("Tugash sanasi/vaqti"))
    priority = models.CharField(choices=PRIORITY.choices, max_length=12, null=True, blank=True, help_text=_("Muhimligi"))
    sending_respon_person = models.CharField(_('Responsible person for sending'), max_length=255, null=True, blank=True, help_text=_("Yuborish uchun mas'ul shaxs"))
    department = models.ForeignKey(Department, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Bo‘lim"))
    list_of_magazine = models.ForeignKey(ListOfMagazine, related_name='list_of_magazine_task', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Jurnal nomi"))
    signed_by = models.ForeignKey(User, related_name='tasks_signed_by', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Imzolovchi'))
    # signed_date = models.DateField(_('Signed date'), null=True, blank=True, help_text=_("Imzolangan sanasi"))
    signed_date = models.DateTimeField(_('Signed date'), null=True, blank=True, help_text=_("Imzolangan sanasi/vaqti"))
    note = models.TextField(_('Note'), blank=True, help_text=_("Izoh"))

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return self.name or f"Task#{self.pk}"

    @property
    def is_split(self) -> bool:
        return self.parts.count() > 1

    def recompute_status(self, save: bool = True) -> str:
        qs = self.parts.all()
        if not qs.exists():
            new_status = Task.STATUS.NEW
        else:
            statuses = set(qs.values_list('status', flat=True))
            if statuses.issubset({TaskPart.STATUS.DONE}):
                new_status = Task.STATUS.DONE
            elif TaskPart.STATUS.CANCELLED in statuses and len(statuses) == 1:
                new_status = Task.STATUS.CANCELLED
            elif TaskPart.STATUS.ON_REVIEW in statuses:
                new_status = Task.STATUS.ON_REVIEW
            elif TaskPart.STATUS.RETURNED in statuses:
                new_status = Task.STATUS.RETURNED
            elif TaskPart.STATUS.IN_PROGRESS in statuses or TaskPart.STATUS.DONE in statuses:
                new_status = Task.STATUS.IN_PROGRESS
            else:
                new_status = Task.STATUS.NEW

        old_status = self.status

        if old_status != new_status:
            self.status = new_status
            if save:
                self.save(update_fields=['status', 'updated_time'])

            # ✅ Task IN_PROGRESS bo‘lganda signed_by ga email
            if new_status == Task.STATUS.IN_PROGRESS and self.signed_by and self.signed_by.email:
                send_new_task_assigned_email(
                    to_email=self.signed_by.email,
                    task_name=self.name or f"Task#{self.pk}",
                    part_title="",
                    task_id=self.pk
                )

        return self.status


class TaskPart(BaseModel):
    """Task bo‘lagi (bo‘lim/subtask): har bir qism 1 ijrochiga biriktiriladi, muddat va status alohida yuradi."""

    class STATUS(models.TextChoices):
        NEW = 'new', _('New')
        IN_PROGRESS = 'in_progress', _('In progress')
        ON_REVIEW = 'on_review', _('On review')
        RETURNED = 'returned', _('Returned')
        DONE = 'done', _('Done')
        CANCELLED = 'cancelled', _('Cancelled')
        EXPIRED = 'expired', _('Expired')

    task = models.ForeignKey(Task, related_name='parts', on_delete=models.CASCADE)
    title = models.CharField(_('Section / Part title'), max_length=255, help_text=_("Bo‘lim nomi"))
    department = models.ForeignKey(
        Department, related_name='task_parts',
        on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Bo‘lim")
    )
    assignee = models.ForeignKey(
        User, related_name='task_parts_assigned',
        on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Ijrochi")
    )
    start_date = models.DateTimeField(_('Start date'), null=True, blank=True, help_text=_("Boshlash sanasi/vaqti"))
    end_date = models.DateTimeField(_('End date'), null=True, blank=True, help_text=_("Tugash sanasi/vaqti"))
    status = models.CharField(choices=STATUS.choices, max_length=20, default=STATUS.NEW, help_text=_("Holati"))
    show_date = models.DateTimeField(_('Show date'), null=True, blank=True, help_text=_("Ko'rish vaqti sanasi"))
    note = models.TextField(blank=True, help_text=_("Izoh"))

    class Meta:
        verbose_name = _('Task Part')
        verbose_name_plural = _('Task Parts')
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['assignee', 'status'])
        ]

    def __str__(self):
        return f"{self.task_id} :: {self.title}"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be earlier than start date."))

    # ==========
    # EMAIL HELPERS
    # ==========
    def _collect_notify_emails(self) -> list:
        """
        Task IN_PROGRESS bo'lganda xabar yuboriladigan email'lar:
        - Task.signed_by.email
        - TaskPart.assignee.email
        """
        emails = set()

        # Task.signed_by
        try:
            signed_by = getattr(self.task, "signed_by", None)
            if signed_by and getattr(signed_by, "email", None):
                emails.add(signed_by.email.strip())
        except Exception:
            pass

        # TaskPart.assignee
        try:
            if self.assignee and getattr(self.assignee, "email", None):
                emails.add(self.assignee.email.strip())
        except Exception:
            pass

        # bo'shlarni olib tashlash
        emails = [e for e in emails if e]
        return emails

    def _send_in_progress_email(self):
        """
        'Sizga yangi task biriktirildi' xabari.
        SMTP muammosi bo'lsa save yiqilmasin (try/except tashqarida).
        """
        recipients = self._collect_notify_emails()
        if not recipients:
            return

        task_name = self.task.name or f"Task#{self.task_id}"
        subject = "Yangi task biriktirildi"
        message = (
            f"Assalomu alaykum!\n\n"
            f"Sizga yangi task biriktirildi.\n\n"
            f"Task: {task_name}\n"
            f"Bo'lim (TaskPart): {self.title}\n"
            f"Status: {self.status}\n\n"
            f"Iltimos tizimga kirib ko‘rib chiqing.\n\n"
            f"Link: https://doc.optivora-group.com/"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
            recipient_list=recipients,
            fail_silently=False,
        )

    def save(self, *args, actor=None, **kwargs):
        """actor berilsa logga kim o‘zgartirgani yoziladi."""
        old = TaskPart.objects.filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)

        if old is None:
            TaskEvent.log(
                task=self.task,
                part=self,
                actor=actor or self.created_by,
                event_type=TaskEvent.TYPE.PART_CREATED,
                message=f"Bo‘lim yaratildi: {self.title}",
                extra={"title": self.title, "assignee_id": self.assignee_id, "status": self.status}
            )
            if self.assignee_id:
                TaskEvent.log(
                    task=self.task,
                    part=self,
                    actor=actor or self.created_by,
                    event_type=TaskEvent.TYPE.ASSIGNED,
                    message="Ijrochiga biriktirildi",
                    extra={"assignee_id": self.assignee_id}
                )
        else:
            if old.assignee_id != self.assignee_id:
                TaskEvent.log(
                    task=self.task,
                    part=self,
                    actor=actor or self.updated_by,
                    event_type=TaskEvent.TYPE.ASSIGNED,
                    message="Ijrochi o‘zgardi",
                    extra={"from_assignee_id": old.assignee_id, "to_assignee_id": self.assignee_id}
                )
            if old.status != self.status:
                TaskEvent.log(
                    task=self.task,
                    part=self,
                    actor=actor or self.updated_by,
                    event_type=TaskEvent.TYPE.STATUS_CHANGED,
                    message="Status o‘zgardi",
                    from_status=old.status,
                    to_status=self.status
                )

        # parent task statusni yangilab turadi
        self.task.recompute_status(save=True)

        # =========================
        # EMAIL NOTIFICATION (LOGIKA BUZILMASIN)
        # =========================
        # TaskPart status IN_PROGRESS ga o'tgan paytda xabar yuborish
        try:
            just_changed_to_in_progress = (
                (old is not None) and (old.status != self.status) and (self.status == self.STATUS.IN_PROGRESS)
            )
            created_with_in_progress = (
                (old is None) and (self.status == self.STATUS.IN_PROGRESS)
            )

            if just_changed_to_in_progress or created_with_in_progress:
                self._send_in_progress_email()
        except Exception:
            # email xatosi save/logikani yiqitmasin
            pass

class TaskEvent(BaseModel):
    """Universal log: ‘Vazifalar tarixi’ va ‘Amalga oshirish jarayoni’ shu jadvaldan chiqadi."""
    class TYPE(models.TextChoices):
        CREATED = 'created', _('Created')
        UPDATED = 'updated', _('Updated')
        PART_CREATED = 'part_created', _('Part created')
        ASSIGNED = 'assigned', _('Assigned')
        STATUS_CHANGED = 'status_changed', _('Status changed')
        SENT_FOR_REVIEW = 'sent_for_review', _('Sent for review')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        RETURNED = 'returned', _('Returned')
        DONE = 'done', _('Done')
        CANCELLED = 'cancelled', _('Cancelled')
        FILE_ADDED = 'file_added', _('File added')
        COMMENTED = 'commented', _('Commented')
        EXPIRED = 'expired', _('Expired')

    task = models.ForeignKey(Task, related_name='events', on_delete=models.CASCADE, null=True, blank=True)
    part = models.ForeignKey(TaskPart, related_name='events', on_delete=models.SET_NULL, null=True, blank=True)
    actor = models.ForeignKey(User, related_name='task_events', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kim bajardi"))
    event_type = models.CharField(max_length=30, choices=TYPE.choices, help_text=_("Event turi"))
    message = models.CharField(max_length=500, blank=True, help_text=_("Xabar"))
    from_status = models.CharField(max_length=20, null=True, blank=True, help_text=_("Oldingi status"))
    to_status = models.CharField(max_length=20, null=True, blank=True, help_text=_("Yangi status"))
    extra = JSONField(default=dict, blank=True, help_text=_("Qo‘shimcha ma’lumot (JSON)"))

    class Meta:
        verbose_name = _('Task Event')
        verbose_name_plural = _('Task Events')
        ordering = ['-created_time']
        indexes = [models.Index(fields=['task', 'created_time']), models.Index(fields=['task', 'event_type'])]

    def __str__(self):
        return f"{self.task_id} - {self.event_type}"

    @staticmethod
    def log(*, task: Task, event_type: str, message: str = "", actor=None, part: TaskPart = None,
            from_status: str = None, to_status: str = None, extra: dict = None) -> "TaskEvent":
        return TaskEvent.objects.create(task=task, part=part, actor=actor, event_type=event_type,
                                        message=message or "", from_status=from_status, to_status=to_status, extra=extra or {})



class TaskComment(BaseModel):
    """Izohlar: UI’da chip/tag ko‘rinishida chiqarish mumkin, har biri tarixga (log) ham tushadi."""
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    part = models.ForeignKey(TaskPart, related_name='comments', on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(User, related_name='task_comments', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Muallif"))
    text = models.TextField(help_text=_("Izoh matni"))
    is_system = models.BooleanField(default=False, help_text=_("Sistemami?"))

    class Meta:
        verbose_name = _('Task Comment')
        verbose_name_plural = _('Task Comments')
        ordering = ['created_time']

    def __str__(self):
        return f"Comment#{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        TaskEvent.log(task=self.task, part=self.part, actor=self.author or self.created_by,
                      event_type=TaskEvent.TYPE.COMMENTED, message="Izoh qo‘shildi",
                      extra={"comment_id": self.pk, "text": (self.text or "")[:200]})



class TaskAttachment(BaseModel):
    """Fayl biriktirish: taskga yoki aniq partga hujjat (docx/pdf/...) qo‘shiladi va logga tushadi."""
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE, null=True, blank=True)
    part = models.ForeignKey(TaskPart, related_name='attachments', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(TaskComment, related_name='attachments', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True, help_text=_("Sarlavha"))
    file = models.FileField(upload_to='task_files/%Y/%m/%d/', null=True, blank=True, help_text=_("Fayl"))
    link = models.CharField(_('Link'), max_length=255, null=True, blank=True, help_text=_("Havola"))
    uploaded_by = models.ForeignKey(User, related_name='task_files', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Kim yukladi"))

    class Meta:
        verbose_name = _('Task Attachment')
        verbose_name_plural = _('Task Attachments')

    def __str__(self):
        return self.title or (self.file.name.split('/')[-1] if self.file else f"Attachment#{self.pk}")

    def save(self, *args, actor=None, **kwargs):
        super().save(*args, **kwargs)

        filename = None
        if self.file and getattr(self.file, "name", None):
            filename = self.file.name.split("/")[-1]

        # File bo'lsa file nomi, bo'lmasa link
        display = filename or (self.link or "")

        # file ham yo'q, link ham yo'q bo'lsa — log yozmaymiz
        if not display:
            return

        TaskEvent.log(
            task=self.task,
            part=self.part,
            actor=actor or self.uploaded_by or self.created_by,
            event_type=TaskEvent.TYPE.FILE_ADDED,
            message=f"Birikma qo‘shildi: {display}",
            extra={
                "attachment_id": self.pk,
                "file": (self.file.name if filename else None),
                "link": (self.link if self.link else None),
            }
        )


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
    organization = models.CharField(_('Organization'), max_length=100, null=True, blank=True,  help_text=_("Chiquvchi tashkilot"))
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
