from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_password(self, password) -> str:
        return make_password(password)


class UserShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForgotPassword
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'