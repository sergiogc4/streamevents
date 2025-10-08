from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.apps import apps

from faker import Faker
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Genera usuaris de prova per l'aplicació StreamEvents (crea admin, grups i usuaris de prova)."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10, help="Nombre d'usuaris de prova a crear (per defecte: 10).")
        parser.add_argument("--clear", action="store_true", help="Elimina usuaris existents (excepte superusers).")
        parser.add_argument("--with-follows", action="store_true", help="Crea relacions de seguiment si existeix el model Follow.")

    def handle(self, *args, **options):
        faker = Faker("es_ES")
        num_users = options["users"]
        do_clear = options["clear"]
        with_follows = options["with_follows"]

        self.stdout.write(self.style.SUCCESS("🔧 Iniciant creació d'usuaris de prova..."))

        with transaction.atomic():
            # --- Neteja prèvia si cal
            if do_clear:
                # Obtenir tots els usuaris que no són superusuaris
                non_super_users = [u for u in User.objects.all() if not u.is_superuser]

                # Esborrar-los un per un
                for user in non_super_users:
                    user.delete()

                self.stdout.write(self.style.SUCCESS(f"🗑️ Esborrats {len(non_super_users)} usuaris de prova!"))


            # --- Crear grups
            groups = {}
            for name in ["Organitzadors", "Participants", "Moderadors"]:
                g, _ = Group.objects.get_or_create(name=name)
                groups[name] = g

            # --- Crear o assegurar superusuari
            admin_user, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@streamevents.com",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password("admin123")
            if hasattr(admin_user, "display_name"):
                admin_user.display_name = "🔧 Administrador"
            if hasattr(admin_user, "bio"):
                admin_user.bio = "Usuari administrador del sistema."
            admin_user.save()
            if created:
                self.stdout.write(self.style.SUCCESS("🔐 Superusuari 'admin' creat."))

            # --- Crear usuaris de prova
            created_users = []
            for i in range(1, num_users + 1):
                first = faker.first_name()
                last = faker.last_name()
                base_username = (first + last).lower().replace(" ", "")
                username = base_username
                count = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{count}"
                    count += 1

                email = f"{username}@streamevents.com"

                # Assignar rol
                if i % 5 == 0:
                    role, emoji = "Organitzadors", "🎯 "
                elif i % 3 == 0:
                    role, emoji = "Moderadors", "🛡️ "
                else:
                    role, emoji = "Participants", ""

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="password123",
                    first_name=first,
                    last_name=last,
                )
                if hasattr(user, "display_name"):
                    user.display_name = f"{emoji}{first} {last}"
                if hasattr(user, "bio"):
                    user.bio = faker.sentence()
                user.save()
                user.groups.add(groups[role])
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f"🆕 {username} → {role}"))

            # --- Crear follows si existeix el model
            follows_created = 0
            if with_follows:
                try:
                    Follow = apps.get_model("users", "Follow")
                    user_pool = created_users
                    if len(user_pool) > 1:
                        for _ in range(num_users):
                            a, b = random.sample(user_pool, 2)
                            Follow.objects.get_or_create(follower=a, following=b)
                            follows_created += 1
                        self.stdout.write(self.style.SUCCESS(f"🔗 {follows_created} follows creats."))
                    else:
                        self.stdout.write(self.style.WARNING("⚠️ Pocs usuaris per crear follows."))
                except LookupError:
                    self.stdout.write(self.style.WARNING("ℹ️ No existeix el model Follow."))

        # Evitar errors amb Djongo en el count
        all_users = User.objects.all()
        non_super_users = [u for u in all_users if not u.is_superuser]
        self.stdout.write(self.style.SUCCESS(f"🎉 Creats {len(non_super_users)} usuaris de prova!"))


       
