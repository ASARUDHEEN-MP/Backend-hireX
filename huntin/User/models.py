from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models    
from django.utils import timezone
import string
import random
from django.contrib.auth import get_user_model

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phonenumber = models.CharField(max_length=15)
    is_superuser = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phonenumber']

    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        # If the user is new (not updating an existing user), generate and save OTP
        if not self.pk:
            self.otp = self.generate_otp()
            self.otp_created_at = timezone.now()

        super().save(*args, **kwargs)

    def is_otp_valid(self, otp):
        # Check if the provided OTP matches the stored OTP and is not expired (valid for 10 minutes)
        return self.otp == otp and timezone.now() <= self.otp_created_at + timezone.timedelta(minutes=10)

    def mark_email_verified(self):
        # Method to mark email as verified (you can implement this based on your requirements)
        self.email_verified = True
        self.save()

    def __str__(self):
        return self.email
    


class UserImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_images/')
    image_url = models.CharField(max_length=300, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.user.username}"
    
class Userdetails(models.Model):
   
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    current_position = models.TextField()
    worked_company =models.TextField()
    experience = models.CharField(max_length=35,)
    education = models.TextField()
    skills =  models.TextField()
    location = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    Expected_salary = models.DecimalField(
        max_digits=10,  # Total number of digits
        decimal_places=2,  # Number of decimal places
        null=True,  # Allow NULL values
        blank=True,  # Allow empty values
    )

    
    def __str__(self):
        return self.current_position
    


class UserFollowsCompany(models.Model):
    user = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    company = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)


class IgnoreJobPost(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ignorepostid = models.ForeignKey('Recruiter.JobPost', on_delete=models.CASCADE)

