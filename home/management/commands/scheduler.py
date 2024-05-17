from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import Faculty_Login

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