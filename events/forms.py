from django import forms
from django.utils import timezone
from .models import Event

class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'scheduled_date',
            'thumbnail', 'max_viewers', 'tags', 'stream_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'class': 'form-control'
            }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']
        if scheduled_date < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return scheduled_date

    def clean_title(self):
        title = self.cleaned_data['title']
        user = self.instance.creator if self.instance.pk else self.initial.get('creator')
        if Event.objects.filter(title=title, creator=user).exists():
            raise forms.ValidationError("Ja tens un esdeveniment amb aquest títol.")
        return title

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data['max_viewers']
        if max_viewers < 1 or max_viewers > 1000:
            raise forms.ValidationError("El nombre màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'scheduled_date', 'thumbnail',
            'max_viewers', 'tags', 'status', 'stream_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'class': 'form-control'
            }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        status = cleaned_data.get('status')
        user = self.instance.creator

        # Només el creador pot canviar l'estat
        if self.initial.get('status') != status and self.initial.get('creator') != self.instance.creator:
            raise forms.ValidationError("Només el creador pot canviar l'estat.")

        # No es pot canviar la data si l'esdeveniment està en directe
        if self.instance.status == 'live' and scheduled_date != self.instance.scheduled_date:
            raise forms.ValidationError("No es pot canviar la data d'un esdeveniment en directe.")

        return cleaned_data


class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    category = forms.ChoiceField(
        choices=[('', 'Totes')] + Event.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Tots')] + Event.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
