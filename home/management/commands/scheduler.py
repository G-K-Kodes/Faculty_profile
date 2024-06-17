from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import Faculty_Login
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Checks and updates the expiry status of logins'

    def handle(self, *args, **options):
        current_time = timezone.now()
        expired_logins = Faculty_Login.objects.filter(edit_granted=True, edit_expiry_time__lte=current_time)
        
        for login in expired_logins:
            login.edit_granted = False
            login.edit_grant_time = None
            login.edit_expiry_time = None
            login.save()
            email=login.personaldetail.email_id
            firstname=login.personaldetail.first_name
            lastname=login.personaldetail.last_name
            subject = 'Edit access request expired'
            message = f'''Hello {firstname} {lastname}, the edit access of your account is expired at time {current_time}. 
            If you want to make more modifications, please consider making an edit access request from your page '''
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)