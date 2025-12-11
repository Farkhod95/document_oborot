from django_filters.rest_framework import FilterSet

from directory.models import District, Region, Country


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
