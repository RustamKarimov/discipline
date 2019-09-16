from django.shortcuts import render, redirect

from rolepermissions.decorators import has_permission_decorator

from .models import Settings
from .forms import SettingsForm


@has_permission_decorator('admin')
def settings_form(request):
    """
    View to submit Settings. Redirection occurs according to call reference.
    If call was enforced by academic year add function it will redirect to that function.
    """
    instance = Settings.objects.all().first()

    form = SettingsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('dashboard')

    context = {
        'form': form,
        'active': 'settings'
    }

    return render(request, 'settings/settings_form.html', context)