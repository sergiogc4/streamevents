from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pàgina principal provisional (pots canviar per una vista real)
    path('', TemplateView.as_view(template_name='base.html'), name='home'),

    # Rutes de l'app d'usuaris
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # Rutes d'autenticació estàndard de Django (password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Rutes de l'app events
    path('events/', include('events.urls', namespace='events')),
]

# Servir fitxers MEDIA (avatars) durant desenvolupament
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
