from rest_framework import serializers
from .models import CustomUser,UserImage,Userdetails,IgnoreJobPost
from rest_framework import serializers, validators
from Recruiter.models import Applicants,JobPost


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'phonenumber', 'password', 'is_superuser', 'is_recruiter', 'date_joined', 'last_login', 'is_active', 'otp', 'otp_created_at','is_staff','is_employee')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'required': True,
                'allow_blank': False,
                'validators': [
                    validators.UniqueValidator(
                        CustomUser.objects.all(),
                        'A user with this email already exists. Please try with another one.'
                    )
                ]
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance
    
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage  # Replace with your actual UserImage model
        fields = '__all__' 

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userdetails
        fields = '__all__'

class Applicantserializer(serializers.ModelSerializer):
    class Meta:
        model = Applicants
        fields = '__all__'



class JobPostSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField()  # Change the field name here

    class Meta:
        model = JobPost
        fields = ('id', 'desgination', 'skills', 'vaccancies', 'location', 'user_image')  # Update the field name here

    def get_user_image(self, obj):  # Change the method name here
        try:
            user_image = UserImage.objects.get(user=obj.company)
            print(user_image.image_url)
            return user_image.image_url
        except UserImage.DoesNotExist:
            return None
        


class IsFollowingSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()


class IgnoreJobPostSerializer(serializers.Serializer):
    class Meta:
       model = IgnoreJobPost
       fields = '__all__'

