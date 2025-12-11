from django_filters.rest_framework import FilterSet

from directory.models import District, Region, Country, Position, Department


class DistrictFilter(FilterSet):

    class Meta:
        model = District
        fields = {
            'code': ['exact'],
            'region': ['exact'],
        }


class CountryFilter(FilterSet):

    class Meta:
        model = Country
        fields = {
            'name': ['exact'],
            'code': ['exact'],
        }


class RegionFilter(FilterSet):

    class Meta:
        model = Region
        fields = {
            'name': ['exact'],
            'code': ['exact'],
        }


class PositionFilter(FilterSet):

    class Meta:
        model = Position
        fields = {
            'name': ['exact'],
            'department': ['exact'],
        }


class DepartmentFilter(FilterSet):

    class Meta:
        model = Department
        fields = {
            'name': ['exact'],
        }
