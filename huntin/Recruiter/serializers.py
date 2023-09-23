from rest_framework import serializers
from User.serializers import CustomUserSerializer
from User.serializers import UserImageSerializer
from .models import RecruiterDetails,Wallet,JobPost
from User.models import CustomUser,UserFollowsCompany
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from User.models import UserImage



User = get_user_model()

class RecruiterDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterDetails
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class imageurlserializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ['id', 'image', 'uploaded_at', 'user']

    
class postcreationserializer(serializers.ModelSerializer):
   
    class Meta:
        model= JobPost
        fields = '__all__'

class companyfollower(serializers.ModelSerializer):
    class Meta:
       model= UserFollowsCompany
       fields = '__all__'

