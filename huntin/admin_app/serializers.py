from rest_framework import serializers
from .models import post,Payment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = post
        fields = '__all__'



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'