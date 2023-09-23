from django.db import models
from User.models import CustomUser

# Create your models here.

class post(models.Model):
    planid = models.AutoField(primary_key=True)
    postdescription = models.TextField()
    postprice = models.DecimalField(max_digits=10, decimal_places=2)
    postcount = models.PositiveIntegerField()
    createdat = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    

    
    def __str__(self):
        return self.postdescription


class Payment(models.Model):
    payment_id = models.CharField(primary_key=True, max_length=100)
    plan_id = models.ForeignKey(post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    createdat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id