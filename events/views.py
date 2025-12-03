from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm

# -----------------------------
# 5.1 Vista de llistat d'esdeveniments
# -----------------------------
def event_list_view(request):
    events = Event.objects.all().order_by('-is_featured', '-created_at').select_related('creator')
    
    # Cerca i filtres
    form = EventSearchForm(request.GET or None)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            events = events.filter(title__icontains=search)
        if category:
            events = events.filter(category=category)
        if status:
            events = events.filter(status=status)
        if date_from:
            events = events.filter(scheduled_date__gte=date_from)
        if date_to:
            events = events.filter(scheduled_date__lte=date_to)
    
    # Paginació
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'events': page_obj,
        'form': form
    }
    return render(request, 'events/event_list.html', context)


# -----------------------------
# 5.2 Vista de detall d'esdeveniment
# -----------------------------
def event_detail_view(request, pk):
    event = get_object_or_404(Event.objects.select_related('creator'), pk=pk)
    is_creator = request.user == event.creator
    context = {
        'event': event,
        'is_creator': is_creator
    }
    return render(request, 'events/event_detail.html', context)


# -----------------------------
# 5.3 Vista de creació d'esdeveniment
# -----------------------------
@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            messages.success(request, "Esdeveniment creat correctament!")
            return redirect('events:event_detail', pk=event.pk)
        else:
            messages.error(request, "Hi ha errors al formulari. Revisa els camps.")
    else:
        form = EventCreationForm()
    return render(request, 'events/event_form.html', {'form': form})


# -----------------------------
# 5.4 Vista d'edició d'esdeveniment
# -----------------------------
@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.creator:
        messages.error(request, "Només el creador pot editar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Esdeveniment actualitzat correctament!")
            return redirect('events:event_detail', pk=event.pk)
        else:
            messages.error(request, "Hi ha errors al formulari. Revisa els camps.")
    else:
        form = EventUpdateForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'event': event})


# -----------------------------
# 5.5 Vista d'eliminació d'esdeveniment
# -----------------------------
@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.creator:
        messages.error(request, "Només el creador pot eliminar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Esdeveniment eliminat correctament!")
        return redirect('events:event_list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})


# -----------------------------
# 5.6 Vista d'esdeveniments de l'usuari
# -----------------------------
@login_required
def my_events_view(request):
    events = Event.objects.filter(creator=request.user).order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        events = events.filter(status=status_filter)
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'events': page_obj}
    return render(request, 'events/my_events.html', context)


# -----------------------------
# 5.7 Vista d'esdeveniments per categoria
# -----------------------------
def events_by_category_view(request, category):
    categories = [c[0] for c in Event.CATEGORY_CHOICES]
    if category not in categories:
        messages.error(request, "Categoria no vàlida.")
        return redirect('events:event_list')
    
    events = Event.objects.filter(category=category).order_by('-is_featured', '-created_at')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'events': page_obj, 'category': category}
    return render(request, 'events/event_list.html', context)
