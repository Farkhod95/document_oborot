from django_filters.rest_framework import FilterSet

from users.models import User, Company


class UserFilter(FilterSet):

    class Meta:
        model = User
        fields = {
            'username': ['exact', 'startswith', 'contains'],
            'fullname': ['exact'],
            'gender': ['exact'],
            'roles': ['exact'],
            'roles__name': ['exact', 'iexact', 'contains', 'icontains', 'startswith'],
            'region': ['exact'],
            'district': ['exact'],
            'companies': ['exact'],
        }


class CompanyFilter(FilterSet):
    roles__name = django_filters.CharFilter(field_name='roles__name', lookup_expr='exact')

    class Meta:
        model = Company
        fields = {
            'code': ['exact', 'startswith', 'contains'],
            'name': ['exact'],
            'region': ['exact'],
            'district': ['exact'],
        }

