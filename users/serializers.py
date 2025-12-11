from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from directory.serializers import RegionListSerializer, DistrictSerializer, CountrySerializer, DistrictListSerializer

from .models import User, Role, AppModule, Company


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class CompanySerializer(serializers.Serializer):
    class Meta:
        model = Company
        fields = ('id', 'code', 'name', 'is_active', 'phone', 'region', 'district', 'address', 'created_time', 'created_by')
        extra_kwargs = {
            'code': {"required": True},
            'name': {"required": True},
        }


class CompanyListSerializer(serializers.Serializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'code', 'name', 'is_active', 'phone', 'region', 'region_detail', 'district', 'district_detail',
                  'address', 'created_time', 'created_by')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(style={'input_type': 'username'})
    password = serializers.CharField(style={'input_type': 'password'})


class UserSerializer(serializers.ModelSerializer):
    # roles = RoleSerializer(source='role', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'fullname', 'is_active', 'date_of_birthday', 'gender', 'phone_number', 'avatar', 'email',
            'date_joined', 'role', 'password', 'region', 'district', 'address', 'avatar')
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator(), UniqueValidator(queryset=User.objects.all())],
            }
        }

    def create(self, validated_data, null=None):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.password = make_password(password)
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data, ):
        instance.username = validated_data.get("username", instance.username)
        instance.fullname = validated_data.get("fullname", instance.fullname)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.date_of_birthday = validated_data.get("date_of_birthday", instance.date_of_birthday)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.email = validated_data.get("email", instance.email)
        instance.date_joined = validated_data.get("date_joined", instance.date_joined)
        instance.role = validated_data.get("role", instance.role)
        # instance.roles = validated_data.get("roles", instance.roles)
        instance.region = validated_data.get("region", instance.region)
        instance.district = validated_data.get("district", instance.district)
        instance.address = validated_data.get("address", instance.address)
        password = validated_data.get("password", instance.password)
        if password:
            instance.password = make_password(password)
        else:
            instance.password = instance.password
        instance.save()
        return instance


class UserListPublicSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictSerializer(source='district', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'fullname', 'is_active', 'date_of_birthday', 'gender', 'phone_number', 'avatar', 'email',
            'date_joined', 'role', 'roles', 'password', 'region', 'region_detail', 'district', 'district_detail', 'address',
            'avatar')

class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'fullname', 'date_of_birthday', 'gender', 'phone_number',)


class UserListSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'fullname', 'is_active', 'date_of_birthday', 'gender', 'phone_number', 'avatar', 'email',
            'date_joined', 'role', 'roles', 'password', 'region', 'district', 'address', 'avatar')


class RelatedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator(), UniqueValidator(queryset=User.objects.all())],
            }
        }


class RelatedUserPutSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'username': {
                'validators': [],
            }
        }


class ContentTypeSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField(method_name='get_permissions')

    class Meta:
        model = ContentType
        fields = ('id', 'model', 'permissions')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if hasattr(instance, 'extendedcontenttype'):
            ret['model'] = instance.extendedcontenttype.extend_name.upper()
        else:
            ret['model'] = ret['model'].upper()
        return ret

    def get_permissions(self, instance):
        permissions = Permission.objects.filter(content_type=instance.id)
        result = []
        for p in permissions:
            result.append(
                {"id": p.id, "name": p.codename.split('_')[0].upper()}
            )
        return result


class AppModuleSerializer(serializers.ModelSerializer):
    modules = ContentTypeSerializer(source='content_types', read_only=True, many=True)

    class Meta:
        model = AppModule
        fields = ('id', 'name', 'modules', 'sorting')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()
        return instance

