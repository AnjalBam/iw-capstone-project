from django.contrib.auth import get_user_model

from rest_framework import serializers

from accounts.models.profile import Profile
from accounts.models.education import Education

User = get_user_model()


class EducationSerializer(serializers.ModelSerializer):
    """education model serializer"""

    class Meta:
        model = Education
        fields = [
            'semester',
            'year',
            'college',
            'faculty',
            'university'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """profile model serializer"""

    education = EducationSerializer()

    class Meta:
        model = Profile
        fields = [
            'contact_number',
            'address',
            'education',
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    serializer for registering user with valid
    profile and education
    """

    profile = UserProfileSerializer()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Confirm_Password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
            'profile'
        )

    def create(self, validated_data):
        """creating profile and education on creating user"""

        profile_data = validated_data.pop('profile')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        education_data = profile_data.pop('education')
        education = Education.objects.create(**education_data)
        Profile.objects.create(
            user=user,
            contact_number=profile_data['contact_number'],
            address=profile_data['address'],
            education=education
        )
        return user

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError("password doesn't match")
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    serializer for updating user with valid
    profile and education
    """

    profile = UserProfileSerializer()
    profile_pic = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_pic', 'profile')

    def update(self, instance, validated_data):
        """updating profile and education while updating user"""
        profile_data = validated_data.pop('profile')
        education_data = profile_data.pop('education')
        instance.username = validated_data['username']
        instance.email = validated_data['email']
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        profile_instance = Profile.objects.get(user=instance)
        profile_instance.contact_number = profile_data['contact_number']
        profile_instance.address = profile_data['address']
        profile_instance.profile_pic = validated_data.get('profile_pic')
        profile_instance.education.semester = education_data['semester']
        profile_instance.education.year = education_data['year']
        profile_instance.education.faculty = education_data['faculty']
        profile_instance.education.university = education_data['university']
        profile_instance.education.college = education_data['college']
        profile_instance.save()
        instance.save()
        return instance


from rest_framework import serializers
from django.contrib.auth.models import User

class ChangePasswordSerializer(serializers.Serializer):

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
