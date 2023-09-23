from django.db import models
from User.models import CustomUser


class RecruiterDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    companyregno = models.CharField(max_length=100, blank=True)
    about_us = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.state


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    post_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Wallet for {self.user.username}"
    

class JobPost(models.Model):
    company = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    desgination = models.CharField(blank=True)
    skills = models.TextField(blank=True)
    vaccancies = models.IntegerField(blank=True,null=True)
    location = models.TextField(blank=True)
    Type = models.CharField(blank=True)
    workmode = models.CharField(blank=True)
    experience_from = models.CharField(blank=True)
    experience_to = models.CharField(blank=True)
    job_description = models.TextField()
    criteria = models.CharField(blank=True)
    payscale_from = models.CharField(blank=True)
    payscale_to = models.CharField(blank=True)
    hired_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) 


class Applicants(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reject', 'Reject'),
        ('interview', 'Interview'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    postid = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    companyid = models.IntegerField(blank=False,null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES ,default='applied')
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.status
