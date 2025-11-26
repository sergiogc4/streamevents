from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import re

User = get_user_model()

class Event(models.Model):
    """
    Model per representar un esdeveniment de streaming.
    Gestiona tota la informació relacionada amb esdeveniments programats,
    en directe o finalitzats.
    """
    
    # Choices per Categories
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres'),
    ]
    
    # Choices per Estats
    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]
    
    # Camps del Model
    title = models.CharField(
        max_length=200,
        verbose_name='Títol',
        help_text='Títol de l\'esdeveniment'
    )
    
    description = models.TextField(
        verbose_name='Descripció',
        help_text='Descripció detallada de l\'esdeveniment'
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Creador'
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoria'
    )
    
    scheduled_date = models.DateTimeField(
        verbose_name='Data Programada',
        help_text='Data i hora de l\'esdeveniment'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Estat'
    )
    
    thumbnail = models.ImageField(
        upload_to='events/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Imatge de Portada'
    )
    
    max_viewers = models.PositiveIntegerField(
        default=100,
        verbose_name='Màxim Espectadors',
        help_text='Nombre màxim d\'espectadors permesos'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacat',
        help_text='Marcar com a esdeveniment destacat'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Creació'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualització'
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Etiquetes',
        help_text='Etiquetes separades per comes'
    )
    
    stream_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='URL del Streaming',
        help_text='URL del streaming o vídeo de demostració'
    )
    
    class Meta:
        ordering = ['-created_at']  # Més recent primer
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'
    
    def __str__(self):
        """Retorna el títol de l'esdeveniment"""
        return self.title
    
    def get_absolute_url(self):
        """URL per veure l'esdeveniment"""
        return reverse('events:event_detail', kwargs={'pk': self.pk})
    
    @property
    def is_live(self):
        """Property que retorna True si està en directe"""
        return self.status == 'live'
    
    @property
    def is_upcoming(self):
        """Property que retorna True si està programat per al futur"""
        return self.status == 'scheduled' and self.scheduled_date > timezone.now()
    
    def get_duration(self):
        """
        Mètode per calcular la durada prevista segons la categoria.
        Retorna la durada en minuts.
        """
        category_durations = {
            'gaming': 180,        # 3 hores
            'music': 90,          # 1.5 hores  
            'talk': 60,           # 1 hora
            'education': 120,     # 2 hores
            'sports': 150,        # 2.5 hores
            'entertainment': 120, # 2 hores
            'technology': 90,     # 1.5 hores
            'art': 120,           # 2 hores
            'other': 90,          # 1.5 hores
        }
        return category_durations.get(self.category, 90)
    
    def get_end_time(self):
        """Retorna la data i hora de finalització prevista"""
        duration_minutes = self.get_duration()
        return self.scheduled_date + timedelta(minutes=duration_minutes)
    
    def get_tags_list(self):
        """Retorna les etiquetes com a llista"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_stream_embed_url(self):
        """
        Converteix URLs de YouTube/Twitch a format embed.
        Retorna la URL embed o None si no és compatible.
        """
        if not self.stream_url:
            return None
        
        # YouTube URLs
        youtube_regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]+)'
        youtube_match = re.search(youtube_regex, self.stream_url)
        if youtube_match:
            video_id = youtube_match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
        
        # Twitch URLs
        twitch_regex = r'(?:https?:\/\/)?(?:www\.)?twitch\.tv\/videos\/(\d+)'
        twitch_match = re.search(twitch_regex, self.stream_url)
        if twitch_match:
            video_id = twitch_match.group(1)
            return f'https://player.twitch.tv/?video={video_id}&parent=localhost'
        
        # Twitch Channel URLs
        twitch_channel_regex = r'(?:https?:\/\/)?(?:www\.)?twitch\.tv\/([a-zA-Z0-9_]+)$'
        twitch_channel_match = re.search(twitch_channel_regex, self.stream_url)
        if twitch_channel_match:
            channel = twitch_channel_match.group(1)
            return f'https://player.twitch.tv/?channel={channel}&parent=localhost'
        
        # Si ja és una URL embed, retornar-la directament
        if 'embed' in self.stream_url or 'player' in self.stream_url:
            return self.stream_url
        
        return None