from django.core.management.base import BaseCommand
from zauth.models import auth_db, tokens_db, verificationSystem, userFields

class Command(BaseCommand):
    help = 'Cleans all authentication related database tables'

    def handle(self, *args, **kwargs):
        auth_db.objects.all().delete()
        tokens_db.objects.all().delete()
        verificationSystem.objects.all().delete()
        userFields.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleaned all auth tables'))