from rest_framework import serializers
from app import models as cmodels
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from app.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
        email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)

    def create(self, validated_data):
        user = User(
        email=validated_data['email'],
        username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        try:
            wallet = Wallet.objects.get(user=user)
        except ObjectDoesNotExist:
            wallet = Wallet.objects.create(user=user)
        return user


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'


class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'
    
class UserTwoFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)


class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields =  '__all__'



class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields =  '__all__'



class RepliesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields =  '__all__'



class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True},}
