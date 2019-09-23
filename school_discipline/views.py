from django.shortcuts import render, redirect,reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

from school_discipline.roles import TeacherRole, LearnerRole
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_permission_decorator

from settings.models import Settings


class Login(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        url = self.get_redirect_url()

        if url:
            return url

        if user.is_superuser:
            return reverse('dashboard')

        if has_role(user, TeacherRole):
            return reverse('teachers:details', args=[user.teacher.slug])

        if has_role(user, LearnerRole):
            return reverse('learners:details', args=[user.learner.slug])


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
@has_permission_decorator('admin')
def dashboard(request):

    if not Settings.objects.first():
        Settings.objects.create()

    context = {
        'active': 'dashboard'
    }
    return render(request, 'dashboard.html', context)