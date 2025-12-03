from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = "Actualitza automàticament l'estat dels esdeveniments"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        updated_count = 0

        events = Event.objects.all()
        for event in events:
            if event.status == 'scheduled' and event.scheduled_date <= now:
                event.status = 'live'
                event.save()
                updated_count += 1
            elif event.status == 'live' and event.scheduled_date <= now:
                # Si vols pots calcular durada i marcar com finished automàticament
                pass

        self.stdout.write(f"Events actualitzats: {updated_count}")
