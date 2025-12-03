from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = "Actualitza automàticament els estats dels esdeveniments"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        events = Event.objects.all()
        for event in events:
            if event.status == 'scheduled' and event.scheduled_date <= now:
                event.status = 'live'
                event.save()
                self.stdout.write(self.style.SUCCESS(f'Esdeveniment {event.title} ara està en directe'))
            elif event.status == 'live' and event.scheduled_date + event.get_duration_timedelta() <= now:
                event.status = 'finished'
                event.save()
                self.stdout.write(self.style.SUCCESS(f'Esdeveniment {event.title} finalitzat'))
