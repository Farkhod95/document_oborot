from rest_framework import serializers

from directory.serializers import DepartmentSerializer, DocumentFormSerializer, ListOfMagazineSerializer
from docoborot.models import Command, CommandFile, ReplyLetter, ReplyLetterFile, EmployeeAccount
from users.serializers import CompanySerializer, UserDetailSerializer
from docoborot.models import Task, TaskPart, TaskEvent, TaskAttachment, TaskComment


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

    basis_en = serializers.CharField(allow_blank=False)
    basis_uz = serializers.CharField(allow_blank=False)
    basis_ru = serializers.CharField(allow_blank=False)

    comment_en = serializers.CharField(allow_blank=False)
    comment_uz = serializers.CharField(allow_blank=False)
    comment_ru = serializers.CharField(allow_blank=False)


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
    REQUIRED_BASES = {'name', 'title', 'subtitle', 'basis', 'comment'}  # muhim maydonlar

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


class CommandSerializer(LocaleSerializer):
    class Meta:
        model = Command
        fields = ('id', 'company', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru', 'created_time')


class CommandListSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = Command
        fields = ('id', 'company', 'company_detail', 'command_number', 'basis', 'basis_en', 'basis_uz', 'basis_ru', 'comment', 'comment_en', 'comment_uz', 'comment_ru', 'created_time')


class CommandFileSerializer(LocaleSerializer):
    class Meta:
        model = CommandFile
        fields = ('id', 'command', 'title', 'file')


class ReplyLetterSerializer(LocaleSerializer):
    class Meta:
        model = ReplyLetter
        fields = ('id', 'company', 'task', 'letter_number', 'responsible_person', 'basis', 'comment', 'organization')


class ReplyLetterListSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)
    responsible_person_detail = UserDetailSerializer(source='responsible_person', read_only=True)

    class Meta:
        model = ReplyLetter
        fields = ('id', 'company', 'company_detail', 'task', 'letter_number', 'responsible_person',
                  'responsible_person_detail', 'basis', 'comment', 'organization')


class ReplyLetterFileSerializer(LocaleSerializer):
    class Meta:
        model = ReplyLetterFile
        fields = ('id', 'reply_letter', 'title', 'file')


class TaskShortSerializer(LocaleSerializer):
    """Ichki detail uchun (TaskPart/TaskEvent/... da task_detail)"""
    company_detail = CompanySerializer(source='company', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)
    list_of_magazine_detail = ListOfMagazineSerializer(source='list_of_magazine', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'status', 'type', 'priority', 'company', 'company_detail', 'department', 'department_detail', 'list_of_magazine', 'list_of_magazine_detail', 'task_type')


class TaskPartShortSerializer(LocaleSerializer):
    """Ichki detail uchun (TaskEvent/Attachment/Comment da part_detail)"""
    assignee_detail = UserDetailSerializer(source='assignee', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = TaskPart
        fields = ('id', 'task', 'title', 'status', 'assignee', 'assignee_detail', 'department', 'department_detail', 'start_date', 'end_date', 'show_date')


class TaskSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)
    task_form_detail = DocumentFormSerializer(source='task_form', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)
    signed_by_detail = UserDetailSerializer(source='signed_by', read_only=True)
    list_of_magazine_detail = ListOfMagazineSerializer(source='list_of_magazine', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'status', 'company', 'company_detail', 'type', 'name', 'task_type',
            'task_form', 'task_form_detail', 'sending_org', 'input_doc_number', 'output_doc_number',
            'start_date', 'end_date', 'priority', 'sending_respon_person',
            'department', 'department_detail', 'signed_by', 'signed_by_detail', 'signed_date', 'note',
            'created_time', 'updated_time', 'created_by', 'updated_by', 'list_of_magazine', 'list_of_magazine_detail'
        )


class TaskPartSerializer(LocaleSerializer):
    task_detail = TaskShortSerializer(source='task', read_only=True)
    assignee_detail = UserDetailSerializer(source='assignee', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = TaskPart
        fields = (
            'id', 'task', 'task_detail', 'title', 'department', 'department_detail',
            'assignee', 'assignee_detail', 'start_date', 'end_date', 'status', 'note',
            'created_time', 'updated_time', 'created_by', 'updated_by', 'show_date'
        )


class TaskWithPartsSerializer(serializers.Serializer):
    task = TaskSerializer()
    parts = TaskPartSerializer(many=True)


class TaskEventSerializer(LocaleSerializer):
    task_detail = TaskShortSerializer(source='task', read_only=True)
    part_detail = TaskPartShortSerializer(source='part', read_only=True)
    actor_detail = UserDetailSerializer(source='actor', read_only=True)

    class Meta:
        model = TaskEvent
        fields = (
            'id', 'task', 'task_detail', 'part', 'part_detail', 'actor', 'actor_detail',
            'event_type', 'message', 'from_status', 'to_status', 'extra',
            'created_time', 'updated_time', 'created_by', 'updated_by',
        )


class TaskAttachmentSerializer(LocaleSerializer):
    task_detail = TaskShortSerializer(source='task', read_only=True)
    part_detail = TaskPartShortSerializer(source='part', read_only=True)
    uploaded_by_detail = UserDetailSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = (
            'id', 'task', 'task_detail', 'part', 'part_detail', 'comment', 'link',
            'title', 'file', 'uploaded_by', 'uploaded_by_detail',
            'created_time', 'updated_time', 'created_by', 'updated_by',
        )


class TaskCommentSerializer(LocaleSerializer):
    task_detail = TaskShortSerializer(source='task', read_only=True)
    part_detail = TaskPartShortSerializer(source='part', read_only=True)
    author_detail = UserDetailSerializer(source='author', read_only=True)

    class Meta:
        model = TaskComment
        fields = (
            'id', 'task', 'task_detail', 'part', 'part_detail',
            'author', 'author_detail', 'text', 'is_system',
            'created_time', 'updated_time', 'created_by', 'updated_by',
        )


class EmployeeAccountSerializer(LocaleSerializer):
    class Meta:
        model = EmployeeAccount
        fields = ('id', 'company', 'employee', 'date', 'type', 'comment')


class EmployeeAccountListSerializer(LocaleSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)
    employee_detail = UserDetailSerializer(source='employee', read_only=True)

    class Meta:
        model = EmployeeAccount
        fields = ('id', 'company', 'company_detail', 'employee', 'employee_detail', 'date', 'type', 'comment')