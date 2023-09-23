from django.db.models.signals import post_save
from django.dispatch import receiver
from .applicantmail import send_mail
from Recruiter.models import Applicants
from User.models import CustomUser
@receiver(post_save, sender=Applicants)
def send_thank_you_email(sender, instance, created, **kwargs):
    user_email = instance.user.email
    companyname=CustomUser.objects.get(id=instance.companyid)
    companyusername=companyname.username
    subject = 'Thank You for Applying'
    
    if created:
        message = f'Thank you for applying for the job with post ID: {instance.postid.skills}. to the {companyusername}'
        print(f'A new applicant was applied: {instance.user}, {instance.postid}')
    else:
        message = f'Your application status for post ID: {instance.postid.skills} has been updated to {instance.status} from the {companyusername} '
        print(f'An applicant was updated: {instance.user}, {instance.postid.skills}')

    from_email = 'hirexjobs66@gmail.com'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
