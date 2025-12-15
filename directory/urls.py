from django.urls import re_path, path

from .views.country import CountryView, CountryDetailView, CountryFieldInfoView
from .views.department import DepartmentView, DepartmentDetailView, DepartmentFieldInfoView
from .views.district import DistrictView, DistrictDetailView, DistrictFieldInfoView
from .views.document_form import DocumentFormView, DocumentFormDetailView, DocumentFormFieldInfoView
from .views.import_country import CountryFileImportView
from .views.list_of_magazine import ListOfMagazineView, ListOfMagazineDetailView, ListOfMagazineFieldInfoView
from .views.position import PositionView, PositionDetailView, PositionFieldInfoView
from .views.region import RegionView, RegionDetailView, RegionFieldInfoView

urlpatterns = [
    re_path(r'^country/$', CountryView.as_view(), name='country_view'),
    path('country/<int:pk>/', CountryDetailView.as_view(), name='country_detail_view'),
    path('country/fields/', CountryFieldInfoView.as_view(), name='country_fields_info'),
    path("country/import-from-file/", CountryFileImportView.as_view(),
             name="country-import-from-file"),

    re_path(r'^region/$', RegionView.as_view(), name='regions_view'),
    path('region/<int:pk>', RegionDetailView.as_view(), name='region_detail_view'),
    path('region/fields/', RegionFieldInfoView.as_view(), name='region_fields_info'),

    re_path(r'^district$', DistrictView.as_view(), name='districts_view'),
    path('district/<int:pk>', DistrictDetailView.as_view(), name='districts_detail_view'),
    path('district/fields/', DistrictFieldInfoView.as_view(), name='district_fields_info'),

    re_path(r'^department/$', DepartmentView.as_view(), name='department_view'),
    path('department/<int:pk>', DepartmentDetailView.as_view(), name='department_detail_view'),
    path('department/fields/', DepartmentFieldInfoView.as_view(), name='department_fields_info'),

    re_path(r'^position/$', PositionView.as_view(), name='position_view'),
    path('position/<int:pk>', PositionDetailView.as_view(), name='position_detail_view'),
    path('position/fields/', PositionFieldInfoView.as_view(), name='position_fields_info'),

    re_path(r'^document-form/$', DocumentFormView.as_view(), name='document_form_view'),
    path('document-form/<int:pk>', DocumentFormDetailView.as_view(), name='document_form_detail_view'),
    path('document-form/fields/', DocumentFormFieldInfoView.as_view(), name='document_form_fields_info'),

    re_path(r'^list-of-magazine/$', ListOfMagazineView.as_view(), name='list_of_magazines_view'),
    path('list-of-magazine/<int:pk>', ListOfMagazineDetailView.as_view(), name='list_of_magazines_detail_view'),
    path('list-of-magazine/fields/', ListOfMagazineFieldInfoView.as_view(), name='list_of_magazines_fields_info'),
]